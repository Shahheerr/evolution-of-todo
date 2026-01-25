"""
Todo Model
==========

Data model for Todo items with proper dataclass structure
for clean, type-safe task representation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Todo:
    """
    Represents a single Todo item with all its properties.

    Attributes:
        id: Unique identifier for the task (auto-generated UUID)
        title: The main title/name of the task
        description: Optional detailed description
        completed: Whether the task is marked as complete
        created_at: Timestamp when the task was created
        updated_at: Timestamp when the task was last modified
    """

    title: str
    description: str = ""
    completed: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def mark_complete(self) -> None:
        """Mark the task as complete."""
        self.completed = True
        self.updated_at = datetime.now()

    def mark_incomplete(self) -> None:
        """Mark the task as incomplete."""
        self.completed = False
        self.updated_at = datetime.now()

    def toggle_status(self) -> None:
        """Toggle the completion status of the task."""
        self.completed = not self.completed
        self.updated_at = datetime.now()

    def update(self, title: Optional[str] = None, description: Optional[str] = None) -> None:
        """
        Update task details.

        Args:
            title: New title for the task (optional)
            description: New description for the task (optional)
        """
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert the Todo to a dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Todo":
        """Create a Todo instance from a dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            completed=data.get("completed", False),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )