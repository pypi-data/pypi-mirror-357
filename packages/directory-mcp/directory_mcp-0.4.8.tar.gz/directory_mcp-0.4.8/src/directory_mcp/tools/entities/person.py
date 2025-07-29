"""Person entity management tools for Directory MCP."""
from mcp.server.fastmcp import FastMCP

def register_person_tools(mcp: FastMCP, db, config, embedder):
    """Register person management tools."""
    
    @mcp.tool()
    async def create_person(
        name: str,
        email: str = None,
        title: str = None,
        skills: str = None,
        location: str = None,
        bio: str = None,
        discord_handle: str = None,
        slack_handle: str = None,
        twitter_handle: str = None,
        linkedin_url: str = None,
        github_handle: str = None
    ) -> dict:
        """Create a new person in the directory.
        
        Args:
            name: Full name of the person
            email: Email address (optional)
            title: Job title or role (optional)
            skills: Comma-separated list of skills (optional)
            location: Geographic location (optional)
            bio: Short biography (optional)
            discord_handle: Discord username (optional)
            slack_handle: Slack username (optional)
            twitter_handle: Twitter username (optional)
            linkedin_url: LinkedIn profile URL (optional)
            github_handle: GitHub username (optional)
        
        Returns:
            Dictionary with success status and person details
        """
        try:
            if not name or not name.strip():
                return {
                    "success": False,
                    "error": "Name is required and cannot be empty"
                }
            
            # Generate embedding if embedder is available
            embedding = None
            if embedder:
                # Create text for embedding from available fields
                text_parts = [name]
                if title:
                    text_parts.append(title)
                if skills:
                    text_parts.append(skills)
                if bio:
                    text_parts.append(bio)
                if location:
                    text_parts.append(location)
                
                text_for_embedding = " ".join(text_parts)
                embedding = await embedder.embed_text(text_for_embedding)
            
            # Build handles dictionary
            handles = {}
            if discord_handle:
                handles["discord"] = discord_handle.strip()
            if slack_handle:
                handles["slack"] = slack_handle.strip()
            if twitter_handle:
                handles["twitter"] = twitter_handle.strip()
            if linkedin_url:
                handles["linkedin"] = linkedin_url.strip()
            if github_handle:
                handles["github"] = github_handle.strip()
            
            # Create person in database
            person_id = await db.create_person(
                names=[name.strip()],
                email=email.strip() if email else None,
                title=title.strip() if title else None,
                skills=[s.strip() for s in skills.split(",")] if skills else None,
                location=location.strip() if location else None,
                bio=bio.strip() if bio else None,
                handles=handles if handles else None,
                vector=embedding
            )
            
            # Get the created person
            person = await db.get_person(person_id)
            
            return {
                "success": True,
                "person": person,
                "message": f"Successfully created person: {name}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    async def get_person_details(person: str) -> dict:
        """Get detailed information about a person including all relationships.
        
        Args:
            person: Person name, email, or ID
        
        Returns:
            Dictionary with person details and connections
        """
        try:
            from ...utils.resolver import resolve_person_id
            
            # Resolve person ID
            person_id = await resolve_person_id(db, person)
            
            # Get person details
            person_data = await db.get_person(person_id)
            if not person_data:
                return {
                    "success": False,
                    "error": f"Person not found: {person}"
                }
            
            # Get connections
            connections = await db.get_person_connections(person_id)
            
            # Organize connections by type
            companies = [conn for conn in connections if conn['type'] == 'company']
            projects = [conn for conn in connections if conn['type'] == 'project']
            channels = [conn for conn in connections if conn['type'] == 'channel']
            
            return {
                "success": True,
                "person": person_data,
                "connections": {
                    "companies": companies,
                    "projects": projects,
                    "channels": channels
                },
                "total_connections": len(connections)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }