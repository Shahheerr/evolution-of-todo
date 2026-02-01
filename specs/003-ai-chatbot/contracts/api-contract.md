# API Contracts: AI-Powered Chatbot for Task Management

**Feature**: 003-ai-chatbot | **Date**: 2026-01-31 | **Phase**: 1 (Design)

## Overview

This document defines the API contracts for the AI chat endpoint between the Next.js frontend and FastAPI backend. The chat endpoint uses Server-Sent Events (SSE) for streaming responses while maintaining JWT authentication for security.

## Authentication Contract

The AI chat endpoint uses the same JWT authentication pattern as Phase II task endpoints.

### Authorization Header Format
- **Header**: `Authorization: Bearer <jwt-token>`
- **Requirement**: Required for all chat requests
- **Validation**: Backend verifies JWT signature using `BETTER_AUTH_SECRET`
- **User Extraction**: `user_id` extracted from token's `sub` claim via `AuthenticatedUser`
- **Failure**: 401 Unauthorized response for invalid tokens

### Token Retrieval (Frontend)
```typescript
// frontend/lib/auth.ts (existing from Phase II)
import { authClient } from './auth-client';

export async function getJwtToken(): Promise<string> {
  const session = await authClient.getSession();
  if (!session?.data?.session?.token) {
    throw new Error('Not authenticated');
  }
  return session.data.session.token;
}
```

### Token Verification (Backend)
```python
# backend/app/core/security.py (existing from Phase II)
from app.core.security import AuthenticatedUser

@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    current_user: AuthenticatedUser  # Automatically extracts user from JWT
):
    # current_user.id is the authenticated user's ID
    # ALWAYS pass this to tool functions for data isolation
    pass
```

## Chat Endpoint

### Send Chat Message

```
POST /api/chat
```

**Description**: Send a message to the AI chatbot and receive a streamed response

**Authentication**: Required (JWT Bearer token)

**Request Body**:
```json
{
  "message": "string (required, 1-1000 characters)",
  "session_id": "string (optional, UUID format)"
}
```

**Request Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message | string | Yes | User's message to the AI (1-1000 chars) |
| session_id | string | No | Existing session ID to resume conversation |

**Response**: Server-Sent Events (SSE) stream with event chunks

**Content-Type**: `text/event-stream`

**Response Format** (Event Stream):
```
data: {"type": "content", "content": "I can help you with that...", "session_id": "uuid-abc123"}

data: {"type": "tool_call", "tool_call": {"id": "call_xyz", "name": "create_task", "arguments": {"title": "Call dentist"}}}

data: {"type": "content", "content": " Done! I've added that task."}

data: {"type": "done"}
```

**Event Types**:

| Type | Description | Fields |
|------|-------------|--------|
| `content` | Text content from AI (streamed token-by-token) | `content: string`, `session_id?: string` |
| `tool_call` | AI is calling a function (shown for transparency) | `tool_call: {id, name, arguments}` |
| `error` | Error occurred during processing | `error: string` |
| `done` | Stream complete (final event) | None |

**Status Codes**:
- `200 OK`: Successful streaming response
- `401 Unauthorized`: Missing or invalid JWT token
- `400 Bad Request`: Invalid request body (empty message, too long)
- `500 Internal Server Error`: Server or AI service error

### Full Request/Response Example

**Request**:
```http
POST /api/chat HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "message": "Add a high priority task to call the dentist tomorrow",
  "session_id": null
}
```

**Response** (SSE Stream):
```
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

data: {"type": "content", "content": "I'll", "session_id": "550e8400-e29b-41d4-a716-446655440000"}

data: {"type": "content", "content": " create"}

data: {"type": "content", "content": " that"}

data: {"type": "content", "content": " task"}

data: {"type": "content", "content": " for you."}

data: {"type": "tool_call", "tool_call": {"id": "call_abc123", "name": "create_task", "arguments": {"title": "Call the dentist", "priority": "HIGH", "due_date": "2026-02-01"}}}

data: {"type": "content", "content": " Done! I've added a high priority task 'Call the dentist' due tomorrow."}

data: {"type": "done"}
```

## Backend Implementation

### Endpoint Handler

```python
# backend/app/routes/chat.py
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional

from app.core.security import AuthenticatedUser
from app.ai.agent import process_chat_stream

router = APIRouter(prefix="/api", tags=["chat"])

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None

@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    current_user: AuthenticatedUser
):
    """
    AI Chat endpoint with SSE streaming.
    
    - Accepts user message
    - Streams AI response as SSE events
    - Automatically handles tool execution
    - Maintains conversation context via session_id
    """
    return StreamingResponse(
        process_chat_stream(
            message=request.message,
            user_id=current_user.id,
            session_id=request.session_id
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
```

### Stream Generator

```python
# backend/app/ai/agent.py
import json
from openai import AsyncOpenAI
from app.core.config import settings
from app.ai.tools import TOOLS, TOOL_HANDLERS
from app.ai.sessions import get_or_create_session

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """You are a helpful task management assistant. You help users manage their tasks by:
- Creating new tasks when they describe something they need to do
- Listing their existing tasks when they ask to see them
- Updating task details when they want to make changes
- Marking tasks as complete when they finish something
- Deleting tasks they no longer need

Be concise and helpful. After performing actions, confirm what you did.
Do not ask for confirmation before creating, updating, or deleting tasks - just do it.
If the user's request is ambiguous, ask for clarification."""

async def process_chat_stream(message: str, user_id: str, session_id: str | None):
    """Generator that yields SSE events for chat response."""
    
    # Get or create session
    session = get_or_create_session(user_id, session_id)
    
    # Add user message to history
    session.add_message("user", message)
    
    # Yield session_id in first event
    first_event = True
    
    # Tool execution loop
    max_iterations = 5
    for iteration in range(max_iterations):
        # Call OpenAI
        response = await client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + session.get_messages_for_api(),
            tools=TOOLS,
            tool_choice="auto",
            stream=True
        )
        
        # Collect full response for tool calls
        full_content = ""
        tool_calls_data = []
        current_tool_call = None
        
        async for chunk in response:
            delta = chunk.choices[0].delta
            
            # Handle content
            if delta.content:
                full_content += delta.content
                event = {"type": "content", "content": delta.content}
                if first_event:
                    event["session_id"] = session.session_id
                    first_event = False
                yield f"data: {json.dumps(event)}\n\n"
            
            # Handle tool calls (collected, not streamed)
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    if tc.index is not None:
                        while len(tool_calls_data) <= tc.index:
                            tool_calls_data.append({"id": "", "name": "", "arguments": ""})
                        if tc.id:
                            tool_calls_data[tc.index]["id"] = tc.id
                        if tc.function:
                            if tc.function.name:
                                tool_calls_data[tc.index]["name"] = tc.function.name
                            if tc.function.arguments:
                                tool_calls_data[tc.index]["arguments"] += tc.function.arguments
        
        # If no tool calls, we're done
        if not tool_calls_data:
            session.add_message("assistant", full_content)
            break
        
        # Add assistant message with tool calls to history
        session.messages.append({
            "role": "assistant",
            "content": full_content if full_content else None,
            "tool_calls": [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {"name": tc["name"], "arguments": tc["arguments"]}
                }
                for tc in tool_calls_data
            ]
        })
        
        # Execute each tool call
        for tc in tool_calls_data:
            # Emit tool_call event for transparency
            yield f"data: {json.dumps({'type': 'tool_call', 'tool_call': {'id': tc['id'], 'name': tc['name'], 'arguments': json.loads(tc['arguments'])}})}\n\n"
            
            # Execute tool with user_id injection
            try:
                handler = TOOL_HANDLERS.get(tc["name"])
                if handler:
                    args = json.loads(tc["arguments"])
                    result = await handler(user_id=user_id, **args)
                else:
                    result = {"error": f"Unknown tool: {tc['name']}"}
            except Exception as e:
                result = {"error": str(e)}
            
            # Add tool result to history
            session.messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": json.dumps(result) if isinstance(result, dict) else str(result)
            })
        
        # Continue loop - OpenAI will process tool results
    
    # Emit done event
    yield f"data: {json.dumps({'type': 'done'})}\n\n"
```

## Tool Function Schemas (Sent to OpenAI)

These schemas are sent to OpenAI API for function calling. They are NOT directly exposed to clients.

### All Tools Array

```python
# backend/app/ai/tools.py
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task for the user. Extract the task title from the user's message. Optionally extract description, priority (HIGH/MEDIUM/LOW), and due date if mentioned.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The task title (required, 1-255 characters)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional detailed description of the task"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["HIGH", "MEDIUM", "LOW"],
                        "description": "Task priority level (default: MEDIUM)"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "ISO 8601 date string (e.g., 2026-02-01) if mentioned"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List the user's tasks with optional filtering. Use this when the user asks to see their tasks, what's pending, high priority tasks, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["PENDING", "IN_PROGRESS", "COMPLETED"],
                        "description": "Filter by task status (optional)"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["HIGH", "MEDIUM", "LOW"],
                        "description": "Filter by priority level (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of tasks to return (default: 20)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update an existing task's details. Use when the user asks to change, modify, or edit a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The ID of the task to update (if known)"
                    },
                    "title_search": {
                        "type": "string",
                        "description": "Search for task by title (if task_id not known)"
                    },
                    "new_title": {"type": "string", "description": "New task title"},
                    "new_description": {"type": "string", "description": "New task description"},
                    "new_priority": {
                        "type": "string",
                        "enum": ["HIGH", "MEDIUM", "LOW"],
                        "description": "New priority level"
                    },
                    "new_status": {
                        "type": "string",
                        "enum": ["PENDING", "IN_PROGRESS", "COMPLETED"],
                        "description": "New task status"
                    },
                    "new_due_date": {"type": "string", "description": "New due date (ISO 8601)"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task by its ID or title.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "The ID of the task to delete"},
                    "title_search": {"type": "string", "description": "The title of the task to delete"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mark_task_complete",
            "description": "Mark a task as completed. Use when the user says they finished something or completed a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "The ID of the task to mark complete"},
                    "title_search": {"type": "string", "description": "The title of the task to mark complete"}
                }
            }
        }
    }
]
```

## Frontend API Client Contract

### TypeScript Interfaces

```typescript
// frontend/lib/chat-api.ts

// Chat request (sent to backend)
export interface ChatRequest {
  message: string;
  session_id?: string | null;
}

// SSE event types (received from backend)
export type ChatStreamEvent =
  | ChatContentEvent
  | ChatToolCallEvent
  | ChatErrorEvent
  | ChatDoneEvent;

export interface ChatContentEvent {
  type: 'content';
  content: string;
  session_id?: string;
}

export interface ChatToolCallEvent {
  type: 'tool_call';
  tool_call: {
    id: string;
    name: string;
    arguments: Record<string, unknown>;
  };
}

export interface ChatErrorEvent {
  type: 'error';
  error: string;
}

export interface ChatDoneEvent {
  type: 'done';
}

// Chat message (for UI display)
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}
```

### API Client Function

```typescript
// frontend/lib/chat-api.ts
import { getJwtToken } from './auth';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function sendChatMessage(
  message: string,
  sessionId: string | null,
  onEvent: (event: ChatStreamEvent) => void,
  signal?: AbortSignal
): Promise<string> {
  const token = await getJwtToken();
  
  const response = await fetch(`${BACKEND_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ message, session_id: sessionId }),
    signal,
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Session expired. Please log in again.');
    }
    throw new Error(`Chat error: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  let newSessionId = sessionId || '';

  if (!reader) throw new Error('No response body');

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6)) as ChatStreamEvent;
            onEvent(data);
            
            if ('session_id' in data && data.session_id) {
              newSessionId = data.session_id;
            }
          } catch {
            // Ignore malformed JSON
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }

  return newSessionId;
}
```

## Error Response Contract

### Error Event Format

All error events in the SSE stream follow this format:
```json
{
  "type": "error",
  "error": "Human-readable error message"
}
```

### HTTP Error Responses

For non-streaming errors (before SSE starts):

```json
{
  "detail": "Error message"
}
```

### Error Scenarios

| Scenario | Status Code | Error Message |
|----------|-------------|---------------|
| Invalid JWT token | 401 | "Could not validate credentials" |
| Expired JWT token | 401 | "Token has expired. Please log in again." |
| Message too long | 400 | "Message exceeds maximum length of 1000 characters" |
| Empty message | 400 | "Message cannot be empty" |
| OpenAI API error | 500 | "AI service unavailable, please try again" |
| Tool execution error | 200 (error event) | "Could not create task: [details]" |
| Rate limit | 429 | "Too many requests. Please wait a moment." |

## Performance Contract

### Response Time Expectations
- **First token latency**: < 1 second (time to first streamed content)
- **Full response**: < 5 seconds for typical queries
- **Tool execution**: < 500ms per tool call
- **Streaming rate**: Real-time as tokens arrive

### Rate Limiting
- Client-side: Debounce user input (300ms)
- OpenAI API: ~200 requests/minute (tier dependent)
- Backend: Consider per-user rate limiting in production

### Resource Limits
- Conversation history: 10 exchanges (20 messages) max
- Message length: 1000 characters max
- Tool execution rounds: 5 max per request
- Session timeout: 24 hours of inactivity

## Security Contract

### Data Isolation
- User ID extracted from JWT `sub` claim via `AuthenticatedUser`
- All tool calls receive authenticated `user_id` from backend
- AI NEVER receives `user_id` in function parameters
- 100% isolation guarantee - users can only access their own tasks

### Input Validation
- Message length: 1-1000 characters
- Session ID: UUID format (if provided)
- XSS protection: Escape content before rendering in frontend

### Prompt Injection Prevention
- System prompt establishes strict boundaries
- User input is just content, not instructions
- Tool functions validate all inputs before database queries
- No dynamic prompt construction from user input

## Testing Contract

### Unit Tests
- Each tool function tested with various inputs
- Error handling paths covered
- User isolation verified (cannot access other users' tasks)

### Integration Tests
- End-to-end chat flow with mocked OpenAI
- Session creation/resumption
- Error scenarios (API failure, invalid input)

### Contract Tests
- Verify SSE event format matches this spec
- Validate tool schemas are valid JSON Schema
- Test authentication flow

### Test Examples

```python
# tests/backend/test_chat.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_chat_requires_auth():
    async with AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/chat",
            json={"message": "Hello"}
        )
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_chat_empty_message():
    async with AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/chat",
            json={"message": ""},
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        assert response.status_code == 400
```
