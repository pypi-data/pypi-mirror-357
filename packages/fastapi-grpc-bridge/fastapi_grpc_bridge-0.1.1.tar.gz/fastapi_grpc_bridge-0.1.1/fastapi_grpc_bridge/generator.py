import os
from inspect import signature
from typing import get_origin, get_args, Union
from pydantic import BaseModel

PROTO_DIR = "generated_protos"

def type_map(py_type):
    """Map Python types to protobuf types"""
    # Handle basic types
    basic_mapping = {
        str: "string",
        int: "int32",
        float: "float",
        bool: "bool",
        bytes: "bytes"
    }
    
    if py_type in basic_mapping:
        return basic_mapping[py_type]
    
    # Handle Optional types (Union[T, None])
    if get_origin(py_type) is Union:
        args = get_args(py_type)
        if len(args) == 2 and type(None) in args:
            # This is Optional[T]
            non_none_type = args[0] if args[1] is type(None) else args[1]
            return type_map(non_none_type)
    
    # Default to string for unknown types
    return "string"

def write_proto_file(route, func, response_model):
    func_name = func.__name__
    sig = signature(func)
    params = list(sig.parameters.values())
    
    proto_lines = [
        f'syntax = "proto3";',
        f'package {func_name};',
        "",
        f"service {func_name.capitalize()}Service {{",
        f"  rpc Call({func_name}Request) returns ({func_name}Response);",
        f"}}",
        ""
    ]

    # Generate request message
    proto_lines.append(f"message {func_name}Request {{")
    for i, param in enumerate(params, 1):
        annotation = param.annotation if param.annotation != param.empty else str
        proto_type = type_map(annotation)
        proto_lines.append(f"  {proto_type} {param.name} = {i};")
    proto_lines.append("}")

    # Generate response message
    proto_lines.append(f"message {func_name}Response {{")
    if response_model and issubclass(response_model, BaseModel):
        for i, (field, type_) in enumerate(response_model.__annotations__.items(), 1):
            proto_type = type_map(type_)
            proto_lines.append(f"  {proto_type} {field} = {i};")
    proto_lines.append("}")

    # Ensure directory exists
    os.makedirs(PROTO_DIR, exist_ok=True)
    
    # Write proto file
    proto_file_path = os.path.join(PROTO_DIR, f"{func_name}.proto")
    with open(proto_file_path, "w") as f:
        f.write("\n".join(proto_lines))

def generate_proto_for_route(route, func, response_model):
    """Generate protobuf definition for a FastAPI route"""
    write_proto_file(route, func, response_model)
