# Running Agents

The Runner class executes agents and handles the agent loop.

## Basic Running

### Synchronous

```python
from agents import Agent, Runner

agent = Agent(name="Test", instructions="Be helpful.")

result = Runner.run_sync(agent, "Hello")
print(result.final_output)
```

### Asynchronous

```python
import asyncio
from agents import Agent, Runner

agent = Agent(name="Test", instructions="Be helpful.")

async def main():
    result = await Runner.run(agent, "Hello")
    print(result.final_output)

asyncio.run(main())
```

## Runner Options

```python
result = Runner.run_sync(
    agent,
    "User message",
    
    # Context data
    context={"user_id": "123"},
    
    # Maximum turns before stopping
    max_turns=10,
    
    # Previous run result for conversation continuity
    # context=previous_result,
)
```

## RunResult Object

```python
from agents import Agent, Runner

agent = Agent(name="Test", instructions="...")
result = Runner.run_sync(agent, "Hello")

# Final text output
output: str = result.final_output

# All items produced during run
items = result.new_items

# The agent that produced the final output
last_agent = result.last_agent

# Check if handoff occurred
if result.last_agent.name != "Test":
    print(f"Handed off to: {result.last_agent.name}")

# Raw API responses
raw_responses = result.raw_responses

# Get typed output (if output_type was set)
from pydantic import BaseModel
class MyOutput(BaseModel):
    answer: str
    
typed_result = result.final_output_as(MyOutput)
```

## Conversation Mode

Continue multi-turn conversations:

```python
from agents import Agent, Runner

agent = Agent(
    name="Chat",
    instructions="You are a conversational assistant. Remember context."
)

# First turn
result1 = Runner.run_sync(agent, "My name is Bob")

# Continue conversation
result2 = Runner.run_sync(agent, "What's my name?", context=result1)

print(result2.final_output)  # Should remember "Bob"

# Keep continuing
result3 = Runner.run_sync(agent, "Tell me a joke", context=result2)
```

## Message Input Formats

### String

```python
result = Runner.run_sync(agent, "Simple string message")
```

### Message Objects

```python
from agents.items import UserMessage, AssistantMessage

# Single message
result = Runner.run_sync(
    agent,
    UserMessage(content="User message")
)

# Message history
messages = [
    UserMessage(content="Hi, I'm Alice"),
    AssistantMessage(content="Hello Alice!"),
    UserMessage(content="What's my name?")
]

result = Runner.run_sync(agent, messages)
```

## Max Turns

Limit execution to prevent infinite loops:

```python
from agents import Agent, Runner
from agents.exceptions import MaxTurnsExceeded

agent = Agent(
    name="Worker",
    instructions="Keep working until done.",
    tools=[some_tool]
)

try:
    result = Runner.run_sync(
        agent,
        "Process all items",
        max_turns=5  # Limit to 5 turns
    )
except MaxTurnsExceeded:
    print("Agent exceeded max turns")
```

## Run Items

Inspect what happened during a run:

```python
result = Runner.run_sync(agent, "Do something")

for item in result.new_items:
    item_type = type(item).__name__
    
    if item_type == "TextOutput":
        print(f"Text: {item.text}")
    
    elif item_type == "ToolCall":
        print(f"Called tool: {item.name}")
        print(f"Arguments: {item.arguments}")
    
    elif item_type == "ToolOutput":
        print(f"Tool returned: {item.output}")
    
    elif item_type == "Handoff":
        print(f"Handed off to: {item.target_agent}")
```

## Error Handling

```python
from agents import Agent, Runner
from agents.exceptions import (
    AgentError,
    MaxTurnsExceeded,
    ToolError,
    GuardrailError
)

agent = Agent(name="Test", instructions="...")

try:
    result = Runner.run_sync(agent, "Query", max_turns=10)
    print(result.final_output)

except MaxTurnsExceeded:
    print("Agent took too many turns")

except ToolError as e:
    print(f"Tool failed: {e}")

except GuardrailError as e:
    print(f"Guardrail blocked: {e}")

except AgentError as e:
    print(f"Agent error: {e}")
```

## Complete Example

```python
"""
Interactive chat with multi-turn support
"""

import asyncio
from agents import Agent, Runner, function_tool

@function_tool
def get_time() -> str:
    """Get current time."""
    from datetime import datetime
    return datetime.now().strftime("%I:%M %p")

@function_tool
def calculate(expression: str) -> str:
    """Calculate a math expression."""
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except:
        return "Invalid expression"

agent = Agent(
    name="Assistant",
    instructions="""You are a helpful assistant.
You can tell the time and do calculations.
Remember the conversation context.""",
    tools=[get_time, calculate]
)

async def chat():
    print("Chat with Assistant (type 'quit' to exit)")
    print("-" * 40)
    
    context = None
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == "quit":
            break
        
        if not user_input:
            continue
        
        try:
            result = await Runner.run(
                agent,
                user_input,
                context=context,
                max_turns=10
            )
            
            print(f"\nAssistant: {result.final_output}")
            
            # Keep context for next turn
            context = result
            
        except Exception as e:
            print(f"\nError: {e}")
            # Keep previous context on error

if __name__ == "__main__":
    asyncio.run(chat())
```
