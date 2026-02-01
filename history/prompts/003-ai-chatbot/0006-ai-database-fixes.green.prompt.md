---
id: 0006
title: AI-database connection fixes for tool execution
stage: green
date: 2026-02-01T00:00:00Z
surface: agent
model: claude-opus-4-5-20251101
feature: 003-ai-chatbot
branch: 003-ai-chatbot
user: shahheerr
command: User diagnostic request
labels: ["bugfix", "ai-chatbot", "database", "tool-execution"]
links:
  spec: specs/003-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/ai/tools.py
  - backend/app/ai/agent.py
  - backend/tests/test_db_connection.py
tests:
  - Manual testing required with OpenAI API key
  - Test script created: backend/tests/test_db_connection.py
---

## Prompt

again check the connection between the AI and the database through MCP. the error is that chatbot unable to do these tasks like adding, deleting, edit, mark as complete etc etc. reckeck the project and fixing it. use your skills in /claude/skills and make the frontend example = frontend, and backend (backend) = backend

## Response snapshot

## Additional Fixes Applied

### Clarification
**This project does NOT use MCP (Model Context Protocol)**. The spec explicitly states "DO NOT USE MCP" - this project uses direct OpenAI function calling with the OpenAI SDK.

### Issues Found and Fixed

**1. Missing dueDate and tags in create_task INSERT**
- **Before**: INSERT only included basic columns, missing `dueDate` and `tags`
- **After**: Now properly includes `dueDate` (when provided) and `tags` (default empty array)

**2. Error handling returned dictionaries instead of strings**
- **Before**: `result = {"error": f"Unknown tool: {tc['name']}"}`
- **After**: `result = f"❌ Unknown tool: {tc['name']}"`

**3. Added detailed logging**
- Tool execution now logs: tool name, args, user_id, and result preview
- Error logging includes full traceback for debugging

**4. Created test script**
- `backend/tests/test_db_connection.py` for verifying database connectivity

### Files Modified

**`backend/app/ai/tools.py`:**
- `create_task()`: Added dueDate parsing and conditional INSERT, added tags column
- Now returns formatted strings with emojis (already done in previous fix)

**`backend/app/ai/agent.py`:**
- Fixed error handling to return strings instead of dicts
- Added info logging for tool execution
- Added error logging with traceback

### Database Schema Verification

**From `frontend/prisma/schema.prisma`:**
```prisma
model Task {
  id          String    @id @default(cuid())
  title       String
  description String?
  status      Status    @default(PENDING)
  priority    Priority  @default(MEDIUM)
  dueDate     DateTime?
  tags        String[]
  ...
  userId String
  ...
  @@map("task")
}
```

- Table name: `task` (lowercase, not `tasks`)
- Column `userId` (camelCase with lowercase u)
- `tags` is `String[]` array type
- `dueDate` is nullable `DateTime?`

### Testing Required

1. Start backend: `cd backend && uv run uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Login and try:
   - "Add a high priority task to call the dentist tomorrow"
   - "Show my tasks"
   - "Mark the dentist task as complete"
   - "Delete the dentist task"

## Outcome

- ✅ Impact: Fixed multiple issues preventing AI tools from working - added dueDate/tags handling, fixed error response format, added logging
- 🧪 Tests: Manual testing required with valid OpenAI API key
- 📁 Files: 2 files modified (tools.py, agent.py), 1 test file created
- 🔁 Next prompts: Test the AI chatbot with real OpenAI API key, verify all 5 tool functions work
- 🧠 Reflection: The issue was NOT related to MCP - this project uses direct OpenAI function calling. The problems were: (1) missing columns in INSERT, (2) error responses returning dicts instead of strings, (3) insufficient logging for debugging.

## Evaluation notes (flywheel)

- Failure modes observed: AI tools failing due to missing database columns in INSERT query and error responses not being plain strings
- Graders run and results (PASS/FAIL): N/A - requires manual testing with OpenAI API
- Prompt variant (if applicable): None - user diagnostic request
- Next experiment: Run the backend server and test with real OpenAI API key to verify all fixes work end-to-end
