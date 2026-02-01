# Feature Specification: AI-Powered Chatbot for Task Management

**Feature Branch**: `003-ai-chatbot`
**Created**: 2026-01-31
**Status**: Draft
**Input**: User description: "i want to add the Ai chatbot and make my project AI-powered Todo APP. when i ask to add, edit, delete, mark as complete etc into my Todo App, AI should do that. now write the specification and write what you have learned. you know how todo something."

## Executive Summary

This feature adds an AI-powered conversational interface to the TaskFlow todo application, enabling users to manage their tasks through natural language. Users can interact with the AI chatbot to create, view, update, delete, and complete tasks without using the traditional form-based interface. The AI understands context, interprets user intent, and executes appropriate actions through function calling capabilities.

## User Scenarios & Testing

### User Story 1 - Conversational Task Creation (Priority: P1)

**Description**: Users can create new tasks by simply describing what they need to do in natural language. The AI chatbot extracts relevant information (title, description, priority, due date, tags) and creates tasks automatically.

**Example interactions**:
- "Add a task to call the dentist tomorrow at 3pm"
- "Create a high priority task to finish the quarterly report by Friday"
- "Remind me to buy groceries: milk, eggs, and bread"
- "I need to review the PR for the authentication module"

**Why this priority**: This is the most fundamental AI capability - it transforms task creation from a multi-step form interaction into a simple conversation, significantly reducing friction for users.

**Independent Test**: Can be tested by sending natural language task creation requests to the AI chatbot and verifying that tasks are created with correct fields (title, description extracted when mentioned, appropriate default priority, etc.).

**Acceptance Scenarios**:

1. **Given** a user is authenticated and on the dashboard with the AI chat open, **When** the user types "Add a task to review the pull request by Friday", **Then** a new task should be created with title "Review the pull request", due date set to upcoming Friday, and medium priority (default)
2. **Given** a user sends "Create a high priority task: Finish the presentation", **When** the AI processes the request, **Then** a task should be created with title "Finish the presentation" and priority set to HIGH
3. **Given** a user types "Remind me to call mom at 5pm tomorrow", **When** the request is processed, **Then** a task should be created with title "Call mom" and due date set to tomorrow at 5pm
4. **Given** a user sends an ambiguous request like "do the thing", **When** the AI cannot determine the task title, **Then** the AI should ask for clarification ("What task would you like me to create?")

---

### User Story 2 - Task Viewing and Listing (Priority: P1)

**Description**: Users can ask to see their tasks in various ways - all tasks, pending tasks, completed tasks, tasks by priority, or tasks matching specific criteria.

**Example interactions**:
- "Show me my tasks"
- "What do I have pending?"
- "List my high priority tasks"
- "What's due this week?"
- "Show me all completed tasks"

**Why this priority**: Task visibility is essential for users to understand their workload. This enables conversational access to the same filtering capabilities available in the traditional UI.

**Independent Test**: Can be tested by sending various list/query requests to the AI chatbot and verifying that the correct tasks are displayed and match the requested criteria.

**Acceptance Scenarios**:

1. **Given** a user has 10 tasks (5 pending, 3 completed, 2 in progress), **When** they ask "Show me my tasks", **Then** the AI should display all 10 tasks with their current status
2. **Given** a user asks "What do I have pending?", **When** the AI processes the request, **Then** only pending tasks should be listed (excluding completed and in-progress)
3. **Given** a user requests "Show me my high priority tasks", **When** the AI responds, **Then** only tasks with priority HIGH should be displayed
4. **Given** a user asks "What's due this week?", **When** the AI calculates the date range, **Then** only tasks with due dates within the current week should be shown

---

### User Story 3 - Task Status Updates (Priority: P1)

**Description**: Users can mark tasks as complete or incomplete through natural language commands without navigating to the task card or clicking checkboxes.

**Example interactions**:
- "Mark 'Call the dentist' as complete"
- "I finished the quarterly report"
- "Mark task 123 as done"
- "Uncomplete the grocery shopping task"
- "Set the presentation task to in progress"

**Why this priority**: Task completion is the most frequent task operation. Enabling this through conversation significantly reduces interaction friction.

**Independent Test**: Can be tested by sending completion/incompletion requests and verifying that task statuses are updated correctly in the database.

**Acceptance Scenarios**:

1. **Given** a user has a pending task titled "Call the dentist", **When** they say "Mark 'Call the dentist' as complete", **Then** the task status should change to COMPLETED
2. **Given** a user says "I finished the quarterly report", **When** the AI interprets this as a completion, **Then** the task titled "Quarterly report" should be marked COMPLETED
3. **Given** a user requests "Mark task 123 as done", **When** the AI looks up task ID 123, **Then** that task's status should change to COMPLETED
4. **Given** a user says "Uncomplete the grocery shopping task", **When** processed, **Then** the grocery shopping task status should change to PENDING (from COMPLETED)
5. **Given** a user states "Set the presentation task to in progress", **When** the request is executed, **Then** the presentation task status should change to IN_PROGRESS

---

### User Story 4 - Task Editing (Priority: P2)

**Description**: Users can modify existing task details (title, description, priority, due date, tags) through conversational commands.

**Example interactions**:
- "Change the dentist appointment to next Tuesday"
- "Update the quarterly report task to high priority"
- "Add 'urgent' tag to the presentation task"
- "Edit the grocery list: add eggs and remove bread"
- "Set the due date for the call mom task to tomorrow evening"

**Why this priority**: Task modification is less frequent than creation and completion, but still essential for maintaining accurate task information.

**Independent Test**: Can be tested by sending various edit commands and verifying that only the specified fields are updated while other fields remain unchanged.

**Acceptance Scenarios**:

1. **Given** a task titled "Dentist appointment" with due date of Friday, **When** the user says "Change the dentist appointment to next Tuesday", **Then** the task due date should update to next Tuesday while title and other fields remain unchanged
2. **Given** a task "Quarterly report" with MEDIUM priority, **When** the user requests "Update the quarterly report task to high priority", **Then** the task priority should change to HIGH
3. **Given** a "Presentation" task with no tags, **When** the user says "Add 'urgent' tag to the presentation task", **Then** the task should have "urgent" in its tags array
4. **Given** a task with description "Buy milk and bread", **When** the user says "Edit the grocery list: add eggs and remove bread", **Then** the description should update to "Buy milk and eggs"

---

### User Story 5 - Task Deletion (Priority: P2)

**Description**: Users can remove tasks they no longer need through simple conversational commands.

**Example interactions**:
- "Delete the dentist appointment task"
- "Remove task 456"
- "I don't need the grocery list task anymore"
- "Cancel the meeting with John"

**Why this priority**: Deletion is a destructive action that's less frequently used than viewing, creating, or updating tasks, but still necessary for maintaining a clean task list.

**Independent Test**: Can be tested by sending delete commands and verifying that tasks are removed from the user's task list and the database.

**Acceptance Scenarios**:

1. **Given** a user has a task titled "Dentist appointment", **When** they say "Delete the dentist appointment task", **Then** the task should be permanently removed from their task list
2. **Given** a user says "Remove task 456", **When** the AI locates task 456, **Then** that task should be deleted
3. **Given** a user states "I don't need the grocery list task anymore", **When** the AI interprets this intent, **Then** the grocery list task should be deleted
4. **Given** a user requests "Cancel the meeting with John" and there's no matching task, **When** the AI processes the request, **Then** the AI should inform the user that no matching task was found

---

### User Story 6 - Context-Aware Multi-Turn Conversations (Priority: P2)

**Description**: Users can have natural, flowing conversations with the AI where context is maintained across multiple turns. The AI remembers previous interactions and can reference them when executing actions.

**Example interactions**:
- User: "Add a task for my project" → AI: "What's the project?" → User: "The website redesign" → AI: Creates task "Website redesign"
- User: "Show me my tasks" → AI: [lists 5 tasks] → User: "Mark the last one as complete" → AI: Marks the 5th task as complete
- User: "Create a task for the meeting" → AI: Creates task → User: "Change it to 2pm" → AI: Updates the created task's time

**Why this priority**: Natural conversation requires context awareness. Without this, every interaction would feel robotic and require users to repeat information.

**Independent Test**: Can be tested by having multi-turn conversations where subsequent commands reference previous context, and verifying the AI correctly maintains and applies that context.

**Acceptance Scenarios**:

1. **Given** a user says "Add a task for my project" and the AI asks for clarification, **When** the user responds "The website redesign", **Then** the AI should create a task titled "Website redesign"
2. **Given** a user asks "Show me my tasks" and the AI lists tasks including "Task A", "Task B", "Task C", **When** the user says "Mark the last one as complete", **Then** "Task C" should be marked as COMPLETED
3. **Given** a user creates "Meeting at 1pm" task, **When** they subsequently say "Change it to 2pm", **Then** the meeting task's due date should update to 2pm
4. **Given** a user has been discussing a specific task in conversation, **When** they use a pronoun like "it" or "that task", **Then** the AI should correctly resolve the reference to the previously discussed task

---

### User Story 7 - AI Chat UI Integration (Priority: P3)

**Description**: The AI chat interface is seamlessly integrated into the existing dashboard, providing an alternative way to interact with tasks alongside the traditional UI components.

**Example interactions**:
- Users see a chat panel on the dashboard (side-by-side or collapsible)
- Users can toggle the chat panel open/closed
- Task changes made via AI are immediately reflected in the task list
- Users receive visual feedback when AI executes actions

**Why this priority**: While critical for usability, the UI can be simple initially and enhanced later. The core AI functionality (Stories 1-6) works independently of the visual presentation.

**Independent Test**: Can be tested by interacting with the AI chat and verifying that UI updates occur, the chat panel functions correctly, and task list stays synchronized.

**Acceptance Scenarios**:

1. **Given** a user is on the dashboard, **When** they open the AI chat panel, **Then** the chat interface should be visible and functional with a welcome message from the AI
2. **Given** the AI chat is open, **When** the AI creates or modifies a task, **Then** the task list on the main dashboard should refresh to show the updated state
3. **Given** a user wants to focus on the traditional UI, **When** they close or minimize the chat panel, **Then** the chat should be hidden but maintain conversation history for when reopened
4. **Given** a user sends a message to the AI, **When** the AI is processing, **Then** a loading/typing indicator should be displayed to provide feedback

---

### Edge Cases

- What happens when the AI cannot determine which task the user is referring to (e.g., multiple tasks with similar titles)?
- How does the system handle AI service outages or API failures?
- What happens when a user requests an action that violates business rules (e.g., deleting a non-existent task, setting an invalid due date)?
- How does the AI handle ambiguous inputs like "do the work" or "handle things"?
- What happens when a user's natural language input is in a different language or contains typos?
- How does the system handle concurrent modifications (user edits via form while AI is also modifying)?
- What happens when the AI generates a tool call with invalid parameters (e.g., priority value not in allowed list)?
- How does the system handle very long conversation histories that might exceed token limits?
- What happens when a user asks the AI to perform an action on another user's tasks (attempting to bypass data isolation)?
- How does the AI handle requests that require multiple steps or compound actions (e.g., "Complete all high priority tasks")?

## Requirements

### Functional Requirements

#### AI Conversation Management
- **FR-001**: The system MUST provide an AI chat interface accessible from the main dashboard
- **FR-002**: The system MUST maintain conversation context for the duration of a chat session
- **FR-003**: The system MUST display AI responses in real-time with streaming support where applicable
- **FR-004**: The system MUST provide visual feedback (typing indicators, loading states) while the AI processes requests
- **FR-005**: The system MUST maintain conversation history for the current session

#### Task Creation via AI
- **FR-006**: The system MUST allow users to create tasks through natural language descriptions
- **FR-007**: The system MUST extract task title from user input (required field)
- **FR-008**: The system MUST extract optional fields from user input when mentioned: description, priority, due date, tags
- **FR-009**: The system MUST use default values for unspecified optional fields (priority: MEDIUM, status: PENDING)
- **FR-010**: The system MUST validate extracted data before creating the task
- **FR-011**: The system MUST confirm task creation by displaying the created task details to the user

#### Task Viewing via AI
- **FR-012**: The system MUST allow users to list all their tasks through conversational queries
- **FR-013**: The system MUST support filtering tasks by status (pending, in progress, completed)
- **FR-014**: The system MUST support filtering tasks by priority (high, medium, low)
- **FR-015**: The system MUST support filtering tasks by date ranges (this week, this month, overdue)
- **FR-016**: The system MUST support searching tasks by keyword or content
- **FR-017**: The system MUST format task lists in a readable, conversational format

#### Task Status Updates via AI
- **FR-018**: The system MUST allow users to mark tasks as complete through conversational commands
- **FR-019**: The system MUST allow users to mark tasks as incomplete (restore to pending) through conversational commands
- **FR-020**: The system MUST allow users to change task status to in-progress through conversational commands
- **FR-021**: The system MUST locate tasks by title for status updates (falling back to ID if title is ambiguous)
- **FR-022**: The system MUST provide confirmation when status updates are completed

#### Task Editing via AI
- **FR-023**: The system MUST allow users to update task title through conversational commands
- **FR-024**: The system MUST allow users to update task description through conversational commands
- **FR-025**: The system MUST allow users to update task priority through conversational commands
- **FR-026**: The system MUST allow users to update task due date through conversational commands
- **FR-027**: The system MUST allow users to add or remove tags from tasks through conversational commands
- **FR-028**: The system MUST only update fields that are explicitly mentioned in the user's command
- **FR-029**: The system MUST validate all updates before applying them

#### Task Deletion via AI
- **FR-030**: The system MUST allow users to delete tasks by referencing the task title
- **FR-031**: The system MUST allow users to delete tasks by referencing the task ID
- **FR-032**: The system MUST ask for confirmation before deleting tasks when the intent is ambiguous
- **FR-033**: The system MUST inform users when a requested task for deletion cannot be found

#### Context & Ambiguity Handling
- **FR-034**: The system MUST ask clarifying questions when user input is ambiguous
- **FR-035**: The system MUST resolve task references across conversation turns (e.g., "mark that one as complete")
- **FR-036**: The system MUST handle multiple tasks with similar titles by asking the user to specify
- **FR-037**: The system MUST maintain context for at least the last 10 conversation turns
- **FR-038**: The system MUST gracefully handle inputs that don't match any known intent (provide helpful guidance)

#### Data Isolation & Security
- **FR-039**: The system MUST ensure all AI-executed operations respect user data isolation (only operate on authenticated user's tasks)
- **FR-040**: The system MUST include the authenticated user's ID in all AI tool function calls
- **FR-041**: The system MUST validate JWT tokens on all AI chat API requests
- **FR-042**: The system MUST prevent users from accessing or modifying other users' tasks through AI commands

#### Error Handling & Reliability
- **FR-043**: The system MUST provide user-friendly error messages when AI operations fail
- **FR-044**: The system MUST log AI operation failures for debugging and monitoring
- **FR-045**: The system MUST handle AI service unavailability gracefully (inform user, suggest alternative actions)
- **FR-046**: The system MUST retry transient AI service failures before reporting errors to users
- **FR-047**: The system MUST validate all tool function parameters before execution

#### User Interface
- **FR-048**: The system MUST provide a chat interface that is accessible from the dashboard
- **FR-049**: The system MUST allow users to toggle the chat panel open/closed
- **FR-050**: The system MUST refresh the task list display when AI makes changes
- **FR-051**: The system MUST support basic markdown rendering in AI responses (bold, code, lists)
- **FR-052**: The system MUST display message timestamps in the chat interface

### Key Entities

- **AIConversation**: A chat session between a user and the AI assistant, containing messages, context, and metadata
  - `sessionId`: Unique identifier for the conversation session
  - `userId`: ID of the user participating in the conversation
  - `messages`: List of messages exchanged (user messages and AI responses)
  - `startedAt`: Timestamp when the conversation began
  - `lastActivityAt`: Timestamp of the last message

- **AIMessage**: A single message in the conversation, either from the user or from the AI
  - `id`: Unique identifier for the message
  - `conversationId`: Reference to the parent conversation
  - `role`: Either "user" or "assistant"
  - `content`: The message text
  - `timestamp`: When the message was sent
  - `toolCalls`: (Optional) List of AI function/tool calls made by the AI in response to this message

- **AIToolCall**: A record of a function/tool invoked by the AI during conversation
  - `id`: Unique identifier for the tool call
  - `messageId`: Reference to the AI message that initiated the tool call
  - `toolName`: The name of the function/tool that was called
  - `parameters`: The parameters passed to the function
  - `result`: The result returned by the function execution
  - `status`: Whether the tool call succeeded, failed, or is pending

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can create a task through natural language in under 15 seconds (including time to type and AI processing)
- **SC-002**: AI correctly interprets user intent 95% of the time for common task management phrases
- **SC-003**: AI-executed task operations have 99.9% data isolation accuracy (no cross-user data leakage)
- **SC-004**: Chat responses stream in under 3 seconds from user message submission
- **SC-005**: Task list updates reflect AI-made changes within 2 seconds of operation completion
- **SC-006**: Users can complete end-to-end task management (create, view, update, delete) using only conversational interface
- **SC-007**: AI handles ambiguous inputs by asking relevant clarifying questions in 90% of cases
- **SC-008**: System maintains conversation context correctly across 10+ turn conversations

### User Experience Outcomes

- **SC-009**: 80% of users report that AI chat is easier than traditional forms for simple task creation
- **SC-010**: Users can accomplish their primary task management goals through conversation alone
- **SC-011**: AI responses feel natural and conversational (not robotic or templated)
- **SC-012**: Error messages are helpful and guide users toward successful completion

### Technical Outcomes

- **SC-013**: AI chat handles 100 concurrent users without performance degradation
- **SC-014**: AI service failures are handled gracefully with appropriate user notification
- **SC-015**: All AI operations complete within OpenAI's API timeout limits
- **SC-016**: System maintains audit logs of all AI-executed operations for compliance

## Constraints & Assumptions

### Technical Constraints

- AI functionality requires OpenAI API key configuration in environment variables
- AI chat requires authenticated user session (JWT token)
- Conversation history is maintained per session and does not persist across logout/login
- AI model selection (e.g., gpt-4o-mini) balances cost and performance
- Token limits may require summarizing very long conversation histories

### Assumptions

- Users have basic familiarity with chat interfaces
- Users primarily communicate in English (natural language processing optimized for English)
- AI service (OpenAI) maintains 99.9% uptime SLA
- Typical task management conversations involve 1-5 turns
- Users prefer concise, action-oriented AI responses over lengthy explanations

### Scope Boundaries

#### In Scope
- Conversational task creation, viewing, updating, and deletion
- Context-aware multi-turn conversations
- AI chat UI integration into dashboard
- Natural language processing for task management intents
- Streaming AI responses for real-time feedback
- Error handling and clarification for ambiguous inputs
- Data isolation enforcement in all AI operations

#### Out of Scope
- Voice input/output (text-based chat only)
- Multi-language support (English only in initial implementation)
- Advanced AI features like task suggestions, prioritization recommendations, or productivity analytics
- File attachments or document analysis in chat
- Persistent conversation history across sessions
- Collaborative task management through AI (multiple users managing shared tasks)
- Integration with external services beyond OpenAI

## Dependencies

### External Dependencies
- **OpenAI API**: Required for AI chat functionality. Must be configured with valid API key.
- **Neon PostgreSQL**: Database for storing tasks, users, and AI conversation metadata
- **Better Auth**: Authentication service for user session and JWT token management

### Internal Dependencies
- **Phase II Full-Stack Implementation**: Relies on existing task CRUD API endpoints
- **JWT Authentication**: Requires working JWT token generation and validation
- **Task API Endpoints**: AI chat uses existing `/api/tasks` endpoints for operations
- **Database Schema**: Requires existing Task, User, and Session tables

### Integration Points
- **FastAPI Backend**: New `/api/chat` endpoint to handle AI chat requests
- **Next.js Frontend**: New AI chat component to be integrated into dashboard
- **Task Service Layer**: AI tool functions use `db` singleton for database operations

### Phase II Code to Reuse
```python
# Backend imports from Phase II:
from app.core.database import db           # Database singleton with fetch, fetchrow, execute
from app.core.security import AuthenticatedUser  # JWT auth dependency
from app.core.config import settings       # Configuration (add OPENAI_API_KEY, AI_MODEL)
```

```typescript
// Frontend imports from Phase II:
import { getJwtToken } from '@/lib/auth';  // JWT token for API calls
```

## ⚠️ Critical Implementation Notes

### DO NOT USE These Technologies
1. **MCP (Model Context Protocol)** - This is for external tool servers, NOT for this feature. We use direct OpenAI function calling.
2. **@openai/chatkit-react** - This package does NOT exist with the documented API. Build a custom React component with raw `fetch()` and SSE parsing.
3. **OpenAI Agents SDK** - Overkill for this use case. Use direct `chat.completions.create()` with `tools=[]` parameter.

### MUST USE These Technologies
1. **OpenAI Python SDK v1.x+** with `AsyncOpenAI` and `chat.completions.create(tools=[...])`
2. **Custom React SSE Handler** - Parse SSE events manually with `fetch()` and `ReadableStream`
3. **Phase II patterns** for database (`db` singleton), auth (`AuthenticatedUser`), and config (`settings`)

### CRITICAL: Tool Execution Loop Pattern
The AI may call tools that require execution. After execution, results must be sent back to OpenAI for the final response. This creates a LOOP:

```python
async def process_chat(messages, tools, user_id):
    max_iterations = 5
    for _ in range(max_iterations):
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools
        )
        
        # If NO tool calls, return the text response (DONE)
        if not response.choices[0].message.tool_calls:
            return response.choices[0].message.content
        
        # Execute tools, add results to messages, LOOP AGAIN
        for tool_call in response.choices[0].message.tool_calls:
            result = await execute_tool(tool_call, user_id)
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})
```

### CRITICAL: User ID Security
- User ID MUST be extracted from JWT token via `AuthenticatedUser`
- User ID is NEVER sent to OpenAI in function parameters
- User ID is INJECTED by the backend into tool function calls
- This ensures users can ONLY access their own tasks

```python
# CORRECT: user_id from JWT
@router.post("/chat")
async def chat(request: ChatRequest, current_user: AuthenticatedUser):
    # Inject user_id into ALL tool calls
    result = await create_task(user_id=current_user.id, **ai_args)

# WRONG: user_id from AI parameters (SECURITY VULNERABILITY!)
result = await create_task(**ai_args)  # AI could spoof any user_id!
```
