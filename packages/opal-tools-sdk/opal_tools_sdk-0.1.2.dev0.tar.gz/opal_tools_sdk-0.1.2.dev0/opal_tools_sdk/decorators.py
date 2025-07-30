import inspect
import re
import logging
from typing import Callable, Any, List, Dict, Type, get_type_hints, Optional, Union
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from deprecated import deprecated

from .models import Parameter, ParameterType, AuthRequirement
from . import _registry

logger = logging.getLogger("opal_tools_sdk")

@deprecated("Use @tool_service.tool decorator instead")
def tool(name: str, description: str, auth_requirements: Optional[Dict[str, Any]] = None):
    """Decorator to register a function as an Opal tool.
    
    Args:
        name: Name of the tool
        description: Description of the tool
        auth_requirements: Authentication requirements (optional)
            Format: {"provider": "oauth_provider", "scope_bundle": "permissions_scope", "required": True}
            Example: {"provider": "google", "scope_bundle": "calendar", "required": True}
    
    Returns:
        Decorator function
    
    Note:
        If your tool requires authentication, define your handler function with two parameters:
        async def my_tool(parameters: ParametersModel, auth_data: Optional[Dict] = None):
            ...
    """
    def decorator(func: Callable):
        if not _registry.services:
            logger.warning("No services registered in registry! Make sure to create ToolsService before decorating functions.")
            return func
            
        # Use the first available service's tool decorator
        service = _registry.services[0]
        return service.tool(name, description, auth_requirements)(func)
    
    return decorator
