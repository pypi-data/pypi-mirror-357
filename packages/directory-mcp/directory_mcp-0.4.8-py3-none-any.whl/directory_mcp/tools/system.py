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
            
            # Get basic database stats
            stats = {}
            if db:
                try:
                    # Count entities in each table
                    person_count = await db.execute_query("SELECT COUNT(*) as count FROM person")
                    company_count = await db.execute_query("SELECT COUNT(*) as count FROM company") 
                    channel_count = await db.execute_query("SELECT COUNT(*) as count FROM channel")
                    project_count = await db.execute_query("SELECT COUNT(*) as count FROM project")
                    
                    stats = {
                        "people": person_count[0]["count"] if person_count else 0,
                        "companies": company_count[0]["count"] if company_count else 0,
                        "channels": channel_count[0]["count"] if channel_count else 0,
                        "projects": project_count[0]["count"] if project_count else 0
                    }
                except Exception as e:
                    stats = {"error": f"Could not retrieve stats: {str(e)}"}
            
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