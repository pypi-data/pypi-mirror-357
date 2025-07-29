"""Company entity management tools for Directory MCP."""
from mcp.server.fastmcp import FastMCP

def register_company_tools(mcp: FastMCP, db, config, embedder):
    """Register company management tools."""
    
    @mcp.tool()
    async def create_company(
        name: str,
        domain: str = None,
        industry: str = None,
        size: str = None,
        location: str = None,
        description: str = None,
        website: str = None,
        linkedin_url: str = None
    ) -> dict:
        """Create a new company in the directory.
        
        Args:
            name: Company name
            domain: Primary email domain (optional)
            industry: Industry sector (optional)
            size: Company size (e.g., "1-10", "11-50", "500+") (optional)
            location: Company headquarters location (optional)
            description: Company description (optional)
            website: Company website URL (optional)
            linkedin_url: LinkedIn company page URL (optional)
        
        Returns:
            Dictionary with success status and company details
        """
        try:
            if not name or not name.strip():
                return {
                    "success": False,
                    "error": "Company name is required and cannot be empty"
                }
            
            # Generate embedding if embedder is available
            embedding = None
            if embedder:
                # Create text for embedding from available fields
                text_parts = [name]
                if industry:
                    text_parts.append(industry)
                if description:
                    text_parts.append(description)
                if location:
                    text_parts.append(location)
                
                text_for_embedding = " ".join(text_parts)
                embedding = await embedder.embed_text(text_for_embedding)
            
            # Create company in database
            company_id = await db.create_company(
                name=name.strip(),
                domain=domain.strip() if domain else None,
                industry=industry.strip() if industry else None,
                size=size.strip() if size else None,
                location_hq=location.strip() if location else None,
                description=description.strip() if description else None,
                vector=embedding
            )
            
            # Get the created company
            company = await db.get_company(company_id)
            
            return {
                "success": True,
                "company": company,
                "message": f"Successfully created company: {name}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def get_company_overview(company: str) -> dict:
        """Get a comprehensive overview of a company including all people and organizational structure.
        
        Args:
            company: Company name, domain, or ID
        
        Returns:
            Dictionary with company details and organizational data
        """
        try:
            from ...utils.resolver import resolve_company_id
            
            # Resolve company ID
            company_id = await resolve_company_id(db, company)
            
            # Get company details
            company_data = await db.get_company(company_id)
            if not company_data:
                return {
                    "success": False,
                    "error": f"Company not found: {company}"
                }
            
            # Get all people at this company
            people = await db.get_company_people(company_id)
            
            # Group by titles/roles
            roles = {}
            for person in people:
                role = person.get('company_role', 'Unknown')
                if role not in roles:
                    roles[role] = []
                roles[role].append(person)
            
            # Get company projects and channels
            projects = await db.get_company_projects(company_id)
            channels = await db.get_company_channels(company_id)
            
            return {
                "success": True,
                "company": company_data,
                "people": {
                    "total": len(people),
                    "by_role": roles
                },
                "projects": {
                    "total": len(projects),
                    "active": [p for p in projects if p.get('status') == 'active'],
                    "all": projects
                },
                "channels": {
                    "total": len(channels),
                    "all": channels
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }