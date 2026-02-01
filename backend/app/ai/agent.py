"""
AI Agent - OpenAI-powered task management agent with function calling.

This module creates an AI agent that can manage tasks through conversation
using OpenAI's function calling feature to invoke task management tools.
"""

import json
import logging
from typing import Optional, Dict

from openai import AsyncOpenAI
from app.core.config import settings
from app.ai.tools import TOOLS, TOOL_HANDLERS
from app.ai.sessions import get_or_create_session

# Configure logging to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# OpenAI Client
# =============================================================================

_client: Optional[AsyncOpenAI] = None


def get_openai_client() -> AsyncOpenAI:
    """Get or create OpenAI client."""
    global _client
    if _client is None:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set")
        _client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


# =============================================================================
# System Prompt
# =============================================================================

SYSTEM_PROMPT = """You are TaskFlow AI, a helpful task management assistant.

You help users manage their tasks through natural conversation. You MUST use your available tools to perform actions - do NOT just say you will do something, actually call the tool to do it.

**Available Tools:**
- `create_task`: Use this to add new tasks. Extract the title from what the user says.
- `list_tasks`: Use this when users ask to see their tasks, what's pending, or check their to-do list.
- `update_task`: Use this to change task details like title, description, priority, or status.
- `delete_task`: Use this to remove tasks the user no longer needs.
- `mark_task_complete`: Use this when users say they finished or completed something.

**Guidelines:**
1. ALWAYS use the appropriate tool when the user asks to add, view, update, delete, or complete tasks
2. When adding a task, extract the title and any details (priority, due date) mentioned
3. Priority mapping: "urgent", "important", "asap" = HIGH; normal = MEDIUM; "when you can", "low priority" = LOW
4. If a user's request is ambiguous, ask for clarification
5. Celebrate when users complete tasks! 🎉
6. Keep responses concise but informative

**CRITICAL**: When you decide to use a tool, you MUST actually call it. Do not describe what you would do - DO IT by calling the tool."""


# =============================================================================
# Chat Stream Processing
# =============================================================================

async def process_chat_stream(message: str, user_id: str, session_id: Optional[str] = None):
    """
    Generator that yields SSE events for chat response.

    This is the CORE function that handles:
    1. Session management
    2. Tool execution loop (CRITICAL - AI may call tools multiple times)
    3. SSE event yielding

    Args:
        message: User's message
        user_id: Authenticated user's ID (from JWT, for data isolation)
        session_id: Optional existing session ID to resume conversation

    Yields:
        SSE event strings (format: "data: {json}\n\n")
    """
    try:
        client = get_openai_client()
    except ValueError as e:
        yield f"data: {json.dumps({'type': 'error', 'error': f'AI features not available: {str(e)}'})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        return

    # Get or create session
    session = get_or_create_session(user_id, session_id)
    session.add_message("user", message)

    # Yield session_id in first event
    yield f"data: {json.dumps({'type': 'content', 'content': '', 'session_id': session.session_id})}\n\n"

    # Build messages for OpenAI
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + session.get_messages_for_api()

    # CRITICAL: Tool Execution Loop
    # AI may call tools multiple times before returning final response
    max_iterations = 5
    for iteration in range(max_iterations):
        try:
            # Call OpenAI with streaming
            stream = await client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                stream=True
            )

            # Collect full response for tool calls
            full_content = ""
            tool_calls_data = []
            current_tools: Dict[int, Dict[str, str]] = {}

            # Process stream
            async for chunk in stream:
                delta = chunk.choices[0].delta

                # Handle content streaming
                if delta.content:
                    full_content += delta.content
                    yield f"data: {json.dumps({'type': 'content', 'content': delta.content})}\n\n"

                # Handle tool calls (collected, not streamed)
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        if tc.index is not None:
                            if tc.index not in current_tools:
                                current_tools[tc.index] = {"id": "", "name": "", "arguments": ""}
                            if tc.id:
                                current_tools[tc.index]["id"] = tc.id
                            if tc.function:
                                if tc.function.name:
                                    current_tools[tc.index]["name"] = tc.function.name
                                if tc.function.arguments:
                                    current_tools[tc.index]["arguments"] += tc.function.arguments

            # Convert collected tools to list
            tool_calls_data = [
                {
                    "id": t["id"],
                    "name": t["name"],
                    "arguments": t["arguments"]
                }
                for t in current_tools.values()
            ]

            logger.info(f"Iteration {iteration}: content='{full_content[:100] if full_content else 'empty'}', tool_calls={len(tool_calls_data)}")

            # If no tool calls, we're done with this iteration
            if not tool_calls_data:
                logger.info(f"No tool calls in iteration {iteration}, final response: {full_content[:200] if full_content else 'empty'}")
                session.add_message("assistant", full_content)
                break

            # Add assistant message with tool calls to history
            messages.append({
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

                # Execute tool with user_id injection (CRITICAL for security)
                try:
                    handler = TOOL_HANDLERS.get(tc["name"])
                    if handler:
                        args = json.loads(tc["arguments"])
                        logger.info(f"Executing tool: {tc['name']} with args: {args} for user: {user_id}")
                        # Inject user_id from JWT, NOT from AI parameters
                        result = await handler(user_id=user_id, **args)
                        logger.info(f"Tool {tc['name']} result: {result[:200] if result else 'empty'}")
                    else:
                        result = f"❌ Unknown tool: {tc['name']}"
                        logger.error(f"Unknown tool requested: {tc['name']}")
                except Exception as e:
                    logger.error(f"Tool execution error for {tc.get('name', 'unknown')}: {e}", exc_info=True)
                    result = f"❌ Tool execution error: {str(e)}"

                # Add tool result to history
                # Tool functions now return formatted strings directly
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": str(result)
                })

            # Continue loop - OpenAI will process tool results

        except Exception as e:
            logger.error(f"Chat stream error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            break

    # Emit done event
    yield f"data: {json.dumps({'type': 'done'})}\n\n"
