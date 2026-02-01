---
id: 0005
title: Tool response format fix for AI Agent
stage: green
date: 2026-02-01T00:00:00Z
surface: agent
model: claude-opus-4-5-20251101
feature: 003-ai-chatbot
branch: 003-ai-chatbot
user: shahheerr
command: User diagnostic request
labels: ["bugfix", "ai-chatbot", "tool-execution"]
links:
  spec: specs/003-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/ai/tools.py
  - backend/app/ai/agent.py
tests:
  - Manual testing required with OpenAI API key
---

## Prompt

The AI Agent is unable to create tasks. The MCP tools/OpenAI functional_tools are not working as expected first Diognos the problem and fix it. read the @frontend example/ and @"backend (example)/" and read my project frontend and backend and fix the problem

## Response snapshot

## DIAGNOSIS: Tool Response Format Issue

### Root Cause Found
By comparing the example backend (`backend (example)/app/ai/tools.py`) with the current implementation (`backend/app/ai/tools.py`), I identified the critical difference:

**Example backend (working)**:
```python
async def add_task(...) -> str:
    return f"""✅ Task created successfully!

**{title}**
- Priority: {priority_emoji} {priority}
- Status: 📋 PENDING
...
"""
```

**Current implementation (broken)**:
```python
async def create_task(...) -> Dict[str, Any]:
    return {
        "success": True,
        "task": dict(row) if row else {},
        "message": f"Created task: {title}"
    }
```

### The Problem
Tool functions were returning **dictionaries** that were JSON-encoded before being sent to OpenAI:
```python
"content": json.dumps(result) if isinstance(result, dict) else str(result)
```

This meant OpenAI received something like:
```json
"{\"success\": true, \"task\": {...}, \"message\": \"Created task: ...\"}"
```

OpenAI works much better with **plain formatted text** describing what happened, which the AI can then interpret to generate natural responses.

### Fix Applied
Updated all 5 tool functions in `backend/app/ai/tools.py`:
1. `create_task()` - Returns formatted success message
2. `list_tasks()` - Returns formatted task list with emojis
3. `update_task()` - Returns formatted update confirmation
4. `delete_task()` - Returns formatted deletion confirmation
5. `mark_task_complete()` - Returns formatted completion message

Also simplified `agent.py` tool result handling:
```python
"content": str(result)  # Already a string now
```

## Outcome

- ✅ Impact: Fixed AI Agent tool execution - tools now return formatted strings that OpenAI can interpret properly
- 🧪 Tests: Manual testing required with valid OpenAI API key
- 📁 Files: 2 files modified (tools.py, agent.py)
- 🔁 Next prompts: Test the AI chatbot with real OpenAI API key, verify task creation works
- 🧠 Reflection: The example backend pattern was correct - tool functions should return plain formatted text, not structured data. This allows the AI to understand what happened and generate natural responses for the user.

## Evaluation notes (flywheel)

- Failure modes observed: AI Agent unable to create tasks due to tool results being JSON-encoded dictionaries instead of plain text
- Graders run and results (PASS/FAIL): N/A - requires manual testing with OpenAI API
- Prompt variant (if applicable): None - user diagnostic request
- Next experiment: Test with real OpenAI API key to verify fix works end-to-end
