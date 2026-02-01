# Data Model: AI-Powered Chatbot for Task Management

**Feature**: 003-ai-chatbot | **Date**: 2026-01-31 | **Phase**: 1 (Design)

## Overview

This document defines the data model for the AI chatbot feature. Importantly, **no database schema changes are required** - the feature uses in-memory session storage for conversation history and leverages existing database entities from Phase II (User, Task, Session).

## Session-Scoped Entities (In-Memory)

### ChatSession

A ChatSession represents an in-memory conversation between a user and the AI assistant. Sessions are created on-demand when a user opens the chat interface and are discarded on logout or server restart.

**Fields**:

| Field | Type | Description | Notes |
|-------|------|-------------|-------|
| session_id | str | Unique session identifier | UUID v4 |
| user_id | str | Authenticated user's ID | Extracted from JWT token |
| messages | list[ChatMessage] | Conversation history | Last 10 messages max (FR-037) |
| created_at | datetime | Session creation timestamp | ISO 8601 |
| last_activity | datetime | Last message timestamp | For session timeout tracking |

**Lifecycle**:
- Created: User opens AI chat panel
- Updated: Each message sent/received
- Destroyed: User logs out or session expires (configurable, default 24 hours)

**Storage**: In-memory (Python dict), no database persistence

**Implementation**:
```python
# In-memory session storage
from datetime import datetime
from typing import Dict
import uuid

# Global session storage (production could use Redis)
sessions: Dict[str, "ChatSession"] = {}

class ChatSession:
    def __init__(self, user_id: str):
        self.session_id = str(uuid.uuid4())
        self.user_id = user_id
        self.messages: list[dict] = []
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
    
    def add_message(self, role: str, content: str | None, tool_calls: list | None = None):
        """Add message and enforce 10-message limit."""
        msg = {"role": role, "content": content}
        if tool_calls:
            msg["tool_calls"] = tool_calls
        self.messages.append(msg)
        self.last_activity = datetime.utcnow()
        
        # Enforce limit (keep system prompt + last 10 exchanges)
        if len(self.messages) > 21:  # 1 system + 10 user + 10 assistant
            self.messages = [self.messages[0]] + self.messages[-20:]
    
    def get_messages_for_api(self) -> list[dict]:
        """Get messages formatted for OpenAI API."""
        return self.messages.copy()
```

### ChatMessage

A single message in the conversation, representing either user input or AI response.

**Fields**:

| Field | Type | Description | Notes |
|-------|------|-------------|-------|
| role | enum | Message sender role | "system", "user", "assistant", "tool" |
| content | str \| null | Message text content | null for tool calls |
| tool_calls | list[ToolCall] \| null | AI-initiated function calls | Only for role="assistant" |
| tool_call_id | str \| null | Reference to parent tool call | Only for role="tool" |

**Role Definitions**:
- `system`: Initial system prompt (establishes AI behavior)
- `user`: Message sent by the human user
- `assistant`: Response from AI (may include tool calls)
- `tool`: Result of executing a tool function

**Storage**: Contained within ChatSession.messages array

### ToolCall

A record of a function/tool invoked by the AI during conversation.

**Fields**:

| Field | Type | Description | Notes |
|-------|------|-------------|-------|
| id | str | Unique tool call identifier | From OpenAI API response |
| type | str | Always "function" | Required by OpenAI |
| function.name | str | Function/tool name | e.g., "create_task", "list_tasks" |
| function.arguments | str | JSON string of parameters | Parsed before execution |

**Storage**: Contained within assistant message's `tool_calls` array

## Reused Database Entities (from Phase II)

The following existing entities are used by AI tool functions. **No schema changes required.**

### User (Existing)

Reused for:
- Extracting userId from JWT token via `AuthenticatedUser`
- Validating user exists before AI operations

### Task (Existing)

AI tools operate on this entity:
- `create_task`: Creates new Task records
- `list_tasks`: Queries Task table filtered by userId
- `update_task`: Modifies Task fields
- `delete_task`: Removes Task records
- `mark_task_complete`: Updates Task.status to "COMPLETED"

**Existing Task Schema (from Phase II)**:
```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'PENDING',  -- PENDING, IN_PROGRESS, COMPLETED
    priority VARCHAR(10) DEFAULT 'MEDIUM', -- HIGH, MEDIUM, LOW
    due_date TIMESTAMPTZ,
    user_id TEXT NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## AI Tool Function Schemas

These schemas are sent to OpenAI API for function calling. The AI chooses which tool to call based on user intent.

### Tool 1: create_task

Creates a new task for the authenticated user.

**OpenAI Schema** (what AI sees):
```json
{
  "type": "function",
  "function": {
    "name": "create_task",
    "description": "Create a new task for the user. Extract the task title from the user's message. Optionally extract description, priority (HIGH/MEDIUM/LOW), due date, and tags if mentioned.",
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
}
```

**Implementation** (backend/app/ai/tools.py):
```python
from app.core.database import db
import uuid

async def create_task(
    title: str,
    user_id: str,  # INJECTED from JWT, NOT from AI
    description: str | None = None,
    priority: str = "MEDIUM",
    due_date: str | None = None
) -> dict:
    """Create a new task. user_id is injected by backend from JWT."""
    task_id = str(uuid.uuid4())
    
    row = await db.fetchrow(
        """
        INSERT INTO tasks (id, title, description, priority, due_date, user_id, status, created_at)
        VALUES ($1, $2, $3, $4, $5::timestamptz, $6, 'PENDING', NOW())
        RETURNING *
        """,
        task_id, title, description, priority, due_date, user_id
    )
    
    return {
        "success": True,
        "task": dict(row),
        "message": f"Created task: {title}"
    }
```

### Tool 2: list_tasks

Retrieves tasks matching specified criteria.

**OpenAI Schema**:
```json
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
}
```

**Implementation**:
```python
async def list_tasks(
    user_id: str,  # INJECTED from JWT
    status: str | None = None,
    priority: str | None = None,
    limit: int = 20
) -> dict:
    """List tasks. user_id is injected by backend from JWT."""
    
    query = "SELECT * FROM tasks WHERE user_id = $1"
    params = [user_id]
    param_idx = 2
    
    if status:
        query += f" AND status = ${param_idx}"
        params.append(status)
        param_idx += 1
    
    if priority:
        query += f" AND priority = ${param_idx}"
        params.append(priority)
        param_idx += 1
    
    query += f" ORDER BY created_at DESC LIMIT ${param_idx}"
    params.append(limit)
    
    rows = await db.fetch(query, *params)
    tasks = [dict(r) for r in rows]
    
    return {
        "success": True,
        "tasks": tasks,
        "count": len(tasks),
        "message": f"Found {len(tasks)} tasks"
    }
```

### Tool 3: update_task

Modifies an existing task.

**OpenAI Schema**:
```json
{
  "type": "function",
  "function": {
    "name": "update_task",
    "description": "Update an existing task's details. Use when the user asks to change, modify, or edit a task. You can update by task_id or by searching for a task by title.",
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
        "new_title": {
          "type": "string",
          "description": "New task title"
        },
        "new_description": {
          "type": "string",
          "description": "New task description"
        },
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
        "new_due_date": {
          "type": "string",
          "description": "New due date (ISO 8601 format)"
        }
      }
    }
  }
}
```

**Implementation**:
```python
async def update_task(
    user_id: str,  # INJECTED from JWT
    task_id: str | None = None,
    title_search: str | None = None,
    new_title: str | None = None,
    new_description: str | None = None,
    new_priority: str | None = None,
    new_status: str | None = None,
    new_due_date: str | None = None
) -> dict:
    """Update a task. user_id is injected by backend from JWT."""
    
    # Find task by ID or title search
    if task_id:
        task = await db.fetchrow(
            "SELECT * FROM tasks WHERE id = $1 AND user_id = $2",
            task_id, user_id
        )
    elif title_search:
        task = await db.fetchrow(
            "SELECT * FROM tasks WHERE user_id = $1 AND LOWER(title) LIKE LOWER($2)",
            user_id, f"%{title_search}%"
        )
    else:
        return {"success": False, "error": "Must provide task_id or title_search"}
    
    if not task:
        return {"success": False, "error": "Task not found"}
    
    # Build update query dynamically
    updates = []
    params = []
    param_idx = 1
    
    if new_title:
        updates.append(f"title = ${param_idx}")
        params.append(new_title)
        param_idx += 1
    if new_description is not None:
        updates.append(f"description = ${param_idx}")
        params.append(new_description)
        param_idx += 1
    if new_priority:
        updates.append(f"priority = ${param_idx}")
        params.append(new_priority)
        param_idx += 1
    if new_status:
        updates.append(f"status = ${param_idx}")
        params.append(new_status)
        param_idx += 1
    if new_due_date:
        updates.append(f"due_date = ${param_idx}::timestamptz")
        params.append(new_due_date)
        param_idx += 1
    
    if not updates:
        return {"success": False, "error": "No updates provided"}
    
    updates.append("updated_at = NOW()")
    
    query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ${param_idx} RETURNING *"
    params.append(task["id"])
    
    row = await db.fetchrow(query, *params)
    
    return {
        "success": True,
        "task": dict(row),
        "message": f"Updated task: {row['title']}"
    }
```

### Tool 4: delete_task

Removes a task by ID or title.

**OpenAI Schema**:
```json
{
  "type": "function",
  "function": {
    "name": "delete_task",
    "description": "Delete a task by its ID or title. Ask for confirmation if multiple tasks match the title.",
    "parameters": {
      "type": "object",
      "properties": {
        "task_id": {
          "type": "string",
          "description": "The ID of the task to delete"
        },
        "title_search": {
          "type": "string",
          "description": "The title of the task to delete (use if ID not known)"
        }
      }
    }
  }
}
```

**Implementation**:
```python
async def delete_task(
    user_id: str,  # INJECTED from JWT
    task_id: str | None = None,
    title_search: str | None = None
) -> dict:
    """Delete a task. user_id is injected by backend from JWT."""
    
    if task_id:
        result = await db.execute(
            "DELETE FROM tasks WHERE id = $1 AND user_id = $2",
            task_id, user_id
        )
        if "DELETE 1" in result:
            return {"success": True, "message": "Task deleted successfully"}
        return {"success": False, "error": "Task not found"}
    
    if title_search:
        # Find matching tasks
        rows = await db.fetch(
            "SELECT id, title FROM tasks WHERE user_id = $1 AND LOWER(title) LIKE LOWER($2)",
            user_id, f"%{title_search}%"
        )
        
        if len(rows) == 0:
            return {"success": False, "error": f"No task found matching '{title_search}'"}
        
        if len(rows) > 1:
            matches = [r["title"] for r in rows]
            return {
                "success": False,
                "error": f"Multiple tasks match '{title_search}'. Please be more specific.",
                "matches": matches
            }
        
        # Single match - delete it
        await db.execute("DELETE FROM tasks WHERE id = $1", rows[0]["id"])
        return {"success": True, "message": f"Deleted task: {rows[0]['title']}"}
    
    return {"success": False, "error": "Must provide task_id or title_search"}
```

### Tool 5: mark_task_complete

Marks a task as completed.

**OpenAI Schema**:
```json
{
  "type": "function",
  "function": {
    "name": "mark_task_complete",
    "description": "Mark a task as completed. Use when the user says they finished something, completed a task, or is done with something.",
    "parameters": {
      "type": "object",
      "properties": {
        "task_id": {
          "type": "string",
          "description": "The ID of the task to mark complete"
        },
        "title_search": {
          "type": "string",
          "description": "The title of the task to mark complete (use if ID not known)"
        }
      }
    }
  }
}
```

**Implementation**:
```python
async def mark_task_complete(
    user_id: str,  # INJECTED from JWT
    task_id: str | None = None,
    title_search: str | None = None
) -> dict:
    """Mark a task as complete. user_id is injected by backend from JWT."""
    
    # Use update_task with status = COMPLETED
    return await update_task(
        user_id=user_id,
        task_id=task_id,
        title_search=title_search,
        new_status="COMPLETED"
    )
```

## Data Flow Diagrams

### Chat Request Flow

```
┌─────────┐  JWT    ┌─────────┐  user_id   ┌──────────┐
│ Frontend│ ──────> │ Backend │ ─────────> │OpenAI API│
│ (Chat)  │ <────── │ (FastAPI)│ <───────── │          │
└─────────┘  Stream └─────────┘  Response   └──────────┘
                     │                       (may include
                     │                        tool_calls)
                     │ tool_calls
                     ▼
              ┌────────────┐
              │ Tool Funcs │
              │ (user_id)  │
              └────────────┘
                     │
                     ▼
              ┌────────────┐
              │ PostgreSQL │
              │ (tasks)    │
              └────────────┘
```

### Tool Execution Loop (CRITICAL)

```
┌─────────────────────────────────────────────────────────────┐
│                   TOOL EXECUTION LOOP                        │
│                                                             │
│  1. User sends message                                      │
│  2. Add to conversation history                             │
│  3. Call OpenAI API                                         │
│  4. Check response:                                         │
│     ├─ No tool_calls? → Return content to user (END)        │
│     └─ Has tool_calls? → Continue to step 5                 │
│  5. Add assistant message (with tool_calls) to history      │
│  6. For each tool_call:                                     │
│     ├─ Parse arguments                                      │
│     ├─ Inject user_id from JWT                              │
│     ├─ Execute tool function                                │
│     └─ Add tool result to history                           │
│  7. Go back to step 3 (call OpenAI again)                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Conversation State Example

```
┌─────────────────────────────────────────────────────────────┐
│                    ChatSession                               │
│  session_id: uuid-a1b2c3d4                                  │
│  user_id: user_123                                          │
│  messages: [                                                │
│    {role: "system", content: "You are a task assistant..."} │
│    {role: "user", content: "Add a task to call dentist"}    │
│    {role: "assistant", content: null, tool_calls: [         │
│      {id: "call_abc", function: {name: "create_task", ...}}│
│    ]}                                                       │
│    {role: "tool", tool_call_id: "call_abc",                │
│     content: "{\"success\": true, \"task\": {...}}"}        │
│    {role: "assistant", content: "Done! Created task..."}   │
│  ]                                                          │
└─────────────────────────────────────────────────────────────┘
```

## API Request/Response Models (Pydantic)

### Request Models

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class ChatRequest(BaseModel):
    """Request body for POST /api/chat"""
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None  # Resume existing session

class ChatMessage(BaseModel):
    """A single message in the conversation"""
    role: Literal["system", "user", "assistant", "tool"]
    content: Optional[str] = None
    tool_calls: Optional[list] = None
    tool_call_id: Optional[str] = None
```

### Response Format (Streaming SSE)

```python
class ChatStreamChunk(BaseModel):
    """Single event in the SSE stream"""
    type: Literal["content", "tool_call", "error", "done"]
    content: Optional[str] = None
    tool_call: Optional[dict] = None
    error: Optional[str] = None
    session_id: Optional[str] = None  # Included in first chunk
```

**Example SSE Stream**:
```
data: {"type": "content", "content": "I'll", "session_id": "uuid-abc123"}

data: {"type": "content", "content": " create that task for you."}

data: {"type": "tool_call", "tool_call": {"id": "call_xyz", "name": "create_task", "arguments": {"title": "Call dentist"}}}

data: {"type": "content", "content": " Done! I've added 'Call dentist' to your tasks."}

data: {"type": "done"}
```

## Data Validation Rules

### Business Logic Constraints

1. **User Isolation** (FR-039, FR-040, FR-042):
   - All tool functions MUST receive user_id from authenticated context
   - All database queries MUST filter by user_id
   - AI NEVER receives user_id in function parameters

2. **Conversation Limits** (FR-037):
   - Maximum 10 exchanges (20 messages) in history (configurable)
   - Oldest messages removed when limit exceeded
   - System prompt always preserved

3. **Task Validation** (reuse Phase II rules):
   - Title: 1-255 characters, required
   - Priority: HIGH, MEDIUM, or LOW
   - Status: PENDING, IN_PROGRESS, or COMPLETED

4. **Tool Execution** (FR-047):
   - All parameters validated before execution
   - Invalid parameters return error without crashing
   - Errors returned to AI for user-friendly messaging
   - Maximum 5 tool execution rounds per request

## Security Considerations

### Data Isolation Enforcement

```python
# ✅ CORRECT: user_id injected from auth context
async def create_task(title: str, user_id: str) -> dict:
    # user_id comes from AuthenticatedUser, NOT from AI
    return await db.fetchrow(
        "INSERT INTO tasks (title, user_id) VALUES ($1, $2) RETURNING *",
        title, user_id
    )

# ❌ WRONG: user_id from AI parameters (security risk!)
# The AI could be tricked into providing any user_id
```

### Prompt Injection Prevention

- Validate all user input before adding to message history
- Limit message length to 1000 characters
- System prompt establishes strict boundaries
- Tool functions validate all inputs

## Migration Notes

**No database migrations required** for this feature:
- Conversation history is session-scoped (in-memory)
- No new tables in PostgreSQL
- Existing Task/User/Session tables unchanged

If future requirements demand persistent chat history, add:
```sql
CREATE TABLE chat_messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    user_id TEXT NOT NULL REFERENCES users(id),
    role TEXT NOT NULL,
    content TEXT,
    tool_calls JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_user ON chat_messages(user_id);
```
