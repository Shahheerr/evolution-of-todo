# Agent Tools

Tools are functions that agents can call to perform actions or retrieve information.

## Defining Tools

### Using @function_tool Decorator

```python
from agents import Agent, Runner, function_tool

@function_tool
def get_weather(city: str) -> str:
    """
    Get the current weather for a city.
    
    Args:
        city: The city name to get weather for
    """
    # Implementation
    return f"The weather in {city} is sunny, 72°F"

agent = Agent(
    name="WeatherBot",
    instructions="Help users with weather information.",
    tools=[get_weather]
)

result = Runner.run_sync(agent, "What's the weather in Paris?")
```

### Tool with Multiple Parameters

```python
from typing import Optional
from agents import function_tool

@function_tool
def search_products(
    query: str,
    category: Optional[str] = None,
    max_price: Optional[float] = None,
    limit: int = 10
) -> str:
    """
    Search for products in the catalog.
    
    Args:
        query: Search query text
        category: Optional category filter
        max_price: Optional maximum price filter
        limit: Maximum number of results (default: 10)
    """
    results = perform_search(query, category, max_price, limit)
    return format_results(results)
```

### Async Tools

```python
from agents import function_tool
import httpx

@function_tool
async def fetch_url(url: str) -> str:
    """
    Fetch content from a URL.
    
    Args:
        url: The URL to fetch
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text[:1000]
```

## Parameter Types

### Supported Types

```python
from typing import Optional, List, Literal
from enum import Enum

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@function_tool
def example_tool(
    # Basic types
    text: str,
    number: int,
    decimal: float,
    flag: bool,
    
    # Optional types
    optional_text: Optional[str] = None,
    
    # Lists
    tags: List[str] = None,
    
    # Literals (enum-like)
    status: Literal["active", "inactive"] = "active",
    
    # Enums
    priority: Priority = Priority.MEDIUM
) -> str:
    """Tool demonstrating parameter types."""
    pass
```

### Pydantic Models

```python
from pydantic import BaseModel, Field
from agents import function_tool

class TaskInput(BaseModel):
    title: str = Field(..., description="Task title")
    description: str = Field("", description="Detailed description")
    priority: str = Field("medium", description="Priority: high, medium, low")

@function_tool
def create_task(task: TaskInput) -> str:
    """
    Create a new task.
    
    Args:
        task: Task details
    """
    return f"Created task: {task.title}"
```

## Tool Context

Access the running context within tools:

```python
from agents import function_tool, RunContext

@function_tool
def tool_with_context(ctx: RunContext, query: str) -> str:
    """
    Tool that accesses run context.
    
    Args:
        query: Search query
    """
    # Access context data
    user_id = ctx.context.get("user_id")
    
    # Access the current agent
    agent_name = ctx.agent.name
    
    return f"User {user_id} searched: {query}"
```

## Error Handling in Tools

```python
from agents import function_tool
from agents.exceptions import ToolError

@function_tool
def risky_operation(param: str) -> str:
    """
    Perform an operation that might fail.
    
    Args:
        param: Input parameter
    """
    if not param:
        raise ToolError("Parameter cannot be empty")
    
    try:
        result = do_something(param)
        return result
    except SomeException as e:
        raise ToolError(f"Operation failed: {e}")
```

## Built-in Tools

### Computer Use (Beta)

```python
from agents.tools import ComputerTool

computer = ComputerTool()

agent = Agent(
    name="ComputerAgent",
    instructions="Help users with computer tasks.",
    tools=[computer]
)
```

### File Search

```python
from agents.tools import FileSearchTool

file_search = FileSearchTool(
    vector_store_ids=["vs_xxx"]
)

agent = Agent(
    name="SearchAgent",
    instructions="Search through documents.",
    tools=[file_search]
)
```

### Code Interpreter

```python
from agents.tools import CodeInterpreterTool

code_interpreter = CodeInterpreterTool()

agent = Agent(
    name="CodeAgent",
    instructions="Help with coding tasks.",
    tools=[code_interpreter]
)
```

## Tool Return Types

### String

```python
@function_tool
def simple_tool() -> str:
    return "Text response"
```

### Structured Data

```python
from typing import TypedDict
from agents import function_tool

class SearchResult(TypedDict):
    title: str
    url: str
    score: float

@function_tool
def search(query: str) -> list[SearchResult]:
    """Search and return structured results."""
    return [
        {"title": "Result 1", "url": "https://...", "score": 0.9}
    ]
```

## Complete Example

```python
"""
Agent with multiple tools
"""

from typing import Optional, List
from agents import Agent, Runner, function_tool
import json

# Define tools
@function_tool
def search_database(
    query: str,
    table: str = "products",
    limit: int = 5
) -> str:
    """
    Search the database.
    
    Args:
        query: Search query
        table: Table to search (products, users, orders)
        limit: Max results
    """
    # Simulated results
    results = [
        {"id": i, "name": f"Result {i}", "score": 0.9 - i*0.1}
        for i in range(limit)
    ]
    return json.dumps(results, indent=2)

@function_tool
def get_details(item_id: int, table: str = "products") -> str:
    """
    Get details of an item.
    
    Args:
        item_id: ID of the item
        table: Table name
    """
    return json.dumps({
        "id": item_id,
        "name": f"Item {item_id}",
        "description": f"Detailed description of item {item_id}",
        "price": 29.99,
        "in_stock": True
    }, indent=2)

@function_tool
def add_to_cart(item_id: int, quantity: int = 1) -> str:
    """
    Add item to shopping cart.
    
    Args:
        item_id: ID of item to add
        quantity: Number of items
    """
    return f"Added {quantity}x item {item_id} to cart"

# Create agent with tools
agent = Agent(
    name="ShopAssistant",
    instructions="""You are a shopping assistant.

Help users:
1. Search for products
2. Get product details
3. Add items to their cart

Be helpful and make recommendations based on their needs.""",
    tools=[search_database, get_details, add_to_cart]
)

# Run
result = Runner.run_sync(
    agent,
    "I'm looking for headphones under $50"
)
print(result.final_output)
```
