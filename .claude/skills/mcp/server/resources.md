# MCP Resources

Resources are read-only data sources that AI assistants can access.

## Defining Resources

### Static Resource

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.resource("config://app/settings")
def get_settings() -> str:
    """Returns application settings."""
    return """
    {
        "theme": "dark",
        "language": "en",
        "version": "1.0.0"
    }
    """
```

### Dynamic Resource

```python
@mcp.resource("file://{path}")
def read_file(path: str) -> str:
    """Read content of a file."""
    with open(path, "r") as f:
        return f.read()
```

### Async Resource

```python
@mcp.resource("db://users/{user_id}")
async def get_user(user_id: str) -> str:
    """Fetch user from database."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM users WHERE id = $1",
            user_id
        )
        if not row:
            return f"User {user_id} not found"
        return str(dict(row))
```

## Resource URIs

### URI Templates

```python
# Static URI
@mcp.resource("config://settings")

# Single parameter
@mcp.resource("user://{id}")

# Multiple parameters
@mcp.resource("file://{directory}/{filename}")

# Complex paths
@mcp.resource("db://{database}/tables/{table}/rows/{row_id}")
```

### URI Examples

| Pattern | Example URI | Parameters |
|---------|-------------|------------|
| `file://{path}` | `file://docs/readme.txt` | `path="docs/readme.txt"` |
| `user://{id}` | `user://123` | `id="123"` |
| `db://{db}/{table}` | `db://main/users` | `db="main"`, `table="users"` |

## Return Types

### String Content

```python
@mcp.resource("config://app")
def get_config() -> str:
    return "key=value\nother=data"
```

### JSON Content

```python
import json

@mcp.resource("data://stats")
def get_stats() -> str:
    data = {
        "users": 100,
        "active": 42,
        "revenue": 5000.00
    }
    return json.dumps(data, indent=2)
```

### Binary Content

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.resource("image://{name}")
def get_image(name: str) -> bytes:
    """Return image as bytes."""
    with open(f"images/{name}", "rb") as f:
        return f.read()
```

## Resource Metadata

```python
@mcp.resource(
    "docs://{doc_id}",
    name="Documentation",
    description="Access project documentation",
    mime_type="text/markdown"
)
def get_doc(doc_id: str) -> str:
    return read_doc(doc_id)
```

## Listing Resources

The server automatically lists available resources. For dynamic resources, you can provide a list function:

```python
@mcp.resource("file://{path}")
def read_file(path: str) -> str:
    with open(path) as f:
        return f.read()

@read_file.list()
def list_files() -> list[str]:
    """List available files."""
    import os
    return [f"file://{f}" for f in os.listdir("data/")]
```

## Error Handling

```python
from mcp.types import McpError, ErrorCode

@mcp.resource("file://{path}")
def read_file(path: str) -> str:
    """Read a file with error handling."""
    
    # Validate path
    if ".." in path:
        raise McpError(
            ErrorCode.InvalidRequest,
            "Path traversal not allowed"
        )
    
    try:
        with open(f"data/{path}") as f:
            return f.read()
    except FileNotFoundError:
        raise McpError(
            ErrorCode.InvalidRequest,
            f"File not found: {path}"
        )
    except PermissionError:
        raise McpError(
            ErrorCode.InvalidRequest,
            f"Permission denied: {path}"
        )
```

## Complete Example

```python
from mcp.server.fastmcp import FastMCP
from mcp.types import McpError, ErrorCode
import json
import os

mcp = FastMCP("file-server")

# Base directory for file access
BASE_DIR = "/data"

@mcp.resource("file://list")
def list_files() -> str:
    """List all available files."""
    files = []
    for root, dirs, filenames in os.walk(BASE_DIR):
        for f in filenames:
            path = os.path.relpath(os.path.join(root, f), BASE_DIR)
            files.append(path)
    return json.dumps(files, indent=2)

@mcp.resource("file://{path}")
def read_file(path: str) -> str:
    """Read content of a specific file."""
    
    # Security: prevent path traversal
    if ".." in path:
        raise McpError(ErrorCode.InvalidRequest, "Invalid path")
    
    full_path = os.path.join(BASE_DIR, path)
    
    # Security: ensure within base directory
    if not os.path.abspath(full_path).startswith(os.path.abspath(BASE_DIR)):
        raise McpError(ErrorCode.InvalidRequest, "Access denied")
    
    if not os.path.exists(full_path):
        raise McpError(ErrorCode.InvalidRequest, f"Not found: {path}")
    
    if os.path.isdir(full_path):
        # List directory contents
        contents = os.listdir(full_path)
        return json.dumps(contents, indent=2)
    
    # Read file
    try:
        with open(full_path, "r") as f:
            return f.read()
    except UnicodeDecodeError:
        raise McpError(
            ErrorCode.InvalidRequest,
            "Cannot read binary file as text"
        )

@mcp.resource("file://{path}/info")
def file_info(path: str) -> str:
    """Get metadata about a file."""
    full_path = os.path.join(BASE_DIR, path)
    
    if not os.path.exists(full_path):
        raise McpError(ErrorCode.InvalidRequest, f"Not found: {path}")
    
    stat = os.stat(full_path)
    info = {
        "path": path,
        "size": stat.st_size,
        "modified": stat.st_mtime,
        "is_directory": os.path.isdir(full_path)
    }
    return json.dumps(info, indent=2)

if __name__ == "__main__":
    mcp.run()
```
