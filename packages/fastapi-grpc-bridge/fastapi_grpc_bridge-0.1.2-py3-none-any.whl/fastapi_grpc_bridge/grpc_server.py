import grpc
from concurrent import futures
import os
import sys
import importlib.util
import asyncio
from grpc_tools import protoc
from typing import Optional

from .decorators import registered_grpc_routes
from .generator import PROTO_DIR
from .config import GRPCSecurityConfig
from .cert_utils import create_server_credentials, validate_certificates

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

def create_grpc_server(config: Optional[GRPCSecurityConfig] = None):
    """Create a gRPC server with the specified configuration"""
    if config is None:
        config = GRPCSecurityConfig()  # Use default insecure configuration
    
    # Validate configuration
    if config.is_secure():
        cert_issues = validate_certificates(config)
        if cert_issues:
            raise ValueError(f"Certificate validation failed: {'; '.join(cert_issues)}")
    
    # Create server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=config.max_workers))
    
    # Register services
    if not registered_grpc_routes:
        print("❌ No gRPC routes registered!")
        print("   Make sure to import your FastAPI app with @grpc_route decorators before starting the server.")
        return None
    
    for path, func, response_model in registered_grpc_routes:
        func_name = func.__name__
        pb2 = import_message_module(func_name)
        pb2_grpc = import_generated_module(func_name)
        servicer = create_servicer(func, func_name, pb2, pb2_grpc)
        add_func = getattr(pb2_grpc, f"add_{func_name.capitalize()}ServiceServicer_to_server")
        add_func(servicer, server)
    
    # Configure server port and security
    server_address = f"{config.host}:{config.port}"
    
    if config.is_secure():
        # Create secure server
        credentials = create_server_credentials(config)
        server.add_secure_port(server_address, credentials)
        
        security_type = "TLS"
        if config.mtls.enabled:
            security_type = "mTLS"
            if config.mtls.client_cert_required:
                security_type += " (client cert required)"
            else:
                security_type += " (client cert optional)"
        
        print(f"✅ Secure gRPC server ({security_type}) running on {server_address}")
        print(f"   Server cert: {config.tls.cert_file}")
        if config.mtls.enabled:
            print(f"   CA cert: {config.mtls.ca_cert_file}")
    else:
        # Create insecure server (backward compatibility)
        server.add_insecure_port(server_address)
        print(f"✅ Insecure gRPC server running on {server_address}")
        print("   ⚠️  Warning: Server is running in insecure mode!")
    
    return server

def main(config: Optional[GRPCSecurityConfig] = None):
    """Start the gRPC server with optional security configuration"""
    compile_protos()
    
    server = create_grpc_server(config)
    if server is None:
        return
    
    server.start()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down gRPC server...")
        server.stop(0)

# Backward compatibility - maintain the original function signature
def start_grpc_server_insecure():
    """Start gRPC server in insecure mode (backward compatibility)"""
    return main(GRPCSecurityConfig())

# Legacy main function for backward compatibility
if __name__ == "__main__":
    main()
