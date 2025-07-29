"""Database manager for Directory MCP."""
import aiosqlite
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from contextlib import asynccontextmanager
import logging

from .schema import SCHEMA

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages all database operations."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._connection = None
    
    async def initialize(self):
        """Initialize the database with schema."""
        # Create parent directory if it doesn't exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Execute schema
        async with self._get_connection() as conn:
            await conn.executescript(SCHEMA)
            await conn.commit()
        
        logger.info(f"Database initialized at {self.db_path}")
    
    @asynccontextmanager
    async def _get_connection(self):
        """Get a database connection with proper context management."""
        conn = await aiosqlite.connect(str(self.db_path))
        conn.row_factory = aiosqlite.Row
        try:
            yield conn
        finally:
            await conn.close()
    
    async def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dicts."""
        async with self._get_connection() as conn:
            async with conn.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an update query and return affected rows."""
        async with self._get_connection() as conn:
            cursor = await conn.execute(query, params)
            await conn.commit()
            return cursor.rowcount
    
    async def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an insert query and return the last row id."""
        async with self._get_connection() as conn:
            cursor = await conn.execute(query, params)
            await conn.commit()
            return cursor.lastrowid
    
    # Person CRUD operations
    async def create_person(
        self,
        names: List[str],
        email: Optional[str] = None,
        secondary_emails: Optional[List[str]] = None,
        company_id: Optional[int] = None,
        title: Optional[str] = None,
        department: Optional[str] = None,
        location: Optional[str] = None,
        timezone: Optional[str] = None,
        handles: Optional[Dict[str, str]] = None,
        aliases: Optional[List[str]] = None,
        bio: Optional[str] = None,
        skills: Optional[List[str]] = None,
        vector: Optional[bytes] = None
    ) -> int:
        """Create a new person."""
        query = """
        INSERT INTO person (
            names, email, secondary_emails, company_id, title, department,
            location, timezone, handles, aliases, bio, skills, vector
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            json.dumps(names),
            email,
            json.dumps(secondary_emails or []),
            company_id,
            title,
            department,
            location,
            timezone,
            json.dumps(handles or {}),
            json.dumps(aliases or []),
            bio,
            json.dumps(skills or []),
            vector
        )
        
        person_id = await self.execute_insert(query, params)
        
        # Also insert primary email into email table if provided
        if email:
            await self.create_email(email, person_id, is_primary=True)
        
        # Insert secondary emails
        for sec_email in (secondary_emails or []):
            await self.create_email(sec_email, person_id, is_primary=False)
        
        return person_id
    
    async def get_person(self, person_id: int) -> Optional[Dict[str, Any]]:
        """Get a person by ID."""
        query = "SELECT * FROM person WHERE person_id = ?"
        results = await self.execute_query(query, (person_id,))
        if results:
            person = results[0]
            # Parse JSON fields
            person['names'] = json.loads(person['names'])
            person['secondary_emails'] = json.loads(person['secondary_emails'])
            person['handles'] = json.loads(person['handles'])
            person['aliases'] = json.loads(person['aliases'])
            person['skills'] = json.loads(person['skills'])
            return person
        return None
    
    async def update_person(self, person_id: int, **kwargs) -> bool:
        """Update a person's data."""
        # Convert lists/dicts to JSON
        json_fields = ['names', 'secondary_emails', 'handles', 'aliases', 'skills']
        for field in json_fields:
            if field in kwargs and kwargs[field] is not None:
                kwargs[field] = json.dumps(kwargs[field])
        
        # Build update query
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        
        if not fields:
            return False
        
        values.append(person_id)
        query = f"UPDATE person SET {', '.join(fields)} WHERE person_id = ?"
        
        affected = await self.execute_update(query, tuple(values))
        return affected > 0
    
    async def delete_person(self, person_id: int) -> bool:
        """Delete a person and related data."""
        # Delete from relationship tables first
        await self.execute_update("DELETE FROM person_company WHERE person_id = ?", (person_id,))
        await self.execute_update("DELETE FROM person_channel WHERE person_id = ?", (person_id,))
        await self.execute_update("DELETE FROM person_project WHERE person_id = ?", (person_id,))
        await self.execute_update("DELETE FROM email WHERE person_id = ?", (person_id,))
        
        # Delete the person
        query = "DELETE FROM person WHERE person_id = ?"
        affected = await self.execute_update(query, (person_id,))
        return affected > 0
    
    # Company CRUD operations
    async def create_company(
        self,
        name: str,
        domain: Optional[str] = None,
        domains: Optional[List[str]] = None,
        industry: Optional[str] = None,
        size: Optional[str] = None,
        location_hq: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        vector: Optional[bytes] = None
    ) -> int:
        """Create a new company."""
        query = """
        INSERT INTO company (
            name, domain, domains, industry, size, location_hq,
            description, tags, vector
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            name,
            domain,
            json.dumps(domains or []),
            industry,
            size,
            location_hq,
            description,
            json.dumps(tags or []),
            vector
        )
        
        return await self.execute_insert(query, params)
    
    async def get_company(self, company_id: int) -> Optional[Dict[str, Any]]:
        """Get a company by ID."""
        query = "SELECT * FROM company WHERE company_id = ?"
        results = await self.execute_query(query, (company_id,))
        if results:
            company = results[0]
            company['domains'] = json.loads(company['domains'])
            company['tags'] = json.loads(company['tags'])
            return company
        return None
    
    # Channel CRUD operations
    async def create_channel(
        self,
        platform: str,
        ext_id: str,
        name: Optional[str] = None,
        type: Optional[str] = None,
        purpose: Optional[str] = None,
        owner_id: Optional[int] = None,
        company_id: Optional[int] = None,
        project_id: Optional[int] = None,
        is_active: bool = True,
        member_count: Optional[int] = None,
        vector: Optional[bytes] = None
    ) -> int:
        """Create a new channel."""
        query = """
        INSERT INTO channel (
            platform, ext_id, name, type, purpose, owner_id,
            company_id, project_id, is_active, member_count, vector
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            platform, ext_id, name, type, purpose, owner_id,
            company_id, project_id, is_active, member_count, vector
        )
        
        return await self.execute_insert(query, params)
    
    async def get_channel(self, channel_id: int) -> Optional[Dict[str, Any]]:
        """Get a channel by ID."""
        query = "SELECT * FROM channel WHERE channel_id = ?"
        results = await self.execute_query(query, (channel_id,))
        return results[0] if results else None
    
    # Project CRUD operations
    async def create_project(
        self,
        name: str,
        code: Optional[str] = None,
        description: Optional[str] = None,
        status: str = 'active',
        company_id: Optional[int] = None,
        lead_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        tags: Optional[List[str]] = None,
        urls: Optional[Dict[str, str]] = None,
        vector: Optional[bytes] = None
    ) -> int:
        """Create a new project."""
        query = """
        INSERT INTO project (
            name, code, description, status, company_id, lead_id,
            start_date, end_date, tags, urls, vector
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            name, code, description, status, company_id, lead_id,
            start_date, end_date, json.dumps(tags or []),
            json.dumps(urls or {}), vector
        )
        
        return await self.execute_insert(query, params)
    
    async def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Get a project by ID."""
        query = "SELECT * FROM project WHERE project_id = ?"
        results = await self.execute_query(query, (project_id,))
        if results:
            project = results[0]
            project['tags'] = json.loads(project['tags'])
            project['urls'] = json.loads(project['urls'])
            return project
        return None
    
    # Email operations
    async def create_email(
        self,
        address: str,
        person_id: int,
        is_primary: bool = False,
        is_verified: bool = False
    ) -> int:
        """Create a new email record."""
        domain = address.split('@')[1] if '@' in address else None
        
        query = """
        INSERT INTO email (address, person_id, is_primary, is_verified, domain)
        VALUES (?, ?, ?, ?, ?)
        """
        
        params = (address, person_id, is_primary, is_verified, domain)
        
        try:
            return await self.execute_insert(query, params)
        except aiosqlite.IntegrityError:
            # Email already exists, update it
            update_query = """
            UPDATE email SET person_id = ?, is_primary = ?, is_verified = ?
            WHERE address = ?
            """
            await self.execute_update(update_query, (person_id, is_primary, is_verified, address))
            return 0
    
    # Relationship operations
    async def create_relationship(self, table: str, **kwargs) -> bool:
        """Create a relationship between entities."""
        fields = list(kwargs.keys())
        placeholders = ['?' for _ in fields]
        
        query = f"""
        INSERT INTO {table} ({', '.join(fields)})
        VALUES ({', '.join(placeholders)})
        """
        
        try:
            await self.execute_insert(query, tuple(kwargs.values()))
            return True
        except aiosqlite.IntegrityError:
            # Relationship already exists
            return False
    
    # Search operations
    async def search_entities(
        self,
        entity_type: str,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search entities using full-text search."""
        fts_table = f"{entity_type}_fts"
        
        search_query = f"""
        SELECT * FROM {entity_type}
        WHERE {entity_type}_id IN (
            SELECT {entity_type}_id FROM {fts_table}
            WHERE {fts_table} MATCH ?
            ORDER BY rank
            LIMIT ?
        )
        """
        
        results = await self.execute_query(search_query, (query, limit))
        
        # Parse JSON fields based on entity type
        for result in results:
            if entity_type == 'person':
                result['names'] = json.loads(result['names'])
                result['handles'] = json.loads(result['handles'])
                result['aliases'] = json.loads(result['aliases'])
                result['skills'] = json.loads(result['skills'])
                result['secondary_emails'] = json.loads(result['secondary_emails'])
            elif entity_type == 'company':
                result['domains'] = json.loads(result['domains'])
                result['tags'] = json.loads(result['tags'])
            elif entity_type == 'project':
                result['tags'] = json.loads(result['tags'])
                result['urls'] = json.loads(result['urls'])
        
        return results
    
    # Utility methods
    async def get_company_name(self, company_id: int) -> Optional[str]:
        """Get company name by ID."""
        query = "SELECT name FROM company WHERE company_id = ?"
        results = await self.execute_query(query, (company_id,))
        return results[0]['name'] if results else None
    
    async def get_project_name(self, project_id: int) -> Optional[str]:
        """Get project name by ID."""
        query = "SELECT name FROM project WHERE project_id = ?"
        results = await self.execute_query(query, (project_id,))
        return results[0]['name'] if results else None
    
    async def get_person_channels(self, person_id: int) -> List[Dict[str, Any]]:
        """Get all channels a person is in."""
        query = """
        SELECT c.*, pc.role, pc.joined_at, pc.is_active as membership_active
        FROM channel c
        JOIN person_channel pc ON c.channel_id = pc.channel_id
        WHERE pc.person_id = ?
        """
        return await self.execute_query(query, (person_id,))
    
    async def get_person_projects(self, person_id: int) -> List[Dict[str, Any]]:
        """Get all projects a person is involved in."""
        query = """
        SELECT p.*, pp.role, pp.allocation, pp.start_date, pp.end_date, pp.is_active
        FROM project p
        JOIN person_project pp ON p.project_id = pp.project_id
        WHERE pp.person_id = ?
        """
        results = await self.execute_query(query, (person_id,))
        for result in results:
            result['tags'] = json.loads(result['tags'])
            result['urls'] = json.loads(result['urls'])
        return results
    
    async def get_company_people(self, company_id: int, exclude_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all people in a company."""
        query = """
        SELECT p.*, pc.role, pc.is_current
        FROM person p
        JOIN person_company pc ON p.person_id = pc.person_id
        WHERE pc.company_id = ? AND pc.is_current = TRUE
        """
        params = [company_id]
        
        if exclude_id:
            query += " AND p.person_id != ?"
            params.append(exclude_id)
        
        results = await self.execute_query(query, tuple(params))
        for result in results:
            result['names'] = json.loads(result['names'])
            result['handles'] = json.loads(result['handles'])
            result['aliases'] = json.loads(result['aliases'])
            result['skills'] = json.loads(result['skills'])
            result['secondary_emails'] = json.loads(result['secondary_emails'])
        return results
    
    async def find_shared_channels(self, person1_id: int, person2_id: int) -> List[Dict[str, Any]]:
        """Find channels that two people share."""
        query = """
        SELECT c.*
        FROM channel c
        WHERE c.channel_id IN (
            SELECT channel_id FROM person_channel WHERE person_id = ? AND is_active = TRUE
            INTERSECT
            SELECT channel_id FROM person_channel WHERE person_id = ? AND is_active = TRUE
        )
        """
        return await self.execute_query(query, (person1_id, person2_id))
    
    async def find_shared_projects(self, person1_id: int, person2_id: int) -> List[Dict[str, Any]]:
        """Find projects that two people share."""
        query = """
        SELECT p.*
        FROM project p
        WHERE p.project_id IN (
            SELECT project_id FROM person_project WHERE person_id = ? AND is_active = TRUE
            INTERSECT
            SELECT project_id FROM person_project WHERE person_id = ? AND is_active = TRUE
        )
        """
        results = await self.execute_query(query, (person1_id, person2_id))
        for result in results:
            result['tags'] = json.loads(result['tags'])
            result['urls'] = json.loads(result['urls'])
        return results
    
    async def get_project_people(self, project_id: int) -> List[Dict[str, Any]]:
        """Get all people working on a project."""
        query = """
        SELECT p.*, pp.role, pp.allocation, pp.start_date, pp.end_date, pp.is_active
        FROM person p
        JOIN person_project pp ON p.person_id = pp.person_id
        WHERE pp.project_id = ?
        """
        results = await self.execute_query(query, (project_id,))
        for result in results:
            result['names'] = json.loads(result['names'])
            result['handles'] = json.loads(result['handles'])
            result['aliases'] = json.loads(result['aliases'])
            result['skills'] = json.loads(result['skills'])
            result['secondary_emails'] = json.loads(result['secondary_emails'])
        return results
    
    async def get_project_channels(self, project_id: int) -> List[Dict[str, Any]]:
        """Get all channels for a project."""
        query = "SELECT * FROM channel WHERE project_id = ?"
        return await self.execute_query(query, (project_id,))
    
    async def close(self):
        """Close database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None