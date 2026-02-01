# Tasks: AI-Powered Chatbot for Task Management

**Input**: Design documents from `/specs/003-ai-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/api-contract.md

**Tests**: Tests are included in this task list.

**Organization**: Tasks are grouped by phase and user story for independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `Phase-II/backend/app/` for application code
- **Frontend**: `Phase-II/frontend/` for Next.js application
- **Tests**: `Phase-II/backend/tests/` for backend tests

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Add dependencies and update configuration

- [X] T001 Add OpenAI SDK dependency: Run `cd Phase-II/backend && uv add openai`
- [X] T002 [P] Add OPENAI_API_KEY to `Phase-II/backend/.env`
- [X] T003 [P] Add AI_MODEL=gpt-4o-mini to `Phase-II/backend/.env`
- [X] T004 Update `Phase-II/backend/app/core/config.py` to add OPENAI_API_KEY and AI_MODEL fields to Settings class
- [X] T005 [P] Create `Phase-II/backend/app/ai/__init__.py` module initialization file
- [X] T006 [P] Create `Phase-II/backend/tests/unit/__init__.py` if not exists
- [X] T007 [P] Create `Phase-II/backend/tests/integration/__init__.py` if not exists

**Checkpoint**: Dependencies installed and configuration ready

---

## Phase 2: Core AI Infrastructure (BLOCKS ALL USER STORIES)

**Purpose**: Build the foundational AI components that all features depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Pydantic Models

- [X] T008 [P] Create `Phase-II/backend/app/ai/models.py` with ChatRequest model (message: str, session_id: Optional[str])
- [X] T009 [P] Add ChatStreamChunk model to `Phase-II/backend/app/ai/models.py` (type, content, tool_call, error, session_id)

### Session Management

- [X] T010 Create `Phase-II/backend/app/ai/sessions.py` with ChatSession class (in-memory storage)
- [X] T011 Add get_or_create_session function to `Phase-II/backend/app/ai/sessions.py`
- [X] T012 Add session cleanup for expired sessions (24h) to `Phase-II/backend/app/ai/sessions.py`

### Tool Definitions

- [X] T013 [P] Create `Phase-II/backend/app/ai/tools.py` with TOOLS array containing all 5 tool schemas
- [X] T014 Implement create_task tool function in `Phase-II/backend/app/ai/tools.py` with user_id injection
- [X] T015 Implement list_tasks tool function in `Phase-II/backend/app/ai/tools.py` with user_id injection
- [X] T016 Implement update_task tool function in `Phase-II/backend/app/ai/tools.py` with user_id injection
- [X] T017 Implement delete_task tool function in `Phase-II/backend/app/ai/tools.py` with user_id injection
- [X] T018 Implement mark_task_complete tool function in `Phase-II/backend/app/ai/tools.py` with user_id injection
- [X] T019 Create TOOL_HANDLERS dict mapping tool names to functions in `Phase-II/backend/app/ai/tools.py`

**FIX (0005)**: Fixed tool response format - all tool functions now return formatted strings (not dictionaries) that OpenAI can interpret properly. Also simplified agent.py tool result handling.

### AI Agent

- [X] T020 Create `Phase-II/backend/app/ai/agent.py` with AsyncOpenAI client initialization
- [X] T021 Add SYSTEM_PROMPT constant to `Phase-II/backend/app/ai/agent.py`
- [X] T022 Implement process_chat_stream generator function in `Phase-II/backend/app/ai/agent.py`
- [X] T023 **CRITICAL**: Implement tool execution loop in process_chat_stream (max 5 iterations)
- [X] T024 Add SSE event yielding (content, tool_call, done) to process_chat_stream

### Chat Endpoint

- [X] T025 Create `Phase-II/backend/app/routes/chat.py` with router
- [X] T026 Implement POST /api/chat endpoint with AuthenticatedUser dependency
- [X] T027 Return StreamingResponse with correct headers (text/event-stream)
- [X] T028 Register chat router in `Phase-II/backend/app/main.py`

### Frontend API Client

- [X] T029 [P] Create `Phase-II/frontend/lib/chat-api.ts` with ChatStreamEvent types
- [X] T030 [P] Add ChatMessage interface for UI display to `Phase-II/frontend/lib/chat-api.ts`
- [X] T031 Implement sendChatMessage function with SSE parsing in `Phase-II/frontend/lib/chat-api.ts`

**Checkpoint**: Foundation complete - backend can process chat, frontend can send messages

---

## Phase 3: User Story 1 - Conversational Task Creation (P1) 🎯 MVP

**Goal**: Users can create tasks by describing them in natural language

**Test**: Send "Add a high priority task to call the dentist tomorrow" → verify task created

### Frontend Chat UI

- [X] T032 [P] [US1] Create `Phase-II/frontend/components/AIChat.tsx` component skeleton
- [X] T033 [P] [US1] Add state management: messages array, input, isLoading, sessionId
- [X] T034 [US1] Add message input form with submit button
- [X] T035 [US1] Add messages display area with user/assistant styling
- [X] T036 [US1] Connect sendChatMessage to form submit
- [X] T037 [US1] Implement streaming content accumulation (append to last assistant message)
- [X] T038 [US1] Add typing indicator during loading state
- [X] T039 [US1] Add error display for failed requests

### Dashboard Integration

- [X] T040 [US1] Import and render AIChat in `Phase-II/frontend/app/dashboard/page.tsx`
- [X] T041 [US1] Position chat panel (sidebar or floating button + modal)

### Tests for US1

- [ ] T042 [P] [US1] Unit test create_task tool in `Phase-II/backend/tests/unit/test_ai_tools.py`
- [ ] T043 [P] [US1] Integration test POST /api/chat creates task in `Phase-II/backend/tests/integration/test_chat.py`

**Checkpoint**: Users can create tasks via natural language - MVP complete!

---

## Phase 4: User Story 2 - Task Viewing and Listing (P1)

**Goal**: Users can ask to see their tasks with various filters

**Test**: Send "Show me my high priority tasks" → verify correct tasks displayed

- [ ] T044 [US2] Verify list_tasks handles status filtering in `Phase-II/backend/app/ai/tools.py`
- [ ] T045 [US2] Verify list_tasks handles priority filtering in `Phase-II/backend/app/ai/tools.py`
- [ ] T046 [US2] Format task list output as readable text (not raw JSON) in list_tasks

### Tests for US2

- [ ] T047 [P] [US2] Unit test list_tasks with filters in `Phase-II/backend/tests/unit/test_ai_tools.py`
- [ ] T048 [P] [US2] Integration test task listing via chat in `Phase-II/backend/tests/integration/test_chat.py`

**Checkpoint**: Users can create AND view tasks via conversation

---

## Phase 5: User Story 3 - Task Status Updates (P1)

**Goal**: Users can mark tasks complete/incomplete via natural language

**Test**: Send "Mark the dentist task as complete" → verify status changes

- [ ] T049 [US3] Verify mark_task_complete finds tasks by title_search in `Phase-II/backend/app/ai/tools.py`
- [ ] T050 [US3] Verify mark_task_complete handles task not found case

### Frontend Feedback

- [ ] T051 [US3] Show tool_call events in chat (e.g., "✓ Marking task complete...") in `Phase-II/frontend/components/AIChat.tsx`

### Tests for US3

- [ ] T052 [P] [US3] Unit test mark_task_complete in `Phase-II/backend/tests/unit/test_ai_tools.py`
- [ ] T053 [P] [US3] Integration test task completion via chat in `Phase-II/backend/tests/integration/test_chat.py`

**Checkpoint**: Core P1 features complete (create, view, complete)

---

## Phase 6: User Story 4 - Task Editing (P2)

**Goal**: Users can modify task details through conversation

**Test**: Send "Change the dentist task to next Tuesday" → verify due_date updates

- [ ] T054 [US4] Verify update_task handles partial updates in `Phase-II/backend/app/ai/tools.py`
- [ ] T055 [US4] Verify update_task finds tasks by title_search
- [ ] T056 [US4] Add validation for update parameters

### Tests for US4

- [ ] T057 [P] [US4] Unit test update_task in `Phase-II/backend/tests/unit/test_ai_tools.py`
- [ ] T058 [P] [US4] Integration test task editing via chat in `Phase-II/backend/tests/integration/test_chat.py`

**Checkpoint**: Users can edit tasks via conversation

---

## Phase 7: User Story 5 - Task Deletion (P2)

**Goal**: Users can delete tasks via conversational commands

**Test**: Send "Delete the dentist task" → verify task removed

- [ ] T059 [US5] Verify delete_task handles multiple matches (ask for clarification)
- [ ] T060 [US5] Verify delete_task handles task not found case

### Tests for US5

- [ ] T061 [P] [US5] Unit test delete_task in `Phase-II/backend/tests/unit/test_ai_tools.py`
- [ ] T062 [P] [US5] Integration test task deletion via chat in `Phase-II/backend/tests/integration/test_chat.py`

**Checkpoint**: Users can delete tasks via conversation

---

## Phase 8: User Story 6 - Context-Aware Multi-Turn Conversations (P2)

**Goal**: AI maintains context across conversation turns

**Test**: Create task, then say "Change it to 2pm" → verify AI updates the correct task

- [ ] T063 [US6] Verify session.add_message preserves history in `Phase-II/backend/app/ai/sessions.py`
- [ ] T064 [US6] Verify 10-message limit enforcement in sessions.py
- [ ] T065 [US6] Verify session_id returned in first SSE event

### Frontend Session

- [ ] T066 [US6] Store sessionId from first response in AIChat.tsx state
- [ ] T067 [US6] Send sessionId with subsequent messages

### Tests for US6

- [ ] T068 [P] [US6] Unit test conversation history in `Phase-II/backend/tests/unit/test_sessions.py`
- [ ] T069 [P] [US6] Integration test multi-turn conversation in `Phase-II/backend/tests/integration/test_chat.py`

**Checkpoint**: AI maintains context across turns

---

## Phase 9: User Story 7 - Chat UI Polish (P3)

**Goal**: Polished chat interface with real-time sync

**Test**: Create task via AI → verify task list on dashboard updates

### UI Enhancements

- [ ] T070 [P] [US7] Add collapsible chat panel toggle in AIChat.tsx
- [ ] T071 [P] [US7] Add message timestamps display
- [ ] T072 [P] [US7] Add markdown rendering for AI responses (bold, lists)
- [ ] T073 [P] [US7] Add glassmorphism styling to chat panel
- [ ] T074 [P] [US7] Add welcome message when chat opens

### Dashboard Sync

- [ ] T075 [US7] Emit event or call callback when AI modifies tasks
- [ ] T076 [US7] Refresh task list in dashboard after AI operations

### Tests for US7

- [ ] T077 [P] [US7] Component test for AIChat in `Phase-II/frontend/__tests__/AIChat.test.tsx`

**Checkpoint**: Polished chat UI with dashboard sync

---

## Phase 10: Error Handling & Security

**Purpose**: Production-ready error handling and security

### Error Handling

- [ ] T078 [P] Add try/catch around OpenAI API calls in agent.py with error SSE events
- [ ] T079 [P] Add retry logic for transient OpenAI errors (rate limits) in agent.py
- [ ] T080 [P] Handle tool execution errors gracefully (return error to AI, not crash)
- [ ] T081 [P] Add timeout for tool execution (5 seconds) in agent.py

### Security

- [ ] T082 [P] Verify ALL tool functions receive user_id from JWT, not from AI parameters
- [ ] T083 [P] Add message length validation (1-1000 chars) in ChatRequest model
- [ ] T084 [P] Add session_id format validation (UUID) in chat endpoint

### Logging & Monitoring

- [ ] T085 [P] Add structured logging for chat requests in chat.py
- [ ] T086 [P] Add logging for tool executions in agent.py
- [ ] T087 [P] Add error logging with request context

**Checkpoint**: Production-ready error handling

---

## Phase 11: Documentation & Cleanup

**Purpose**: Final documentation and cleanup

- [ ] T088 Update `Phase-II/README.md` with AI chatbot feature documentation
- [ ] T089 Add inline code comments to agent.py explaining tool execution loop
- [ ] T090 Verify quickstart.md instructions work end-to-end
- [ ] T091 Run all tests and verify passing

**Checkpoint**: Feature complete and documented

---

## Implementation Strategy

### MVP First Approach

1. **Phase 1**: Setup (15 min)
2. **Phase 2**: Core Infrastructure (2-3 hours) ⚠️ CRITICAL
3. **Phase 3**: User Story 1 - Task Creation (1-2 hours) → **MVP DONE!**
4. **Phase 4-5**: User Stories 2-3 (1-2 hours) → Core complete
5. **Phase 6-9**: User Stories 4-7 (2-3 hours) → Full feature
6. **Phase 10-11**: Polish (1 hour) → Production ready

### Parallel Opportunities

After Phase 2 is complete, these can run in parallel:
- All [P] marked tasks within each phase
- Different user stories (if multiple developers)
- Frontend and backend work within each story

### Task Summary

| Phase | Tasks | Parallel |
|-------|-------|----------|
| Phase 1: Setup | 7 | 5 |
| Phase 2: Core Infrastructure | 24 | 6 |
| Phase 3: US1 Task Creation | 12 | 3 |
| Phase 4: US2 Task Viewing | 5 | 2 |
| Phase 5: US3 Status Updates | 5 | 2 |
| Phase 6: US4 Task Editing | 5 | 2 |
| Phase 7: US5 Task Deletion | 4 | 2 |
| Phase 8: US6 Multi-Turn | 7 | 2 |
| Phase 9: US7 UI Polish | 8 | 6 |
| Phase 10: Error Handling | 10 | 10 |
| Phase 11: Documentation | 4 | 0 |
| **Total** | **91** | **40** |

---

## ⚠️ Critical Implementation Notes

### DO NOT USE
1. **MCP (Model Context Protocol)** - Wrong technology for this feature
2. **@openai/chatkit-react** - Does not exist with documented API
3. **OpenAI Agents SDK** - Overkill; use direct function calling

### MUST USE
1. **OpenAI SDK `chat.completions.create()`** with `tools=[]` parameter
2. **Custom React component** with raw `fetch()` + SSE parsing
3. **Phase II patterns**: `db` singleton, `AuthenticatedUser`, `settings`

### CRITICAL: Tool Execution Loop
```python
# This loop is ESSENTIAL - AI may call tools multiple times
while iteration < max_iterations:
    response = await client.chat.completions.create(...)
    if not response.choices[0].message.tool_calls:
        break  # No more tools, return response
    # Execute tools, add results to messages, loop again
```

### CRITICAL: User ID Injection
```python
# CORRECT: user_id from JWT
result = await create_task(user_id=current_user.id, **args)

# WRONG: user_id from AI parameters (security vulnerability!)
result = await create_task(**args)  # AI could spoof user_id!
```
