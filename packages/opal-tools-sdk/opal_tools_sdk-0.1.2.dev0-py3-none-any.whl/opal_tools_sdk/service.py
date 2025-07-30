from typing import Dict, List, Any, Callable, Type, Optional, get_type_hints, Union
import inspect
import logging
from fastapi import FastAPI, APIRouter, Depends, Header, HTTPException, Request
from fastapi.routing import APIRoute
from pydantic import BaseModel, create_model

from .models import Function, Parameter, ParameterType, AuthRequirement
from . import _registry

logger = logging.getLogger("opal_tools_sdk")

class ToolsService:
    """Main class for managing Opal tools."""
    
    def __init__(self, app: FastAPI):
        """Initialize the tools service.
        
        Args:
            app: FastAPI application to attach routes to
        """
        self.app = app
        self.router = APIRouter()
        self.functions: List[Function] = []
        self._init_routes()
        
        # Register in the global registry
        _registry.services.append(self)
        
        # Debug existing routes
        @app.get("/debug-routes")
        async def debug_routes():
            routes = []
            for route in app.routes:
                if isinstance(route, APIRoute):
                    routes.append({
                        "path": route.path,
                        "name": route.name,
                        "methods": route.methods
                    })
            return {"routes": routes}
    
    def _init_routes(self) -> None:
        """Initialize the discovery endpoint."""
        @self.router.get("/discovery")
        async def discovery() -> Dict[str, Any]:
            """Return the discovery information for this tools service."""
            return {"functions": [f.to_dict() for f in self.functions]}
        
        # Include router in app
        self.app.include_router(self.router)
    
    def register_tool(self, 
                     name: str, 
                     description: str, 
                     handler: Callable, 
                     parameters: List[Parameter],
                     endpoint: str,
                     auth_requirements: Optional[AuthRequirement] = None) -> None:
        """Register a tool function.
        
        Args:
            name: Name of the tool
            description: Description of the tool
            handler: Function that implements the tool
            parameters: List of parameters for the tool
            endpoint: API endpoint for the tool
            auth_requirements: Authentication requirements (optional)
        """
        logger.info(f"Registering tool: {name} with endpoint: {endpoint}")
        
        function = Function(
            name=name,
            description=description,
            parameters=parameters,
            endpoint=endpoint,
            auth_requirements=auth_requirements
        )
        
        self.functions.append(function)
        
        # Create a direct route with the app for better control
        @self.app.post(endpoint)
        async def tool_endpoint(request: Request):
            try:
                # Parse JSON body
                body = await request.json()
                logger.debug(f"Received request for {endpoint} with body: {body}")
                
                # Parameters should be in the "parameters" key according to the spec
                # This matches how the tools-mgmt-service calls tools
                if "parameters" in body:
                    params = body["parameters"]
                else:
                    # For backward compatibility with direct test calls
                    logger.warning(f"'parameters' key not found in request body. Using body directly.")
                    params = body
                
                # Extract auth data if available
                auth_data = body.get("auth")
                if auth_data:
                    logger.debug(f"Auth data provided for provider: {auth_data.get('provider', 'unknown')}")
                
                logger.debug(f"Extracted parameters: {params}")
                
                # Get the parameter model from handler's signature
                sig = inspect.signature(handler)
                param_name = list(sig.parameters.keys())[0]
                param_type = get_type_hints(handler).get(param_name)
                
                # Check signature to see if it accepts auth data
                accepts_auth = len(sig.parameters) > 1
                
                if param_type:
                    # Create instance of param model
                    model_instance = param_type(**params)
                    if accepts_auth:
                        # Call with auth data if the handler accepts it
                        result = await handler(model_instance, auth_data)
                    else:
                        # Call without auth data
                        result = await handler(model_instance)
                else:
                    # Fall back if type hints not available
                    if accepts_auth:
                        result = await handler(BaseModel(**params), auth_data)
                    else:
                        result = await handler(BaseModel(**params))
                
                logger.debug(f"Tool {name} returned: {result}")
                return result
            except Exception as e:
                import traceback
                logger.error(f"Error in tool {name}: {str(e)}")
                logger.error(traceback.format_exc())
                raise HTTPException(status_code=500, detail=str(e))
        
        # Update the route function name and docstring
        tool_endpoint.__name__ = f"tool_{name}"
        tool_endpoint.__doc__ = description

    def tool(self, name: str, description: str, auth_requirements: Optional[Dict[str, Any]] = None):
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
            # Extract parameters from function signature
            sig = inspect.signature(func)
            type_hints = get_type_hints(func)
            
            parameters: List[Parameter] = []
            param_model = None
            
            # Look for a parameter that is a pydantic model (for parameters)
            for param_name, param in sig.parameters.items():
                if param_name in type_hints:
                    param_type = type_hints[param_name]
                    if hasattr(param_type, '__fields__') or hasattr(param_type, 'model_fields'):  # Pydantic v1 or v2
                        param_model = param_type
                        break
            
            # If we found a pydantic model, extract parameters
            if param_model:
                model_fields = getattr(param_model, 'model_fields', getattr(param_model, '__fields__', {}))
                for field_name, field in model_fields.items():
                    # Get field metadata
                    field_info = field.field_info if hasattr(field, 'field_info') else field
                    
                    # Determine type
                    if hasattr(field, 'outer_type_'):
                        field_type = field.outer_type_
                    elif hasattr(field, 'annotation'):
                        field_type = field.annotation
                    else:
                        field_type = str
                    
                    # Map Python type to Parameter type
                    param_type = ParameterType.string
                    if field_type == int:
                        param_type = ParameterType.integer
                    elif field_type == float:
                        param_type = ParameterType.number
                    elif field_type == bool:
                        param_type = ParameterType.boolean
                    elif field_type == list or field_type == List:
                        param_type = ParameterType.list
                    elif field_type == dict or field_type == Dict:
                        param_type = ParameterType.dictionary
                    
                    # Determine if required
                    field_info_extra = getattr(field_info, "json_schema_extra") or {}
                    if "required" in field_info_extra:
                        required = field_info_extra["required"]
                    else:
                        required = field_info.default is ... if hasattr(field_info, 'default') else True

                    
                    # Get description
                    description_text = ""
                    if hasattr(field_info, 'description'):
                        description_text = field_info.description
                    elif hasattr(field, 'description'):
                        description_text = field.description
                    
                    parameters.append(Parameter(
                        name=field_name,
                        param_type=param_type,
                        description=description_text,
                        required=required
                    ))
                    
                    logger.debug(f"Registered parameter: {field_name} of type {param_type.value}, required: {required}")
            else:
                logger.warning(f"No parameter model found for {name}")
            
            endpoint = f"/tools/{name}"
            
            # Register the tool with the service
            auth_req = None
            if auth_requirements:
                auth_req = AuthRequirement(
                    provider=auth_requirements.get("provider", ""),
                    scope_bundle=auth_requirements.get("scope_bundle", ""),
                    required=auth_requirements.get("required", True)
                )
            
            logger.info(f"Registering tool {name} with endpoint {endpoint}")
            
            self.register_tool(
                name=name,
                description=description,
                handler=func,
                parameters=parameters,
                endpoint=endpoint,
                auth_requirements=auth_req
            )
            
            return func
        
        return decorator
