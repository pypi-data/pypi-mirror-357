"""Project entity management tools for Directory MCP."""
from mcp.server.fastmcp import FastMCP

def register_project_tools(mcp: FastMCP, db, config, embedder):
    """Register project management tools."""
    
    @mcp.tool()
    async def create_project(
        name: str,
        description: str = None,
        status: str = "active",
        company: str = None,
        start_date: str = None,
        end_date: str = None,
        budget: float = None,
        priority: str = "medium"
    ) -> dict:
        """Create a new project in the directory.
        
        Args:
            name: Project name
            description: Project description or goals (optional)
            status: Project status ("active", "completed", "on-hold", "cancelled") (optional, defaults to "active")
            company: Associated company name, domain, or ID (optional)
            start_date: Project start date in YYYY-MM-DD format (optional)
            end_date: Project end date in YYYY-MM-DD format (optional)
            budget: Project budget amount (optional)
            priority: Project priority ("low", "medium", "high", "critical") (optional, defaults to "medium")
        
        Returns:
            Dictionary with success status and project details
        """
        try:
            if not name or not name.strip():
                return {
                    "success": False,
                    "error": "Project name is required and cannot be empty"
                }
            
            # Resolve company ID if provided
            company_id = None
            if company:
                from ...utils.resolver import resolve_company_id
                try:
                    company_id = await resolve_company_id(db, company)
                except ValueError:
                    # If company not found, continue without it
                    pass
            
            # Validate status
            valid_statuses = ["active", "completed", "on-hold", "cancelled"]
            if status and status.lower() not in valid_statuses:
                return {
                    "success": False,
                    "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                }
            
            # Validate priority
            valid_priorities = ["low", "medium", "high", "critical"]
            if priority and priority.lower() not in valid_priorities:
                return {
                    "success": False,
                    "error": f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"
                }
            
            # Generate embedding if embedder is available
            embedding = None
            if embedder:
                # Create text for embedding from available fields
                text_parts = [name]
                if description:
                    text_parts.append(description)
                if status:
                    text_parts.append(status)
                if priority:
                    text_parts.append(priority)
                
                text_for_embedding = " ".join(text_parts)
                embedding = await embedder.embed_text(text_for_embedding)
            
            # Create project in database
            project_id = await db.create_project(
                name=name.strip(),
                description=description.strip() if description else None,
                status=status.lower() if status else "active",
                company_id=company_id,
                start_date=start_date.strip() if start_date else None,
                end_date=end_date.strip() if end_date else None,
                budget=budget,
                priority=priority.lower() if priority else "medium",
                embedding=embedding
            )
            
            # Get the created project
            project = await db.get_project(project_id)
            
            return {
                "success": True,
                "project": project,
                "message": f"Successfully created project: {name}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }