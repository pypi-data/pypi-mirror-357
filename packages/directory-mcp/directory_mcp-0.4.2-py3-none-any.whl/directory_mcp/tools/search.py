"""Search and discovery tools for Directory MCP."""
from mcp.server.fastmcp import FastMCP

def register_search_tools(mcp: FastMCP, db, config, embedder):
    """Register search and discovery tools."""
    
    @mcp.tool()
    async def search_people(
        query: str,
        limit: int = 10
    ) -> dict:
        """Search for people in the directory using text search.
        
        Args:
            query: Search query (name, email, title, skills, etc.)
            limit: Maximum number of results to return (optional, defaults to 10)
        
        Returns:
            Dictionary with search results and metadata
        """
        try:
            if not query or not query.strip():
                return {
                    "success": False,
                    "error": "Search query is required and cannot be empty"
                }
            
            if limit <= 0 or limit > 100:
                limit = 10
            
            # Perform search
            results = await db.search_people(query.strip(), limit=limit)
            
            return {
                "success": True,
                "query": query.strip(),
                "results": results,
                "count": len(results),
                "limit": limit
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def find_people_by_criteria(
        company: str = None,
        title: str = None,
        skills: str = None,
        location: str = None,
        limit: int = 20
    ) -> dict:
        """Find people based on specific criteria like company, title, skills, or location.
        
        Args:
            company: Company name or domain to filter by (optional)
            title: Job title to search for (optional)
            skills: Skills to search for (optional)
            location: Location to filter by (optional)
            limit: Maximum number of results to return (optional, defaults to 20)
        
        Returns:
            Dictionary with filtered results and applied criteria
        """
        try:
            if not any([company, title, skills, location]):
                return {
                    "success": False,
                    "error": "At least one search criterion is required (company, title, skills, or location)"
                }
            
            if limit <= 0 or limit > 100:
                limit = 20
            
            # Build search criteria
            criteria = {}
            if company:
                criteria['company'] = company.strip()
            if title:
                criteria['title'] = title.strip()
            if skills:
                criteria['skills'] = skills.strip()
            if location:
                criteria['location'] = location.strip()
            
            # Perform filtered search
            results = await db.find_people_by_criteria(criteria, limit=limit)
            
            return {
                "success": True,
                "criteria": criteria,
                "results": results,
                "count": len(results),
                "limit": limit
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }