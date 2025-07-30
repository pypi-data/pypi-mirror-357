"""Tools package for Directory MCP."""

def register_all_tools(mcp, db, config, embedder):
    """Register all MCP tools."""
    
    # Import and register system tools
    from .system import register_system_tools
    register_system_tools(mcp, db, config, embedder)
    
    # Import and register entity tools
    from .entities.person import register_person_tools
    from .entities.company import register_company_tools
    from .entities.channel import register_channel_tools
    from .entities.project import register_project_tools
    
    register_person_tools(mcp, db, config, embedder)
    register_company_tools(mcp, db, config, embedder)
    register_channel_tools(mcp, db, config, embedder)
    register_project_tools(mcp, db, config, embedder)
    
    # Import and register search tools
    from .search import register_search_tools
    register_search_tools(mcp, db, config, embedder)
    
    # Import and register relationship tools
    from .relationships import register_relationship_tools
    register_relationship_tools(mcp, db, config, embedder)
    
    # Import and register analysis tools
    from .analysis import register_analysis_tools
    register_analysis_tools(mcp, db, config, embedder)