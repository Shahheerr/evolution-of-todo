# MCP Tools

Tools are functions that an AI assistant can call to perform actions.

## Defining Tools

### Basic Tool

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
async def greet(name: str) -> str:
    """Greet a person by name."""
    return f"Hello, {name}!"
```

### Tool with Description

```python
@mcp.tool(description="Search for items in the database")
async def search(query: str) -> str:
    """
    The docstring is used as description if not specified.
    """
    pass
```

### Tool with Multiple Parameters

```python
from typing import Optional

@mcp.tool()
async def create_item(
    name: str,
    description: str = "",
    quantity: int = 1,
    tags: Optional[list[str]] = None
) -> str:
    """
    Create a new item.
    
    Args:
        name: Item name (required)
        description: Optional description
        quantity: Number of items (default: 1)
        tags: Optional list of tags
    """
    return f"Created: {name}"
```

## Parameter Types

### Supported Types

```python
from typing import Optional, List, Dict, Any
from enum import Enum

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@mcp.tool()
async def example_types(
    # Basic types
    text: str,
    number: int,
    decimal: float,
    flag: bool,
    
    # Optional types
    optional_text: Optional[str] = None,
    
    # Collections
    items: List[str] = None,
    metadata: Dict[str, Any] = None,
    
    # Enums
    priority: Priority = Priority.MEDIUM
) -> str:
    """Example showing all supported parameter types."""
    pass
```

### Pydantic Models

```python
from pydantic import BaseModel, Field

class TaskInput(BaseModel):
    title: str = Field(..., description="Task title")
    description: str = Field("", description="Task description")
    priority: str = Field("medium", description="Priority level")

@mcp.tool()
async def create_task(task: TaskInput) -> str:
    """Create a task using structured input."""
    return f"Created: {task.title}"
```

## Return Types

### String Return

```python
@mcp.tool()
async def simple_tool() -> str:
    return "Simple string response"
```

### Structured Return

```python
from typing import TypedDict

class SearchResult(TypedDict):
    id: str
    title: str
    score: float

@mcp.tool()
async def search(query: str) -> list[SearchResult]:
    """Returns structured data."""
    return [
        {"id": "1", "title": "Result 1", "score": 0.9},
        {"id": "2", "title": "Result 2", "score": 0.8},
    ]
```

### Image Return

```python
from mcp.server.fastmcp import FastMCP, Image

mcp = FastMCP("my-server")

@mcp.tool()
async def generate_chart(data: list[int]) -> Image:
    """Generate a chart image."""
    # Generate image bytes
    image_bytes = create_chart(data)
    return Image(data=image_bytes, format="png")
```

## Context Access

```python
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("my-server")

@mcp.tool()
async def tool_with_context(ctx: Context, query: str) -> str:
    """Tool that uses context features."""
    
    # Progress reporting
    await ctx.report_progress(0, 100)
    
    # Logging
    await ctx.info("Starting operation...")
    await ctx.debug(f"Query: {query}")
    
    # Do work
    for i in range(10):
        await ctx.report_progress(i * 10, 100)
        # ... process ...
    
    await ctx.info("Operation complete")
    return "Done"
```

## Async vs Sync

### Async Tool (Recommended)

```python
@mcp.tool()
async def async_tool(param: str) -> str:
    result = await some_async_operation(param)
    return result
```

### Sync Tool

```python
@mcp.tool()
def sync_tool(param: str) -> str:
    # Synchronous operations only
    return f"Result: {param}"
```

## Error Handling in Tools

```python
from mcp.types import McpError, ErrorCode

@mcp.tool()
async def validated_tool(
    name: str,
    age: int
) -> str:
    """Tool with validation."""
    
    # Validation
    if not name:
        raise McpError(
            ErrorCode.InvalidParams,
            "Name is required"
        )
    
    if age < 0 or age > 150:
        raise McpError(
            ErrorCode.InvalidParams,
            f"Invalid age: {age}"
        )
    
    # Business logic error
    try:
        result = await process(name, age)
        return result
    except NotFoundException:
        raise McpError(
            ErrorCode.InvalidRequest,
            f"User {name} not found"
        )
    except Exception as e:
        raise McpError(
            ErrorCode.InternalError,
            f"Processing failed: {str(e)}"
        )
```

## Tool Naming

```python
# Tool name defaults to function name
@mcp.tool()
async def my_tool() -> str:  # Tool name: "my_tool"
    pass

# Override tool name
@mcp.tool(name="custom-name")
async def my_tool() -> str:  # Tool name: "custom-name"
    pass
```

## Complete Example

```python
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import McpError, ErrorCode
from typing import Optional
import asyncpg

mcp = FastMCP("database-tools")

pool: Optional[asyncpg.Pool] = None

@mcp.on_startup
async def startup():
    global pool
    pool = await asyncpg.create_pool("postgresql://...")

@mcp.on_shutdown
async def shutdown():
    global pool
    if pool:
        await pool.close()

@mcp.tool()
async def query_database(
    ctx: Context,
    table: str,
    limit: int = 10
) -> str:
    """
    Query a database table.
    
    Args:
        table: Table name to query
        limit: Maximum rows to return (default: 10)
    """
    if not pool:
        raise McpError(ErrorCode.InternalError, "Database not connected")
    
    # Validate table name (prevent SQL injection)
    allowed_tables = ["users", "products", "orders"]
    if table not in allowed_tables:
        raise McpError(
            ErrorCode.InvalidParams,
            f"Invalid table. Allowed: {allowed_tables}"
        )
    
    await ctx.info(f"Querying {table}...")
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(f"SELECT * FROM {table} LIMIT $1", limit)
    
    if not rows:
        return f"No data in {table}"
    
    # Format as string
    result = f"Results from {table} ({len(rows)} rows):\n"
    for row in rows:
        result += str(dict(row)) + "\n"
    
    return result
```
