from .decorators import grpc_route
from .utils import (
    add_grpc_support, 
    start_grpc_server_standalone,
    create_secure_grpc_config,
    start_grpc_server_insecure,
    start_grpc_server_with_tls,
    start_grpc_server_with_mtls
)
from .grpc_server import main as start_grpc_server, create_grpc_server
from .config import GRPCSecurityConfig, TLSConfig, MTLSConfig
from .cert_utils import (
    create_server_credentials,
    create_client_credentials,
    validate_certificates,
    generate_self_signed_cert
)

__version__ = "0.1.2"
__all__ = [
    # Core functionality
    "grpc_route",
    "add_grpc_support", 
    "start_grpc_server_standalone",
    "start_grpc_server",
    "create_grpc_server",
    
    # Security configuration
    "GRPCSecurityConfig",
    "TLSConfig", 
    "MTLSConfig",
    
    # Convenience functions
    "create_secure_grpc_config",
    "start_grpc_server_insecure",
    "start_grpc_server_with_tls",
    "start_grpc_server_with_mtls",
    
    # Certificate utilities
    "create_server_credentials",
    "create_client_credentials", 
    "validate_certificates",
    "generate_self_signed_cert"
]

# Backward compatibility - keep the old exports at the module level
start_grpc_server_legacy = start_grpc_server
