# Streaming Responses

Stream agent output in real-time as it's generated.

## Basic Streaming

```python
from agents import Agent, Runner

agent = Agent(name="Writer", instructions="Write a short story.")

# Stream events
async for event in Runner.run_streamed(agent, "Write about a robot"):
    if event.type == "text_delta":
        print(event.delta, end="", flush=True)
    
    elif event.type == "text_done":
        print("\n[Complete]")
```

## Event Types

```python
async for event in Runner.run_streamed(agent, "Query"):
    
    # Text chunk
    if event.type == "text_delta":
        text_chunk = event.delta
    
    # Text complete
    elif event.type == "text_done":
        full_text = event.text
    
    # Tool call started
    elif event.type == "tool_call_start":
        tool_name = event.name
        tool_id = event.id
    
    # Tool call arguments (streaming)
    elif event.type == "tool_call_delta":
        args_chunk = event.delta
    
    # Tool call complete
    elif event.type == "tool_call_done":
        tool_name = event.name
        tool_args = event.arguments
    
    # Tool output
    elif event.type == "tool_output":
        output = event.output
    
    # Handoff
    elif event.type == "handoff":
        target = event.target_agent
    
    # Run complete
    elif event.type == "run_done":
        final_result = event.result
```

## Streaming with Context

```python
from agents import Agent, Runner

agent = Agent(name="Chat", instructions="Be conversational.")

context = None

async def stream_chat(message: str):
    global context
    
    full_response = ""
    
    async for event in Runner.run_streamed(
        agent,
        message,
        context=context
    ):
        if event.type == "text_delta":
            full_response += event.delta
            print(event.delta, end="", flush=True)
        
        elif event.type == "run_done":
            context = event.result
    
    print()  # Newline
    return full_response
```

## Streaming with Tools

```python
from agents import Agent, Runner, function_tool

@function_tool
async def search(query: str) -> str:
    """Search the database."""
    await asyncio.sleep(1)  # Simulate search
    return f"Results for: {query}"

agent = Agent(
    name="SearchBot",
    instructions="Help users search.",
    tools=[search]
)

async def main():
    async for event in Runner.run_streamed(
        agent,
        "Search for Python tutorials"
    ):
        if event.type == "tool_call_start":
            print(f"[Calling {event.name}...]")
        
        elif event.type == "tool_output":
            print(f"[Tool returned: {event.output}]")
        
        elif event.type == "text_delta":
            print(event.delta, end="", flush=True)
    
    print()
```

## HTTP Streaming

Integrate with web frameworks:

### FastAPI

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from agents import Agent, Runner

app = FastAPI()

agent = Agent(name="API", instructions="Be helpful.")

@app.get("/chat")
async def chat(message: str):
    async def generate():
        async for event in Runner.run_streamed(agent, message):
            if event.type == "text_delta":
                yield event.delta
    
    return StreamingResponse(generate(), media_type="text/plain")
```

### Server-Sent Events

```python
from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse
from agents import Agent, Runner
import json

app = FastAPI()

agent = Agent(name="API", instructions="Be helpful.")

@app.get("/stream")
async def stream(message: str):
    async def generate():
        async for event in Runner.run_streamed(agent, message):
            if event.type == "text_delta":
                yield {
                    "event": "message",
                    "data": json.dumps({"delta": event.delta})
                }
            
            elif event.type == "run_done":
                yield {
                    "event": "done",
                    "data": json.dumps({"complete": True})
                }
    
    return EventSourceResponse(generate())
```

## Collecting Streamed Output

```python
from agents import Agent, Runner

agent = Agent(name="Writer", instructions="Write content.")

async def collect_stream(agent, message):
    full_text = ""
    tool_calls = []
    
    async for event in Runner.run_streamed(agent, message):
        if event.type == "text_delta":
            full_text += event.delta
        
        elif event.type == "tool_call_done":
            tool_calls.append({
                "name": event.name,
                "arguments": event.arguments
            })
        
        elif event.type == "run_done":
            return {
                "text": full_text,
                "tool_calls": tool_calls,
                "result": event.result
            }
```

## Complete Example

```python
"""
Streaming chat interface
"""

import asyncio
from agents import Agent, Runner, function_tool

@function_tool
def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"Sunny, 72°F in {city}"

@function_tool
def search_web(query: str) -> str:
    """Search the web."""
    return f"Top result: Wikipedia article about {query}"

agent = Agent(
    name="StreamBot",
    instructions="""You are a helpful assistant.
You can check weather and search the web.
Provide detailed, thoughtful responses.""",
    tools=[get_weather, search_web]
)

async def interactive_stream():
    print("Streaming Bot (type 'quit' to exit)")
    print("-" * 40)
    
    context = None
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == "quit":
            break
        
        if not user_input:
            continue
        
        print("\nAssistant: ", end="", flush=True)
        
        async for event in Runner.run_streamed(
            agent,
            user_input,
            context=context
        ):
            if event.type == "tool_call_start":
                print(f"\n[Using {event.name}...] ", end="", flush=True)
            
            elif event.type == "text_delta":
                print(event.delta, end="", flush=True)
            
            elif event.type == "run_done":
                context = event.result
        
        print()  # Newline after response

if __name__ == "__main__":
    asyncio.run(interactive_stream())
```
