# Implementation Plan: AI-Powered Chatbot for Task Management

**Branch**: `003-ai-chatbot` | **Date**: 2026-01-31 | **Spec**: [specs/003-ai-chatbot/spec.md](specs/003-ai-chatbot/spec.md)

## Summary

Implementation of AI-Powered Chatbot for Task Management, adding a conversational interface to the existing Phase-II full-stack Todo application. The feature enables users to manage tasks through natural language by integrating OpenAI's function calling API with the existing FastAPI backend and Next.js frontend. The AI interprets user intent and executes task operations (create, view, update, delete, complete) through structured function calling, maintaining data isolation and context across conversation turns.

## Technical Context

**Language/Version**: Python 3.13+ (backend), Next.js 15+, React 19, TypeScript 5+ (frontend)

**Primary Dependencies**:
- Backend: FastAPI (0.115+), Pydantic (v2+), OpenAI SDK (1.x+), asyncpg, Neon PostgreSQL
- Frontend: Next.js (15+), Better-Auth (v1.4+), React 19, TypeScript 5+, TailwindCSS 4

**Storage**: Neon Serverless PostgreSQL (existing schema from Phase II)

**Testing**: pytest for backend unit/integration tests

**Target Platform**: Web application (Chrome, Firefox, Safari, Edge browsers)

**Project Type**: Decoupled monorepo (frontend + backend as separate directories) - extending Phase II

**Performance Goals**: AI responses stream within 3 seconds, task operations complete within 1 second, supports 100 concurrent users

**Constraints**: 
- Stateless authentication using JWT
- Data isolation by user ID enforced in all AI tool calls
- Conversation history maintained in-memory per session (no persistent storage)
- OpenAI API key required

**Scale/Scope**: Multi-user SaaS application, session-based conversation history (last 10 turns)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance Verification
- ✅ **Spec-Driven Development**: Following spec from `/specs/003-ai-chatbot/spec.md`
- ✅ **Specification Management**: Using sequential numbering format `specs/003-ai-chatbot`
- ✅ **Git Workflow**: Using feature branch `003-ai-chatbot` for isolation
- ✅ **Directory Evolution**: Extending existing Phase II `frontend/` and `backend/` directories
- ✅ **Tech Stack Compliance**: Building on Phase II stack (Next.js, FastAPI, Neon DB) + adding OpenAI SDK
- ✅ **Quality Assurance**: Following testing and linting practices
- ✅ **Architecture Pattern**: Extending existing clean architecture with new AI chat endpoint and frontend component

## Project Structure

### Documentation (this feature)

```text
specs/003-ai-chatbot/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           
│   └── api-contract.md  # AI Chat API contract
├── checklists/
│   └── requirements.md  # Requirements checklist
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
Phase-II/
├── backend/                         # FastAPI application (extended)
│   ├── app/
│   │   ├── main.py                  # Updated: Register new chat routes
│   │   ├── ai/                      # NEW: AI chatbot module
│   │   │   ├── __init__.py
│   │   │   ├── agent.py             # OpenAI agent with function calling
│   │   │   ├── tools.py             # Task management functions for AI
│   │   │   └── models.py            # AI chat Pydantic models
│   │   ├── core/
│   │   │   ├── config.py            # Updated: Add OPENAI_API_KEY
│   │   │   ├── database.py          # Existing: db singleton (reused)
│   │   │   └── security.py          # Existing: JWT verification (reused)
│   │   └── routes/
│   │       ├── tasks.py             # Existing: Task CRUD endpoints (reused)
│   │       └── chat.py              # NEW: AI chat endpoint
│   ├── pyproject.toml               # Updated: Add openai dependency
│   └── .env                         # Updated: Add OPENAI_API_KEY
│
├── frontend/                        # Next.js application (extended)
│   ├── app/
│   │   ├── dashboard/
│   │   │   └── page.tsx             # Updated: Import AIChat component
│   │   └── api/
│   │       └── auth/
│   │           └── [...all]/route.ts  # Existing: Better Auth (reused)
│   ├── components/
│   │   └── AIChat.tsx               # NEW: AI chat UI component
│   ├── lib/
│   │   ├── auth.ts                  # Existing: Better-Auth client (reused)
│   │   ├── api.ts                   # Existing: API client (extended)
│   │   └── chat-api.ts              # NEW: Chat SSE API client
│   └── package.json                 # Existing: Dependencies unchanged
│
└── specs/003-ai-chatbot/            # This feature's specifications
```

### Tests (within each project)

```text
Phase-II/
├── backend/
│   └── tests/
│       ├── unit/
│       │   └── test_ai_tools.py     # NEW: AI tool function tests
│       ├── integration/
│       │   └── test_chat_api.py     # NEW: Chat endpoint tests
│       └── contract/
│           └── test_chat_contract.py  # NEW: Chat contract tests
└── frontend/
    └── __tests__/
        └── components/
            └── AIChat.test.tsx      # NEW: AI chat component tests
```

**Structure Decision**: Extends the existing Phase II architecture. The AI chatbot is implemented as a new module in the backend (`app/ai/`) with a corresponding route handler (`app/routes/chat.py`). The frontend adds a single new component (`components/AIChat.tsx`) that integrates into the existing dashboard. All AI tool calls reuse existing database patterns from Phase II, ensuring consistency and avoiding code duplication. Data isolation is maintained by injecting the authenticated user's ID (from `AuthenticatedUser`) into all AI tool function calls.

## Key Integration Points with Phase II

### Backend Integration

```python
# Files to import from Phase II:
from app.core.database import db           # Database singleton
from app.core.security import AuthenticatedUser  # JWT auth dependency
from app.core.config import settings       # Configuration (add OPENAI_API_KEY)

# Pattern for chat endpoint:
@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    current_user: AuthenticatedUser  # Injects user from JWT
):
    # current_user.id is ALWAYS used for data isolation
    result = await process_chat(request.message, current_user.id)
    return result
```

### Frontend Integration

```typescript
// Files to import from Phase II:
import { getJwtToken } from '@/lib/auth';  // JWT token for API calls

// Pattern for chat API (custom SSE, NOT ChatKit):
const token = await getJwtToken();
const response = await fetch(`${BACKEND_URL}/api/chat`, {
  headers: { Authorization: `Bearer ${token}` },
  // ...
});
```

## ⚠️ Critical Implementation Notes

### DO NOT USE
1. **MCP (Model Context Protocol)** - Wrong technology for this feature
2. **@openai/chatkit-react** - Does not exist with documented API
3. **OpenAI Agents SDK** - Overkill; use direct function calling

### MUST USE
1. **OpenAI SDK `chat.completions.create()`** with `tools=[]` parameter
2. **Custom React component** with raw `fetch()` + SSE parsing
3. **Phase II patterns** for database (`db` singleton), auth (`AuthenticatedUser`), config

### CRITICAL: Tool Execution Loop
```python
# AI may call tools, requiring a loop:
while True:
    response = await client.chat.completions.create(...)
    if not response.choices[0].message.tool_calls:
        return response.choices[0].message.content  # Done!
    # Execute tools, add results, loop again
```

## Complexity Tracking

> No constitutional violations - this section is not applicable

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| N/A | N/A | N/A |
