# ChatKit Server

The ChatKit server handles AI chat requests and streams responses.

## Basic Server

```python
from chatkit import ChatKit
import openai

# Initialize ChatKit
ck = ChatKit()

# Set OpenAI client
openai_client = openai.OpenAI()

@ck.handler()
async def chat_handler(messages, context):
    """Handle chat requests."""
    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        stream=True
    )
    
    # Stream the response
    async for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# Run the server
if __name__ == "__main__":
    ck.run(host="0.0.0.0", port=8000)
```

## Server Configuration

```python
from chatkit import ChatKit

ck = ChatKit(
    # Server settings
    host="0.0.0.0",
    port=8000,
    
    # CORS settings
    cors_origins=["http://localhost:3000"],
    
    # Path settings
    path="/chatkit",
    
    # Debug mode
    debug=True
)
```

## Handler Function

```python
@ck.handler()
async def handler(messages, context):
    """
    Chat handler function.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        context: Request context with metadata
    
    Yields:
        str: Text chunks to stream back
    """
    # Access message history
    for msg in messages:
        role = msg["role"]     # "user", "assistant", or "tool"
        content = msg["content"]
    
    # Access context
    user_id = context.get("user_id")
    session_id = context.get("session_id")
    
    # Stream response
    yield "Hello! "
    yield "How can I help you today?"
```

## Using OpenAI

```python
from chatkit import ChatKit
import openai

ck = ChatKit()
client = openai.AsyncOpenAI()

@ck.handler()
async def handler(messages, context):
    """Stream OpenAI response."""
    
    # Convert to OpenAI format
    openai_messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ] + messages
    
    # Create streaming completion
    stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=openai_messages,
        stream=True
    )
    
    # Yield chunks
    async for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content
```

## State Management

```python
from chatkit import ChatKit, State

ck = ChatKit()

# Define state class
class ChatState(State):
    user_name: str = ""
    message_count: int = 0

@ck.handler(state_class=ChatState)
async def handler(messages, context, state: ChatState):
    """Handler with persistent state."""
    
    # Read state
    name = state.user_name
    count = state.message_count
    
    # Update state
    state.message_count += 1
    
    # State is automatically persisted
    yield f"Hello {name}! This is message #{count + 1}"
```

## Error Handling

```python
from chatkit import ChatKit, ChatKitError

ck = ChatKit()

@ck.handler()
async def handler(messages, context):
    """Handler with error handling."""
    
    try:
        response = await call_ai(messages)
        async for chunk in response:
            yield chunk
            
    except openai.RateLimitError:
        raise ChatKitError(
            message="Rate limit exceeded. Please try again later.",
            code="rate_limit"
        )
    
    except openai.AuthenticationError:
        raise ChatKitError(
            message="AI service unavailable.",
            code="auth_error"
        )
    
    except Exception as e:
        raise ChatKitError(
            message=f"An error occurred: {str(e)}",
            code="internal_error"
        )
```

## Authentication

```python
from chatkit import ChatKit

ck = ChatKit()

@ck.auth()
async def authenticate(request):
    """Authenticate incoming requests."""
    
    # Get token from header
    auth_header = request.headers.get("Authorization", "")
    
    if not auth_header.startswith("Bearer "):
        return None  # Reject request
    
    token = auth_header[7:]
    
    # Verify token
    try:
        user = await verify_token(token)
        return {"user_id": user.id}  # Add to context
    except:
        return None  # Reject request

@ck.handler()
async def handler(messages, context):
    """Handler with authenticated context."""
    user_id = context["user_id"]  # From auth
    yield f"Hello user {user_id}!"
```

## Lifecycle Hooks

```python
from chatkit import ChatKit

ck = ChatKit()

@ck.on_startup()
async def startup():
    """Called when server starts."""
    global db_pool
    db_pool = await create_pool()
    print("ChatKit server started")

@ck.on_shutdown()
async def shutdown():
    """Called when server stops."""
    await db_pool.close()
    print("ChatKit server stopped")

@ck.on_connect()
async def on_connect(context):
    """Called when client connects."""
    print(f"Client connected: {context['session_id']}")

@ck.on_disconnect()
async def on_disconnect(context):
    """Called when client disconnects."""
    print(f"Client disconnected: {context['session_id']}")
```

## Complete Example

```python
"""
Complete ChatKit Server
"""

from chatkit import ChatKit, ChatKitError
import openai
from typing import List, Dict

# Initialize
ck = ChatKit(
    path="/chatkit",
    cors_origins=["http://localhost:3000"]
)

client = openai.AsyncOpenAI()

# =============================================================================
# Authentication
# =============================================================================

@ck.auth()
async def authenticate(request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    
    try:
        user = verify_jwt(auth[7:])
        return {"user_id": user["sub"]}
    except:
        return None

# =============================================================================
# Handler
# =============================================================================

SYSTEM_PROMPT = """You are a helpful assistant.
Be concise and friendly."""

@ck.handler()
async def chat_handler(
    messages: List[Dict],
    context: Dict
):
    """Main chat handler."""
    
    user_id = context.get("user_id", "anonymous")
    
    # Build OpenAI messages
    openai_messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ] + messages
    
    try:
        # Create streaming completion
        stream = await client.chat.completions.create(
            model="gpt-4o",
            messages=openai_messages,
            stream=True,
            max_tokens=1000
        )
        
        # Stream response
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
                
    except openai.RateLimitError:
        raise ChatKitError("Rate limited. Try again later.", "rate_limit")
    
    except Exception as e:
        raise ChatKitError(f"Error: {e}", "internal")

# =============================================================================
# Lifecycle
# =============================================================================

@ck.on_startup()
async def startup():
    print("ChatKit server started on port 8000")

# =============================================================================
# Run
# =============================================================================

if __name__ == "__main__":
    ck.run(host="0.0.0.0", port=8000)
```
