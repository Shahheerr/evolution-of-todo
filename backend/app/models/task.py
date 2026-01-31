"""
Task Models - Pydantic schemas for Task CRUD operations.

These models define the request/response structure for the Task API endpoints.
They match the Prisma schema definitions.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


# =============================================================================
# Enums (matching Prisma schema)
# =============================================================================

class Priority(str, Enum):
    """Task priority levels."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Status(str, Enum):
    """Task status options."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


# =============================================================================
# Request Models
# =============================================================================

class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    status: Status = Field(default=Status.PENDING, description="Task status")
    priority: Priority = Field(default=Priority.MEDIUM, description="Task priority")
    dueDate: Optional[datetime] = Field(None, description="Due date for the task")
    tags: List[str] = Field(default_factory=list, description="Tags for organization")


class TaskUpdate(BaseModel):
    """Schema for updating an existing task. All fields are optional."""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    status: Optional[Status] = Field(None, description="Task status")
    priority: Optional[Priority] = Field(None, description="Task priority")
    dueDate: Optional[datetime] = Field(None, description="Due date for the task")
    tags: Optional[List[str]] = Field(None, description="Tags for organization")


class TaskStatusUpdate(BaseModel):
    """Schema for marking task as complete/incomplete."""
    status: Status = Field(..., description="New status for the task")


# =============================================================================
# Response Models
# =============================================================================

class TaskResponse(BaseModel):
    """Schema for task response."""
    id: str
    title: str
    description: Optional[str]
    status: Status
    priority: Priority
    dueDate: Optional[datetime]
    tags: List[str]
    createdAt: datetime
    updatedAt: datetime
    userId: str

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for paginated task list response."""
    tasks: List[TaskResponse]
    total: int
    page: int
    pageSize: int
    totalPages: int


# =============================================================================
# Query Parameters
# =============================================================================

class TaskQueryParams(BaseModel):
    """Query parameters for filtering, searching, and sorting tasks."""
    # Search
    search: Optional[str] = Field(None, description="Search keyword in title/description")
    
    # Filters
    status: Optional[Status] = Field(None, description="Filter by status")
    priority: Optional[Priority] = Field(None, description="Filter by priority")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    
    # Sorting
    sortBy: Optional[str] = Field("createdAt", description="Sort field: createdAt, dueDate, priority")
    sortOrder: Optional[str] = Field("desc", description="Sort order: asc or desc")
    
    # Pagination
    page: int = Field(1, ge=1, description="Page number")
    pageSize: int = Field(10, ge=1, le=100, description="Items per page")
