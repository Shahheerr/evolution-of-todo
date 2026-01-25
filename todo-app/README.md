# Todo App - A Beautiful Terminal-Based Task Manager

A modern, elegant terminal application for managing your daily tasks with rich formatting, beautiful UI, and intuitive interactions.

## Features

- 📋 Beautiful terminal interface using Rich library
- ✅ Add, view, update, and delete tasks
- 🔄 Toggle task completion status
- 📊 View pending and completed tasks separately
- 🧹 Bulk clear completed tasks
- 💾 Persistent storage with JSON files
- 🌈 Colorful, visually appealing design
- ⌨️ Intuitive keyboard-driven navigation

## Requirements

- Python 3.13+
- UV package manager

## Installation

1. Clone or download the repository
2. Install UV package manager if not already installed
3. Navigate to the project directory
4. Install dependencies:

```bash
cd todo-app
uv sync
```

## Usage

Run the application with:

```bash
uv run main.py
```

Or if you've set up the script in pyproject.toml:

```bash
uv run todo
```

## Menu Options

- `1` - Add new task
- `2` - View all tasks
- `3` - Update task
- `4` - Delete task
- `5` - Toggle task completion
- `6` - View pending tasks only
- `7` - View completed tasks only
- `8` - Clear completed tasks
- `0` - Exit

## Architecture

The application follows a clean architecture pattern:

- **Models**: Data classes representing Todo entities
- **Storage**: JSON file persistence layer
- **Manager**: Business logic (CRUD operations)
- **UI**: Rich-based terminal interface

## License

MIT