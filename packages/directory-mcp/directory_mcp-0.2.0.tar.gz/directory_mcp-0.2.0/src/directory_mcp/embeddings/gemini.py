"""Gemini embeddings module for Directory MCP."""
import hashlib
import json
import struct
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import asyncio

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)


class SmartEmbedder:
    """Smart embedder using Google's Gemini API with context building."""
    
    def __init__(self, api_key: str, db_manager=None):
        """Initialize the embedder with API key and optional database manager for caching.
        
        Args:
            api_key: Google AI API key for Gemini
            db_manager: Optional DatabaseManager instance for caching embeddings
        """
        if not genai:
            raise ImportError("google-generativeai package is required. Install with: pip install google-generativeai")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.embedding_model = "models/text-embedding-004"
        self.db = db_manager
        self._rate_limit_delay = 0.1  # 100ms between requests
        self._last_request_time = None
        self._batch_size = 100  # Max texts per batch
        
        logger.info("SmartEmbedder initialized with Gemini API")
    
    def _compute_text_hash(self, text: str) -> str:
        """Compute SHA256 hash of text for caching."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def _serialize_embedding(self, embedding: List[float]) -> bytes:
        """Serialize embedding vector to bytes for storage."""
        # Store as float32 array (4 bytes per float)
        return struct.pack(f'{len(embedding)}f', *embedding)
    
    def _deserialize_embedding(self, data: bytes) -> List[float]:
        """Deserialize embedding bytes back to float list."""
        # Assuming 768-dimensional embeddings (text-embedding-004)
        num_floats = len(data) // 4
        return list(struct.unpack(f'{num_floats}f', data))
    
    async def _check_cache(self, text: str) -> Optional[bytes]:
        """Check if embedding exists in cache."""
        if not self.db:
            return None
        
        text_hash = self._compute_text_hash(text)
        
        try:
            result = await self.db.execute_query(
                "SELECT vector FROM embedding_cache WHERE text_hash = ? AND model = ?",
                (text_hash, self.embedding_model)
            )
            
            if result:
                logger.debug(f"Cache hit for text hash: {text_hash[:8]}...")
                return result[0]['vector']
                
        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
        
        return None
    
    async def _store_cache(self, text: str, vector: bytes) -> None:
        """Store embedding in cache."""
        if not self.db:
            return
        
        text_hash = self._compute_text_hash(text)
        
        try:
            await self.db.execute_insert(
                """
                INSERT OR REPLACE INTO embedding_cache (text_hash, text, vector, model)
                VALUES (?, ?, ?, ?)
                """,
                (text_hash, text, vector, self.embedding_model)
            )
            logger.debug(f"Cached embedding for text hash: {text_hash[:8]}...")
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")
    
    async def _rate_limit(self):
        """Apply rate limiting between API calls."""
        if self._last_request_time:
            elapsed = datetime.now() - self._last_request_time
            if elapsed < timedelta(seconds=self._rate_limit_delay):
                await asyncio.sleep(self._rate_limit_delay - elapsed.total_seconds())
        
        self._last_request_time = datetime.now()
    
    async def embed_text(self, text: str, use_cache: bool = True) -> bytes:
        """Generate embedding for a single text.
        
        Args:
            text: The text to embed
            use_cache: Whether to use cached embeddings if available
            
        Returns:
            Serialized embedding vector as bytes
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return self._serialize_embedding([0.0] * 768)
        
        # Check cache first
        if use_cache:
            cached = await self._check_cache(text)
            if cached:
                return cached
        
        # Rate limiting
        await self._rate_limit()
        
        try:
            # Generate embedding using Gemini
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document"
            )
            
            embedding = result['embedding']
            vector_bytes = self._serialize_embedding(embedding)
            
            # Store in cache
            if use_cache:
                await self._store_cache(text, vector_bytes)
            
            return vector_bytes
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            # Return zero vector on failure
            return self._serialize_embedding([0.0] * 768)
    
    async def batch_embed(self, texts: List[str], use_cache: bool = True) -> List[bytes]:
        """Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            use_cache: Whether to use cached embeddings
            
        Returns:
            List of serialized embedding vectors
        """
        results = []
        
        # Process in batches
        for i in range(0, len(texts), self._batch_size):
            batch = texts[i:i + self._batch_size]
            batch_results = []
            
            for text in batch:
                embedding = await self.embed_text(text, use_cache)
                batch_results.append(embedding)
            
            results.extend(batch_results)
            
            # Extra delay between batches
            if i + self._batch_size < len(texts):
                await asyncio.sleep(1.0)
        
        return results
    
    def build_person_context(self, person_data: Dict[str, Any]) -> str:
        """Build contextual text representation of a person.
        
        Creates a rich text representation that captures:
        - Names and aliases
        - Professional information
        - Contact details
        - Skills and expertise
        - Biographical information
        """
        parts = []
        
        # Names and aliases
        names = person_data.get('names', [])
        if isinstance(names, str):
            names = json.loads(names)
        if names:
            parts.append(f"Name: {', '.join(names)}")
        
        aliases = person_data.get('aliases', [])
        if isinstance(aliases, str):
            aliases = json.loads(aliases)
        if aliases:
            parts.append(f"Also known as: {', '.join(aliases)}")
        
        # Professional info
        if person_data.get('title'):
            parts.append(f"Title: {person_data['title']}")
        
        if person_data.get('department'):
            parts.append(f"Department: {person_data['department']}")
        
        if person_data.get('company_name'):
            parts.append(f"Company: {person_data['company_name']}")
        
        # Contact info
        if person_data.get('email'):
            parts.append(f"Email: {person_data['email']}")
        
        handles = person_data.get('handles', {})
        if isinstance(handles, str):
            handles = json.loads(handles)
        if handles:
            handle_strs = [f"{platform}: {handle}" for platform, handle in handles.items()]
            parts.append(f"Handles: {', '.join(handle_strs)}")
        
        # Location
        if person_data.get('location'):
            parts.append(f"Location: {person_data['location']}")
        
        if person_data.get('timezone'):
            parts.append(f"Timezone: {person_data['timezone']}")
        
        # Skills
        skills = person_data.get('skills', [])
        if isinstance(skills, str):
            skills = json.loads(skills)
        if skills:
            parts.append(f"Skills: {', '.join(skills)}")
        
        # Bio
        if person_data.get('bio'):
            parts.append(f"Bio: {person_data['bio']}")
        
        return ' | '.join(parts)
    
    def build_company_context(self, company_data: Dict[str, Any]) -> str:
        """Build contextual text representation of a company."""
        parts = []
        
        # Basic info
        if company_data.get('name'):
            parts.append(f"Company: {company_data['name']}")
        
        if company_data.get('domain'):
            parts.append(f"Domain: {company_data['domain']}")
        
        domains = company_data.get('domains', [])
        if isinstance(domains, str):
            domains = json.loads(domains)
        if domains:
            parts.append(f"Other domains: {', '.join(domains)}")
        
        # Details
        if company_data.get('industry'):
            parts.append(f"Industry: {company_data['industry']}")
        
        if company_data.get('size'):
            parts.append(f"Size: {company_data['size']}")
        
        if company_data.get('location_hq'):
            parts.append(f"HQ: {company_data['location_hq']}")
        
        # Tags
        tags = company_data.get('tags', [])
        if isinstance(tags, str):
            tags = json.loads(tags)
        if tags:
            parts.append(f"Tags: {', '.join(tags)}")
        
        # Description
        if company_data.get('description'):
            parts.append(f"Description: {company_data['description']}")
        
        return ' | '.join(parts)
    
    def build_channel_context(self, channel_data: Dict[str, Any]) -> str:
        """Build contextual text representation of a channel."""
        parts = []
        
        # Basic info
        if channel_data.get('name'):
            parts.append(f"Channel: {channel_data['name']}")
        
        if channel_data.get('platform'):
            parts.append(f"Platform: {channel_data['platform']}")
        
        if channel_data.get('type'):
            parts.append(f"Type: {channel_data['type']}")
        
        # Details
        if channel_data.get('purpose'):
            parts.append(f"Purpose: {channel_data['purpose']}")
        
        if channel_data.get('company_name'):
            parts.append(f"Company: {channel_data['company_name']}")
        
        if channel_data.get('project_name'):
            parts.append(f"Project: {channel_data['project_name']}")
        
        if channel_data.get('member_count'):
            parts.append(f"Members: {channel_data['member_count']}")
        
        if channel_data.get('is_active') is False:
            parts.append("Status: Inactive")
        
        return ' | '.join(parts)
    
    def build_project_context(self, project_data: Dict[str, Any]) -> str:
        """Build contextual text representation of a project."""
        parts = []
        
        # Basic info
        if project_data.get('name'):
            parts.append(f"Project: {project_data['name']}")
        
        if project_data.get('code'):
            parts.append(f"Code: {project_data['code']}")
        
        if project_data.get('status'):
            parts.append(f"Status: {project_data['status']}")
        
        # Details
        if project_data.get('company_name'):
            parts.append(f"Company: {project_data['company_name']}")
        
        if project_data.get('lead_name'):
            parts.append(f"Lead: {project_data['lead_name']}")
        
        # Dates
        if project_data.get('start_date'):
            parts.append(f"Start: {project_data['start_date']}")
        
        if project_data.get('end_date'):
            parts.append(f"End: {project_data['end_date']}")
        
        # Tags
        tags = project_data.get('tags', [])
        if isinstance(tags, str):
            tags = json.loads(tags)
        if tags:
            parts.append(f"Tags: {', '.join(tags)}")
        
        # URLs
        urls = project_data.get('urls', {})
        if isinstance(urls, str):
            urls = json.loads(urls)
        if urls:
            url_strs = [f"{name}: {url}" for name, url in urls.items()]
            parts.append(f"Links: {', '.join(url_strs)}")
        
        # Description
        if project_data.get('description'):
            parts.append(f"Description: {project_data['description']}")
        
        return ' | '.join(parts)
    
    async def embed_person(self, person_data: Dict[str, Any]) -> bytes:
        """Generate embedding for a person entity."""
        context = self.build_person_context(person_data)
        return await self.embed_text(context)
    
    async def embed_company(self, company_data: Dict[str, Any]) -> bytes:
        """Generate embedding for a company entity."""
        context = self.build_company_context(company_data)
        return await self.embed_text(context)
    
    async def embed_channel(self, channel_data: Dict[str, Any]) -> bytes:
        """Generate embedding for a channel entity."""
        context = self.build_channel_context(channel_data)
        return await self.embed_text(context)
    
    async def embed_project(self, project_data: Dict[str, Any]) -> bytes:
        """Generate embedding for a project entity."""
        context = self.build_project_context(project_data)
        return await self.embed_text(context)