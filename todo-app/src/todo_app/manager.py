"""
Todo Manager - Core business logic for managing Todo items.
"""

from typing import List, Optional, Tuple
from .models import Todo
from .storage import TodoStorage


class TodoManager:
    """Manages Todo items lifecycle and operations."""

    def __init__(self, storage: Optional[TodoStorage] = None):
        self.storage = storage or TodoStorage()
        self.todos: List[Todo] = self.storage.load()

    def add_task(self, title: str, description: str = "") -> Todo:
        """Add a new task."""
        todo = Todo(title=title, description=description)
        self.todos.append(todo)
        self._save()
        return todo

    def delete_task(self, task_id: str) -> Tuple[bool, str]:
        """Delete a task by ID."""
        for i, todo in enumerate(self.todos):
            if todo.id == task_id:
                deleted = self.todos.pop(i)
                self._save()
                return True, f"Task '{deleted.title}' deleted!"
        return False, f"Task ID '{task_id}' not found."

    def update_task(self, task_id: str, title: Optional[str] = None,
                    description: Optional[str] = None) -> Tuple[bool, str]:
        """Update task details."""
        todo = self.get_task_by_id(task_id)
        if todo:
            todo.update(title=title, description=description)
            self._save()
            return True, f"Task '{todo.title}' updated!"
        return False, f"Task ID '{task_id}' not found."

    def toggle_task(self, task_id: str) -> Tuple[bool, str]:
        """Toggle task completion status."""
        todo = self.get_task_by_id(task_id)
        if todo:
            todo.toggle_status()
            self._save()
            status = "complete" if todo.completed else "incomplete"
            return True, f"Task marked as {status}!"
        return False, f"Task ID '{task_id}' not found."

    def get_task_by_id(self, task_id: str) -> Optional[Todo]:
        """Find task by ID."""
        for todo in self.todos:
            if todo.id == task_id:
                return todo
        return None

    def get_all_tasks(self) -> List[Todo]:
        return self.todos

    def get_pending_tasks(self) -> List[Todo]:
        return [t for t in self.todos if not t.completed]

    def get_completed_tasks(self) -> List[Todo]:
        return [t for t in self.todos if t.completed]

    def get_task_count(self) -> Tuple[int, int, int]:
        """Returns (total, completed, pending)."""
        total = len(self.todos)
        completed = len(self.get_completed_tasks())
        return total, completed, total - completed

    def clear_completed_tasks(self) -> Tuple[bool, str]:
        """Delete all completed tasks."""
        count = len(self.todos) - len(self.get_pending_tasks())
        self.todos = self.get_pending_tasks()
        self._save()
        return True, f"Cleared {count} completed task(s)!"

    def _save(self) -> None:
        self.storage.save(self.todos)