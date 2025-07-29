# FastAPI gRPC Bridge

A Python package that seamlessly adds gRPC support to FastAPI applications using decorators. It automatically generates Protocol Buffer definitions from Pydantic models and creates gRPC services that mirror your FastAPI routes.

## Features

- 🚀 **Easy Integration**: Add gRPC support to existing FastAPI apps with a simple decorator
- 🔄 **Auto Proto Generation**: Automatically generates `.proto` files from Pydantic models
- 📡 **Dual Protocol Support**: Serve both HTTP and gRPC from the same codebase
- ⚡ **Auto-Start gRPC**: Automatically starts gRPC server when FastAPI starts (configurable)
- 🎯 **Type Safety**: Full type safety with Pydantic models
- 🔧 **FastAPI Router Support**: Works with FastAPI routers and sub-applications
- 🌐 **Async Support**: Full support for async/await functions

## Installation

```bash
pip install fastapi-grpc-bridge
```

## Quick Start

### 1. Basic Usage with Auto-Start (Recommended)

```python
from fastapi import FastAPI
from fastapi_grpc_bridge import grpc_route, add_grpc_support
from pydantic import BaseModel

app = FastAPI()

class HelloResponse(BaseModel):
    message: str

@app.get("/hello")
@grpc_route("/hello")
async def say_hello(name: str) -> HelloResponse:
    return HelloResponse(message=f"Hello, {name}!")

# Add gRPC support - this will auto-start the gRPC server when FastAPI starts
add_grpc_support(app)

if __name__ == "__main__":
    import uvicorn
    # Both HTTP (port 8000) and gRPC (port 50051) will start automatically
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2. Manual gRPC Server Control

```python
from fastapi import FastAPI
from fastapi_grpc_bridge import grpc_route, add_grpc_support, start_grpc_server_standalone
from pydantic import BaseModel

app = FastAPI()

class HelloResponse(BaseModel):
    message: str

@app.get("/hello")
@grpc_route("/hello")
async def say_hello(name: str) -> HelloResponse:
    return HelloResponse(message=f"Hello, {name}!")

# Disable auto-start
add_grpc_support(app, auto_start_grpc=False)

# Start gRPC server manually in a separate script
if __name__ == "__main__":
    start_grpc_server_standalone()  # Or use this for standalone gRPC server
```

### 3. Start Both Services

**Option A: Auto-Start (Single Command)**
```bash
python app.py
# This starts both FastAPI (HTTP) on port 8000 and gRPC on port 50051
```

**Option B: Manual Start (Separate Commands)**
```bash
# Terminal 1: Start FastAPI
uvicorn app:app --host 0.0.0.0 --port 8000

# Terminal 2: Start gRPC server
python -c "from app import app; from fastapi_grpc_bridge import start_grpc_server_standalone; start_grpc_server_standalone()"
```

## Working with FastAPI Routers

```python
from fastapi import FastAPI, APIRouter
from fastapi_grpc_bridge import grpc_route, add_grpc_support
from pydantic import BaseModel

app = FastAPI()
api_router = APIRouter(prefix="/api")

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

@api_router.get("/user")
@grpc_route("/user")
async def get_user(user_id: int) -> UserResponse:
    return UserResponse(
        id=user_id,
        name=f"User {user_id}",
        email=f"user{user_id}@example.com"
    )

app.include_router(api_router)
add_grpc_support(app)  # Auto-starts gRPC server

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Type Support

The package automatically maps Python types to Protocol Buffer types:

| Python Type | Protocol Buffer Type |
|-------------|---------------------|
| `str` | `string` |
| `int` | `int32` |
| `float` | `float` |
| `bool` | `bool` |
| `bytes` | `bytes` |
| `Optional[T]` | `T` (optional) |

## API Reference

### `@grpc_route(path: str, response_model: Optional[Type[BaseModel]] = None)`

Decorator to add gRPC support to FastAPI routes.

**Parameters:**
- `path`: Route path (used for naming the gRPC service)
- `response_model`: Pydantic model for the response (optional if return annotation is provided)

### `add_grpc_support(app_or_router, auto_start_grpc=True)`

Add gRPC support to a FastAPI app or router.

**Parameters:**
- `app_or_router`: FastAPI app or APIRouter instance
- `auto_start_grpc`: Whether to automatically start gRPC server when FastAPI starts (default: True)

### `start_grpc_server_standalone()`

Start the gRPC server in standalone mode (for manual control).

## Examples

See the `examples/` directory for complete working examples:

- `examples/app.py`: Complete example with auto-start functionality
- `examples/start_grpc_server.py`: Standalone gRPC server launcher
- `examples/test_auto_start.py`: Test script to verify both services

## Testing Your Services

### Test HTTP Service
```bash
curl "http://localhost:8000/hello?name=World"
curl "http://localhost:8000/api/user?user_id=123"
curl "http://localhost:8000/health"  # Shows gRPC routes status
```

### Test gRPC Service
```python
import grpc
import sys
sys.path.append('generated_protos')

import say_hello_pb2
import say_hello_pb2_grpc

def test_grpc_service():
    channel = grpc.insecure_channel('localhost:50051')
    stub = say_hello_pb2_grpc.Say_helloServiceStub(channel)
    
    request = say_hello_pb2.say_helloRequest(name="World")
    response = stub.Call(request)
    
    print(f"Response: {response.message}")
    channel.close()

if __name__ == "__main__":
    test_grpc_service()
```

### Automated Testing
```bash
# Start the app
python examples/app.py &

# Run tests
python examples/test_auto_start.py
```

## Generated Files

The package automatically generates:

- `.proto` files in the `generated_protos/` directory
- Python gRPC client and server stubs (`*_pb2.py` and `*_pb2_grpc.py`)

## Configuration

### Ports
- **HTTP**: 8000 (configurable via uvicorn)
- **gRPC**: 50051 (fixed, can be modified in `grpc_server.py`)

### Auto-Start Behavior
- **Default**: gRPC server auto-starts when FastAPI starts
- **Disable**: Set `auto_start_grpc=False` in `add_grpc_support()`
- **Manual**: Use `start_grpc_server_standalone()` for manual control

## Requirements

- Python 3.7+
- FastAPI
- Pydantic
- grpcio
- grpcio-tools
- requests (for testing)

## License

MIT License 