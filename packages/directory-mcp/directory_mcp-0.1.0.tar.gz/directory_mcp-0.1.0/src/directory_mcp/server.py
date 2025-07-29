"""MCP server implementation for Directory."""
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError

from .config import Config
from .database.manager import DatabaseManager

# Initialize FastMCP server
mcp = FastMCP("directory-mcp", version="0.1.0")

# Global instances
db = None
config = None

async def initialize():
    """Initialize the server components."""
    global db, config
    
    # Initialize configuration
    config = Config()
    
    # Initialize database
    db = DatabaseManager(config.db_path)
    await db.initialize()

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
        
        # Create person (without embeddings for now)
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