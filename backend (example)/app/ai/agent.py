"""
AI Agent - OpenAI-powered task management agent with function calling.

This module creates an AI agent that can manage tasks through conversation
using OpenAI's function calling feature to invoke task management tools.
"""

import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

import asyncpg
from openai import AsyncOpenAI

from app.core.config import settings

# =============================================================================
# OpenAI Client
# =============================================================================

client: Optional[AsyncOpenAI] = None


def get_openai_client() -> AsyncOpenAI:
    """Get or create OpenAI client."""
    global client
    if client is None:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set")
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return client


# =============================================================================
# Database Pool
# =============================================================================

_db_pool: Optional[asyncpg.Pool] = None


async def get_db_pool() -> asyncpg.Pool:
    """Get or create the database connection pool."""
    global _db_pool
    if _db_pool is None:
        _db_pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=2,
            max_size=10,
            command_timeout=60
        )
    return _db_pool


# =============================================================================
# Task Management Functions
# =============================================================================

async def add_task(
    user_id: str,
    title: str,
    description: str = "",
    priority: str = "MEDIUM",
    due_date: Optional[str] = None,
    tags: Optional[str] = None
) -> str:
    """Add a new task to the user's task list."""
    valid_priorities = ["HIGH", "MEDIUM", "LOW"]
    priority = priority.upper()
    if priority not in valid_priorities:
        return f"❌ Invalid priority '{priority}'. Must be one of: {', '.join(valid_priorities)}"
    
    tag_list = []
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            return f"❌ Invalid date format '{due_date}'. Please use YYYY-MM-DD format."
    
    task_id = str(uuid.uuid4()).replace("-", "")[:25]
    now = datetime.utcnow()
    
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO task (id, title, description, status, priority, "dueDate", tags, "createdAt", "updatedAt", "userId")
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """,
            task_id, title, description or "", "PENDING", priority,
            parsed_due_date, tag_list, now, now, user_id
        )
    
    priority_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(priority, "⚪")
    tags_str = f" | Tags: {', '.join(tag_list)}" if tag_list else ""
    due_str = f" | Due: {due_date}" if due_date else ""
    
    return f"""✅ Task created successfully!

**{title}**
- Priority: {priority_emoji} {priority}
- Status: 📋 PENDING
- Description: {description or 'No description'}{due_str}{tags_str}

The task has been added to your dashboard!"""


async def list_tasks(
    user_id: str,
    status_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    limit: int = 10
) -> str:
    """List tasks for a user with optional filters."""
    pool = await get_db_pool()
    
    conditions = ['"userId" = $1']
    params: List[Any] = [user_id]
    param_count = 1
    
    if status_filter:
        param_count += 1
        conditions.append(f"status = ${param_count}")
        params.append(status_filter.upper())
    
    if priority_filter:
        param_count += 1
        conditions.append(f"priority = ${param_count}")
        params.append(priority_filter.upper())
    
    param_count += 1
    params.append(limit)
    
    query = f"""
        SELECT id, title, description, status, priority, "dueDate", tags, "createdAt"
        FROM task
        WHERE {" AND ".join(conditions)}
        ORDER BY 
            CASE priority WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 WHEN 'LOW' THEN 3 END,
            "createdAt" DESC
        LIMIT ${param_count}
    """
    
    async with pool.acquire() as conn:
        records = await conn.fetch(query, *params)
    
    if not records:
        filter_msg = ""
        if status_filter:
            filter_msg += f" with status '{status_filter}'"
        if priority_filter:
            filter_msg += f" with priority '{priority_filter}'"
        return f"📭 No tasks found{filter_msg}. Create one by asking me to add a task!"
    
    lines = [f"📋 **Your Tasks** ({len(records)} shown):\n"]
    
    for task in records:
        status_emoji = {"PENDING": "📋", "IN_PROGRESS": "🔄", "COMPLETED": "✅"}.get(task["status"], "⚪")
        priority_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(task["priority"], "⚪")
        
        lines.append(f"{status_emoji} **{task['title']}** ({priority_emoji} {task['priority']})")
        
        if task["description"]:
            lines.append(f"   📝 {task['description'][:100]}{'...' if len(task['description']) > 100 else ''}")
        
        if task["dueDate"]:
            lines.append(f"   📅 Due: {task['dueDate'].strftime('%Y-%m-%d')}")
        
        if task["tags"]:
            lines.append(f"   🏷️ Tags: {', '.join(task['tags'])}")
        
        lines.append("")
    
    return "\n".join(lines)


async def update_task(
    user_id: str,
    task_title: str,
    new_title: Optional[str] = None,
    new_description: Optional[str] = None,
    new_priority: Optional[str] = None,
    new_status: Optional[str] = None
) -> str:
    """Update an existing task by its title."""
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        task = await conn.fetchrow(
            """
            SELECT id, title FROM task
            WHERE "userId" = $1 AND LOWER(title) LIKE LOWER($2)
            LIMIT 1
            """,
            user_id, f"%{task_title}%"
        )
    
    if not task:
        return f"❌ Task not found matching '{task_title}'. Use 'list tasks' to see your tasks."
    
    updates = []
    params: List[Any] = []
    param_count = 0
    
    if new_title:
        param_count += 1
        updates.append(f"title = ${param_count}")
        params.append(new_title)
    
    if new_description is not None:
        param_count += 1
        updates.append(f"description = ${param_count}")
        params.append(new_description)
    
    if new_priority:
        new_priority = new_priority.upper()
        if new_priority not in ["HIGH", "MEDIUM", "LOW"]:
            return "❌ Invalid priority. Must be HIGH, MEDIUM, or LOW."
        param_count += 1
        updates.append(f"priority = ${param_count}")
        params.append(new_priority)
    
    if new_status:
        new_status = new_status.upper().replace(" ", "_")
        if new_status not in ["PENDING", "IN_PROGRESS", "COMPLETED"]:
            return "❌ Invalid status. Must be PENDING, IN_PROGRESS, or COMPLETED."
        param_count += 1
        updates.append(f"status = ${param_count}")
        params.append(new_status)
    
    if not updates:
        return "❌ No updates specified."
    
    param_count += 1
    updates.append(f'"updatedAt" = ${param_count}')
    params.append(datetime.utcnow())
    
    param_count += 1
    params.append(task["id"])
    param_count += 1
    params.append(user_id)
    
    query = f"""
        UPDATE task SET {", ".join(updates)}
        WHERE id = ${param_count - 1} AND "userId" = ${param_count}
        RETURNING title, status, priority
    """
    
    async with pool.acquire() as conn:
        updated = await conn.fetchrow(query, *params)
    
    if updated:
        return f"""✏️ Task updated successfully!

**{updated['title']}** has been updated.
- Status: {updated['status']}
- Priority: {updated['priority']}"""
    
    return "❌ Failed to update task."


async def delete_task(user_id: str, task_title: str) -> str:
    """Delete a task by its title."""
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        task = await conn.fetchrow(
            """
            SELECT id, title FROM task
            WHERE "userId" = $1 AND LOWER(title) LIKE LOWER($2)
            LIMIT 1
            """,
            user_id, f"%{task_title}%"
        )
        
        if not task:
            return f"❌ Task not found matching '{task_title}'."
        
        await conn.execute(
            'DELETE FROM task WHERE id = $1 AND "userId" = $2',
            task["id"], user_id
        )
    
    return f"🗑️ Task **{task['title']}** has been deleted!"


async def mark_task_complete(user_id: str, task_title: str) -> str:
    """Mark a task as completed."""
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        task = await conn.fetchrow(
            """
            SELECT id, title, status FROM task
            WHERE "userId" = $1 AND LOWER(title) LIKE LOWER($2)
            LIMIT 1
            """,
            user_id, f"%{task_title}%"
        )
        
        if not task:
            return f"❌ Task not found matching '{task_title}'."
        
        if task["status"] == "COMPLETED":
            return f"ℹ️ Task **{task['title']}** is already completed!"
        
        await conn.execute(
            """
            UPDATE task SET status = 'COMPLETED', "updatedAt" = $1
            WHERE id = $2 AND "userId" = $3
            """,
            datetime.utcnow(), task["id"], user_id
        )
    
    return f"✅ Task **{task['title']}** has been marked as completed! Great job! 🎉"


# =============================================================================
# Tool Definitions for OpenAI
# =============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a new task to the user's task list",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the task (required)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional detailed description of the task"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["HIGH", "MEDIUM", "LOW"],
                        "description": "Priority level (default: MEDIUM)"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Optional due date in YYYY-MM-DD format"
                    },
                    "tags": {
                        "type": "string",
                        "description": "Optional comma-separated tags"
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
            "description": "List tasks for the user with optional filters",
            "parameters": {
                "type": "object",
                "properties": {
                    "status_filter": {
                        "type": "string",
                        "enum": ["PENDING", "IN_PROGRESS", "COMPLETED"],
                        "description": "Optional filter by status"
                    },
                    "priority_filter": {
                        "type": "string",
                        "enum": ["HIGH", "MEDIUM", "LOW"],
                        "description": "Optional filter by priority"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of tasks to return (default: 10)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update an existing task by its title",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_title": {
                        "type": "string",
                        "description": "The current title of the task to update"
                    },
                    "new_title": {
                        "type": "string",
                        "description": "Optional new title"
                    },
                    "new_description": {
                        "type": "string",
                        "description": "Optional new description"
                    },
                    "new_priority": {
                        "type": "string",
                        "enum": ["HIGH", "MEDIUM", "LOW"],
                        "description": "Optional new priority"
                    },
                    "new_status": {
                        "type": "string",
                        "enum": ["PENDING", "IN_PROGRESS", "COMPLETED"],
                        "description": "Optional new status"
                    }
                },
                "required": ["task_title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task by its title",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_title": {
                        "type": "string",
                        "description": "The title of the task to delete"
                    }
                },
                "required": ["task_title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mark_task_complete",
            "description": "Mark a task as completed",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_title": {
                        "type": "string",
                        "description": "The title of the task to mark as complete"
                    }
                },
                "required": ["task_title"]
            }
        }
    }
]

# Function mapping
FUNCTION_MAP = {
    "add_task": add_task,
    "list_tasks": list_tasks,
    "update_task": update_task,
    "delete_task": delete_task,
    "mark_task_complete": mark_task_complete,
}


# =============================================================================
# AI Agent
# =============================================================================

SYSTEM_PROMPT = """You are TaskFlow AI, a helpful task management assistant.

You help users manage their tasks through natural conversation. You have access to tools that can:
- Add new tasks with title, description, priority, due date, and tags
- List tasks with optional filtering by status or priority
- Update task details like title, description, priority, or status
- Delete tasks
- Mark tasks as complete

Guidelines:
1. Always be helpful and friendly
2. When adding a task, extract the title and any details mentioned
3. Use appropriate priority levels based on language: "urgent", "important", "asap" = HIGH; normal = MEDIUM; "when you can", "low priority" = LOW
4. If a user's request is ambiguous, ask for clarification
5. Celebrate when users complete tasks! 🎉
6. Keep responses concise but informative

Important: When you use a tool, wait for the result and share it with the user."""


async def chat_with_ai(user_id: str, message: str, conversation_history: List[Dict[str, str]] = None) -> str:
    """
    Send a message to the AI and get a response, handling tool calls.
    
    Args:
        user_id: The authenticated user's ID for data isolation
        message: The user's message
        conversation_history: Previous messages in the conversation
    
    Returns:
        The AI's response as a string
    """
    try:
        openai_client = get_openai_client()
    except ValueError as e:
        return f"⚠️ AI features are not available: {str(e)}\n\nPlease configure your OPENAI_API_KEY in the .env file."
    
    # Build messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if conversation_history:
        messages.extend(conversation_history[-10:])  # Keep last 10 messages
    
    messages.append({"role": "user", "content": message})
    
    try:
        # Call OpenAI
        response = await openai_client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=1024,
            temperature=0.7,
        )
        
        assistant_message = response.choices[0].message
        
        # Handle tool calls
        if assistant_message.tool_calls:
            tool_results = []
            
            for tool_call in assistant_message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                
                # Add user_id to all function calls
                func_args["user_id"] = user_id
                
                # Execute the function
                if func_name in FUNCTION_MAP:
                    result = await FUNCTION_MAP[func_name](**func_args)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "output": result
                    })
                else:
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "output": f"Unknown function: {func_name}"
                    })
            
            # Add tool call message
            messages.append({
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })
            
            # Add tool results
            for result in tool_results:
                messages.append({
                    "role": "tool",
                    "tool_call_id": result["tool_call_id"],
                    "content": result["output"]
                })
            
            # Get final response
            final_response = await openai_client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=messages,
                max_tokens=1024,
                temperature=0.7,
            )
            
            return final_response.choices[0].message.content or "I completed the action but couldn't generate a response."
        
        # No tool calls, return the response directly
        return assistant_message.content or "I'm not sure how to respond to that."
        
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return f"❌ Sorry, I encountered an error: {str(e)}"
