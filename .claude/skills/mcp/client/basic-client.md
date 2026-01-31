# MCP Client

This document covers creating MCP clients to connect to MCP servers.

## Basic Client

```python
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async def run_client():
    # Connect to stdio server
    async with stdio_client(
        command="python",
        args=["server.py"]
    ) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")
            
            # Call a tool
            result = await session.call_tool("hello", {"name": "World"})
            print(f"Result: {result}")
```

## Connecting to Different Transports

### stdio

```python
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async with stdio_client(
    command="python",
    args=["server.py"],
    env={"KEY": "value"}  # Optional environment
) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
```

### SSE

```python
from mcp import ClientSession
from mcp.client.sse import sse_client

async with sse_client(
    url="http://localhost:8080/sse"
) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
```

### Streamable HTTP

```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async with streamablehttp_client(
    url="http://localhost:8080/mcp"
) as (read, write, _):
    async with ClientSession(read, write) as session:
        await session.initialize()
```

## Client Operations

### List Tools

```python
tools_response = await session.list_tools()

for tool in tools_response.tools:
    print(f"Tool: {tool.name}")
    print(f"  Description: {tool.description}")
    print(f"  Parameters: {tool.inputSchema}")
```

### Call Tool

```python
# Call with arguments
result = await session.call_tool(
    name="search",
    arguments={"query": "hello", "limit": 10}
)

# Access result content
for content in result.content:
    if content.type == "text":
        print(content.text)
```

### List Resources

```python
resources_response = await session.list_resources()

for resource in resources_response.resources:
    print(f"Resource: {resource.uri}")
    print(f"  Name: {resource.name}")
    print(f"  Description: {resource.description}")
```

### Read Resource

```python
resource_content = await session.read_resource("config://settings")

for content in resource_content.contents:
    if content.type == "text":
        print(content.text)
```

### List Prompts

```python
prompts_response = await session.list_prompts()

for prompt in prompts_response.prompts:
    print(f"Prompt: {prompt.name}")
    print(f"  Description: {prompt.description}")
```

### Get Prompt

```python
prompt = await session.get_prompt(
    name="code_review",
    arguments={"code": "def hello(): pass"}
)

for message in prompt.messages:
    print(f"{message.role}: {message.content}")
```

## Error Handling

```python
from mcp.types import McpError

async def safe_call_tool(session, name, args):
    try:
        result = await session.call_tool(name, args)
        return result
    except McpError as e:
        print(f"MCP Error: {e.error.code} - {e.error.message}")
        return None
    except Exception as e:
        print(f"Connection error: {e}")
        return None
```

## Subscribing to Changes

```python
# Subscribe to resource changes
await session.subscribe_resource("data://live-feed")

# Handle notifications
session.on_resource_updated = lambda uri: print(f"Resource updated: {uri}")
```

## Complete Client Example

```python
"""
Complete MCP Client Example
"""

import asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async def main():
    print("Connecting to MCP server...")
    
    async with stdio_client(
        command="python",
        args=["server.py"]
    ) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            init_result = await session.initialize()
            print(f"Connected to: {init_result.serverInfo.name}")
            
            # List capabilities
            print("\n=== Tools ===")
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            print("\n=== Resources ===")
            resources = await session.list_resources()
            for resource in resources.resources:
                print(f"  - {resource.uri}: {resource.name}")
            
            print("\n=== Prompts ===")
            prompts = await session.list_prompts()
            for prompt in prompts.prompts:
                print(f"  - {prompt.name}: {prompt.description}")
            
            # Interactive loop
            print("\n=== Interactive Mode ===")
            while True:
                cmd = input("\nCommand (tool/resource/quit): ").strip()
                
                if cmd == "quit":
                    break
                
                elif cmd == "tool":
                    name = input("Tool name: ").strip()
                    args_str = input("Arguments (JSON): ").strip()
                    
                    import json
                    args = json.loads(args_str) if args_str else {}
                    
                    try:
                        result = await session.call_tool(name, args)
                        for content in result.content:
                            print(f"Result: {content.text}")
                    except Exception as e:
                        print(f"Error: {e}")
                
                elif cmd == "resource":
                    uri = input("Resource URI: ").strip()
                    
                    try:
                        result = await session.read_resource(uri)
                        for content in result.contents:
                            print(f"Content: {content.text}")
                    except Exception as e:
                        print(f"Error: {e}")
            
            print("Disconnected.")

if __name__ == "__main__":
    asyncio.run(main())
```

## Client with Reconnection

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

class MCPClient:
    def __init__(self, url: str):
        self.url = url
        self.session = None
        self._connected = False
    
    async def connect(self, max_retries: int = 3):
        for attempt in range(max_retries):
            try:
                return await self._connect()
            except Exception as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
        raise ConnectionError("Failed to connect after retries")
    
    async def _connect(self):
        async with streamablehttp_client(self.url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self.session = session
                self._connected = True
                return session
    
    async def call_tool(self, name: str, args: dict):
        if not self._connected:
            await self.connect()
        return await self.session.call_tool(name, args)
```
