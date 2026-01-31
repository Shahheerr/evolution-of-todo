"""
Task Routes - CRUD API endpoints for Task management.

All routes are protected by JWT authentication.
All database queries are filtered by user_id for DATA ISOLATION.
"""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.core.security import AuthenticatedUser
from app.core.database import Database, get_db
from app.models.task import (
    TaskCreate,
    TaskUpdate,
    TaskStatusUpdate,
    TaskResponse,
    TaskListResponse,
    Priority,
    Status
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# =============================================================================
# Helper Functions
# =============================================================================

def record_to_task(record) -> TaskResponse:
    """Convert database record to TaskResponse."""
    return TaskResponse(
        id=record["id"],
        title=record["title"],
        description=record["description"],
        status=Status(record["status"]),
        priority=Priority(record["priority"]),
        dueDate=record["dueDate"],
        tags=record["tags"] if record["tags"] else [],
        createdAt=record["createdAt"],
        updatedAt=record["updatedAt"],
        userId=record["userId"]
    )


def get_priority_order(priority: str) -> int:
    """Get numeric order for priority sorting."""
    order = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}
    return order.get(priority, 2)


# =============================================================================
# CREATE - POST /tasks
# =============================================================================

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    user: AuthenticatedUser,
    db: Database = Depends(get_db)
):
    """
    Create a new task for the authenticated user.
    """
    import uuid
    task_id = str(uuid.uuid4()).replace("-", "")[:25]  # cuid-like ID
    now = datetime.utcnow()
    
    query = """
        INSERT INTO task (id, title, description, status, priority, "dueDate", tags, "createdAt", "updatedAt", "userId")
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        RETURNING id, title, description, status, priority, "dueDate", tags, "createdAt", "updatedAt", "userId"
    """
    
    record = await db.fetchrow(
        query,
        task_id,
        task.title,
        task.description,
        task.status.value,
        task.priority.value,
        task.dueDate,
        task.tags,
        now,
        now,
        user.id  # DATA ISOLATION: Task belongs to authenticated user
    )
    
    return record_to_task(record)


# =============================================================================
# READ - GET /tasks (List with Search, Filter, Sort)
# =============================================================================

@router.get("", response_model=TaskListResponse)
async def list_tasks(
    user: AuthenticatedUser,
    db: Database = Depends(get_db),
    # Search
    search: Optional[str] = Query(None, description="Search in title/description"),
    # Filters
    status_filter: Optional[Status] = Query(None, alias="status", description="Filter by status"),
    priority_filter: Optional[Priority] = Query(None, alias="priority", description="Filter by priority"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    # Sorting
    sortBy: str = Query("createdAt", description="Sort by: createdAt, dueDate, priority, title"),
    sortOrder: str = Query("desc", description="Sort order: asc, desc"),
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    pageSize: int = Query(10, ge=1, le=100, description="Items per page")
):
    """
    List all tasks for the authenticated user with search, filter, and sort options.
    
    **DATA ISOLATION**: Only returns tasks belonging to the authenticated user.
    """
    # Build WHERE clause - ALWAYS filter by userId
    conditions = ['"userId" = $1']
    params = [user.id]
    param_count = 1
    
    # Search filter
    if search:
        param_count += 1
        conditions.append(f"(title ILIKE ${param_count} OR description ILIKE ${param_count})")
        params.append(f"%{search}%")
    
    # Status filter
    if status_filter:
        param_count += 1
        conditions.append(f"status = ${param_count}")
        params.append(status_filter.value)
    
    # Priority filter
    if priority_filter:
        param_count += 1
        conditions.append(f"priority = ${param_count}")
        params.append(priority_filter.value)
    
    # Tag filter
    if tag:
        param_count += 1
        conditions.append(f"${param_count} = ANY(tags)")
        params.append(tag)
    
    where_clause = " AND ".join(conditions)
    
    # Validate and build ORDER BY clause
    valid_sort_fields = {
        "createdAt": '"createdAt"',
        "dueDate": '"dueDate"',
        "priority": "priority",
        "title": "title",
        "updatedAt": '"updatedAt"'
    }
    sort_field = valid_sort_fields.get(sortBy, '"createdAt"')
    sort_direction = "DESC" if sortOrder.lower() == "desc" else "ASC"
    
    # Special handling for priority sorting (HIGH > MEDIUM > LOW)
    if sortBy == "priority":
        order_clause = f"""
            CASE priority 
                WHEN 'HIGH' THEN 1 
                WHEN 'MEDIUM' THEN 2 
                WHEN 'LOW' THEN 3 
            END {sort_direction}
        """
    else:
        order_clause = f"{sort_field} {sort_direction}"
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM task WHERE {where_clause}"
    total = await db.fetchval(count_query, *params)
    
    # Calculate pagination
    offset = (page - 1) * pageSize
    total_pages = (total + pageSize - 1) // pageSize if total > 0 else 1
    
    # Fetch tasks
    query = f"""
        SELECT id, title, description, status, priority, "dueDate", tags, "createdAt", "updatedAt", "userId"
        FROM task
        WHERE {where_clause}
        ORDER BY {order_clause}
        LIMIT ${param_count + 1} OFFSET ${param_count + 2}
    """
    params.extend([pageSize, offset])
    
    records = await db.fetch(query, *params)
    tasks = [record_to_task(record) for record in records]
    
    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=page,
        pageSize=pageSize,
        totalPages=total_pages
    )


# =============================================================================
# READ - GET /tasks/{task_id} (Single Task)
# =============================================================================

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    user: AuthenticatedUser,
    db: Database = Depends(get_db)
):
    """
    Get a single task by ID.
    
    **DATA ISOLATION**: Only returns the task if it belongs to the authenticated user.
    """
    query = """
        SELECT id, title, description, status, priority, "dueDate", tags, "createdAt", "updatedAt", "userId"
        FROM task
        WHERE id = $1 AND "userId" = $2
    """
    
    record = await db.fetchrow(query, task_id, user.id)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you don't have permission to access it"
        )
    
    return record_to_task(record)


# =============================================================================
# UPDATE - PUT /tasks/{task_id}
# =============================================================================

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    user: AuthenticatedUser,
    db: Database = Depends(get_db)
):
    """
    Update a task. Only provided fields will be updated.
    
    **DATA ISOLATION**: Only updates the task if it belongs to the authenticated user.
    """
    # First check if task exists and belongs to user
    check_query = 'SELECT id FROM task WHERE id = $1 AND "userId" = $2'
    existing = await db.fetchrow(check_query, task_id, user.id)
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you don't have permission to update it"
        )
    
    # Build dynamic UPDATE query
    updates = []
    params = []
    param_count = 0
    
    if task_update.title is not None:
        param_count += 1
        updates.append(f"title = ${param_count}")
        params.append(task_update.title)
    
    if task_update.description is not None:
        param_count += 1
        updates.append(f"description = ${param_count}")
        params.append(task_update.description)
    
    if task_update.status is not None:
        param_count += 1
        updates.append(f"status = ${param_count}")
        params.append(task_update.status.value)
    
    if task_update.priority is not None:
        param_count += 1
        updates.append(f"priority = ${param_count}")
        params.append(task_update.priority.value)
    
    if task_update.dueDate is not None:
        param_count += 1
        updates.append(f'"dueDate" = ${param_count}')
        params.append(task_update.dueDate)
    
    if task_update.tags is not None:
        param_count += 1
        updates.append(f"tags = ${param_count}")
        params.append(task_update.tags)
    
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # Add updatedAt
    param_count += 1
    updates.append(f'"updatedAt" = ${param_count}')
    params.append(datetime.utcnow())
    
    # Add WHERE conditions
    param_count += 1
    task_id_param = param_count
    param_count += 1
    user_id_param = param_count
    
    params.extend([task_id, user.id])
    
    query = f"""
        UPDATE task
        SET {", ".join(updates)}
        WHERE id = ${task_id_param} AND "userId" = ${user_id_param}
        RETURNING id, title, description, status, priority, "dueDate", tags, "createdAt", "updatedAt", "userId"
    """
    
    record = await db.fetchrow(query, *params)
    return record_to_task(record)


# =============================================================================
# UPDATE STATUS - PATCH /tasks/{task_id}/status
# =============================================================================

@router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: str,
    status_update: TaskStatusUpdate,
    user: AuthenticatedUser,
    db: Database = Depends(get_db)
):
    """
    Update only the status of a task (mark as complete/incomplete).
    
    **DATA ISOLATION**: Only updates the task if it belongs to the authenticated user.
    """
    query = """
        UPDATE task
        SET status = $1, "updatedAt" = $2
        WHERE id = $3 AND "userId" = $4
        RETURNING id, title, description, status, priority, "dueDate", tags, "createdAt", "updatedAt", "userId"
    """
    
    record = await db.fetchrow(
        query,
        status_update.status.value,
        datetime.utcnow(),
        task_id,
        user.id
    )
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you don't have permission to update it"
        )
    
    return record_to_task(record)


# =============================================================================
# DELETE - DELETE /tasks/{task_id}
# =============================================================================

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    user: AuthenticatedUser,
    db: Database = Depends(get_db)
):
    """
    Delete a task.
    
    **DATA ISOLATION**: Only deletes the task if it belongs to the authenticated user.
    """
    query = 'DELETE FROM task WHERE id = $1 AND "userId" = $2 RETURNING id'
    
    result = await db.fetchrow(query, task_id, user.id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you don't have permission to delete it"
        )
    
    return None


# =============================================================================
# BULK OPERATIONS
# =============================================================================

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_completed_tasks(
    user: AuthenticatedUser,
    db: Database = Depends(get_db)
):
    """
    Delete all completed tasks for the authenticated user.
    
    **DATA ISOLATION**: Only deletes completed tasks belonging to the authenticated user.
    """
    query = """
        DELETE FROM task 
        WHERE "userId" = $1 AND status = 'COMPLETED'
    """
    
    await db.execute(query, user.id)
    return None
