# Quickstart Guide: Phase-I Terminal-Based Todo Application

## Prerequisites

- Python 3.13+
- UV package manager installed

## Installation

1. **Clone or create the project:**
```bash
uv init todo-app
cd todo-app
```

2. **Install dependencies:**
```bash
uv add rich
```

3. **Create the project structure:**
```bash
mkdir -p src/todo_app
```

4. **Update pyproject.toml:**
```toml
[project]
name = "todo-app"
version = "1.0.0"
description = "A beautiful terminal-based Todo application with rich UI"
readme = "README.md"
requires-python = ">=3.13"
authors = [
    {name = "Todo App Team", email = "todo@example.com"}
]
keywords = ["todo", "task", "terminal", "cli", "rich", "productivity"]
dependencies = [
    "rich>=14.3.0",
]

[project.scripts]
todo = "todo_app.ui:main"
```

## File Creation Order

Follow this exact order to ensure proper dependencies:

### 1. Create `src/todo_app/__init__.py`
```python
"""
Todo App - A Beautiful Terminal-Based Task Manager
=================================================

A modern, elegant terminal application for managing your daily tasks
with rich formatting, beautiful UI, and intuitive interactions.

Author: Todo App Team
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Todo App Team"
```

### 2. Create `src/todo_app/models.py`
Contains the Todo dataclass with all required fields and methods.

### 3. Create `src/todo_app/storage.py`
Contains the TodoStorage class for JSON persistence.

### 4. Create `src/todo_app/manager.py`
Contains the TodoManager class with all business logic.

### 5. Create `src/todo_app/ui.py`
Contains the TodoUI class with Rich-based terminal interface.

### 6. Update `main.py` in project root
Contains the entry point for the application.

## Running the Application

```bash
# Run the application
uv run main.py

# Or if you set up the script in pyproject.toml:
uv run todo
```

## Key Features Access

- **Add Task**: Press `1` in the main menu
- **View All Tasks**: Press `2` in the main menu
- **Update Task**: Press `3` in the main menu
- **Delete Task**: Press `4` in the main menu
- **Toggle Complete**: Press `5` in the main menu
- **View Pending Only**: Press `6` in the main menu
- **View Completed Only**: Press `7` in the main menu
- **Clear Completed**: Press `8` in the main menu
- **Exit**: Press `0` in the main menu

## Data Storage

Tasks are automatically saved to:
- **Location**: `~/.todo_app/tasks.json`
- **Format**: JSON with versioning
- **Persistence**: Saved after every modification

## Troubleshooting

- **ModuleNotFoundError**: Ensure `sys.path.insert(0, 'src')` is in main.py
- **Rich not found**: Run `uv add rich` to install the dependency
- **Emojis not showing**: Use a modern terminal that supports Unicode
- **Colors not appearing**: Some terminals may not support 256-color mode