# MCP Decorators Reference

Complete reference for all MCP decorators in the Python SDK.

## @mcp.tool()

Registers a function as a callable tool.

### Signature

```python
@mcp.tool(
    name: str = None,           # Tool name (defaults to function name)
    description: str = None     # Tool description (defaults to docstring)
)
```

### Examples

```python
# Basic
@mcp.tool()
async def my_tool(param: str) -> str:
    """Tool description from docstring."""
    return result

# With explicit name
@mcp.tool(name="custom-name")
async def my_tool() -> str:
    pass

# With explicit description
@mcp.tool(description="Custom description")
async def my_tool() -> str:
    pass

# Sync function
@mcp.tool()
def sync_tool() -> str:
    return "sync result"
```

## @mcp.resource()

Registers a function as a readable resource.

### Signature

```python
@mcp.resource(
    uri: str,                    # Resource URI template
    name: str = None,            # Resource name
    description: str = None,     # Resource description
    mime_type: str = None        # MIME type of content
)
```

### URI Templates

```python
# Static URI
@mcp.resource("config://settings")

# Single parameter
@mcp.resource("user://{id}")

# Multiple parameters
@mcp.resource("file://{folder}/{name}")
```

### Examples

```python
# Static resource
@mcp.resource("config://app")
def get_config() -> str:
    return '{"key": "value"}'

# Dynamic resource
@mcp.resource("file://{path}")
def read_file(path: str) -> str:
    with open(path) as f:
        return f.read()

# With metadata
@mcp.resource(
    "docs://{doc_id}",
    name="Documentation",
    description="Project documentation",
    mime_type="text/markdown"
)
def get_doc(doc_id: str) -> str:
    return load_doc(doc_id)

# Async resource
@mcp.resource("db://users/{id}")
async def get_user(id: str) -> str:
    return await fetch_user(id)

# Binary resource
@mcp.resource("image://{name}")
def get_image(name: str) -> bytes:
    with open(f"images/{name}", "rb") as f:
        return f.read()
```

## @mcp.prompt()

Registers a function as a prompt template.

### Signature

```python
@mcp.prompt(
    name: str = None,           # Prompt name (defaults to function name)
    description: str = None     # Prompt description (defaults to docstring)
)
```

### Examples

```python
# Simple prompt returning string
@mcp.prompt()
def code_review() -> str:
    """Code review prompt."""
    return "Review this code for bugs and improvements."

# Prompt with parameters
@mcp.prompt()
def summarize(text: str, max_words: int = 100) -> str:
    return f"Summarize in {max_words} words:\n{text}"

# Returning message list
from mcp.types import PromptMessage, TextContent

@mcp.prompt()
def chat_context(context: str) -> list[PromptMessage]:
    return [
        PromptMessage(
            role="user",
            content=TextContent(type="text", text=context)
        )
    ]
```

## @mcp.on_startup

Registers a startup handler.

```python
@mcp.on_startup
async def startup():
    """Called when server starts."""
    global pool
    pool = await create_connection_pool()
```

## @mcp.on_shutdown

Registers a shutdown handler.

```python
@mcp.on_shutdown
async def shutdown():
    """Called when server stops."""
    global pool
    if pool:
        await pool.close()
```

## @resource.list()

Registers a list function for a dynamic resource.

```python
@mcp.resource("file://{path}")
def read_file(path: str) -> str:
    with open(path) as f:
        return f.read()

@read_file.list()
def list_files() -> list[str]:
    """Return available resource URIs."""
    import os
    return [f"file://{f}" for f in os.listdir("data/")]
```

## Parameter Annotations

### Type Hints

```python
from typing import Optional, List, Dict

@mcp.tool()
async def example(
    required_str: str,              # Required string
    optional_str: Optional[str] = None,  # Optional string
    with_default: str = "default",  # String with default
    number: int = 0,                # Integer
    decimal: float = 0.0,           # Float
    flag: bool = False,             # Boolean
    items: List[str] = None,        # List of strings
    data: Dict[str, str] = None     # Dictionary
) -> str:
    pass
```

### Pydantic Models

```python
from pydantic import BaseModel, Field

class TaskInput(BaseModel):
    title: str = Field(..., description="Task title")
    priority: str = Field("medium")

@mcp.tool()
async def create_task(task: TaskInput) -> str:
    return f"Created: {task.title}"
```

### Enums

```python
from enum import Enum

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@mcp.tool()
async def set_priority(priority: Priority) -> str:
    return f"Set to {priority.value}"
```

## Context Parameter

```python
from mcp.server.fastmcp import Context

@mcp.tool()
async def tool_with_context(ctx: Context, param: str) -> str:
    # Logging
    await ctx.info("Info message")
    await ctx.debug("Debug message")
    await ctx.warning("Warning message")
    await ctx.error("Error message")
    
    # Progress
    await ctx.report_progress(50, 100)
    
    # Request info
    request_id = ctx.request_id
    
    return "Done"
```

## Return Types

### String

```python
@mcp.tool()
async def returns_string() -> str:
    return "text result"
```

### Image

```python
from mcp.server.fastmcp import Image

@mcp.tool()
async def returns_image() -> Image:
    image_bytes = generate_image()
    return Image(data=image_bytes, format="png")
```

### Structured Data

```python
from typing import TypedDict

class Result(TypedDict):
    id: str
    value: int

@mcp.tool()
async def returns_structured() -> Result:
    return {"id": "123", "value": 42}
```
