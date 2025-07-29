"""MCP server implementation for Directory."""
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError

from .config import Config
from .database.manager import DatabaseManager
from .embeddings.gemini import SmartEmbedder

# Initialize FastMCP server
mcp = FastMCP("directory-mcp", version="0.3.0")

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
async def add_person_to_channel(
    person: str,
    channel: str,
    role: str = "member"
) -> dict:
    """Add a person to a communication channel with a specific role.
    
    Args:
        person: Person name or ID
        channel: Channel name or ID
        role: Role in channel ('member', 'admin', 'owner')
    
    Returns:
        Result of adding person to channel
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Resolve person
        person_id = None
        if person.isdigit():
            person_id = int(person)
        else:
            people = await db.search_entities('person', person, 1)
            if people:
                person_id = people[0]['person_id']
            else:
                return {
                    "success": False,
                    "error": f"Person '{person}' not found"
                }
        
        # Resolve channel
        channel_id = None
        if channel.isdigit():
            channel_id = int(channel)
        else:
            channels = await db.search_entities('channel', channel, 1)
            if channels:
                channel_id = channels[0]['channel_id']
            else:
                return {
                    "success": False,
                    "error": f"Channel '{channel}' not found"
                }
        
        # Add person to channel
        await db.add_person_to_channel(
            person_id=person_id,
            channel_id=channel_id,
            role=role
        )
        
        # Get person and channel details
        person_details = await db.get_person(person_id)
        channel_details = await db.get_channel(channel_id)
        
        return {
            "success": True,
            "person": person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names'],
            "channel": channel_details['name'],
            "role": role,
            "message": f"Added {person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names']} to {channel_details['name']} as {role}"
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
    allocation: int = 50
) -> dict:
    """Assign a person to a project with role and time allocation.
    
    Args:
        person: Person name or ID
        project: Project name or ID
        role: Role in project ('lead', 'contributor', 'reviewer')
        allocation: Time allocation percentage (0-100)
    
    Returns:
        Result of assigning person to project
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Resolve person
        person_id = None
        if person.isdigit():
            person_id = int(person)
        else:
            people = await db.search_entities('person', person, 1)
            if people:
                person_id = people[0]['person_id']
            else:
                return {
                    "success": False,
                    "error": f"Person '{person}' not found"
                }
        
        # Resolve project
        project_id = None
        if project.isdigit():
            project_id = int(project)
        else:
            projects = await db.search_entities('project', project, 1)
            if projects:
                project_id = projects[0]['project_id']
            else:
                return {
                    "success": False,
                    "error": f"Project '{project}' not found"
                }
        
        # Add person to project
        await db.add_person_to_project(
            person_id=person_id,
            project_id=project_id,
            role=role,
            allocation=allocation
        )
        
        # Get person and project details
        person_details = await db.get_person(person_id)
        project_details = await db.get_project(project_id)
        
        return {
            "success": True,
            "person": person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names'],
            "project": project_details['name'],
            "role": role,
            "allocation": allocation,
            "message": f"Assigned {person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names']} to {project_details['name']} as {role} ({allocation}% allocation)"
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
    is_current: bool = True
) -> dict:
    """Link a person to a company with employment information.
    
    Args:
        person: Person name or ID
        company: Company name or ID
        role: Role at company ('employee', 'contractor', 'intern', 'executive')
        is_current: Whether this is current employment
    
    Returns:
        Result of linking person to company
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Resolve person
        person_id = None
        if person.isdigit():
            person_id = int(person)
        else:
            people = await db.search_entities('person', person, 1)
            if people:
                person_id = people[0]['person_id']
            else:
                return {
                    "success": False,
                    "error": f"Person '{person}' not found"
                }
        
        # Resolve company
        company_id = None
        if company.isdigit():
            company_id = int(company)
        else:
            companies = await db.search_entities('company', company, 1)
            if companies:
                company_id = companies[0]['company_id']
            else:
                return {
                    "success": False,
                    "error": f"Company '{company}' not found"
                }
        
        # Update person's company
        await db.update_person(
            person_id=person_id,
            company_id=company_id
        )
        
        # Add to company relationship
        await db.add_person_to_company(
            person_id=person_id,
            company_id=company_id,
            role=role,
            is_current=is_current
        )
        
        # Get person and company details
        person_details = await db.get_person(person_id)
        company_details = await db.get_company(company_id)
        
        return {
            "success": True,
            "person": person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names'],
            "company": company_details['name'],
            "role": role,
            "is_current": is_current,
            "message": f"Linked {person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names']} to {company_details['name']} as {role}"
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
async def add_person_to_channel(
    person: str,
    channel: str,
    role: str = "member"
) -> dict:
    """Add a person to a communication channel with a specific role.
    
    Args:
        person: Person name or ID
        channel: Channel name or ID
        role: Role in channel ('member', 'admin', 'owner')
    
    Returns:
        Result of adding person to channel
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Resolve person
        person_id = None
        if person.isdigit():
            person_id = int(person)
        else:
            people = await db.search_entities('person', person, 1)
            if people:
                person_id = people[0]['person_id']
            else:
                return {
                    "success": False,
                    "error": f"Person '{person}' not found"
                }
        
        # Resolve channel
        channel_id = None
        if channel.isdigit():
            channel_id = int(channel)
        else:
            channels = await db.search_entities('channel', channel, 1)
            if channels:
                channel_id = channels[0]['channel_id']
            else:
                return {
                    "success": False,
                    "error": f"Channel '{channel}' not found"
                }
        
        # Add person to channel
        await db.add_person_to_channel(
            person_id=person_id,
            channel_id=channel_id,
            role=role
        )
        
        # Get person and channel details
        person_details = await db.get_person(person_id)
        channel_details = await db.get_channel(channel_id)
        
        return {
            "success": True,
            "person": person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names'],
            "channel": channel_details['name'],
            "role": role,
            "message": f"Added {person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names']} to {channel_details['name']} as {role}"
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
    allocation: int = 50
) -> dict:
    """Assign a person to a project with role and time allocation.
    
    Args:
        person: Person name or ID
        project: Project name or ID
        role: Role in project ('lead', 'contributor', 'reviewer')
        allocation: Time allocation percentage (0-100)
    
    Returns:
        Result of assigning person to project
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Resolve person
        person_id = None
        if person.isdigit():
            person_id = int(person)
        else:
            people = await db.search_entities('person', person, 1)
            if people:
                person_id = people[0]['person_id']
            else:
                return {
                    "success": False,
                    "error": f"Person '{person}' not found"
                }
        
        # Resolve project
        project_id = None
        if project.isdigit():
            project_id = int(project)
        else:
            projects = await db.search_entities('project', project, 1)
            if projects:
                project_id = projects[0]['project_id']
            else:
                return {
                    "success": False,
                    "error": f"Project '{project}' not found"
                }
        
        # Add person to project
        await db.add_person_to_project(
            person_id=person_id,
            project_id=project_id,
            role=role,
            allocation=allocation
        )
        
        # Get person and project details
        person_details = await db.get_person(person_id)
        project_details = await db.get_project(project_id)
        
        return {
            "success": True,
            "person": person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names'],
            "project": project_details['name'],
            "role": role,
            "allocation": allocation,
            "message": f"Assigned {person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names']} to {project_details['name']} as {role} ({allocation}% allocation)"
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
    is_current: bool = True
) -> dict:
    """Link a person to a company with employment information.
    
    Args:
        person: Person name or ID
        company: Company name or ID
        role: Role at company ('employee', 'contractor', 'intern', 'executive')
        is_current: Whether this is current employment
    
    Returns:
        Result of linking person to company
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Resolve person
        person_id = None
        if person.isdigit():
            person_id = int(person)
        else:
            people = await db.search_entities('person', person, 1)
            if people:
                person_id = people[0]['person_id']
            else:
                return {
                    "success": False,
                    "error": f"Person '{person}' not found"
                }
        
        # Resolve company
        company_id = None
        if company.isdigit():
            company_id = int(company)
        else:
            companies = await db.search_entities('company', company, 1)
            if companies:
                company_id = companies[0]['company_id']
            else:
                return {
                    "success": False,
                    "error": f"Company '{company}' not found"
                }
        
        # Update person's company
        await db.update_person(
            person_id=person_id,
            company_id=company_id
        )
        
        # Add to company relationship
        await db.add_person_to_company(
            person_id=person_id,
            company_id=company_id,
            role=role,
            is_current=is_current
        )
        
        # Get person and company details
        person_details = await db.get_person(person_id)
        company_details = await db.get_company(company_id)
        
        return {
            "success": True,
            "person": person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names'],
            "company": company_details['name'],
            "role": role,
            "is_current": is_current,
            "message": f"Linked {person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names']} to {company_details['name']} as {role}"
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

@mcp.tool()
async def add_person_to_channel(
    person: str,
    channel: str,
    role: str = "member"
) -> dict:
    """Add a person to a communication channel with a specific role.
    
    Args:
        person: Person name or ID
        channel: Channel name or ID
        role: Role in channel ('member', 'admin', 'owner')
    
    Returns:
        Result of adding person to channel
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Resolve person
        person_id = None
        if person.isdigit():
            person_id = int(person)
        else:
            people = await db.search_entities('person', person, 1)
            if people:
                person_id = people[0]['person_id']
            else:
                return {
                    "success": False,
                    "error": f"Person '{person}' not found"
                }
        
        # Resolve channel
        channel_id = None
        if channel.isdigit():
            channel_id = int(channel)
        else:
            channels = await db.search_entities('channel', channel, 1)
            if channels:
                channel_id = channels[0]['channel_id']
            else:
                return {
                    "success": False,
                    "error": f"Channel '{channel}' not found"
                }
        
        # Add person to channel
        await db.add_person_to_channel(
            person_id=person_id,
            channel_id=channel_id,
            role=role
        )
        
        # Get person and channel details
        person_details = await db.get_person(person_id)
        channel_details = await db.get_channel(channel_id)
        
        return {
            "success": True,
            "person": person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names'],
            "channel": channel_details['name'],
            "role": role,
            "message": f"Added {person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names']} to {channel_details['name']} as {role}"
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
    allocation: int = 50
) -> dict:
    """Assign a person to a project with role and time allocation.
    
    Args:
        person: Person name or ID
        project: Project name or ID
        role: Role in project ('lead', 'contributor', 'reviewer')
        allocation: Time allocation percentage (0-100)
    
    Returns:
        Result of assigning person to project
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Resolve person
        person_id = None
        if person.isdigit():
            person_id = int(person)
        else:
            people = await db.search_entities('person', person, 1)
            if people:
                person_id = people[0]['person_id']
            else:
                return {
                    "success": False,
                    "error": f"Person '{person}' not found"
                }
        
        # Resolve project
        project_id = None
        if project.isdigit():
            project_id = int(project)
        else:
            projects = await db.search_entities('project', project, 1)
            if projects:
                project_id = projects[0]['project_id']
            else:
                return {
                    "success": False,
                    "error": f"Project '{project}' not found"
                }
        
        # Add person to project
        await db.add_person_to_project(
            person_id=person_id,
            project_id=project_id,
            role=role,
            allocation=allocation
        )
        
        # Get person and project details
        person_details = await db.get_person(person_id)
        project_details = await db.get_project(project_id)
        
        return {
            "success": True,
            "person": person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names'],
            "project": project_details['name'],
            "role": role,
            "allocation": allocation,
            "message": f"Assigned {person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names']} to {project_details['name']} as {role} ({allocation}% allocation)"
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
    is_current: bool = True
) -> dict:
    """Link a person to a company with employment information.
    
    Args:
        person: Person name or ID
        company: Company name or ID
        role: Role at company ('employee', 'contractor', 'intern', 'executive')
        is_current: Whether this is current employment
    
    Returns:
        Result of linking person to company
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Resolve person
        person_id = None
        if person.isdigit():
            person_id = int(person)
        else:
            people = await db.search_entities('person', person, 1)
            if people:
                person_id = people[0]['person_id']
            else:
                return {
                    "success": False,
                    "error": f"Person '{person}' not found"
                }
        
        # Resolve company
        company_id = None
        if company.isdigit():
            company_id = int(company)
        else:
            companies = await db.search_entities('company', company, 1)
            if companies:
                company_id = companies[0]['company_id']
            else:
                return {
                    "success": False,
                    "error": f"Company '{company}' not found"
                }
        
        # Update person's company
        await db.update_person(
            person_id=person_id,
            company_id=company_id
        )
        
        # Add to company relationship
        await db.add_person_to_company(
            person_id=person_id,
            company_id=company_id,
            role=role,
            is_current=is_current
        )
        
        # Get person and company details
        person_details = await db.get_person(person_id)
        company_details = await db.get_company(company_id)
        
        return {
            "success": True,
            "person": person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names'],
            "company": company_details['name'],
            "role": role,
            "is_current": is_current,
            "message": f"Linked {person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names']} to {company_details['name']} as {role}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def create_company(
    name: str,
    domain: str = None,
    industry: str = None,
    size: str = None,
    location_hq: str = None,
    description: str = None,
    tags: list = None
) -> dict:
    """Create a new company with comprehensive information.
    
    Args:
        name: Company name (required)
        domain: Primary domain (e.g., 'techcorp.com')
        industry: Industry sector (e.g., 'Technology', 'Finance')
        size: Company size (e.g., '1-10', '50-200', '1000+')
        location_hq: Headquarters location
        description: Company description
        tags: List of tags/keywords
    
    Returns:
        Company creation result with ID
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Create company
        company_id = await db.create_company(
            name=name,
            domain=domain,
            industry=industry,
            size=size,
            location_hq=location_hq,
            description=description,
            tags=tags or []
        )
        
        # Get created company
        company = await db.get_company(company_id)
        
        # Generate embedding if embedder is available
        if embedder and company:
            vector = await embedder.embed_company(company)
            await db.update_company(company_id, vector=vector)
        
        return {
            "success": True,
            "company_id": company_id,
            "company": {
                'name': name,
                'domain': domain,
                'industry': industry,
                'size': size,
                'location_hq': location_hq,
                'description': description,
                'tags': tags
            },
            "message": f"Successfully created company: {name}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def add_person_to_channel(
    person: str,
    channel: str,
    role: str = "member"
) -> dict:
    """Add a person to a communication channel with a specific role.
    
    Args:
        person: Person name or ID
        channel: Channel name or ID
        role: Role in channel ('member', 'admin', 'owner')
    
    Returns:
        Result of adding person to channel
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Resolve person
        person_id = None
        if person.isdigit():
            person_id = int(person)
        else:
            people = await db.search_entities('person', person, 1)
            if people:
                person_id = people[0]['person_id']
            else:
                return {
                    "success": False,
                    "error": f"Person '{person}' not found"
                }
        
        # Resolve channel
        channel_id = None
        if channel.isdigit():
            channel_id = int(channel)
        else:
            channels = await db.search_entities('channel', channel, 1)
            if channels:
                channel_id = channels[0]['channel_id']
            else:
                return {
                    "success": False,
                    "error": f"Channel '{channel}' not found"
                }
        
        # Add person to channel
        await db.add_person_to_channel(
            person_id=person_id,
            channel_id=channel_id,
            role=role
        )
        
        # Get person and channel details
        person_details = await db.get_person(person_id)
        channel_details = await db.get_channel(channel_id)
        
        return {
            "success": True,
            "person": person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names'],
            "channel": channel_details['name'],
            "role": role,
            "message": f"Added {person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names']} to {channel_details['name']} as {role}"
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
    allocation: int = 50
) -> dict:
    """Assign a person to a project with role and time allocation.
    
    Args:
        person: Person name or ID
        project: Project name or ID
        role: Role in project ('lead', 'contributor', 'reviewer')
        allocation: Time allocation percentage (0-100)
    
    Returns:
        Result of assigning person to project
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Resolve person
        person_id = None
        if person.isdigit():
            person_id = int(person)
        else:
            people = await db.search_entities('person', person, 1)
            if people:
                person_id = people[0]['person_id']
            else:
                return {
                    "success": False,
                    "error": f"Person '{person}' not found"
                }
        
        # Resolve project
        project_id = None
        if project.isdigit():
            project_id = int(project)
        else:
            projects = await db.search_entities('project', project, 1)
            if projects:
                project_id = projects[0]['project_id']
            else:
                return {
                    "success": False,
                    "error": f"Project '{project}' not found"
                }
        
        # Add person to project
        await db.add_person_to_project(
            person_id=person_id,
            project_id=project_id,
            role=role,
            allocation=allocation
        )
        
        # Get person and project details
        person_details = await db.get_person(person_id)
        project_details = await db.get_project(project_id)
        
        return {
            "success": True,
            "person": person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names'],
            "project": project_details['name'],
            "role": role,
            "allocation": allocation,
            "message": f"Assigned {person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names']} to {project_details['name']} as {role} ({allocation}% allocation)"
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
    is_current: bool = True
) -> dict:
    """Link a person to a company with employment information.
    
    Args:
        person: Person name or ID
        company: Company name or ID
        role: Role at company ('employee', 'contractor', 'intern', 'executive')
        is_current: Whether this is current employment
    
    Returns:
        Result of linking person to company
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Resolve person
        person_id = None
        if person.isdigit():
            person_id = int(person)
        else:
            people = await db.search_entities('person', person, 1)
            if people:
                person_id = people[0]['person_id']
            else:
                return {
                    "success": False,
                    "error": f"Person '{person}' not found"
                }
        
        # Resolve company
        company_id = None
        if company.isdigit():
            company_id = int(company)
        else:
            companies = await db.search_entities('company', company, 1)
            if companies:
                company_id = companies[0]['company_id']
            else:
                return {
                    "success": False,
                    "error": f"Company '{company}' not found"
                }
        
        # Update person's company
        await db.update_person(
            person_id=person_id,
            company_id=company_id
        )
        
        # Add to company relationship
        await db.add_person_to_company(
            person_id=person_id,
            company_id=company_id,
            role=role,
            is_current=is_current
        )
        
        # Get person and company details
        person_details = await db.get_person(person_id)
        company_details = await db.get_company(company_id)
        
        return {
            "success": True,
            "person": person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names'],
            "company": company_details['name'],
            "role": role,
            "is_current": is_current,
            "message": f"Linked {person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names']} to {company_details['name']} as {role}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def create_channel(
    name: str,
    platform: str,
    channel_type: str = "channel",
    purpose: str = None,
    company: str = None,
    project: str = None,
    is_active: bool = True
) -> dict:
    """Create a new communication channel.
    
    Args:
        name: Channel name (required)
        platform: Platform (e.g., 'slack', 'discord', 'teams')
        channel_type: Type (e.g., 'channel', 'dm', 'group')
        purpose: Channel purpose/description
        company: Company name (will create if doesn't exist)
        project: Project name (will create if doesn't exist)
        is_active: Whether channel is currently active
    
    Returns:
        Channel creation result with ID
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Resolve company ID if provided
        company_id = None
        if company:
            companies = await db.search_entities('company', company, 1)
            if companies:
                company_id = companies[0]['company_id']
            else:
                # Create company
                company_id = await db.create_company(name=company)
        
        # Resolve project ID if provided
        project_id = None
        if project:
            projects = await db.search_entities('project', project, 1)
            if projects:
                project_id = projects[0]['project_id']
            else:
                # Create project
                project_id = await db.create_project(
                    name=project,
                    company_id=company_id
                )
        
        # Create channel
        channel_id = await db.create_channel(
            name=name,
            platform=platform,
            type=channel_type,
            purpose=purpose,
            company_id=company_id,
            project_id=project_id,
            is_active=is_active
        )
        
        # Get created channel
        channel = await db.get_channel(channel_id)
        
        # Generate embedding if embedder is available
        if embedder and channel:
            # Add company/project names for context
            if company_id:
                channel['company_name'] = company
            if project_id:
                channel['project_name'] = project
            
            vector = await embedder.embed_channel(channel)
            await db.update_channel(channel_id, vector=vector)
        
        return {
            "success": True,
            "channel_id": channel_id,
            "channel": {
                'name': name,
                'platform': platform,
                'type': channel_type,
                'purpose': purpose,
                'company': company,
                'project': project,
                'is_active': is_active
            },
            "message": f"Successfully created {platform} channel: {name}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def add_person_to_channel(
    person: str,
    channel: str,
    role: str = "member"
) -> dict:
    """Add a person to a communication channel with a specific role.
    
    Args:
        person: Person name or ID
        channel: Channel name or ID
        role: Role in channel ('member', 'admin', 'owner')
    
    Returns:
        Result of adding person to channel
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Resolve person
        person_id = None
        if person.isdigit():
            person_id = int(person)
        else:
            people = await db.search_entities('person', person, 1)
            if people:
                person_id = people[0]['person_id']
            else:
                return {
                    "success": False,
                    "error": f"Person '{person}' not found"
                }
        
        # Resolve channel
        channel_id = None
        if channel.isdigit():
            channel_id = int(channel)
        else:
            channels = await db.search_entities('channel', channel, 1)
            if channels:
                channel_id = channels[0]['channel_id']
            else:
                return {
                    "success": False,
                    "error": f"Channel '{channel}' not found"
                }
        
        # Add person to channel
        await db.add_person_to_channel(
            person_id=person_id,
            channel_id=channel_id,
            role=role
        )
        
        # Get person and channel details
        person_details = await db.get_person(person_id)
        channel_details = await db.get_channel(channel_id)
        
        return {
            "success": True,
            "person": person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names'],
            "channel": channel_details['name'],
            "role": role,
            "message": f"Added {person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names']} to {channel_details['name']} as {role}"
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
    allocation: int = 50
) -> dict:
    """Assign a person to a project with role and time allocation.
    
    Args:
        person: Person name or ID
        project: Project name or ID
        role: Role in project ('lead', 'contributor', 'reviewer')
        allocation: Time allocation percentage (0-100)
    
    Returns:
        Result of assigning person to project
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Resolve person
        person_id = None
        if person.isdigit():
            person_id = int(person)
        else:
            people = await db.search_entities('person', person, 1)
            if people:
                person_id = people[0]['person_id']
            else:
                return {
                    "success": False,
                    "error": f"Person '{person}' not found"
                }
        
        # Resolve project
        project_id = None
        if project.isdigit():
            project_id = int(project)
        else:
            projects = await db.search_entities('project', project, 1)
            if projects:
                project_id = projects[0]['project_id']
            else:
                return {
                    "success": False,
                    "error": f"Project '{project}' not found"
                }
        
        # Add person to project
        await db.add_person_to_project(
            person_id=person_id,
            project_id=project_id,
            role=role,
            allocation=allocation
        )
        
        # Get person and project details
        person_details = await db.get_person(person_id)
        project_details = await db.get_project(project_id)
        
        return {
            "success": True,
            "person": person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names'],
            "project": project_details['name'],
            "role": role,
            "allocation": allocation,
            "message": f"Assigned {person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names']} to {project_details['name']} as {role} ({allocation}% allocation)"
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
    is_current: bool = True
) -> dict:
    """Link a person to a company with employment information.
    
    Args:
        person: Person name or ID
        company: Company name or ID
        role: Role at company ('employee', 'contractor', 'intern', 'executive')
        is_current: Whether this is current employment
    
    Returns:
        Result of linking person to company
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Resolve person
        person_id = None
        if person.isdigit():
            person_id = int(person)
        else:
            people = await db.search_entities('person', person, 1)
            if people:
                person_id = people[0]['person_id']
            else:
                return {
                    "success": False,
                    "error": f"Person '{person}' not found"
                }
        
        # Resolve company
        company_id = None
        if company.isdigit():
            company_id = int(company)
        else:
            companies = await db.search_entities('company', company, 1)
            if companies:
                company_id = companies[0]['company_id']
            else:
                return {
                    "success": False,
                    "error": f"Company '{company}' not found"
                }
        
        # Update person's company
        await db.update_person(
            person_id=person_id,
            company_id=company_id
        )
        
        # Add to company relationship
        await db.add_person_to_company(
            person_id=person_id,
            company_id=company_id,
            role=role,
            is_current=is_current
        )
        
        # Get person and company details
        person_details = await db.get_person(person_id)
        company_details = await db.get_company(company_id)
        
        return {
            "success": True,
            "person": person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names'],
            "company": company_details['name'],
            "role": role,
            "is_current": is_current,
            "message": f"Linked {person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names']} to {company_details['name']} as {role}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def create_project(
    name: str,
    code: str = None,
    description: str = None,
    status: str = "active",
    company: str = None,
    lead_person: str = None,
    start_date: str = None,
    end_date: str = None,
    tags: list = None,
    urls: dict = None
) -> dict:
    """Create a new project with team and timeline information.
    
    Args:
        name: Project name (required)
        code: Project code/identifier
        description: Project description
        status: Project status (e.g., 'active', 'completed', 'on-hold')
        company: Company name (will create if doesn't exist)
        lead_person: Project lead name (will link if exists)
        start_date: Start date (YYYY-MM-DD format)
        end_date: End date (YYYY-MM-DD format)
        tags: List of project tags
        urls: Dictionary of URLs (e.g., {'github': 'https://...', 'docs': 'https://...'})
    
    Returns:
        Project creation result with ID
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Resolve company ID if provided
        company_id = None
        if company:
            companies = await db.search_entities('company', company, 1)
            if companies:
                company_id = companies[0]['company_id']
            else:
                # Create company
                company_id = await db.create_company(name=company)
        
        # Resolve lead person ID if provided
        lead_person_id = None
        if lead_person:
            people = await db.search_entities('person', lead_person, 1)
            if people:
                lead_person_id = people[0]['person_id']
        
        # Create project
        project_id = await db.create_project(
            name=name,
            code=code,
            description=description,
            status=status,
            company_id=company_id,
            lead_person_id=lead_person_id,
            start_date=start_date,
            end_date=end_date,
            tags=tags or [],
            urls=urls or {}
        )
        
        # Get created project
        project = await db.get_project(project_id)
        
        # Generate embedding if embedder is available
        if embedder and project:
            # Add company/lead names for context
            if company_id:
                project['company_name'] = company
            if lead_person_id:
                project['lead_name'] = lead_person
            
            vector = await embedder.embed_project(project)
            await db.update_project(project_id, vector=vector)
        
        # If lead person provided, add them to the project
        if lead_person_id:
            await db.add_person_to_project(
                person_id=lead_person_id,
                project_id=project_id,
                role="lead",
                allocation=100
            )
        
        return {
            "success": True,
            "project_id": project_id,
            "project": {
                'name': name,
                'code': code,
                'description': description,
                'status': status,
                'company': company,
                'lead_person': lead_person,
                'start_date': start_date,
                'end_date': end_date,
                'tags': tags,
                'urls': urls
            },
            "message": f"Successfully created project: {name}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def add_person_to_channel(
    person: str,
    channel: str,
    role: str = "member"
) -> dict:
    """Add a person to a communication channel with a specific role.
    
    Args:
        person: Person name or ID
        channel: Channel name or ID
        role: Role in channel ('member', 'admin', 'owner')
    
    Returns:
        Result of adding person to channel
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Resolve person
        person_id = None
        if person.isdigit():
            person_id = int(person)
        else:
            people = await db.search_entities('person', person, 1)
            if people:
                person_id = people[0]['person_id']
            else:
                return {
                    "success": False,
                    "error": f"Person '{person}' not found"
                }
        
        # Resolve channel
        channel_id = None
        if channel.isdigit():
            channel_id = int(channel)
        else:
            channels = await db.search_entities('channel', channel, 1)
            if channels:
                channel_id = channels[0]['channel_id']
            else:
                return {
                    "success": False,
                    "error": f"Channel '{channel}' not found"
                }
        
        # Add person to channel
        await db.add_person_to_channel(
            person_id=person_id,
            channel_id=channel_id,
            role=role
        )
        
        # Get person and channel details
        person_details = await db.get_person(person_id)
        channel_details = await db.get_channel(channel_id)
        
        return {
            "success": True,
            "person": person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names'],
            "channel": channel_details['name'],
            "role": role,
            "message": f"Added {person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names']} to {channel_details['name']} as {role}"
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
    allocation: int = 50
) -> dict:
    """Assign a person to a project with role and time allocation.
    
    Args:
        person: Person name or ID
        project: Project name or ID
        role: Role in project ('lead', 'contributor', 'reviewer')
        allocation: Time allocation percentage (0-100)
    
    Returns:
        Result of assigning person to project
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Resolve person
        person_id = None
        if person.isdigit():
            person_id = int(person)
        else:
            people = await db.search_entities('person', person, 1)
            if people:
                person_id = people[0]['person_id']
            else:
                return {
                    "success": False,
                    "error": f"Person '{person}' not found"
                }
        
        # Resolve project
        project_id = None
        if project.isdigit():
            project_id = int(project)
        else:
            projects = await db.search_entities('project', project, 1)
            if projects:
                project_id = projects[0]['project_id']
            else:
                return {
                    "success": False,
                    "error": f"Project '{project}' not found"
                }
        
        # Add person to project
        await db.add_person_to_project(
            person_id=person_id,
            project_id=project_id,
            role=role,
            allocation=allocation
        )
        
        # Get person and project details
        person_details = await db.get_person(person_id)
        project_details = await db.get_project(project_id)
        
        return {
            "success": True,
            "person": person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names'],
            "project": project_details['name'],
            "role": role,
            "allocation": allocation,
            "message": f"Assigned {person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names']} to {project_details['name']} as {role} ({allocation}% allocation)"
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
    is_current: bool = True
) -> dict:
    """Link a person to a company with employment information.
    
    Args:
        person: Person name or ID
        company: Company name or ID
        role: Role at company ('employee', 'contractor', 'intern', 'executive')
        is_current: Whether this is current employment
    
    Returns:
        Result of linking person to company
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Resolve person
        person_id = None
        if person.isdigit():
            person_id = int(person)
        else:
            people = await db.search_entities('person', person, 1)
            if people:
                person_id = people[0]['person_id']
            else:
                return {
                    "success": False,
                    "error": f"Person '{person}' not found"
                }
        
        # Resolve company
        company_id = None
        if company.isdigit():
            company_id = int(company)
        else:
            companies = await db.search_entities('company', company, 1)
            if companies:
                company_id = companies[0]['company_id']
            else:
                return {
                    "success": False,
                    "error": f"Company '{company}' not found"
                }
        
        # Update person's company
        await db.update_person(
            person_id=person_id,
            company_id=company_id
        )
        
        # Add to company relationship
        await db.add_person_to_company(
            person_id=person_id,
            company_id=company_id,
            role=role,
            is_current=is_current
        )
        
        # Get person and company details
        person_details = await db.get_person(person_id)
        company_details = await db.get_company(company_id)
        
        return {
            "success": True,
            "person": person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names'],
            "company": company_details['name'],
            "role": role,
            "is_current": is_current,
            "message": f"Linked {person_details['names'][0] if isinstance(person_details['names'], list) else person_details['names']} to {company_details['name']} as {role}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
@mcp.tool()
async def find_people_by_criteria(
    company: str = None,
    skills: list = None,
    location: str = None,
    title: str = None,
    limit: int = 10
) -> dict:
    """Find people by various criteria like company, skills, location, or title.
    
    Args:
        company: Company name to filter by
        skills: List of skills to search for
        location: Location to filter by
        title: Job title to search for
        limit: Maximum number of results
    
    Returns:
        List of matching people
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Build search terms
        search_terms = []
        if company:
            search_terms.append(company)
        if skills:
            search_terms.extend(skills)
        if location:
            search_terms.append(location)
        if title:
            search_terms.append(title)
        
        # Perform search
        query = ' '.join(search_terms)
        people = await db.search_entities('person', query, limit)
        
        # Format results with company names
        formatted_results = []
        for person in people:
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
            "criteria": {
                "company": company,
                "skills": skills,
                "location": location,
                "title": title
            },
            "count": len(formatted_results),
            "results": formatted_results
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def get_person_network(person: str) -> dict:
    """Get a person's complete network including channels, projects, and colleagues.
    
    Args:
        person: Person name or ID
    
    Returns:
        Complete network information for the person
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Resolve person
        person_id = None
        person_details = None
        if person.isdigit():
            person_id = int(person)
            person_details = await db.get_person(person_id)
        else:
            people = await db.search_entities('person', person, 1)
            if people:
                person_id = people[0]['person_id']
                person_details = people[0]
        
        if not person_details:
            return {
                "success": False,
                "error": f"Person '{person}' not found"
            }
        
        # Get company info
        company_name = None
        company_details = None
        if person_details.get('company_id'):
            company_name = await db.get_company_name(person_details['company_id'])
            company_details = await db.get_company(person_details['company_id'])
        
        # Get channels
        channels = await db.get_person_channels(person_id)
        
        # Get projects
        projects = await db.get_person_projects(person_id)
        
        # Get colleagues
        colleagues = []
        if person_details.get('company_id'):
            colleagues = await db.get_company_people(person_details['company_id'], exclude_id=person_id)
        
        # Calculate network statistics
        total_connections = len(channels) + len(projects) + len(colleagues)
        
        return {
            "success": True,
            "person": {
                'person_id': person_details['person_id'],
                'names': person_details['names'],
                'email': person_details.get('email'),
                'title': person_details.get('title'),
                'company': company_name
            },
            "network_stats": {
                "total_connections": total_connections,
                "channels": len(channels),
                "projects": len(projects),
                "colleagues": len(colleagues)
            },
            "company": {
                'name': company_name,
                'domain': company_details.get('domain') if company_details else None,
                'industry': company_details.get('industry') if company_details else None
            } if company_details else None,
            "channels": [
                {
                    'name': ch['name'],
                    'platform': ch['platform'],
                    'role': ch.get('role'),
                    'purpose': ch.get('purpose')
                }
                for ch in channels
            ],
            "projects": [
                {
                    'name': proj['name'],
                    'role': proj.get('role'),
                    'allocation': proj.get('allocation'),
                    'status': proj.get('status')
                }
                for proj in projects
            ],
            "colleagues": [
                {
                    'names': col['names'],
                    'title': col.get('title'),
                    'department': col.get('department')
                }
                for col in colleagues[:10]  # Limit to 10 for readability
            ]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def get_company_overview(company: str) -> dict:
    """Get comprehensive overview of a company including people, projects, and channels.
    
    Args:
        company: Company name or ID
    
    Returns:
        Complete company overview with organizational structure
    """
    try:
        # Ensure initialization
        if db is None:
            await initialize()
        
        # Resolve company
        company_id = None
        company_details = None
        if company.isdigit():
            company_id = int(company)
            company_details = await db.get_company(company_id)
        else:
            companies = await db.search_entities('company', company, 1)
            if companies:
                company_id = companies[0]['company_id']
                company_details = companies[0]
        
        if not company_details:
            return {
                "success": False,
                "error": f"Company '{company}' not found"
            }
        
        # Get all people at company
        people = await db.get_company_people(company_id)
        
        # Get company projects  
        projects_query = """
        SELECT * FROM project WHERE company_id = ?
        """
        projects = await db.execute_query(projects_query, (company_id,))
        
        # Get company channels
        channels_query = """
        SELECT * FROM channel WHERE company_id = ?
        """
        channels = await db.execute_query(channels_query, (company_id,))
        
        # Organize people by department
        departments = {}
        for person in people:
            dept = person.get('department', 'Unknown')
            if dept not in departments:
                departments[dept] = []
            departments[dept].append({
                'names': person['names'],
                'title': person.get('title'),
                'email': person.get('email')
            })
        
        return {
            "success": True,
            "company": {
                'company_id': company_details['company_id'],
                'name': company_details['name'],
                'domain': company_details.get('domain'),
                'industry': company_details.get('industry'),
                'size': company_details.get('size'),
                'location_hq': company_details.get('location_hq'),
                'description': company_details.get('description')
            },
            "statistics": {
                "total_people": len(people),
                "total_projects": len(projects),
                "total_channels": len(channels),
                "departments": len(departments)
            },
            "departments": departments,
            "projects": [
                {
                    'name': proj['name'],
                    'code': proj.get('code'),
                    'status': proj.get('status'),
                    'description': proj.get('description')
                }
                for proj in projects
            ],
            "channels": [
                {
                    'name': ch['name'],
                    'platform': ch['platform'],
                    'type': ch.get('type'),
                    'purpose': ch.get('purpose')
                }
                for ch in channels
            ]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
EOF < /dev/null