# Research: AI-Powered Chatbot for Task Management

**Feature**: 003-ai-chatbot | **Date**: 2026-01-31 | **Phase**: 0 (Research)

## Overview

This document captures research findings for implementing an AI-powered chatbot that enables natural language task management in the Todo application. The research focuses on OpenAI's function calling API, integration patterns with FastAPI, and best practices for maintaining data isolation and context in conversational interfaces.

## Research Questions

### 1. How does OpenAI function calling work for task management operations?

**Findings**:
- OpenAI's function calling (also called "tool calling") allows the LLM to request execution of specific functions defined by the application
- The model decides when and how to call functions based on user intent
- Functions are defined using JSON Schema format with clear descriptions
- The model can call multiple functions in a single response (parallel execution)
- Function calls are returned in the `tool_calls` field of the API response

**Key Pattern (Modern OpenAI SDK v1.x+)**:
```python
from openai import AsyncOpenAI

client = AsyncOpenAI()  # Uses OPENAI_API_KEY from env

tools = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task for the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string"},
                    "priority": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]}
                },
                "required": ["title"]
            }
        }
    }
]

response = await client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools,
    tool_choice="auto"  # Let AI decide when to call tools
)
```

### 2. How to maintain conversation context across multiple turns?

**Findings**:
- Conversation history must be included in each API call to the OpenAI API
- Messages array should include: system prompt, all previous user/assistant exchanges
- Tool call responses must be added to the message thread with role "tool"
- System prompt should establish the assistant's purpose and behavior
- Context window limits require managing history length (spec: last 10 turns)

**Message Structure**:
```python
messages = [
    {"role": "system", "content": "You are a helpful task management assistant..."},
    {"role": "user", "content": "Add a task to call the dentist"},
    {"role": "assistant", "content": None, "tool_calls": [...]},
    {"role": "tool", "tool_call_id": "call_abc123", "content": "Task created successfully"}
]
```

### 3. How to ensure data isolation in AI-executed operations?

**Findings**:
- User ID must be extracted from JWT token BEFORE AI processing
- User ID is NOT sent to OpenAI - it's a security parameter
- All tool function implementations MUST filter by user_id internally
- The `user_id` parameter is injected into tool calls by the backend, not provided by the AI

**Security Pattern (Using Phase II security.py)**:
```python
from app.core.security import AuthenticatedUser, get_current_user

# Define tool schema WITHOUT user_id parameter
tool_schema = {
    "name": "list_tasks",
    "parameters": {
        "properties": {
            "status": {"type": "string"},
            # NO user_id - AI doesn't choose whose tasks to list
        }
    }
}

# Implementation receives user_id from authenticated context
async def list_tasks(status: str | None, user_id: str) -> list[dict]:
    """user_id comes from JWT, NOT from AI parameters."""
    from app.core.database import db
    rows = await db.fetch(
        "SELECT * FROM tasks WHERE user_id = $1 AND ($2::text IS NULL OR status = $2)",
        user_id, status
    )
    return [dict(r) for r in rows]
```

### 4. How to handle streaming responses for better UX?

**Findings**:
- OpenAI API supports Server-Sent Events (SSE) for streaming
- Streaming tokens appear as `delta` updates in the response
- Function calls are NOT streamed - they appear when complete
- Hybrid approach: stream text responses, show loading state during tool execution

**Streaming Pattern**:
```python
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
import json

client = AsyncOpenAI()

async def stream_chat_response(messages: list, tools: list):
    """Generator that yields SSE events."""
    stream = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        stream=True
    )
    
    async for chunk in stream:
        delta = chunk.choices[0].delta
        
        if delta.content:
            yield f"data: {json.dumps({'type': 'content', 'content': delta.content})}\n\n"
        
        if delta.tool_calls:
            for tc in delta.tool_calls:
                yield f"data: {json.dumps({'type': 'tool_call', 'tool_call': {'id': tc.id, 'name': tc.function.name, 'arguments': tc.function.arguments}})}\n\n"
    
    yield f"data: {json.dumps({'type': 'done'})}\n\n"
```

### 5. What AI model should be used?

**Findings**:
- `gpt-4o-mini`: Best balance of cost and performance for task management
- Fast response times (~1-2 seconds for typical queries)
- Lower cost than GPT-4o while maintaining good function calling accuracy
- `gpt-4o`: Consider for complex multi-step reasoning (if needed)

**Recommendation**: Start with `gpt-4o-mini`, monitor accuracy metrics (SC-002: 95% intent interpretation), upgrade if needed.

### 6. Critical: Tool Execution Loop Pattern

**Findings**:
- OpenAI may return tool calls that need to be executed
- After execution, results must be sent back to OpenAI for final response
- This creates a LOOP that continues until AI returns text (no more tool calls)

**⚠️ CRITICAL PATTERN - Tool Execution Loop**:
```python
async def chat_with_tools(messages: list, tools: list, user_id: str) -> str:
    """
    Execute chat completion with tool calling loop.
    This loop is CRITICAL - AI may need multiple rounds of tool calls.
    """
    client = AsyncOpenAI()
    
    while True:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        assistant_message = response.choices[0].message
        
        # If NO tool calls, return the final text response
        if not assistant_message.tool_calls:
            return assistant_message.content
        
        # Add assistant's message (with tool calls) to history
        messages.append(assistant_message.model_dump())
        
        # Execute each tool call and add results
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            # Execute tool with user_id injection (NEVER trust AI for user_id)
            result = await execute_tool(tool_name, arguments, user_id)
            
            # Add tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result) if isinstance(result, dict) else str(result)
            })
        
        # Loop continues - OpenAI will process tool results and respond
```

## Technology Stack Validation

### OpenAI Python SDK (v1.x+)
- ✅ Official library with async support (`AsyncOpenAI`)
- ✅ Pydantic integration for type safety
- ✅ Built-in retry logic for transient failures
- ✅ Streaming support via async generators
- ⚠️ Use `openai` package version 1.0.0+

### FastAPI Integration (Phase II Patterns)
- ✅ Async route handlers match OpenAI SDK's async nature
- ✅ Pydantic models for request/response validation
- ✅ Existing JWT authentication reused (`AuthenticatedUser`)
- ✅ Database access via `db` singleton from `app.core.database`
- ✅ StreamingResponse for SSE

### Next.js Frontend (Phase II Patterns)
- ✅ Existing API client pattern in `lib/api.ts`
- ✅ React state management for chat UI
- ✅ JWT token from Better Auth session
- ✅ TailwindCSS for chat panel styling
- ⚠️ Build custom SSE handler - no external chat libraries

## Implementation Patterns from Phase II Analysis

### Pattern 1: Database Access (from Phase II database.py)
```python
from app.core.database import db

async def create_task_in_db(title: str, user_id: str, priority: str = "MEDIUM"):
    """Use the db singleton for all database operations."""
    row = await db.fetchrow(
        """
        INSERT INTO tasks (id, title, user_id, priority, status, created_at)
        VALUES (gen_random_uuid(), $1, $2, $3, 'PENDING', now())
        RETURNING *
        """,
        title, user_id, priority
    )
    return dict(row)
```

### Pattern 2: Authentication (from Phase II security.py)
```python
from app.core.security import AuthenticatedUser

@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    current_user: AuthenticatedUser  # Automatically extracts user from JWT
):
    # current_user.id is the authenticated user's ID
    # Pass this to ALL tool functions for data isolation
    response = await process_chat(request.message, current_user.id)
    return response
```

### Pattern 3: Custom React SSE Handler (NOT ChatKit)
```typescript
// frontend/lib/chat-api.ts
// ⚠️ DO NOT use @openai/chatkit-react - it doesn't exist as documented!
// Build a custom SSE handler instead:

export async function sendChatMessage(
  message: string,
  sessionId: string | null,
  onEvent: (event: ChatStreamEvent) => void
): Promise<string> {
  const token = await getJwtToken();
  
  const response = await fetch(`${BACKEND_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ message, session_id: sessionId })
  });
  
  if (!response.ok) {
    throw new Error(`Chat failed: ${response.statusText}`);
  }
  
  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let newSessionId = sessionId || '';
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const event = JSON.parse(line.slice(6));
        onEvent(event);
        if (event.session_id) newSessionId = event.session_id;
      }
    }
  }
  
  return newSessionId;
}
```

## Risk Assessment

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| OpenAI API downtime | High | Graceful degradation: inform user, suggest traditional UI |
| Function calling accuracy | Medium | Clear tool descriptions, handle ambiguous inputs (FR-034) |
| Token limit exceeded | Medium | Truncate history to last 10 turns (FR-037), summarize if needed |
| Context loss across sessions | Low | Session-scoped history is acceptable per spec |
| Tool execution loop hangs | Medium | Set max iterations (5), timeout per iteration |

### Security Considerations

| Concern | Mitigation |
|---------|------------|
| Prompt injection | Validate inputs, sanitize before tool execution |
| Data leakage | Never send other users' data in conversation history |
| API key exposure | Store in environment variables, server-side only |
| Token tampering | Existing JWT validation (from Phase II security.py) |
| User ID spoofing | Inject user_id from JWT, NEVER from AI parameters |

## Performance Considerations

### OpenAI API Limits
- Rate limits: ~200 requests/minute for tier 3
- Timeout: Default 60s for completions
- Streaming: Reduces perceived latency

### Conversation Memory
- Store last 10 messages per user session
- Estimated tokens per turn: ~200-300
- Total context: ~2000-3000 tokens (well within limits)

### Database Load
- AI operations reuse existing task endpoints
- No additional query patterns introduced
- Data isolation enforced at query level

## Key Design Decisions

### Decision 1: In-Memory Conversation History
**Choice**: Store conversation history in-memory (dict), not in database

**Rationale**:
- Spec states conversation history is session-scoped and non-persistent
- Simpler implementation, no database schema changes
- Faster access, no additional DB load
- Sessions naturally expire on logout

**Trade-off**: Lost context on server restart - acceptable per spec

### Decision 2: Direct Tool Execution vs. Queue
**Choice**: Execute tool functions synchronously within chat endpoint

**Rationale**:
- Task operations are fast (<200ms per Phase II SLA)
- Simpler error handling and response flow
- No need for background job infrastructure

**Trade-off**: Chat response time depends on tool execution - acceptable for task CRUD operations

### Decision 3: Reuse vs. Duplicate Task Service Methods
**Choice**: AI tools call existing db queries directly (like Phase II routes)

**Rationale**:
- Consistent with Phase II architecture
- Same SQL patterns, same data isolation
- Easier maintenance

**Trade-off**: Some code duplication between routes and tools - acceptable for clarity

### Decision 4: No External Chat Libraries
**Choice**: Build custom React component with raw fetch + SSE parsing

**Rationale**:
- `@openai/chatkit-react` does NOT exist with the hooks documented elsewhere
- Custom implementation gives full control
- Matches Phase II frontend patterns
- No external dependencies to manage

## Dependencies and Integration Points

### New Dependencies Required
```toml
# backend/pyproject.toml
[project.dependencies]
openai = ">=1.0.0"
```

### Existing Dependencies Reused (from Phase II)
- FastAPI, Pydantic, asyncpg
- Better Auth, JWT validation (security.py)
- React, Next.js, TailwindCSS

### Environment Variables Required
```bash
# New for this feature (backend/.env)
OPENAI_API_KEY=sk-...

# Existing (from Phase II)
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=...
FRONTEND_URL=http://localhost:3000
```

### Integration with Phase II Code
```python
# Files to reuse:
from app.core.database import db        # Database singleton
from app.core.security import AuthenticatedUser  # JWT auth
from app.core.config import settings    # Add OPENAI_API_KEY here
```

## ⚠️ Critical Implementation Notes

### DO NOT USE:
1. **MCP (Model Context Protocol)** - This is for external tool servers, NOT for this feature
2. **@openai/chatkit-react** - This package doesn't exist with the documented API
3. **OpenAI Agents SDK** - Overkill for this use case; use direct function calling

### MUST USE:
1. **Direct OpenAI chat.completions.create()** with `tools=[]` parameter
2. **Custom React component** with raw `fetch()` and SSE parsing
3. **Phase II patterns** for database, auth, and config

## Next Steps

### Phase 1: Design
- [x] Create data model extensions for AI chat (data-model.md)
- [x] Define API contracts for chat endpoint (contracts/api-contract.md)
- [x] Create quickstart guide for local development (quickstart.md)

### Phase 2: Implementation Planning
- [ ] Generate detailed tasks.md from `/sp.tasks` command
- [ ] Define test cases for AI tool functions
- [ ] Plan integration testing approach

## References

1. **OpenAI Function Calling Documentation**: https://platform.openai.com/docs/guides/function-calling
2. **OpenAI Python SDK**: https://github.com/openai/openai-python
3. **Phase II Backend Code**: `backend/app/core/database.py`, `backend/app/core/security.py`
4. **Phase II Frontend Code**: `frontend/lib/api.ts`, `frontend/lib/auth.ts`
