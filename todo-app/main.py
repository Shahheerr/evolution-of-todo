#!/usr/bin/env python3
"""
Todo App - A Beautiful Terminal-Based Task Manager
===================================================

Run with: uv run main.py

Features:
    - Add tasks with title and description
    - View all tasks with status indicators
    - Update task details
    - Delete tasks by ID
    - Mark tasks as complete/incomplete
    - Beautiful, colorful terminal interface
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from todo_app.ui import TodoUI, main


if __name__ == "__main__":
    main()