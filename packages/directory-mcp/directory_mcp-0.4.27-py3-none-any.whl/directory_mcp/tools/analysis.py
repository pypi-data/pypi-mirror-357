"""Network analysis and overview tools for Directory MCP."""
from mcp.server.fastmcp import FastMCP
from ..utils.serialization import remove_vectors

def register_analysis_tools(mcp: FastMCP, db, config, embedder):
    """Register network analysis and overview tools."""
    
    @mcp.tool()
    async def get_person_network(person: str) -> dict:
        """Get a comprehensive view of a person's professional network and connections.
        
        Args:
            person: Person name, email, or ID
        
        Returns:
            Dictionary with network analysis and connection data
        """
        try:
            from ..utils.resolver import resolve_person_id
            
            # Resolve person ID
            person_id = await resolve_person_id(db, person)
            
            # Get person details
            person_data = await db.get_person(person_id)
            if not person_data:
                return {
                    "success": False,
                    "error": f"Person not found: {person}"
                }
            
            # Remove vector for JSON serialization
            remove_vectors(person_data)
            
            # Get all connections
            connections = await db.get_person_connections(person_id)
            
            # Extract connection data
            companies = connections.get('companies', [])
            projects = connections.get('projects', [])
            channels = connections.get('channels', [])
            
            # Get colleagues (people in same companies)
            colleagues = []
            for company_conn in companies:
                company_people = await db.get_company_people(company_conn['company_id'])
                remove_vectors(company_people)
                colleagues.extend([p for p in company_people if p['person_id'] != person_id])
            
            # Get project teammates
            teammates = []
            for project_conn in projects:
                project_people = await db.get_project_people(project_conn['project_id'])
                remove_vectors(project_people)
                teammates.extend([p for p in project_people if p['person_id'] != person_id])
            
            # Get channel members
            channel_members = []
            for channel_conn in channels:
                channel_people = await db.get_channel_people(channel_conn['channel_id'])
                remove_vectors(channel_people)
                channel_members.extend([p for p in channel_people if p['person_id'] != person_id])
            
            # Remove duplicates and count connections
            unique_colleagues = {p['person_id']: p for p in colleagues}
            unique_teammates = {p['person_id']: p for p in teammates}
            unique_channel_members = {p['person_id']: p for p in channel_members}
            
            # Calculate network metrics
            total_connections = len(unique_colleagues) + len(unique_teammates) + len(unique_channel_members)
            
            return {
                "success": True,
                "person": person_data,
                "network": {
                    "companies": {
                        "count": len(companies),
                        "details": companies
                    },
                    "projects": {
                        "count": len(projects),
                        "details": projects
                    },
                    "channels": {
                        "count": len(channels),
                        "details": channels
                    },
                    "colleagues": {
                        "count": len(unique_colleagues),
                        "people": list(unique_colleagues.values())
                    },
                    "teammates": {
                        "count": len(unique_teammates),
                        "people": list(unique_teammates.values())
                    },
                    "channel_members": {
                        "count": len(unique_channel_members),
                        "people": list(unique_channel_members.values())
                    }
                },
                "metrics": {
                    "total_connections": total_connections,
                    "direct_relationships": len(connections),
                    "network_reach": len(set(list(unique_colleagues.keys()) + list(unique_teammates.keys()) + list(unique_channel_members.keys())))
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }