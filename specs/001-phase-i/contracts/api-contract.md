# API Contracts: Phase-I Terminal-Based Todo Application

## Overview
This document defines the interface contracts between different layers of the application. Since this is a terminal-based application without a traditional API, these contracts represent the method signatures and expected behaviors between the different architectural layers.

## Layer Contracts

### 1. Model Layer Contract (`models.py`)

#### Todo Class Interface
```python
class Todo:
    def __init__(self, title: str, description: str = "", completed: bool = False) -> None:
        """Initialize a new Todo item."""

    def mark_complete(self) -> None:
        """Mark the task as complete."""

    def mark_incomplete(self) -> None:
        """Mark the task as incomplete."""

    def toggle_status(self) -> None:
        """Toggle the completion status of the task."""

    def update(self, title: Optional[str] = None, description: Optional[str] = None) -> None:
        """Update task details."""

    def to_dict(self) -> dict:
        """Convert the Todo to a dictionary for serialization."""

    @classmethod
    def from_dict(cls, data: dict) -> "Todo":
        """Create a Todo instance from a dictionary."""
```

### 2. Storage Layer Contract (`storage.py`)

#### TodoStorage Class Interface
```python
class TodoStorage:
    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize the storage manager."""

    def save(self, todos: List[Todo]) -> bool:
        """Save all todos to the storage file."""

    def load(self) -> List[Todo]:
        """Load all todos from the storage file."""

    def clear(self) -> bool:
        """Clear all stored tasks."""
```

### 3. Manager Layer Contract (`manager.py`)

#### TodoManager Class Interface
```python
class TodoManager:
    def __init__(self, storage: Optional[TodoStorage] = None):
        """Initialize the manager with optional storage."""

    def add_task(self, title: str, description: str = "") -> Todo:
        """Add a new task."""

    def delete_task(self, task_id: str) -> Tuple[bool, str]:
        """Delete a task by ID."""

    def update_task(self, task_id: str, title: Optional[str] = None,
                   description: Optional[str] = None) -> Tuple[bool, str]:
        """Update task details."""

    def toggle_task(self, task_id: str) -> Tuple[bool, str]:
        """Toggle task completion status."""

    def get_task_by_id(self, task_id: str) -> Optional[Todo]:
        """Find task by ID."""

    def get_all_tasks(self) -> List[Todo]:
        """Get all tasks."""

    def get_pending_tasks(self) -> List[Todo]:
        """Get pending tasks only."""

    def get_completed_tasks(self) -> List[Todo]:
        """Get completed tasks only."""

    def get_task_count(self) -> Tuple[int, int, int]:
        """Get task counts (total, completed, pending)."""

    def clear_completed_tasks(self) -> Tuple[bool, str]:
        """Delete all completed tasks."""
```

### 4. UI Layer Contract (`ui.py`)

#### TodoUI Class Interface
```python
class TodoUI:
    def __init__(self, manager: Optional[TodoManager] = None):
        """Initialize the UI with optional manager."""

    def run(self) -> None:
        """Start the main application loop."""

    def display_tasks_table(self, todos: List[Todo], title: str = "Your Tasks") -> None:
        """Display tasks in a formatted table."""

    def display_success(self, message: str) -> None:
        """Display a success message."""

    def display_error(self, message: str) -> None:
        """Display an error message."""

    def display_info(self, message: str) -> None:
        """Display an informational message."""
```

## User Interaction Contracts

### Menu Options Contract
- **Option 0**: Exit the application
- **Option 1**: Add new task
- **Option 2**: View all tasks
- **Option 3**: Update task
- **Option 4**: Delete task
- **Option 5**: Toggle task completion
- **Option 6**: View pending tasks only
- **Option 7**: View completed tasks only
- **Option 8**: Clear completed tasks

### Error Handling Contract
- All error messages are displayed in red panels
- All success messages are displayed in green panels
- All warnings are displayed in yellow panels
- Invalid inputs trigger appropriate error messages

## Data Persistence Contract
- Tasks are saved to `~/.todo_app/tasks.json` automatically
- Data is saved after every modification operation
- File is created with proper directory structure if it doesn't exist
- JSON format includes version information for future compatibility