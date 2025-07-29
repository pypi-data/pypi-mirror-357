"""Entity resolution utilities for Directory MCP."""

async def resolve_person_id(db, person_identifier: str) -> str:
    """Resolve a person identifier to database ID."""
    if not person_identifier:
        raise ValueError("Person identifier is required")
    
    # Try to find by ID first
    person = await db.get_person(person_identifier)
    if person:
        return person_identifier
    
    # Try to find by name or email
    results = await db.search_people(person_identifier, limit=1)
    if results:
        return results[0]['id']
    
    raise ValueError(f"Person not found: {person_identifier}")

async def resolve_company_id(db, company_identifier: str) -> str:
    """Resolve a company identifier to database ID."""
    if not company_identifier:
        raise ValueError("Company identifier is required")
    
    # Try to find by ID first
    company = await db.get_company(company_identifier)
    if company:
        return company_identifier
    
    # Try to find by name or domain
    results = await db.search_companies(company_identifier, limit=1)
    if results:
        return results[0]['id']
    
    raise ValueError(f"Company not found: {company_identifier}")

async def resolve_channel_id(db, channel_identifier: str) -> str:
    """Resolve a channel identifier to database ID."""
    if not channel_identifier:
        raise ValueError("Channel identifier is required")
    
    # Try to find by ID first
    channel = await db.get_channel(channel_identifier)
    if channel:
        return channel_identifier
    
    # Try to find by name
    results = await db.search_channels(channel_identifier, limit=1)
    if results:
        return results[0]['id']
    
    raise ValueError(f"Channel not found: {channel_identifier}")

async def resolve_project_id(db, project_identifier: str) -> str:
    """Resolve a project identifier to database ID."""
    if not project_identifier:
        raise ValueError("Project identifier is required")
    
    # Try to find by ID first
    project = await db.get_project(project_identifier)
    if project:
        return project_identifier
    
    # Try to find by name
    results = await db.search_projects(project_identifier, limit=1)
    if results:
        return results[0]['id']
    
    raise ValueError(f"Project not found: {project_identifier}")