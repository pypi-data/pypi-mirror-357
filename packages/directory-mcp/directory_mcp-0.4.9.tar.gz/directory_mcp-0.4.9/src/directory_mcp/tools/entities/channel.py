"""Channel entity management tools for Directory MCP."""
from mcp.server.fastmcp import FastMCP

def register_channel_tools(mcp: FastMCP, db, config, embedder):
    """Register channel management tools."""
    
    @mcp.tool()
    async def create_channel(
        name: str,
        platform: str,
        description: str = None,
        channel_type: str = "public",
        company: str = None
    ) -> dict:
        """Create a new communication channel in the directory.
        
        Args:
            name: Channel name (e.g., "#general", "Engineering Team")
            platform: Platform where the channel exists (e.g., "slack", "discord", "teams")
            description: Purpose or description of the channel (optional)
            channel_type: Type of channel ("public", "private", "dm") (optional, defaults to "public")
            company: Associated company name, domain, or ID (optional)
        
        Returns:
            Dictionary with success status and channel details
        """
        try:
            if not name or not name.strip():
                return {
                    "success": False,
                    "error": "Channel name is required and cannot be empty"
                }
            
            if not platform or not platform.strip():
                return {
                    "success": False,
                    "error": "Platform is required and cannot be empty"
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
            
            # Generate embedding if embedder is available
            embedding = None
            if embedder:
                # Create text for embedding from available fields
                text_parts = [name, platform]
                if description:
                    text_parts.append(description)
                if channel_type:
                    text_parts.append(channel_type)
                
                text_for_embedding = " ".join(text_parts)
                embedding = await embedder.embed_text(text_for_embedding)
            
            # Create channel in database
            channel_id = await db.create_channel(
                name=name.strip(),
                platform=platform.strip().lower(),
                description=description.strip() if description else None,
                channel_type=channel_type.strip().lower() if channel_type else "public",
                company_id=company_id,
                embedding=embedding
            )
            
            # Get the created channel
            channel = await db.get_channel(channel_id)
            
            return {
                "success": True,
                "channel": channel,
                "message": f"Successfully created channel: {name} on {platform}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }