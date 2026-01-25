"""
Todo Storage Manager
====================

Handles persistence of Todo items to a JSON file,
providing save and load functionality for task data.
"""

import json
import os
from pathlib import Path
from typing import List, Optional

from .models import Todo


# Default storage location in user's home directory
DEFAULT_STORAGE_FILE = Path.home() / ".todo_app" / "tasks.json"


class TodoStorage:
    """
    Manages the persistence of Todo items to a JSON file.

    This class handles:
    - Creating storage directory if needed
    - Saving tasks to JSON
    - Loading tasks from JSON
    - Error handling for file operations
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize the storage manager.

        Args:
            storage_path: Custom path for the storage file.
                         Defaults to ~/.todo_app/tasks.json
        """
        self.storage_path = storage_path or DEFAULT_STORAGE_FILE
        self._ensure_storage_directory()

    def _ensure_storage_directory(self) -> None:
        """Create the storage directory if it doesn't exist."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, todos: List[Todo]) -> bool:
        """
        Save all todos to the storage file.

        Args:
            todos: List of Todo items to save

        Returns:
            True if save was successful, False otherwise
        """
        try:
            data = {
                "version": "1.0",
                "tasks": [todo.to_dict() for todo in todos]
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except (IOError, OSError) as e:
            print(f"Error saving tasks: {e}")
            return False

    def load(self) -> List[Todo]:
        """
        Load all todos from the storage file.

        Returns:
            List of Todo items from storage, or empty list if file doesn't exist
        """
        if not self.storage_path.exists():
            return []

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            tasks_data = data.get("tasks", [])
            return [Todo.from_dict(task) for task in tasks_data]
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading tasks: {e}")
            return []

    def clear(self) -> bool:
        """
        Clear all stored tasks.

        Returns:
            True if clear was successful, False otherwise
        """
        try:
            if self.storage_path.exists():
                self.storage_path.unlink()
            return True
        except OSError as e:
            print(f"Error clearing tasks: {e}")
            return False