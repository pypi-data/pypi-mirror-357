from functools import wraps
from typing import Optional, Type
from pydantic import BaseModel
from .generator import generate_proto_for_route

registered_grpc_routes = []

def grpc_route(path: str, response_model: Optional[Type[BaseModel]] = None):
    """
    Decorator to add gRPC support to FastAPI routes.
    
    Args:
        path: The route path (used for naming the gRPC service)
        response_model: Pydantic model for the response (optional, will try to infer from function annotations)
    
    Usage:
        @app.get("/hello")
        @grpc_route("/hello", response_model=HelloResponse)
        async def say_hello(name: str) -> HelloResponse:
            return HelloResponse(message=f"Hello, {name}")
    """
    def decorator(func):
        # Try to infer response_model from function annotations if not provided
        actual_response_model = response_model
        if actual_response_model is None:
            return_annotation = func.__annotations__.get('return')
            if return_annotation and hasattr(return_annotation, '__bases__') and BaseModel in return_annotation.__bases__:
                actual_response_model = return_annotation
        
        if actual_response_model is None:
            raise ValueError(f"Response model must be provided either as parameter or function return annotation for {func.__name__}")
        
        # Register the route for gRPC generation
        registered_grpc_routes.append((path, func, actual_response_model))
        
        # Generate proto file
        generate_proto_for_route(path, func, actual_response_model)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator
