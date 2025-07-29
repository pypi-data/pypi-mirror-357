"""MCP server implementation for Directory."""
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError

from .config import Config
from .database.manager import DatabaseManager
from .embeddings.gemini import SmartEmbedder

# Initialize FastMCP server
mcp = FastMCP("directory-mcp", version="0.2.0")

# Global instances
db = None
config = None
embedder = None

async def initialize():
    """Initialize the server components."""
    global db, config, embedder
    
    # Initialize configuration
    config = Config()
    
    # Initialize database
    db = DatabaseManager(config.db_path)
    await db.initialize()
    
    # Initialize embedder if API key is available
    if config.gemini_api_key:
        embedder = SmartEmbedder(config.gemini_api_key, db)

async def run_server():
    """Run the MCP server."""
    # Initialize components
    await initialize()
    
    # Run stdio server
    await mcp.run_stdio_async()

# Basic tool for testing
@mcp.tool()
async def get_directory_status() -> dict:
    """Get the current status of the directory database."""
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Get counts
        person_count = await db.execute_query("SELECT COUNT(*) as count FROM person")
        company_count = await db.execute_query("SELECT COUNT(*) as count FROM company")
        channel_count = await db.execute_query("SELECT COUNT(*) as count FROM channel")
        project_count = await db.execute_query("SELECT COUNT(*) as count FROM project")
        
        return {
            "status": "operational",
            "database": str(config.db_path),
            "entities": {
                "people": person_count[0]['count'] if person_count else 0,
                "companies": company_count[0]['count'] if company_count else 0,
                "channels": channel_count[0]['count'] if channel_count else 0,
                "projects": project_count[0]['count'] if project_count else 0
            },
            "configuration": {
                "embedding_model": config.embedding_model,
                "similarity_threshold": config.similarity_threshold
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@mcp.tool()
async def create_person(
    names: list[str],
    email: str = None,
    company: str = None,
    title: str = None,
    department: str = None,
    location: str = None,
    handles: dict = None,
    skills: list[str] = None,
    bio: str = None
) -> dict:
    """Create a new person in the directory.
    
    Args:
        names: List of names (e.g., ["John Doe", "John"])
        email: Primary email address
        company: Company name (will be created if doesn't exist)
        title: Job title
        department: Department or team
        location: City, Country
        handles: Dict of platform handles (e.g., {"discord": "john#1234", "slack": "U123"})
        skills: List of skills
        bio: Short biography
    
    Returns:
        Created person details
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Handle company
        company_id = None
        if company:
            # Check if company exists
            existing = await db.execute_query(
                "SELECT company_id FROM company WHERE name = ?", 
                (company,)
            )
            
            if existing:
                company_id = existing[0]['company_id']
            else:
                # Create company
                company_id = await db.create_company(name=company)
        
        # Create person
        person_id = await db.create_person(
            names=names,
            email=email,
            company_id=company_id,
            title=title,
            department=department,
            location=location,
            handles=handles,
            skills=skills,
            bio=bio
        )
        
        # Get created person
        person = await db.get_person(person_id)
        
        # Generate embedding if embedder is available
        if embedder and person:
            # Add company name for context
            if company_id:
                person['company_name'] = company
            
            # Generate and store embedding
            vector = await embedder.embed_person(person)
            await db.update_person(person_id, vector=vector)
        
        return {
            "success": True,
            "person_id": person_id,
            "person": person,
            "message": f"Successfully created person: {names[0]}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def search_people(
    query: str,
    limit: int = 10
) -> dict:
    """Search for people using natural language queries.
    
    Args:
        query: Natural language search query (e.g., "engineers at TechCorp", "people with Python skills")
        limit: Maximum number of results to return
    
    Returns:
        Search results with matching people
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # First try full-text search
        results = await db.search_entities('person', query, limit)
        
        # Format results
        formatted_results = []
        for person in results:
            # Get company name if available
            company_name = None
            if person.get('company_id'):
                company_name = await db.get_company_name(person['company_id'])
            
            formatted_results.append({
                'person_id': person['person_id'],
                'names': person['names'],
                'email': person.get('email'),
                'title': person.get('title'),
                'department': person.get('department'),
                'company': company_name,
                'location': person.get('location'),
                'skills': person.get('skills'),
                'bio': person.get('bio')
            })
        
        return {
            "success": True,
            "query": query,
            "count": len(formatted_results),
            "results": formatted_results
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def get_person_details(
    person_id: int,
    include_connections: bool = True
) -> dict:
    """Get detailed information about a person including their connections.
    
    Args:
        person_id: The ID of the person to retrieve
        include_connections: Whether to include channels, projects, and colleagues
    
    Returns:
        Detailed person information with connections
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Get person details
        person = await db.get_person(person_id)
        if not person:
            return {
                "success": False,
                "error": f"Person with ID {person_id} not found"
            }
        
        # Get company name
        company_name = None
        if person.get('company_id'):
            company_name = await db.get_company_name(person['company_id'])
        
        result = {
            "success": True,
            "person": {
                'person_id': person['person_id'],
                'names': person['names'],
                'email': person.get('email'),
                'secondary_emails': person.get('secondary_emails', []),
                'title': person.get('title'),
                'department': person.get('department'),
                'company': company_name,
                'company_id': person.get('company_id'),
                'location': person.get('location'),
                'timezone': person.get('timezone'),
                'handles': person.get('handles', {}),
                'aliases': person.get('aliases', []),
                'skills': person.get('skills', []),
                'bio': person.get('bio'),
                'created_at': person.get('created_at'),
                'updated_at': person.get('updated_at')
            }
        }
        
        # Include connections if requested
        if include_connections:
            # Get channels
            channels = await db.get_person_channels(person_id)
            result['channels'] = [
                {
                    'channel_id': ch['channel_id'],
                    'name': ch.get('name'),
                    'platform': ch['platform'],
                    'type': ch.get('type'),
                    'role': ch.get('role'),
                    'joined_at': ch.get('joined_at')
                }
                for ch in channels
            ]
            
            # Get projects
            projects = await db.get_person_projects(person_id)
            result['projects'] = [
                {
                    'project_id': proj['project_id'],
                    'name': proj['name'],
                    'code': proj.get('code'),
                    'status': proj.get('status'),
                    'role': proj.get('role'),
                    'allocation': proj.get('allocation'),
                    'start_date': proj.get('start_date'),
                    'end_date': proj.get('end_date')
                }
                for proj in projects
            ]
            
            # Get colleagues
            if person.get('company_id'):
                colleagues = await db.get_company_people(person['company_id'], exclude_id=person_id)
                result['colleagues'] = [
                    {
                        'person_id': col['person_id'],
                        'names': col['names'],
                        'email': col.get('email'),
                        'title': col.get('title'),
                        'department': col.get('department')
                    }
                    for col in colleagues[:10]  # Limit to 10 colleagues
                ]
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }