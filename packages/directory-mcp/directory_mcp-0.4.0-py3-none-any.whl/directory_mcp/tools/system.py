"""System management tools for Directory MCP."""
from mcp.server.fastmcp import FastMCP

def register_system_tools(mcp: FastMCP, db, config, embedder):
    """Register system management tools."""
    
    @mcp.tool()
    async def get_directory_status() -> dict:
        """Get the current status of the Directory MCP server.
        
        Returns information about the database, embedder, and configuration.
        """
        try:
            # Check database status
            db_status = "connected" if db else "not initialized"
            
            # Check embedder status
            embedder_status = "available" if embedder else "not available"
            
            # Check configuration
            config_status = "loaded" if config else "not loaded"
            
            # Get database stats
            stats = {}
            if db:
                stats = await db.get_stats()
            
            return {
                "success": True,
                "status": "operational",
                "database": db_status,
                "embedder": embedder_status,
                "configuration": config_status,
                "statistics": stats,
                "version": "0.3.2"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }