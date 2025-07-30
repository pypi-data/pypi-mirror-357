"""Entity resolution utilities for Directory MCP."""

async def resolve_person_id(db, person_identifier: str) -> int:
    """Resolve a person identifier to database ID."""
    if not person_identifier:
        raise ValueError("Person identifier is required")
    
    # Try to parse as integer ID first
    try:
        person_id = int(person_identifier)
        person = await db.get_person(person_id)
        if person:
            return person_id
    except (ValueError, TypeError):
        pass
    
    # Try exact email match first (avoid FTS5 issues with special chars)
    if '@' in person_identifier:
        query = "SELECT person_id FROM person WHERE email = ?"
        results = await db.execute_query(query, (person_identifier,))
        if results:
            return results[0]['person_id']
    
    # Try to find by name using search
    try:
        results = await db.search_people(person_identifier, limit=1)
        if results:
            return results[0]['person_id']
    except Exception:
        # FTS5 search failed, ignore and continue
        pass
    
    raise ValueError(f"Person not found: {person_identifier}")

async def resolve_company_id(db, company_identifier: str) -> int:
    """Resolve a company identifier to database ID."""
    if not company_identifier:
        raise ValueError("Company identifier is required")
    
    # Try to parse as integer ID first
    try:
        company_id = int(company_identifier)
        company = await db.get_company(company_id)
        if company:
            return company_id
    except (ValueError, TypeError):
        pass
    
    # Try to find by name or domain
    results = await db.search_companies(company_identifier, limit=1)
    if results:
        return results[0]['company_id']
    
    raise ValueError(f"Company not found: {company_identifier}")

async def resolve_channel_id(db, channel_identifier: str) -> int:
    """Resolve a channel identifier to database ID."""
    if not channel_identifier:
        raise ValueError("Channel identifier is required")
    
    # Try to parse as integer ID first
    try:
        channel_id = int(channel_identifier)
        channel = await db.get_channel(channel_id)
        if channel:
            return channel_id
    except (ValueError, TypeError):
        pass
    
    # Try to find by name
    results = await db.search_channels(channel_identifier, limit=1)
    if results:
        return results[0]['channel_id']
    
    raise ValueError(f"Channel not found: {channel_identifier}")

async def resolve_project_id(db, project_identifier: str) -> int:
    """Resolve a project identifier to database ID."""
    if not project_identifier:
        raise ValueError("Project identifier is required")
    
    # Try to parse as integer ID first
    try:
        project_id = int(project_identifier)
        project = await db.get_project(project_id)
        if project:
            return project_id
    except (ValueError, TypeError):
        pass
    
    # Try to find by name
    results = await db.search_projects(project_identifier, limit=1)
    if results:
        return results[0]['project_id']
    
    raise ValueError(f"Project not found: {project_identifier}")