# MCP Types Reference

Complete reference for MCP type definitions.

## Core Types

### McpError

```python
from mcp.types import McpError, ErrorCode

# Raise an MCP error
raise McpError(
    ErrorCode.InvalidParams,
    "Parameter 'name' is required"
)
```

### ErrorCode Enum

```python
from mcp.types import ErrorCode

ErrorCode.ParseError        # -32700: Invalid JSON
ErrorCode.InvalidRequest    # -32600: Invalid request
ErrorCode.MethodNotFound    # -32601: Method not found
ErrorCode.InvalidParams     # -32602: Invalid parameters
ErrorCode.InternalError     # -32603: Internal error
```

## Message Types

### PromptMessage

```python
from mcp.types import PromptMessage, TextContent, ImageContent

# Text message
text_message = PromptMessage(
    role="user",  # or "assistant"
    content=TextContent(
        type="text",
        text="Message content"
    )
)

# Image message
image_message = PromptMessage(
    role="assistant",
    content=ImageContent(
        type="image",
        data="base64-encoded-data",
        mimeType="image/png"
    )
)
```

### TextContent

```python
from mcp.types import TextContent

content = TextContent(
    type="text",
    text="The text content"
)
```

### ImageContent

```python
from mcp.types import ImageContent

content = ImageContent(
    type="image",
    data="base64-encoded-image-data",
    mimeType="image/png"  # or image/jpeg, image/gif, etc.
)
```

### EmbeddedResource

```python
from mcp.types import EmbeddedResource, TextResourceContents

resource = EmbeddedResource(
    type="resource",
    resource=TextResourceContents(
        uri="file://example.txt",
        mimeType="text/plain",
        text="File contents"
    )
)
```

## Tool Types

### Tool

```python
from mcp.types import Tool

# Tool definition (returned by list_tools)
tool = Tool(
    name="search",
    description="Search the database",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        },
        "required": ["query"]
    }
)
```

### CallToolResult

```python
from mcp.types import CallToolResult, TextContent

# Tool result (returned by call_tool)
result = CallToolResult(
    content=[
        TextContent(type="text", text="Result text")
    ],
    isError=False
)
```

## Resource Types

### Resource

```python
from mcp.types import Resource

# Resource definition (returned by list_resources)
resource = Resource(
    uri="config://settings",
    name="Settings",
    description="Application settings",
    mimeType="application/json"
)
```

### ResourceContents

```python
from mcp.types import TextResourceContents, BlobResourceContents

# Text resource
text_resource = TextResourceContents(
    uri="file://readme.txt",
    mimeType="text/plain",
    text="File contents here"
)

# Binary resource
blob_resource = BlobResourceContents(
    uri="image://logo.png",
    mimeType="image/png",
    blob="base64-encoded-data"
)
```

## Prompt Types

### Prompt

```python
from mcp.types import Prompt, PromptArgument

# Prompt definition (returned by list_prompts)
prompt = Prompt(
    name="code_review",
    description="Code review prompt",
    arguments=[
        PromptArgument(
            name="code",
            description="Code to review",
            required=True
        ),
        PromptArgument(
            name="language",
            description="Programming language",
            required=False
        )
    ]
)
```

### GetPromptResult

```python
from mcp.types import GetPromptResult, PromptMessage, TextContent

# Prompt result (returned by get_prompt)
result = GetPromptResult(
    description="Review this code",
    messages=[
        PromptMessage(
            role="user",
            content=TextContent(type="text", text="Please review...")
        )
    ]
)
```

## Server Types

### InitializationOptions

```python
from mcp.types import InitializationOptions

options = InitializationOptions(
    server_name="my-server",
    server_version="1.0.0",
    capabilities={
        "tools": {},
        "resources": {},
        "prompts": {}
    }
)
```

### ServerCapabilities

```python
from mcp.types import ServerCapabilities

capabilities = ServerCapabilities(
    tools={"listChanged": True},
    resources={"subscribe": True, "listChanged": True},
    prompts={"listChanged": True}
)
```

## Client Types

### ClientCapabilities

```python
from mcp.types import ClientCapabilities

capabilities = ClientCapabilities(
    roots={"listChanged": True},
    sampling={}
)
```

## Request/Response Types

### ListToolsResult

```python
from mcp.types import ListToolsResult

result = ListToolsResult(
    tools=[...]
)
```

### ListResourcesResult

```python
from mcp.types import ListResourcesResult

result = ListResourcesResult(
    resources=[...]
)
```

### ListPromptsResult

```python
from mcp.types import ListPromptsResult

result = ListPromptsResult(
    prompts=[...]
)
```

## Type Checking

```python
from mcp.types import TextContent, ImageContent

def process_content(content):
    if isinstance(content, TextContent):
        return content.text
    elif isinstance(content, ImageContent):
        return f"Image: {content.mimeType}"
    else:
        return "Unknown content type"
```

## JSON Schema Types

For tool input schemas:

```python
# String
{"type": "string", "description": "A text value"}

# Integer
{"type": "integer", "description": "A whole number"}

# Number (float)
{"type": "number", "description": "A decimal number"}

# Boolean
{"type": "boolean", "description": "True or false"}

# Array
{
    "type": "array",
    "items": {"type": "string"},
    "description": "List of strings"
}

# Object
{
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}
    },
    "required": ["name"]
}

# Enum
{
    "type": "string",
    "enum": ["high", "medium", "low"],
    "description": "Priority level"
}
```
