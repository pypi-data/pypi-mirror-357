"""MCP server implementation for Directory v0.4.27."""
import os
import sys
import asyncio
from mcp.server.fastmcp import FastMCP

from .config import Config
from .database.manager import DatabaseManager
from .embeddings.gemini import SmartEmbedder
from .tools import register_all_tools

# Initialize configuration early
config = Config()

# Verify API key early
if not config.gemini_api_key:
    print("❌ GEMINI_API_KEY environment variable is required", file=sys.stderr)
    print("Set it with: export GEMINI_API_KEY=your_api_key_here", file=sys.stderr)
    sys.exit(1)

# Initialize FastMCP server
# Name must match the MCP registration in Claude (from 'claude mcp list')
mcp = FastMCP("directory", version="0.4.27")

# Initialize components synchronously where possible
db = DatabaseManager(config.db_path)
embedder = SmartEmbedder(config.gemini_api_key, db)

# Register all tools with the initialized components
register_all_tools(mcp, db, config, embedder)

# Handle async database initialization
async def init_db():
    """Initialize database asynchronously."""
    await db.initialize()

# Run initialization before starting server
def run_server():
    """Run the MCP server."""
    try:
        # Initialize database
        asyncio.run(init_db())
        
        # Run the MCP server with stdio transport (default)
        mcp.run()
    except KeyboardInterrupt:
        print("\nShutting down Directory MCP server...")
    except Exception as e:
        print(f"Error running server: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_server()