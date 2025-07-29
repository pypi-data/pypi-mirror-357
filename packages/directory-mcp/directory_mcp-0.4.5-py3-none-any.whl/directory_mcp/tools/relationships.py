"""Relationship management tools for Directory MCP."""
from mcp.server.fastmcp import FastMCP

def register_relationship_tools(mcp: FastMCP, db, config, embedder):
    """Register relationship management tools."""
    
    @mcp.tool()
    async def add_person_to_channel(
        person: str,
        channel: str,
        role: str = "member"
    ) -> dict:
        """Add a person to a communication channel with a specific role.
        
        Args:
            person: Person name, email, or ID
            channel: Channel name or ID
            role: Role in the channel ("member", "admin", "moderator", "owner") (optional, defaults to "member")
        
        Returns:
            Dictionary with success status and relationship details
        """
        try:
            from ..utils.resolver import resolve_person_id, resolve_channel_id
            
            # Resolve IDs
            person_id = await resolve_person_id(db, person)
            channel_id = await resolve_channel_id(db, channel)
            
            # Validate role
            valid_roles = ["member", "admin", "moderator", "owner"]
            if role.lower() not in valid_roles:
                return {
                    "success": False,
                    "error": f"Invalid role. Must be one of: {', '.join(valid_roles)}"
                }
            
            # Add person to channel
            await db.add_person_to_channel(person_id, channel_id, role.lower())
            
            # Get updated details
            person_data = await db.get_person(person_id)
            channel_data = await db.get_channel(channel_id)
            
            return {
                "success": True,
                "person": person_data,
                "channel": channel_data,
                "role": role.lower(),
                "message": f"Successfully added {person_data['name']} to {channel_data['name']} as {role}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def assign_person_to_project(
        person: str,
        project: str,
        role: str = "contributor",
        allocation: float = None
    ) -> dict:
        """Assign a person to a project with a specific role and time allocation.
        
        Args:
            person: Person name, email, or ID
            project: Project name or ID
            role: Role in the project ("lead", "contributor", "reviewer", "stakeholder") (optional, defaults to "contributor")
            allocation: Time allocation percentage (0.0 to 1.0) (optional)
        
        Returns:
            Dictionary with success status and assignment details
        """
        try:
            from ..utils.resolver import resolve_person_id, resolve_project_id
            
            # Resolve IDs
            person_id = await resolve_person_id(db, person)
            project_id = await resolve_project_id(db, project)
            
            # Validate role
            valid_roles = ["lead", "contributor", "reviewer", "stakeholder"]
            if role.lower() not in valid_roles:
                return {
                    "success": False,
                    "error": f"Invalid role. Must be one of: {', '.join(valid_roles)}"
                }
            
            # Validate allocation
            if allocation is not None:
                if allocation < 0.0 or allocation > 1.0:
                    return {
                        "success": False,
                        "error": "Allocation must be between 0.0 and 1.0"
                    }
            
            # Assign person to project
            await db.assign_person_to_project(person_id, project_id, role.lower(), allocation)
            
            # Get updated details
            person_data = await db.get_person(person_id)
            project_data = await db.get_project(project_id)
            
            allocation_text = f" ({allocation:.0%} allocation)" if allocation else ""
            
            return {
                "success": True,
                "person": person_data,
                "project": project_data,
                "role": role.lower(),
                "allocation": allocation,
                "message": f"Successfully assigned {person_data['name']} to {project_data['name']} as {role}{allocation_text}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def link_person_to_company(
        person: str,
        company: str,
        role: str = "employee",
        start_date: str = None,
        end_date: str = None
    ) -> dict:
        """Link a person to a company with employment details.
        
        Args:
            person: Person name, email, or ID
            company: Company name, domain, or ID
            role: Role at the company (e.g., "employee", "contractor", "ceo", "cto") (optional, defaults to "employee")
            start_date: Employment start date in YYYY-MM-DD format (optional)
            end_date: Employment end date in YYYY-MM-DD format (optional)
        
        Returns:
            Dictionary with success status and employment details
        """
        try:
            from ..utils.resolver import resolve_person_id, resolve_company_id
            
            # Resolve IDs
            person_id = await resolve_person_id(db, person)
            company_id = await resolve_company_id(db, company)
            
            # Link person to company
            await db.link_person_to_company(
                person_id, 
                company_id, 
                role.lower() if role else "employee",
                start_date.strip() if start_date else None,
                end_date.strip() if end_date else None
            )
            
            # Get updated details
            person_data = await db.get_person(person_id)
            company_data = await db.get_company(company_id)
            
            date_text = ""
            if start_date:
                date_text = f" (started {start_date}"
                if end_date:
                    date_text += f", ended {end_date})"
                else:
                    date_text += ")"
            
            return {
                "success": True,
                "person": person_data,
                "company": company_data,
                "role": role.lower() if role else "employee",
                "start_date": start_date,
                "end_date": end_date,
                "message": f"Successfully linked {person_data['name']} to {company_data['name']} as {role}{date_text}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }