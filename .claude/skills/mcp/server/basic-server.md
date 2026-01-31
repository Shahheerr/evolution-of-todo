# Basic MCP Server

This document covers creating a basic MCP server using the Python SDK.

## Minimal Server

```python
from mcp.server.fastmcp import FastMCP

# Create server instance
mcp = FastMCP("my-server")

# Run the server
if __name__ == "__main__":
    mcp.run()
```

## Server with Configuration

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="my-server",
    version="1.0.0",
    description="Description of what this server does"
)
```

## Running the Server

### stdio Transport (Default)

```bash
python server.py
```

### SSE Transport

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

if __name__ == "__main__":
    mcp.run(transport="sse")
```

### Streamable HTTP Transport

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8080
    )
```

## Server Lifecycle

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.on_startup
async def on_startup():
    """Called when server starts."""
    print("Server starting...")
    # Initialize resources, database connections, etc.

@mcp.on_shutdown
async def on_shutdown():
    """Called when server stops."""
    print("Server stopping...")
    # Cleanup resources

if __name__ == "__main__":
    mcp.run()
```

## Server with Context

```python
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("my-server")

@mcp.tool()
async def my_tool(ctx: Context, param: str) -> str:
    """Tool with context access."""
    # Access request context
    request_id = ctx.request_id
    
    # Log messages back to client
    await ctx.info(f"Processing: {param}")
    await ctx.debug("Debug information")
    await ctx.warning("Warning message")
    await ctx.error("Error message")
    
    # Report progress
    await ctx.report_progress(50, 100)  # 50% complete
    
    return f"Result for {param}"
```

## Error Handling

```python
from mcp.server.fastmcp import FastMCP
from mcp.types import McpError, ErrorCode

mcp = FastMCP("my-server")

@mcp.tool()
async def my_tool(param: str) -> str:
    if not param:
        raise McpError(
            ErrorCode.InvalidParams,
            "Parameter 'param' is required"
        )
    
    try:
        result = await do_something(param)
        return result
    except SomeException as e:
        raise McpError(
            ErrorCode.InternalError,
            f"Operation failed: {str(e)}"
        )
```

## Complete Example

```python
"""
Complete MCP Server Example
"""

import asyncio
from mcp.server.fastmcp import FastMCP, Context

# Create server
mcp = FastMCP(
    name="example-server",
    version="1.0.0",
    description="Example MCP server with tools and resources"
)

# In-memory storage
data_store = {}

@mcp.on_startup
async def startup():
    print("Example server started")

@mcp.on_shutdown
async def shutdown():
    print("Example server stopped")

@mcp.tool()
async def store_value(key: str, value: str) -> str:
    """Store a value in the data store."""
    data_store[key] = value
    return f"Stored '{key}' = '{value}'"

@mcp.tool()
async def get_value(key: str) -> str:
    """Retrieve a value from the data store."""
    if key not in data_store:
        return f"Key '{key}' not found"
    return f"{key} = {data_store[key]}"

@mcp.tool()
async def list_keys() -> str:
    """List all keys in the data store."""
    if not data_store:
        return "Data store is empty"
    return "Keys: " + ", ".join(data_store.keys())

if __name__ == "__main__":
    mcp.run()
```
