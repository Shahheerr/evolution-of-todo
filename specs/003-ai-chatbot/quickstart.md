# Quickstart Guide: AI-Powered Chatbot for Task Management

**Feature**: 003-ai-chatbot | **Date**: 2026-01-31 | **Phase**: 1 (Design)

## Overview

This guide helps developers quickly set up and run the AI-powered chatbot feature locally. It assumes you have a working Phase II full-stack Todo application.

## Prerequisites

### Required Software
- Python 3.13+
- Node.js 20+
- UV package manager (Python)
- NPM package manager (JavaScript)

### Required Services
- Neon PostgreSQL database (from Phase II)
- OpenAI API account with API key

### Existing Setup
- Phase II Todo application running locally
- Better-Auth configured and working
- JWT authentication functioning

## Setup Instructions

### 1. Obtain OpenAI API Key

1. Visit https://platform.openai.com/api-keys
2. Create a new API key
3. Save the key securely (you'll need it in step 3)

### 2. Backend Setup

#### 2.1 Add OpenAI Dependency

```bash
cd Phase-II/backend
uv add openai
```

#### 2.2 Update Environment Variables

Add to `backend/.env`:

```bash
# Existing from Phase II
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=your-secret-here
FRONTEND_URL=http://localhost:3000

# New for AI Chatbot
OPENAI_API_KEY=sk-your-openai-api-key-here
AI_MODEL=gpt-4o-mini
```

#### 2.3 Update Configuration

Update `backend/app/core/config.py`:

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Existing settings...
    DATABASE_URL: str
    BETTER_AUTH_SECRET: str
    FRONTEND_URL: str = "http://localhost:3000"
    JWT_ALGORITHM: str = "HS256"
    
    # New for AI Chatbot
    OPENAI_API_KEY: Optional[str] = None
    AI_MODEL: str = "gpt-4o-mini"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
```

#### 2.4 Verify Configuration

```bash
# Test that the OpenAI key is valid
uv run python -c "from openai import OpenAI; c = OpenAI(); print('OpenAI SDK ready!')"
```

### 3. Frontend Setup

No new dependencies required! The AI chat uses existing packages from Phase II.

### 4. Database Setup

**No migrations required!** The AI chatbot uses existing Phase II tables (users, tasks, sessions).

### 5. Start the Application

#### 5.1 Start Backend

```bash
cd Phase-II/backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verify health check:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "healthy",
  "app": "Todo API"
}
```

#### 5.2 Start Frontend

```bash
cd Phase-II/frontend
npm run dev
```

Visit: http://localhost:3000

## Usage

### First Time: Enable AI Chat

1. Login to the application
2. Navigate to the dashboard
3. Click the "AI Assistant" button (or chat icon) to open the chat panel

### Try These Commands

**Create a task:**
```
Add a high priority task to call the dentist tomorrow at 3pm
```

**List tasks:**
```
Show me my pending tasks
```

**Complete a task:**
```
Mark the dentist task as complete
```

**Update a task:**
```
Change the dentist appointment to next Tuesday
```

**Delete a task:**
```
Delete the dentist task
```

**Natural conversation:**
```
User: I need to finish the quarterly report
AI: I'll create a task for that.
User: Set it to high priority
AI: Done! I've updated the priority.
```

## Development Workflow

### Backend Development

#### Project Structure
```
backend/
├── app/
│   ├── ai/              # AI chatbot module (NEW)
│   │   ├── __init__.py
│   │   ├── agent.py     # OpenAI agent implementation
│   │   ├── tools.py     # Task management functions
│   │   └── models.py    # Pydantic models
│   ├── routes/
│   │   └── chat.py      # Chat endpoint (NEW)
│   └── core/
│       ├── config.py    # Updated with OPENAI_API_KEY
│       ├── database.py  # Existing: db singleton
│       └── security.py  # Existing: AuthenticatedUser
```

#### Key Imports for AI Module

```python
# In backend/app/ai/agent.py
from openai import AsyncOpenAI
from app.core.config import settings
from app.core.database import db

# Create OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# In backend/app/routes/chat.py
from app.core.security import AuthenticatedUser
from app.ai.agent import process_chat

@router.post("/chat")
async def chat_endpoint(request: ChatRequest, current_user: AuthenticatedUser):
    # current_user.id is the authenticated user - ALWAYS use this for data isolation
    return await process_chat(request.message, current_user.id)
```

#### Running Tests
```bash
cd Phase-II/backend
uv run pytest tests/ -v
```

#### Adding a New Tool

1. Add function in `app/ai/tools.py`:
```python
from app.core.database import db

async def my_new_tool(
    param1: str,
    user_id: str  # ALWAYS include for security - injected from JWT
) -> dict:
    """Tool description for AI."""
    # Use db singleton for database access
    result = await db.fetchrow(
        "SELECT * FROM tasks WHERE user_id = $1 AND title = $2",
        user_id, param1
    )
    return dict(result) if result else {"error": "Not found"}
```

2. Register in `app/ai/agent.py`:
```python
TOOLS = [
    # ... existing tools
    {
        "type": "function",
        "function": {
            "name": "my_new_tool",
            "description": "Description for AI to understand when to use this",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "..."}
                    # NO user_id - this is injected by backend, not AI
                },
                "required": ["param1"]
            }
        }
    }
]
```

### Frontend Development

#### Project Structure
```
frontend/
├── components/
│   └── AIChat.tsx       # Chat UI component (NEW)
├── lib/
│   ├── auth.ts          # Existing: JWT token functions
│   ├── api.ts           # Existing: API client
│   └── chat-api.ts      # NEW: Chat SSE client
└── app/
    └── dashboard/
        └── page.tsx     # Updated to include AIChat
```

#### Key Pattern: SSE Chat Client

```typescript
// frontend/lib/chat-api.ts
// ⚠️ DO NOT use @openai/chatkit-react - build custom SSE handler

import { getJwtToken } from './auth';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export interface ChatStreamEvent {
  type: 'content' | 'tool_call' | 'error' | 'done';
  content?: string;
  tool_call?: { id: string; name: string; arguments: Record<string, unknown> };
  error?: string;
}

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
        try {
          const event: ChatStreamEvent = JSON.parse(line.slice(6));
          onEvent(event);
        } catch {
          // Ignore malformed lines
        }
      }
    }
  }
  
  return newSessionId;
}
```

#### Running Tests
```bash
cd Phase-II/frontend
npm test
```

#### Customizing Chat UI

Edit `components/AIChat.tsx`:
- Adjust panel width/height
- Change colors and styling
- Add message timestamps
- Customize welcome message

## Troubleshooting

### Common Issues

**Issue: "401 Unauthorized" when sending chat message**
- Cause: JWT token expired or missing
- Fix: Log out and log back in

**Issue: "AI service unavailable" error**
- Cause: OpenAI API key invalid or service down
- Fix: Verify OPENAI_API_KEY in .env, check https://status.openai.com

**Issue: Chat responses are slow**
- Cause: Network latency or OpenAI API rate limiting
- Fix: Check network, consider upgrading OpenAI tier

**Issue: AI doesn't understand commands**
- Cause: Tool descriptions unclear
- Fix: Improve tool descriptions in `app/ai/agent.py`

**Issue: "Tool execution failed" errors**
- Cause: Database query error or missing data
- Fix: Check backend logs, verify database connection

### Debug Mode

#### Backend Debug Logging
```python
# In backend/app/ai/agent.py
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add logs in key places
logger.debug(f"Processing message: {message}")
logger.debug(f"Tool calls: {response.choices[0].message.tool_calls}")
```

#### Frontend Debug Logging
```typescript
// In frontend/components/AIChat.tsx
const handleEvent = (event: ChatStreamEvent) => {
  console.log('Chat event:', event);
  // ... rest of handler
};
```

## API Testing

### Using cURL

```bash
# 1. Get JWT token (from browser dev tools or login)
TOKEN="your-jwt-token-here"

# 2. Send chat message
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries",
    "session_id": null
  }'
```

### Using Python

```python
import requests
import json

TOKEN = "your-jwt-token-here"

response = requests.post(
    "http://localhost:8000/api/chat",
    headers={"Authorization": f"Bearer {TOKEN}"},
    json={"message": "Show me my tasks", "session_id": None},
    stream=True
)

for line in response.iter_lines():
    if line.startswith(b"data: "):
        event = json.loads(line[6:])
        print(event)
```

## Environment Variables Reference

### Backend (.env)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | Yes | - | Secret for JWT tokens |
| `FRONTEND_URL` | Yes | http://localhost:3000 | Frontend CORS origin |
| `OPENAI_API_KEY` | Yes | - | OpenAI API key for chat |
| `AI_MODEL` | No | gpt-4o-mini | OpenAI model to use |
| `JWT_ALGORITHM` | No | HS256 | JWT signing algorithm |

### Frontend (.env.local)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_BACKEND_URL` | Yes | http://localhost:8000 | Backend API URL |
| `BETTER_AUTH_SECRET` | Yes | - | Shared with backend |

## Performance Tuning

### Reduce Latency

1. **Use faster OpenAI model** (in `backend/.env`):
```bash
AI_MODEL=gpt-4o-mini  # Faster, cheaper (recommended)
# vs
AI_MODEL=gpt-4o       # Slower, smarter (if needed)
```

2. **Reduce conversation history** (in `backend/app/ai/agent.py`):
```python
MAX_HISTORY = 5  # Instead of 10
```

3. **Set tool execution timeout**:
```python
# Prevent hanging on slow queries
TOOL_TIMEOUT_SECONDS = 5
```

### Increase Throughput

1. **Use async connection pooling** (already configured in Phase II)
2. **Enable gzip compression** in FastAPI
3. **Implement rate limiting** to prevent abuse

## Deployment Checklist

### Pre-Deployment

- [ ] Set `OPENAI_API_KEY` in production environment
- [ ] Verify JWT authentication works with production domain
- [ ] Configure CORS for production frontend URL
- [ ] Set up monitoring for OpenAI API usage
- [ ] Configure rate limiting for /api/chat endpoint
- [ ] Test error handling (invalid API key, service downtime)

### Production Environment Variables

```bash
# Production .env
DATABASE_URL=postgresql://user:pass@prod-host/db
BETTER_AUTH_SECRET=production-secret-key
FRONTEND_URL=https://your-app.com
OPENAI_API_KEY=sk-prod-key-here
AI_MODEL=gpt-4o-mini
```

### Monitoring Metrics

Track these in production:
- API response times (target: <3s p95)
- OpenAI API costs and rate limits
- Error rates (target: <1%)
- Concurrent users (target: 100+)

## Next Steps

1. **Implement**: Follow tasks in `specs/003-ai-chatbot/tasks.md`
2. **Test**: Run test suite and verify all acceptance criteria
3. **Deploy**: Follow deployment checklist above

## Resources

- **Spec**: [specs/003-ai-chatbot/spec.md](spec.md)
- **Plan**: [specs/003-ai-chatbot/plan.md](plan.md)
- **API Contract**: [specs/003-ai-chatbot/contracts/api-contract.md](contracts/api-contract.md)
- **OpenAI Docs**: https://platform.openai.com/docs/guides/function-calling
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Next.js Docs**: https://nextjs.org/docs
