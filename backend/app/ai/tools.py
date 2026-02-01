"""
AI Tool Functions for Task Management

These functions are called by the AI agent to perform task operations.
All functions receive user_id from the authenticated context for data isolation.

IMPORTANT: All tool functions return plain strings (formatted text) that are
sent directly to the AI. This allows the AI to understand what happened and
generate natural responses to the user.
"""

import uuid
from typing import Optional

from app.core.database import db


# =============================================================================
# Tool Schemas (sent to OpenAI)
# =============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task for the user. Extract the task title from the user's message. Optionally extract description, priority (HIGH/MEDIUM/LOW), and due date if mentioned.",
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
    },
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
    },
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
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task by its ID or title.",
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
    },
    {
        "type": "function",
        "function": {
            "name": "mark_task_complete",
            "description": "Mark a task as completed. Use when the user says they finished something or completed a task.",
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
]


# =============================================================================
# Tool Implementation Functions
# =============================================================================

async def create_task(
    title: str,
    user_id: str,  # INJECTED from JWT
    description: str | None = None,
    priority: str = "MEDIUM",
    due_date: str | None = None
) -> str:
    """Create a new task. user_id is injected by backend from JWT. Returns formatted string for AI."""
    from datetime import datetime

    task_id = str(uuid.uuid4())

    # Parse due_date if provided
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        except ValueError:
            pass  # Invalid date format, will be set to NULL

    # Build INSERT query with optional dueDate
    if parsed_due_date:
        row = await db.fetchrow(
            """
            INSERT INTO task (id, title, description, priority, status, "dueDate", tags, "userId", "createdAt", "updatedAt")
            VALUES ($1, $2, $3, $4, 'PENDING', $5, $6, $7, NOW(), NOW())
            RETURNING id, title, description, priority, status, "createdAt"
            """,
            task_id, title, description, priority, parsed_due_date, [], user_id
        )
    else:
        row = await db.fetchrow(
            """
            INSERT INTO task (id, title, description, priority, status, tags, "userId", "createdAt", "updatedAt")
            VALUES ($1, $2, $3, $4, 'PENDING', $5, $6, NOW(), NOW())
            RETURNING id, title, description, priority, status, "createdAt"
            """,
            task_id, title, description, priority, [], user_id
        )

    if not row:
        return f"❌ Failed to create task: {title}"

    priority_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(priority, "⚪")
    due_str = f" | 📅 Due: {due_date}" if due_date else ""
    desc_str = f"\n   📝 {description}" if description else ""

    return f"""✅ Task created successfully!

**{title}**
- Priority: {priority_emoji} {priority}
- Status: 📋 PENDING{desc_str}{due_str}

The task has been added to your dashboard!"""


async def list_tasks(
    user_id: str,  # INJECTED from JWT
    status: str | None = None,
    priority: str | None = None,
    limit: int = 20
) -> str:
    """List tasks. user_id is injected by backend from JWT. Returns formatted string for AI."""

    query = "SELECT * FROM task WHERE \"userId\" = $1"
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

    query += f" ORDER BY \"createdAt\" DESC LIMIT ${param_idx}"
    params.append(limit)

    rows = await db.fetch(query, *params)
    tasks = [dict(r) for r in rows]

    # Format as readable text for AI
    if not tasks:
        filter_msg = ""
        if status:
            filter_msg += f" with status '{status}'"
        if priority:
            filter_msg += f" with priority '{priority}'"
        return f"📭 No tasks found{filter_msg}. Create one by asking me to add a task!"

    lines = [f"📋 **Your Tasks** ({len(tasks)} shown):\n"]
    for task in tasks:
        status_emoji = {"PENDING": "📋", "IN_PROGRESS": "🔄", "COMPLETED": "✅"}.get(task["status"], "⚪")
        priority_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(task["priority"], "⚪")
        lines.append(f"{status_emoji} **{task['title']}** ({priority_emoji} {task['priority']})")
        if task.get("description"):
            lines.append(f"   📝 {task['description'][:100]}{'...' if len(task.get('description', '')) > 100 else ''}")

    return "\n".join(lines)


async def update_task(
    user_id: str,  # INJECTED from JWT
    task_id: str | None = None,
    title_search: str | None = None,
    new_title: str | None = None,
    new_description: str | None = None,
    new_priority: str | None = None,
    new_status: str | None = None,
    new_due_date: str | None = None
) -> str:
    """Update a task. user_id is injected by backend from JWT. Returns formatted string for AI."""

    # Find task by ID or title search
    if task_id:
        task = await db.fetchrow(
            'SELECT * FROM task WHERE id = $1 AND "userId" = $2',
            task_id, user_id
        )
    elif title_search:
        task = await db.fetchrow(
            'SELECT * FROM task WHERE "userId" = $1 AND LOWER(title) LIKE LOWER($2)',
            user_id, f"%{title_search}%"
        )
    else:
        return "❌ Must provide task_id or title_search"

    if not task:
        return f"❌ Task not found matching '{task_id or title_search}'. Use 'list tasks' to see your tasks."

    # Build update query dynamically
    updates = []
    params = []
    param_idx = 1

    if new_title:
        updates.append(f'title = ${param_idx}')
        params.append(new_title)
        param_idx += 1
    if new_description is not None:
        updates.append(f'description = ${param_idx}')
        params.append(new_description)
        param_idx += 1
    if new_priority:
        updates.append(f'priority = ${param_idx}')
        params.append(new_priority)
        param_idx += 1
    if new_status:
        updates.append(f'status = ${param_idx}')
        params.append(new_status)
        param_idx += 1
    if new_due_date:
        updates.append(f'"dueDate" = ${param_idx}::timestamptz')
        params.append(new_due_date)
        param_idx += 1

    if not updates:
        return "❌ No updates provided"

    updates.append('"updatedAt" = NOW()')

    query = f'UPDATE task SET {", ".join(updates)} WHERE id = ${param_idx} RETURNING title, status, priority'
    params.append(task["id"])

    row = await db.fetchrow(query, *params)

    if row:
        return f"""✏️ Task updated successfully!

**{row['title']}** has been updated.
- Status: {row['status']}
- Priority: {row['priority']}"""

    return "❌ Failed to update task."


async def delete_task(
    user_id: str,  # INJECTED from JWT
    task_id: str | None = None,
    title_search: str | None = None
) -> str:
    """Delete a task. user_id is injected by backend from JWT. Returns formatted string for AI."""

    if task_id:
        # First get the task title for the message
        task = await db.fetchrow(
            'SELECT title FROM task WHERE id = $1 AND "userId" = $2',
            task_id, user_id
        )
        if not task:
            return f"❌ Task not found with ID '{task_id}'"

        result = await db.execute(
            'DELETE FROM task WHERE id = $1 AND "userId" = $2',
            task_id, user_id
        )
        if "DELETE 1" in result:
            return f"🗑️ Task **{task['title']}** has been deleted!"
        return "❌ Failed to delete task."

    if title_search:
        # Find matching tasks
        rows = await db.fetch(
            'SELECT id, title FROM task WHERE "userId" = $1 AND LOWER(title) LIKE LOWER($2)',
            user_id, f"%{title_search}%"
        )

        if len(rows) == 0:
            return f"❌ No task found matching '{title_search}'"

        if len(rows) > 1:
            matches = [r["title"] for r in rows]
            return f"❌ Multiple tasks match '{title_search}': {', '.join(matches)}. Please be more specific."

        # Single match - delete it
        title = rows[0]["title"]
        await db.execute('DELETE FROM task WHERE id = $1', rows[0]["id"])
        return f"🗑️ Task **{title}** has been deleted!"

    return "❌ Must provide task_id or title_search"


async def mark_task_complete(
    user_id: str,  # INJECTED from JWT
    task_id: str | None = None,
    title_search: str | None = None
) -> str:
    """Mark a task as complete. user_id is injected by backend from JWT. Returns formatted string for AI."""

    # Find task first
    if task_id:
        task = await db.fetchrow(
            'SELECT id, title, status FROM task WHERE id = $1 AND "userId" = $2',
            task_id, user_id
        )
    elif title_search:
        task = await db.fetchrow(
            'SELECT id, title, status FROM task WHERE "userId" = $1 AND LOWER(title) LIKE LOWER($2)',
            user_id, f"%{title_search}%"
        )
    else:
        return "❌ Must provide task_id or title_search"

    if not task:
        return f"❌ Task not found matching '{task_id or title_search}'. Use 'list tasks' to see your tasks."

    if task["status"] == "COMPLETED":
        return f"ℹ️ Task **{task['title']}** is already completed!"

    # Update the task
    await db.execute(
        'UPDATE task SET status = \'COMPLETED\', "updatedAt" = NOW() WHERE id = $1 AND "userId" = $2',
        task["id"], user_id
    )

    return f"✅ Task **{task['title']}** has been marked as completed! Great job! 🎉"


# =============================================================================
# Tool Handlers Mapping
# =============================================================================

TOOL_HANDLERS = {
    "create_task": create_task,
    "list_tasks": list_tasks,
    "update_task": update_task,
    "delete_task": delete_task,
    "mark_task_complete": mark_task_complete,
}
