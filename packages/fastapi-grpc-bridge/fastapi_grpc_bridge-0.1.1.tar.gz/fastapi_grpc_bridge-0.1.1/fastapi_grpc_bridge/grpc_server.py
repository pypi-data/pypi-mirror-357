import grpc
from concurrent import futures
import os
import sys
import importlib.util
import asyncio
from grpc_tools import protoc

from .decorators import registered_grpc_routes
from .generator import PROTO_DIR

def compile_protos():
    for file in os.listdir(PROTO_DIR):
        if file.endswith(".proto"):
            protoc.main((
                '',
                f'-I{PROTO_DIR}',
                f'--python_out={PROTO_DIR}',
                f'--grpc_python_out={PROTO_DIR}',
                os.path.join(PROTO_DIR, file),
            ))

def import_generated_module(func_name):
    # Add the proto directory to sys.path if not already there
    abs_proto_dir = os.path.abspath(PROTO_DIR)
    if abs_proto_dir not in sys.path:
        sys.path.insert(0, abs_proto_dir)
    
    module_path = os.path.join(PROTO_DIR, f"{func_name}_pb2_grpc.py")
    spec = importlib.util.spec_from_file_location(f"{func_name}_pb2_grpc", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def import_message_module(func_name):
    # Add the proto directory to sys.path if not already there
    abs_proto_dir = os.path.abspath(PROTO_DIR)
    if abs_proto_dir not in sys.path:
        sys.path.insert(0, abs_proto_dir)
    
    module_path = os.path.join(PROTO_DIR, f"{func_name}_pb2.py")
    spec = importlib.util.spec_from_file_location(f"{func_name}_pb2", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def create_servicer(func, func_name, pb2, pb2_grpc):
    class GenericServicer(getattr(pb2_grpc, f"{func_name.capitalize()}ServiceServicer")):
        def Call(self, request, context):
            try:
                kwargs = {field: getattr(request, field) for field in request.DESCRIPTOR.fields_by_name}

                if asyncio.iscoroutinefunction(func):
                    result = asyncio.run(func(**kwargs))
                else:
                    result = func(**kwargs)

                return pb2.__getattribute__(f"{func_name}Response")(**result.dict())

            except Exception as e:
                context.set_details(str(e))
                context.set_code(grpc.StatusCode.INTERNAL)
                return pb2.__getattribute__(f"{func_name}Response")()

    return GenericServicer()

def main():
    compile_protos()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    if not registered_grpc_routes:
        print("❌ No gRPC routes registered!")
        print("   Make sure to import your FastAPI app with @grpc_route decorators before starting the server.")
        return

    for path, func, response_model in registered_grpc_routes:
        func_name = func.__name__
        pb2 = import_message_module(func_name)
        pb2_grpc = import_generated_module(func_name)
        servicer = create_servicer(func, func_name, pb2, pb2_grpc)
        add_func = getattr(pb2_grpc, f"add_{func_name.capitalize()}ServiceServicer_to_server")
        add_func(servicer, server)

    print("✅ gRPC server running on port 50051")
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
