"""MCP server implementation for Directory."""
import os
import sys
from mcp.server.fastmcp import FastMCP

from .config import Config
from .database.manager import DatabaseManager
from .embeddings.gemini import SmartEmbedder
from .tools import register_all_tools

# Initialize FastMCP server
mcp = FastMCP("directory-mcp", version="0.4.0")

# Global instances
db = None
config = None
embedder = None

async def initialize():
    """Initialize the server components."""
    global db, config, embedder
    
    # Initialize configuration
    config = Config()
    
    # Verify API key
    if not config.gemini_api_key:
        print("❌ GEMINI_API_KEY environment variable is required", file=sys.stderr)
        print("Set it with: export GEMINI_API_KEY=your_api_key_here", file=sys.stderr)
        sys.exit(1)
    
    # Initialize database
    db = DatabaseManager(config.db_path)
    await db.initialize()
    
    # Initialize embedder
    embedder = SmartEmbedder(config.gemini_api_key, db)
    
    # Register all tools
    register_all_tools(mcp, db, config, embedder)

# Note: get_directory_status is now defined in tools/system.py

def run_server():
    """Run the MCP server."""
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\nShutting down Directory MCP server...")
    except Exception as e:
        print(f"Error running server: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_server()