from fastapi import FastAPI
from fastapi.routing import APIRouter
import threading
import time
from .grpc_server import main as start_grpc_server
from .decorators import registered_grpc_routes

def add_grpc_support(app_or_router, auto_start_grpc=True):
    """
    Add gRPC support to a FastAPI app or router.
    
    Args:
        app_or_router: FastAPI app instance or APIRouter instance
        auto_start_grpc: Whether to automatically start gRPC server when FastAPI starts
    
    Usage:
        app = FastAPI()
        add_grpc_support(app)  # Auto-starts gRPC server
        
        # Or disable auto-start
        add_grpc_support(app, auto_start_grpc=False)
        
        # Or with a router
        router = APIRouter()
        add_grpc_support(router)
    """
    if not isinstance(app_or_router, (FastAPI, APIRouter)):
        raise ValueError("app_or_router must be a FastAPI app or APIRouter instance")
    
    # Mark as gRPC enabled
    app_or_router._grpc_enabled = True
    
    # If it's a FastAPI app and auto_start is enabled, add startup event
    if isinstance(app_or_router, FastAPI) and auto_start_grpc:
        @app_or_router.on_event("startup")
        async def start_grpc_on_startup():
            """Start gRPC server in background thread when FastAPI starts"""
            def run_grpc_server():
                # Small delay to ensure FastAPI is fully initialized
                time.sleep(1)
                if registered_grpc_routes:
                    print(f"🚀 Auto-starting gRPC server with {len(registered_grpc_routes)} registered routes...")
                    try:
                        start_grpc_server()
                    except Exception as e:
                        print(f"❌ Failed to start gRPC server: {e}")
                else:
                    print("⚠️  No gRPC routes registered. gRPC server not started.")
            
            # Start gRPC server in a separate thread
            grpc_thread = threading.Thread(target=run_grpc_server, daemon=True)
            grpc_thread.start()
            print("✅ FastAPI startup complete. gRPC server starting in background...")

def start_grpc_server_standalone():
    """Start the gRPC server in standalone mode"""
    if not registered_grpc_routes:
        print("❌ No gRPC routes registered!")
        print("   Make sure to import your FastAPI app with @grpc_route decorators first.")
        return False
    
    print(f"🚀 Starting gRPC server with {len(registered_grpc_routes)} registered routes...")
    start_grpc_server()
    return True 