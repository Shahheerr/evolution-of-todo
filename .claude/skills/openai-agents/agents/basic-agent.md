# Basic Agent

This document covers creating and running basic agents with the OpenAI Agents SDK.

## Minimal Agent

```python
from agents import Agent, Runner

# Create an agent
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant."
)

# Run the agent
result = Runner.run_sync(agent, "Hello!")
print(result.final_output)
```

## Agent Configuration

```python
from agents import Agent

agent = Agent(
    name="MyAgent",                    # Agent name
    instructions="You are helpful.",   # System prompt
    model="gpt-4o",                    # Model to use
    model_settings={                   # Model settings
        "temperature": 0.7,
        "max_tokens": 1000
    }
)
```

## Running Agents

### Synchronous

```python
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="Be helpful.")

# Run synchronously
result = Runner.run_sync(agent, "What is 2+2?")
print(result.final_output)  # "4"
```

### Asynchronous

```python
import asyncio
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="Be helpful.")

async def main():
    result = await Runner.run(agent, "What is 2+2?")
    print(result.final_output)

asyncio.run(main())
```

## RunResult Object

```python
result = Runner.run_sync(agent, "Hello")

# Final output text
output = result.final_output

# All items produced
items = result.new_items

# Latest agent in the run (may differ if handoffs occurred)
last_agent = result.last_agent

# Raw response data
raw = result.raw_responses
```

## Multi-Turn Conversations

```python
from agents import Agent, Runner

agent = Agent(name="Chat", instructions="You are a conversational assistant.")

# First turn
result = Runner.run_sync(agent, "My name is Alice.")

# Continue with context
result = Runner.run_sync(
    agent,
    "What's my name?",
    context=result  # Pass previous result as context
)

print(result.final_output)  # "Your name is Alice."
```

## Message History

```python
from agents import Agent, Runner
from agents.items import UserMessage, AssistantMessage

agent = Agent(name="Chat", instructions="Be helpful.")

# Build message history
messages = [
    UserMessage(content="Hello, I'm Bob."),
    AssistantMessage(content="Hi Bob! How can I help?"),
    UserMessage(content="What's my name?")
]

result = Runner.run_sync(agent, messages)
print(result.final_output)  # "Your name is Bob."
```

## Agent with Output Type

```python
from pydantic import BaseModel
from agents import Agent, Runner

class Answer(BaseModel):
    answer: str
    confidence: float

agent = Agent(
    name="QA",
    instructions="Answer questions with confidence scores.",
    output_type=Answer
)

result = Runner.run_sync(agent, "What is the capital of France?")
answer: Answer = result.final_output_as(Answer)

print(f"Answer: {answer.answer}")
print(f"Confidence: {answer.confidence}")
```

## Error Handling

```python
from agents import Agent, Runner
from agents.exceptions import AgentError, MaxTurnsExceeded

agent = Agent(name="Test", instructions="Test agent")

try:
    result = Runner.run_sync(
        agent,
        "Do something",
        max_turns=5  # Limit execution turns
    )
except MaxTurnsExceeded:
    print("Agent exceeded maximum turns")
except AgentError as e:
    print(f"Agent error: {e}")
```

## Complete Example

```python
"""
Complete basic agent example
"""

import asyncio
from agents import Agent, Runner

# Create agent with detailed instructions
agent = Agent(
    name="WeatherAssistant",
    instructions="""You are a weather information assistant.

When users ask about weather, provide helpful information.
If they don't specify a location, ask for one.
Be concise but friendly.""",
    model="gpt-4o-mini"
)

async def chat():
    print("Weather Assistant (type 'quit' to exit)")
    print("-" * 40)
    
    context = None
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        # Run agent with conversation context
        result = await Runner.run(
            agent,
            user_input,
            context=context
        )
        
        print(f"\nAssistant: {result.final_output}")
        
        # Keep context for next turn
        context = result

if __name__ == "__main__":
    asyncio.run(chat())
```
