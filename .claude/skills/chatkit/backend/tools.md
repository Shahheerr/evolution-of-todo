# ChatKit Tools

Define tools that the AI can call to perform actions.

## Defining Tools

```python
from chatkit import ChatKit, Tool

ck = ChatKit()

# Define a tool
get_weather = Tool(
    name="get_weather",
    description="Get the current weather for a location",
    parameters={
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name or location"
            },
            "units": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "Temperature units"
            }
        },
        "required": ["location"]
    }
)

# Register tools
ck.register_tools([get_weather])
```

## Tool Handlers

```python
from chatkit import ChatKit, Tool

ck = ChatKit()

# Define tool
search_tool = Tool(
    name="search",
    description="Search the database",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        },
        "required": ["query"]
    }
)

# Handle tool calls
@ck.tool_handler("search")
async def handle_search(arguments, context):
    """Execute the search tool."""
    query = arguments["query"]
    
    # Perform search
    results = await search_database(query)
    
    # Return result (will be sent back to AI)
    return f"Found {len(results)} results: {results}"

ck.register_tools([search_tool])
```

## Multiple Tools

```python
from chatkit import ChatKit, Tool

ck = ChatKit()

# Define tools
tools = [
    Tool(
        name="get_weather",
        description="Get weather for a location",
        parameters={
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"]
        }
    ),
    Tool(
        name="search_products",
        description="Search for products",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "category": {"type": "string"},
                "max_price": {"type": "number"}
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="create_order",
        description="Create a new order",
        parameters={
            "type": "object",
            "properties": {
                "product_id": {"type": "string"},
                "quantity": {"type": "integer"}
            },
            "required": ["product_id"]
        }
    )
]

# Register all tools
ck.register_tools(tools)

# Define handlers
@ck.tool_handler("get_weather")
async def handle_weather(args, ctx):
    location = args["location"]
    return f"Weather in {location}: Sunny, 72°F"

@ck.tool_handler("search_products")
async def handle_search(args, ctx):
    query = args["query"]
    return f"Products matching '{query}': [Product A, Product B]"

@ck.tool_handler("create_order")
async def handle_order(args, ctx):
    product_id = args["product_id"]
    quantity = args.get("quantity", 1)
    return f"Order created: {quantity}x {product_id}"
```

## Tool with Context

```python
@ck.tool_handler("get_user_data")
async def handle_get_user_data(arguments, context):
    """Tool that uses authentication context."""
    
    # Access authenticated user
    user_id = context.get("user_id")
    
    if not user_id:
        return "Error: Not authenticated"
    
    # Fetch user data
    user = await get_user(user_id)
    
    return f"User: {user.name}, Email: {user.email}"
```

## Async Tool Execution

```python
import asyncio

@ck.tool_handler("long_running_task")
async def handle_long_task(arguments, context):
    """Tool with async operations."""
    
    task_type = arguments["task_type"]
    
    # Perform async operation
    result = await asyncio.wait_for(
        process_task(task_type),
        timeout=30.0
    )
    
    return f"Task completed: {result}"
```

## Tool Error Handling

```python
from chatkit import ToolError

@ck.tool_handler("risky_operation")
async def handle_risky(arguments, context):
    """Tool with error handling."""
    
    param = arguments.get("param")
    
    # Validation
    if not param:
        raise ToolError("Parameter 'param' is required")
    
    try:
        result = await perform_operation(param)
        return result
    except NotFoundException:
        raise ToolError(f"Item '{param}' not found")
    except PermissionError:
        raise ToolError("You don't have permission for this action")
    except Exception as e:
        raise ToolError(f"Operation failed: {str(e)}")
```

## Handler with Tool Calls

```python
from chatkit import ChatKit, Tool
import openai

ck = ChatKit()
client = openai.AsyncOpenAI()

# Convert ChatKit tools to OpenAI format
def get_openai_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
        }
        for tool in ck.tools
    ]

@ck.handler()
async def handler(messages, context):
    """Handler that supports tool calling."""
    
    openai_messages = [
        {"role": "system", "content": "You are helpful."}
    ] + messages
    
    # First API call
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=openai_messages,
        tools=get_openai_tools(),
        stream=True
    )
    
    # Collect response and tool calls
    full_content = ""
    tool_calls = []
    
    async for chunk in response:
        delta = chunk.choices[0].delta
        
        if delta.content:
            full_content += delta.content
            yield delta.content
        
        if delta.tool_calls:
            for tc in delta.tool_calls:
                # Collect tool call data
                pass
    
    # If tool calls, execute them
    if tool_calls:
        for tool_call in tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            # Execute tool handler
            result = await ck.execute_tool(name, args, context)
            
            # Add to messages
            openai_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })
        
        # Continue conversation
        follow_up = await client.chat.completions.create(
            model="gpt-4o",
            messages=openai_messages,
            stream=True
        )
        
        async for chunk in follow_up:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
```

## Complete Example

```python
"""
ChatKit server with tools
"""

from chatkit import ChatKit, Tool, ToolError
import openai
import json

ck = ChatKit(path="/chatkit")
client = openai.AsyncOpenAI()

# =============================================================================
# Tools Definition
# =============================================================================

tools = [
    Tool(
        name="search_database",
        description="Search the database for records",
        parameters={
            "type": "object",
            "properties": {
                "table": {
                    "type": "string",
                    "enum": ["users", "products", "orders"]
                },
                "query": {"type": "string"},
                "limit": {"type": "integer"}
            },
            "required": ["table", "query"]
        }
    ),
    Tool(
        name="get_record",
        description="Get a specific record by ID",
        parameters={
            "type": "object",
            "properties": {
                "table": {"type": "string"},
                "id": {"type": "string"}
            },
            "required": ["table", "id"]
        }
    ),
    Tool(
        name="update_record",
        description="Update a record",
        parameters={
            "type": "object",
            "properties": {
                "table": {"type": "string"},
                "id": {"type": "string"},
                "updates": {"type": "object"}
            },
            "required": ["table", "id", "updates"]
        }
    )
]

ck.register_tools(tools)

# =============================================================================
# Tool Handlers
# =============================================================================

@ck.tool_handler("search_database")
async def handle_search(args, ctx):
    table = args["table"]
    query = args["query"]
    limit = args.get("limit", 10)
    
    results = await db.search(table, query, limit)
    return json.dumps(results)

@ck.tool_handler("get_record")
async def handle_get(args, ctx):
    record = await db.get(args["table"], args["id"])
    if not record:
        raise ToolError(f"Record not found: {args['id']}")
    return json.dumps(record)

@ck.tool_handler("update_record")
async def handle_update(args, ctx):
    user_id = ctx.get("user_id")
    if not user_id:
        raise ToolError("Authentication required")
    
    await db.update(args["table"], args["id"], args["updates"])
    return f"Updated {args['table']} record {args['id']}"

# =============================================================================
# Handler
# =============================================================================

SYSTEM = "You are a database assistant. Use tools to query and modify data."

@ck.handler()
async def handler(messages, context):
    # Implementation with tool calling
    # ... (as shown above)
    pass

if __name__ == "__main__":
    ck.run(port=8000)
```
