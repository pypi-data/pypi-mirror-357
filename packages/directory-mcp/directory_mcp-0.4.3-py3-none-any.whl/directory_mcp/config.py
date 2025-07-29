"""Configuration management for Directory MCP."""
import os
from pathlib import Path
from typing import Optional
import json

class Config:
    """Configuration manager for Directory MCP."""
    
    def __init__(self):
        # Base paths
        self.home_dir = Path.home()
        self.config_dir = self.home_dir / ".directory-mcp"
        self.config_file = self.config_dir / "config.json"
        self.db_path = self.config_dir / "directory.db"
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)
        
        # Load or create config
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file or create default."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
        else:
            config = self._create_default_config()
        
        # Set attributes from config
        self.gemini_api_key = config.get('gemini_api_key') or os.getenv('GEMINI_API_KEY')
        self.embedding_model = config.get('embedding_model', 'models/gemini-embedding-exp-03-07')
        self.similarity_threshold = config.get('similarity_threshold', 0.7)
        self.batch_size = config.get('batch_size', 100)
        self.cache_embeddings = config.get('cache_embeddings', True)
        
    def _create_default_config(self) -> dict:
        """Create default configuration."""
        config = {
            'gemini_api_key': None,
            'embedding_model': 'models/gemini-embedding-exp-03-07',
            'similarity_threshold': 0.7,
            'batch_size': 100,
            'cache_embeddings': True
        }
        
        # Save default config
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def save_api_key(self, api_key: str):
        """Save API key to config file."""
        # Load current config
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
        else:
            config = self._create_default_config()
        
        # Update API key
        config['gemini_api_key'] = api_key
        self.gemini_api_key = api_key
        
        # Save back to file
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def prompt_for_api_key(self) -> Optional[str]:
        """Prompt user for API key if not configured."""
        if self.gemini_api_key:
            return self.gemini_api_key
        
        print("\n🔑 Gemini API key not found!")
        print("Get your free API key at: https://makersuite.google.com/app/apikey")
        api_key = input("\nEnter your Gemini API key: ").strip()
        
        if api_key:
            self.save_api_key(api_key)
            print("✅ API key saved to ~/.directory-mcp/config.json")
            return api_key
        
        return None
    
    @property
    def is_configured(self) -> bool:
        """Check if the configuration is complete."""
        return bool(self.gemini_api_key)