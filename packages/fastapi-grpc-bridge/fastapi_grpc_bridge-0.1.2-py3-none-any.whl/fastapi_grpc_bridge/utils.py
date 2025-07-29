from fastapi import FastAPI
from fastapi.routing import APIRouter
import threading
import time
from typing import Optional, Dict, Any
from .grpc_server import main as start_grpc_server, create_grpc_server
from .decorators import registered_grpc_routes
from .config import GRPCSecurityConfig

def add_grpc_support(app_or_router, 
                    auto_start_grpc=True, 
                    config: Optional[GRPCSecurityConfig] = None,
                    config_dict: Optional[Dict[str, Any]] = None):
    """
    Add gRPC support to a FastAPI app or router.
    
    Args:
        app_or_router: FastAPI app instance or APIRouter instance
        auto_start_grpc: Whether to automatically start gRPC server when FastAPI starts
        config: GRPCSecurityConfig instance for server configuration
        config_dict: Dictionary configuration (alternative to config parameter)
    
    Usage:
        # Basic usage (insecure)
        app = FastAPI()
        add_grpc_support(app)  # Auto-starts insecure gRPC server
        
        # With TLS
        tls_config = GRPCSecurityConfig(
            insecure=False,
            tls=TLSConfig(
                enabled=True,
                cert_file="path/to/server.crt",
                key_file="path/to/server.key"
            )
        )
        add_grpc_support(app, config=tls_config)
        
        # With mTLS
        mtls_config = GRPCSecurityConfig(
            insecure=False,
            tls=TLSConfig(
                enabled=True,
                cert_file="path/to/server.crt",
                key_file="path/to/server.key"
            ),
            mtls=MTLSConfig(
                enabled=True,
                ca_cert_file="path/to/ca.crt"
            )
        )
        add_grpc_support(app, config=mtls_config)
        
        # From dictionary
        config_dict = {
            "insecure": False,
            "host": "0.0.0.0",
            "port": 443,
            "tls": {
                "enabled": True,
                "cert_file": "server.crt",
                "key_file": "server.key"
            }
        }
        add_grpc_support(app, config_dict=config_dict)
        
        # From environment variables
        add_grpc_support(app, config=GRPCSecurityConfig.from_env())
        
        # Or disable auto-start
        add_grpc_support(app, auto_start_grpc=False)
        
        # Or with a router
        router = APIRouter()
        add_grpc_support(router)
    """
    if not isinstance(app_or_router, (FastAPI, APIRouter)):
        raise ValueError("app_or_router must be a FastAPI app or APIRouter instance")
    
    # Handle configuration
    if config is None:
        if config_dict is not None:
            config = GRPCSecurityConfig.from_dict(config_dict)
        else:
            config = GRPCSecurityConfig()  # Default insecure configuration
    
    # Mark as gRPC enabled and store config
    app_or_router._grpc_enabled = True
    app_or_router._grpc_config = config
    
    # If it's a FastAPI app and auto_start is enabled, add startup event
    if isinstance(app_or_router, FastAPI) and auto_start_grpc:
        @app_or_router.on_event("startup")
        async def start_grpc_on_startup():
            """Start gRPC server in background thread when FastAPI starts"""
            def run_grpc_server():
                # Small delay to ensure FastAPI is fully initialized
                time.sleep(1)
                if registered_grpc_routes:
                    route_count = len(registered_grpc_routes)
                    security_mode = "secure" if config.is_secure() else "insecure"
                    print(f"🚀 Auto-starting {security_mode} gRPC server with {route_count} registered routes...")
                    try:
                        start_grpc_server(config)
                    except Exception as e:
                        print(f"❌ Failed to start gRPC server: {e}")
                        # Print more details for certificate issues
                        if "Certificate" in str(e) or "TLS" in str(e) or "SSL" in str(e):
                            print("   Check your certificate files and configuration.")
                else:
                    print("⚠️  No gRPC routes registered. gRPC server not started.")
            
            # Start gRPC server in a separate thread
            grpc_thread = threading.Thread(target=run_grpc_server, daemon=True)
            grpc_thread.start()
            print("✅ FastAPI startup complete. gRPC server starting in background...")

def start_grpc_server_standalone(config: Optional[GRPCSecurityConfig] = None,
                                config_dict: Optional[Dict[str, Any]] = None,
                                from_env: bool = False):
    """
    Start the gRPC server in standalone mode with optional security configuration
    
    Args:
        config: GRPCSecurityConfig instance
        config_dict: Dictionary configuration
        from_env: Load configuration from environment variables
    
    Returns:
        bool: True if server started successfully, False otherwise
    """
    if not registered_grpc_routes:
        print("❌ No gRPC routes registered!")
        print("   Make sure to import your FastAPI app with @grpc_route decorators first.")
        return False
    
    # Handle configuration
    if config is None:
        if from_env:
            config = GRPCSecurityConfig.from_env()
        elif config_dict is not None:
            config = GRPCSecurityConfig.from_dict(config_dict)
        else:
            config = GRPCSecurityConfig()  # Default insecure configuration
    
    route_count = len(registered_grpc_routes)
    security_mode = "secure" if config.is_secure() else "insecure"
    print(f"🚀 Starting {security_mode} gRPC server with {route_count} registered routes...")
    
    try:
        start_grpc_server(config)
        return True
    except Exception as e:
        print(f"❌ Failed to start gRPC server: {e}")
        return False

def create_secure_grpc_config(cert_file: str, 
                             key_file: str,
                             ca_cert_file: Optional[str] = None,
                             enable_mtls: bool = False,
                             client_cert_required: bool = True,
                             host: str = "[::]",
                             port: int = 50051) -> GRPCSecurityConfig:
    """
    Convenience function to create a secure gRPC configuration
    
    Args:
        cert_file: Path to server certificate file
        key_file: Path to server private key file
        ca_cert_file: Path to CA certificate file (required for mTLS)
        enable_mtls: Whether to enable mutual TLS
        client_cert_required: Whether client certificates are required (mTLS only)
        host: Host to bind to
        port: Port to bind to
    
    Returns:
        GRPCSecurityConfig: Configured security config
    """
    from .config import TLSConfig, MTLSConfig
    
    tls_config = TLSConfig(
        enabled=True,
        cert_file=cert_file,
        key_file=key_file,
        ca_cert_file=ca_cert_file if not enable_mtls else None
    )
    
    mtls_config = MTLSConfig(
        enabled=enable_mtls,
        ca_cert_file=ca_cert_file if enable_mtls else None,
        client_cert_required=client_cert_required
    )
    
    return GRPCSecurityConfig(
        host=host,
        port=port,
        insecure=False,
        tls=tls_config,
        mtls=mtls_config
    )

# Backward compatibility functions
def start_grpc_server_insecure():
    """Start gRPC server in insecure mode (backward compatibility)"""
    return start_grpc_server_standalone(GRPCSecurityConfig())

def start_grpc_server_with_tls(cert_file: str, key_file: str, 
                              host: str = "[::]", port: int = 50051):
    """Start gRPC server with TLS (convenience function)"""
    config = create_secure_grpc_config(cert_file, key_file, host=host, port=port)
    return start_grpc_server_standalone(config)

def start_grpc_server_with_mtls(cert_file: str, key_file: str, ca_cert_file: str,
                               client_cert_required: bool = True,
                               host: str = "[::]", port: int = 50051):
    """Start gRPC server with mTLS (convenience function)"""
    config = create_secure_grpc_config(
        cert_file, key_file, ca_cert_file, 
        enable_mtls=True, client_cert_required=client_cert_required,
        host=host, port=port
    )
    return start_grpc_server_standalone(config) 