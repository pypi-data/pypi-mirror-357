"""Utility functions for JSON serialization of database entities."""
from typing import Any, Dict, List, Optional, Union


def remove_vectors(data: Union[Dict[str, Any], List[Dict[str, Any]], None]) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
    """Remove binary vector fields from entities to enable JSON serialization.
    
    Args:
        data: Entity dict, list of entity dicts, or None
        
    Returns:
        The same data structure with 'vector' fields removed
    """
    if data is None:
        return None
        
    if isinstance(data, list):
        # Handle list of entities
        for item in data:
            if isinstance(item, dict) and 'vector' in item:
                item.pop('vector', None)
        return data
        
    elif isinstance(data, dict):
        # Handle single entity
        if 'vector' in data:
            data.pop('vector', None)
        return data
        
    return data