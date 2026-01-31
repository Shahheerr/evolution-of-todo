# MCP Transports

Transports define how the MCP server communicates with clients.

## Available Transports

| Transport | Use Case | Protocol |
|-----------|----------|----------|
| `stdio` | Local processes, CLI tools | stdin/stdout |
| `sse` | Web applications | HTTP + Server-Sent Events |
| `streamable-http` | HTTP APIs | HTTP with streaming |

## stdio Transport

Default transport for local MCP servers.

### Server

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
async def hello() -> str:
    return "Hello!"

if __name__ == "__main__":
    mcp.run()  # Defaults to stdio
```

### Running

```bash
python server.py
```

### Client Configuration (Claude Desktop)

```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["/path/to/server.py"]
    }
  }
}
```

## SSE Transport

Server-Sent Events over HTTP.

### Server

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
async def hello() -> str:
    return "Hello!"

if __name__ == "__main__":
    mcp.run(transport="sse")
```

### Configuration Options

```python
mcp.run(
    transport="sse",
    host="0.0.0.0",      # Bind address
    port=8080,            # Port number
    sse_path="/sse",      # SSE endpoint path
    message_path="/message"  # Message endpoint path
)
```

### Endpoints Created

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/sse` | GET | SSE connection endpoint |
| `/message` | POST | Send messages to server |

## Streamable HTTP Transport

Full HTTP-based transport with bidirectional streaming.

### Server

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
async def hello() -> str:
    return "Hello!"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

### Configuration Options

```python
mcp.run(
    transport="streamable-http",
    host="127.0.0.1",
    port=8080,
    path="/mcp"           # MCP endpoint path
)
```

### Endpoint Created

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/mcp` | POST | All MCP communication |

## Low-Level Transport API

For custom transport implementations:

### Server Transports

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route

# Create base server
server = Server("my-server")

# stdio
async def run_stdio():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

# SSE with Starlette
sse_transport = SseServerTransport("/message")

async def handle_sse(request):
    async with sse_transport.connect_sse(
        request.scope,
        request.receive,
        request._send
    ) as streams:
        await server.run(
            streams[0],
            streams[1],
            server.create_initialization_options()
        )

app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/message", endpoint=sse_transport.handle_post_message, methods=["POST"]),
    ]
)
```

### Client Transports

```python
from mcp import ClientSession
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

# stdio client
async def connect_stdio():
    async with stdio_client(
        command="python",
        args=["server.py"]
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # Use session...

# SSE client
async def connect_sse():
    async with sse_client(
        url="http://localhost:8080/sse"
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # Use session...
```

## Transport Security

### HTTPS for SSE/HTTP

```python
import ssl

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain("cert.pem", "key.pem")

# Use with uvicorn or similar
# uvicorn server:app --ssl-keyfile key.pem --ssl-certfile cert.pem
```

### Authentication

```python
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware

# Add authentication middleware to your ASGI app
```

## Complete HTTP Server Example

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("http-server")

@mcp.tool()
async def process_data(data: str) -> str:
    """Process input data."""
    return f"Processed: {data}"

@mcp.resource("status://health")
def health_check() -> str:
    """Server health status."""
    return '{"status": "healthy"}'

if __name__ == "__main__":
    print("Starting MCP server on http://127.0.0.1:8080/mcp")
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8080,
        path="/mcp"
    )
```

## Transport Comparison

| Feature | stdio | SSE | Streamable HTTP |
|---------|-------|-----|-----------------|
| Latency | Lowest | Low | Low |
| Firewall friendly | N/A | Yes | Yes |
| Browser compatible | No | Yes | No |
| Bidirectional | Yes | Limited | Yes |
| Use case | CLI, local | Web apps | APIs |
