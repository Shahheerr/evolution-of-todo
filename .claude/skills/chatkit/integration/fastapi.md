# ChatKit FastAPI Integration

Integrate ChatKit server with FastAPI.

## Basic Integration

```python
from fastapi import FastAPI
from chatkit import ChatKit
import openai

# Create FastAPI app
app = FastAPI()

# Create ChatKit instance
ck = ChatKit()

# OpenAI client
client = openai.AsyncOpenAI()

@ck.handler()
async def chat_handler(messages, context):
    stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are helpful."}] + messages,
        stream=True
    )
    
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# Mount ChatKit routes on FastAPI
app.mount("/chatkit", ck.app)

# Your other FastAPI routes
@app.get("/health")
async def health():
    return {"status": "ok"}
```

## With Authentication

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from chatkit import ChatKit
import jwt

app = FastAPI()
ck = ChatKit()
security = HTTPBearer()

# JWT verification
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(
            credentials.credentials,
            "your-secret-key",
            algorithms=["HS256"]
        )
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ChatKit auth handler
@ck.auth()
async def chatkit_auth(request):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    
    try:
        token = auth_header[7:]
        payload = jwt.decode(token, "your-secret-key", algorithms=["HS256"])
        return {"user_id": payload["sub"]}
    except:
        return None

@ck.handler()
async def handler(messages, context):
    user_id = context.get("user_id")
    # Use user_id for personalized responses
    yield f"Hello user {user_id}!"

# Mount ChatKit
app.mount("/chatkit", ck.app)
```

## Full Stack Example

```python
"""
FastAPI + ChatKit Complete Example
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from chatkit import ChatKit, Tool
import openai
import asyncpg
from pydantic import BaseModel
from typing import List, Optional

# =============================================================================
# Configuration
# =============================================================================

app = FastAPI(title="ChatKit API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database pool
pool: Optional[asyncpg.Pool] = None

@app.on_event("startup")
async def startup():
    global pool
    pool = await asyncpg.create_pool("postgresql://...")

@app.on_event("shutdown")
async def shutdown():
    await pool.close()

# OpenAI client
openai_client = openai.AsyncOpenAI()

# =============================================================================
# ChatKit Setup
# =============================================================================

ck = ChatKit()

# Tools
tools = [
    Tool(
        name="get_user_tasks",
        description="Get tasks for the current user",
        parameters={
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["pending", "completed", "all"]
                }
            },
            "required": []
        }
    ),
    Tool(
        name="create_task",
        description="Create a new task",
        parameters={
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "priority": {
                    "type": "string",
                    "enum": ["high", "medium", "low"]
                }
            },
            "required": ["title"]
        }
    )
]

ck.register_tools(tools)

# Tool handlers
@ck.tool_handler("get_user_tasks")
async def handle_get_tasks(args, ctx):
    user_id = ctx.get("user_id")
    status = args.get("status", "all")
    
    query = 'SELECT * FROM tasks WHERE user_id = $1'
    if status != "all":
        query += f" AND status = '{status}'"
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, user_id)
    
    return str([dict(r) for r in rows])

@ck.tool_handler("create_task")
async def handle_create_task(args, ctx):
    user_id = ctx.get("user_id")
    
    async with pool.acquire() as conn:
        await conn.execute(
            'INSERT INTO tasks (user_id, title, priority) VALUES ($1, $2, $3)',
            user_id, args["title"], args.get("priority", "medium")
        )
    
    return f"Created task: {args['title']}"

# Auth
@ck.auth()
async def auth_handler(request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    
    try:
        import jwt
        payload = jwt.decode(auth[7:], "secret", algorithms=["HS256"])
        return {"user_id": payload["sub"]}
    except:
        return None

# Main handler
SYSTEM_PROMPT = """You are a task management assistant.
Use the available tools to help users manage their tasks.
Be concise and helpful."""

@ck.handler()
async def chat_handler(messages, context):
    user_id = context.get("user_id", "anonymous")
    
    # Build messages
    openai_messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ] + messages
    
    # Get OpenAI tools format
    openai_tools = [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters
            }
        }
        for t in tools
    ]
    
    # Call OpenAI
    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=openai_messages,
        tools=openai_tools,
        stream=True
    )
    
    # Stream response
    async for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            yield content

# =============================================================================
# Mount ChatKit on FastAPI
# =============================================================================

app.mount("/chatkit", ck.app)

# =============================================================================
# Additional API Routes
# =============================================================================

class TaskCreate(BaseModel):
    title: str
    priority: str = "medium"

@app.get("/api/tasks")
async def get_tasks(user_id: str):
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM tasks WHERE user_id = $1",
            user_id
        )
    return {"tasks": [dict(r) for r in rows]}

@app.post("/api/tasks")
async def create_task(user_id: str, task: TaskCreate):
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO tasks (user_id, title, priority)
               VALUES ($1, $2, $3) RETURNING *""",
            user_id, task.title, task.priority
        )
    return dict(row)

# =============================================================================
# Run
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-frontend.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
```

## Environment Configuration

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    
    # Database
    database_url: str
    
    # Auth
    jwt_secret: str
    
    # CORS
    frontend_url: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"

settings = Settings()
```
