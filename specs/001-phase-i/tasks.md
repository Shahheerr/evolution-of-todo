# Tasks: Phase-I Terminal-Based Todo Application

## Feature Overview
Implementation of Phase-I: Terminal-Based Todo Application with beautiful Rich UI, following clean architecture principles (Model-Storage-Manager-UI pattern). The application provides comprehensive task management capabilities with persistent JSON storage, supporting all CRUD operations in an aesthetically pleasing terminal interface. Built with Python 3.13+, UV package manager, and Rich library for cross-platform compatibility.

## Dependencies
- Python 3.13+
- UV package manager
- Rich library (14.x+)
- Standard Python libraries: dataclasses, datetime, json, pathlib, uuid, typing

## Parallel Execution Examples
- T001-T003 can be executed in parallel (project setup tasks)
- T008-T012 can be executed in parallel (different module implementations)
- T015-T020 can be executed in parallel (UI components)

## Implementation Strategy
- MVP First: Implement minimal functionality (add/view tasks) to establish architecture
- Incremental Delivery: Add features progressively (update/delete/toggle)
- Test Early: Implement error handling and persistence early in the process

---

## Phase 1: Setup and Project Initialization

### Goal
Create the project structure and configure dependencies to support the terminal-based todo application.

### Independent Test Criteria
- Project can be created with UV
- Dependencies can be installed
- Basic project structure is in place

- [X] T001 Create project directory and initialize with UV
- [X] T002 Configure pyproject.toml with required dependencies and metadata
- [X] T003 Create src directory structure (src/todo_app/)

---

## Phase 2: Foundational Components

### Goal
Implement the foundational components that all user stories depend on: the Todo data model and storage layer.

### Independent Test Criteria
- Todo model can be instantiated with required fields
- Storage layer can save and load tasks to/from JSON
- Both components follow the interface contracts defined in the plan

- [X] T004 [P] Create Todo dataclass with all required fields and methods in src/todo_app/models.py
- [X] T005 [P] Create package initialization file in src/todo_app/__init__.py
- [X] T006 [P] Create TodoStorage class with save/load/clear functionality in src/todo_app/storage.py
- [X] T007 [P] Implement helper functions and constants (colors, icons) in src/todo_app/models.py

---

## Phase 3: [US1] Core Task Management - Add and View Tasks

### Goal
Implement the ability for users to add new tasks and view all tasks (Scenario 1: New User Experience)

### Independent Test Criteria
- User can add tasks with title and description (REQ-001)
- User can view all tasks in a formatted table (REQ-002)
- Tasks persist between application sessions (REQ-009, REQ-010)

### Tests (if requested)
- [X] T008 [P] [US1] Create unit tests for Todo model functionality in tests/unit/test_models.py
- [X] T009 [P] [US1] Create unit tests for storage functionality in tests/unit/test_storage.py

### Implementation
- [X] T010 [P] [US1] Create TodoManager class with add_task and get_all_tasks methods in src/todo_app/manager.py
- [X] T011 [P] [US1] Implement UI header display with ASCII logo in src/todo_app/ui.py
- [X] T012 [P] [US1] Implement UI task table display functionality in src/todo_app/ui.py
- [X] T013 [US1] Create main application entry point with basic loop in main.py
- [X] T014 [US1] Integrate all components and test add/view functionality

---

## Phase 4: [US2] Task Modification - Update and Toggle

### Goal
Implement the ability for users to update existing tasks and toggle completion status (Scenario 2: Daily Task Management)

### Independent Test Criteria
- User can update task details by ID (REQ-003)
- User can toggle task completion status by ID (REQ-005)
- Updated tasks are properly persisted (REQ-009)

### Tests (if requested)
- [X] T015 [P] [US2] Create unit tests for manager update functionality in tests/unit/test_manager.py
- [X] T016 [P] [US2] Create unit tests for task completion toggling in tests/unit/test_manager.py

### Implementation
- [X] T017 [P] [US2] Add update_task method to TodoManager in src/todo_app/manager.py
- [X] T018 [P] [US2] Add toggle_task method to TodoManager in src/todo_app/manager.py
- [X] T019 [P] [US2] Implement UI update task functionality in src/todo_app/ui.py
- [X] T020 [P] [US2] Implement UI toggle task functionality in src/todo_app/ui.py
- [X] T021 [US2] Integrate update/toggle functionality and test

---

## Phase 5: [US3] Task Deletion and Filtering

### Goal
Implement the ability for users to delete tasks and filter views (Scenario 3: Task Organization)

### Independent Test Criteria
- User can delete individual tasks by ID (REQ-004)
- User can view only pending tasks (REQ-006)
- User can view only completed tasks (REQ-007)
- User can bulk delete completed tasks (REQ-008)

### Tests (if requested)
- [X] T022 [P] [US3] Create unit tests for delete functionality in tests/unit/test_manager.py
- [X] T023 [P] [US3] Create unit tests for filtering functionality in tests/unit/test_manager.py

### Implementation
- [X] T024 [P] [US3] Add delete_task method to TodoManager in src/todo_app/manager.py
- [X] T025 [P] [US3] Add filtering methods (get_pending_tasks, get_completed_tasks) to TodoManager in src/todo_app/manager.py
- [X] T026 [P] [US3] Add clear_completed_tasks method to TodoManager in src/todo_app/manager.py
- [X] T027 [P] [US3] Implement UI delete task functionality in src/todo_app/ui.py
- [X] T028 [P] [US3] Implement UI filter view functionality in src/todo_app/ui.py
- [X] T029 [US3] Implement UI clear completed functionality in src/todo_app/ui.py
- [X] T030 [US3] Integrate deletion/filtering functionality and test

---

## Phase 6: [US4] Enhanced UI and User Experience

### Goal
Implement enhanced UI features including menus, error handling, and visual indicators (completes all usability acceptance criteria)

### Independent Test Criteria
- Application presents clear, intuitive menu system (usability acceptance)
- Visual indicators clearly distinguish completed vs pending tasks (REQ-016)
- Error messages are informative and styled appropriately (REQ-018)
- Navigation between screens is logical and predictable (usability acceptance)
- Application provides clear feedback for all user actions (usability acceptance)

### Tests (if requested)
- [X] T031 [P] [US4] Create UI integration tests in tests/integration/test_ui_integration.py

### Implementation
- [X] T032 [P] [US4] Implement main menu display with options in src/todo_app/ui.py
- [X] T033 [P] [US4] Implement UI input handlers (get_menu_choice, get_task_input, etc.) in src/todo_app/ui.py
- [X] T034 [P] [US4] Implement styled success/error/info message displays in src/todo_app/ui.py
- [X] T035 [P] [US4] Implement confirmation prompts for destructive actions in src/todo_app/ui.py
- [X] T036 [P] [US4] Implement screen clearing functionality in src/todo_app/ui.py
- [X] T037 [P] [US4] Implement task statistics display in src/todo_app/ui.py
- [X] T038 [US4] Complete full application workflow with all menu options
- [X] T039 [US4] Test complete user flows from all scenarios

---

## Phase 7: Polish and Cross-Cutting Concerns

### Goal
Complete the application by implementing remaining requirements and polish features.

### Independent Test Criteria
- Application handles keyboard interrupts gracefully (REQ-022)
- All datetime functionality works correctly (REQ-012)
- Tasks are stored in correct location with proper structure (REQ-013)
- All requirements from the specification are implemented

### Implementation
- [X] T040 Implement keyboard interrupt handling in main application loop
- [X] T041 Add proper datetime handling and validation to Todo model
- [X] T042 Ensure tasks are stored at ~/.todo_app/tasks.json as required
- [X] T043 Add proper error handling throughout all layers
- [X] T044 Add comprehensive docstrings to all classes and methods
- [X] T045 Add type hints to all functions and methods
- [X] T046 Test cross-platform compatibility (Windows, macOS, Linux)
- [X] T047 Final integration testing and bug fixes
- [X] T048 Update README.md with usage instructions