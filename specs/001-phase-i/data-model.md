# Data Model: Phase-I Terminal-Based Todo Application

## Todo Entity

### Fields
- **id** (str): Unique 8-character identifier (truncated UUID)
  - Auto-generated on creation
  - Immutable after creation
  - Required field

- **title** (str): Task title/description
  - Required field
  - Minimum 1 character
  - Maximum 255 characters (practical limit)

- **description** (str): Optional detailed task description
  - Default: empty string
  - Optional field
  - Maximum 1000 characters (practical limit)

- **completed** (bool): Completion status indicator
  - Default: False
  - Tracks whether task is completed
  - Can be toggled by user

- **created_at** (datetime): Timestamp of creation
  - Auto-set on creation
  - Immutable after creation
  - ISO format for JSON serialization

- **updated_at** (datetime): Timestamp of last modification
  - Auto-updated on any modification
  - Changes when title, description, or completion status is modified
  - ISO format for JSON serialization

### Validations
- Title must not be empty or whitespace-only
- ID must be unique within the collection
- created_at must be before or equal to updated_at
- All datetime fields use ISO 8601 format for JSON serialization

### State Transitions
- **Initial State**: completed = False
- **Complete**: completed → True (via toggle or update)
- **Incomplete**: completed → False (via toggle or update)

## Todo Collection

### Operations
- **Add**: Insert new Todo with auto-generated ID and current timestamp
- **Retrieve**: Find by unique ID
- **Update**: Modify title, description, or completion status
- **Delete**: Remove by unique ID
- **Filter**: Retrieve subsets (completed, pending, all)
- **Count**: Get totals (all, completed, pending)

### Persistence Model
- **Storage Format**: JSON file with version header
- **File Location**: ~/.todo_app/tasks.json (user home directory)
- **Schema Version**: Fixed at "1.0" for this phase
- **Data Structure**:
```json
{
  "version": "1.0",
  "tasks": [
    {
      "id": "abc12345",
      "title": "Task title",
      "description": "Optional description",
      "completed": false,
      "created_at": "2025-01-24T23:00:00",
      "updated_at": "2025-01-24T23:00:00"
    }
  ]
}
```

## Relationships
- Todos exist as independent entities with no direct relationships
- Collection maintains list of todos for aggregation operations
- Timestamp relationships: created_at ≤ updated_at (always)

## Indexes/Access Patterns
- Primary lookup by ID (hash map for O(1) access)
- Filter operations by completion status (for viewing subsets)
- Sequential access for display in tables