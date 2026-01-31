# Data Model: Phase-II Full-Stack Todo Application

## User Entity

### Fields
- **id** (String): Unique identifier (cuid)
  - Auto-generated on creation
  - Immutable after creation
  - Primary key in database
  - Required field

- **email** (String): User's email address
  - Required field
  - Unique constraint
  - Valid email format
  - Lowercase normalized

- **name** (String): User's display name
  - Required field
  - Maximum 100 characters
  - Can be updated by user

- **createdAt** (DateTime): Timestamp of account creation
  - Auto-set on creation
  - Immutable after creation
  - ISO format for API responses

- **updatedAt** (DateTime): Timestamp of last modification
  - Auto-updated on any modification
  - ISO format for API responses

### Validations
- Email must be valid email format
- Email must be unique across all users
- Name must not be empty or whitespace-only
- All datetime fields use ISO 8601 format for API responses

## Task Entity

### Fields
- **id** (String): Unique identifier (cuid)
  - Auto-generated on creation
  - Immutable after creation
  - Primary key in database
  - Required field

- **title** (String): Task title/description
  - Required field
  - Maximum 255 characters
  - Minimum 1 character

- **description** (String): Optional detailed task description
  - Default: empty string
  - Optional field
  - Maximum 1000 characters

- **completed** (Boolean): Completion status indicator
  - Default: False
  - Tracks whether task is completed
  - Can be toggled by user

- **priority** (Enum: "HIGH"|"MEDIUM"|"LOW"): Task importance level
  - Default: "MEDIUM"
  - Required field
  - Affects sorting and display

- **status** (Enum: "PENDING"|"IN_PROGRESS"|"COMPLETED"): Task state
  - Default: "PENDING"
  - Required field
  - More granular than just completed flag

- **userId** (String): Foreign key linking to owner user
  - Required field
  - References User.id
  - Enforced by foreign key constraint

- **createdAt** (DateTime): Timestamp of task creation
  - Auto-set on creation
  - Immutable after creation
  - ISO format for API responses

- **updatedAt** (DateTime): Timestamp of last modification
  - Auto-updated on any modification
  - ISO format for API responses

### Validations
- Title must not be empty or whitespace-only
- userId must reference an existing user
- priority must be one of the allowed enum values
- status must be one of the allowed enum values
- All datetime fields use ISO 8601 format for API responses

### State Transitions
- **Initial State**: status = "PENDING", completed = False
- **Progress**: status → "IN_PROGRESS" (via update)
- **Complete**: status → "COMPLETED", completed → True (via update)
- **Reopen**: status → "PENDING", completed → False (via update)

## Session Entity

### Fields
- **id** (String): Unique identifier (cuid)
  - Auto-generated on creation
  - Immutable after creation
  - Primary key in database
  - Required field

- **userId** (String): Foreign key linking to user
  - Required field
  - References User.id
  - Enforced by foreign key constraint

- **expiresAt** (DateTime): Timestamp when session expires
  - Required field
  - Set to future time on creation
  - ISO format for database storage

- **createdAt** (DateTime): Timestamp of session creation
  - Auto-set on creation
  - Immutable after creation
  - ISO format for database storage

### Validations
- userId must reference an existing user
- expiresAt must be in the future
- All datetime fields use ISO 8601 format for API responses

## Relationships

### User ↔ Task
- **Relationship**: One-to-Many (User has many Tasks)
- **Cardinality**: 1 User → 0..N Tasks
- **Constraint**: Cascade delete (Tasks deleted when User deleted)
- **Access Pattern**: User.tasks[] for all user's tasks
- **Database**: Foreign key on Task.userId pointing to User.id

### User ↔ Session
- **Relationship**: One-to-Many (User has many Sessions)
- **Cardinality**: 1 User → 0..N Sessions
- **Constraint**: Cascade delete (Sessions deleted when User deleted)
- **Access Pattern**: User.sessions[] for all user's active sessions
- **Database**: Foreign key on Session.userId pointing to User.id

## Database Schema (Prisma)

```prisma
// User model
model User {
  id          String   @id @default(cuid())
  email       String   @unique @map("email_address")
  name        String   @map("display_name")
  createdAt   DateTime @default(now()) @map("created_at")
  updatedAt   DateTime @default(now()) @updatedAt @map("updated_at")

  // Relations
  tasks     Task[]
  sessions  Session[]

  @@map("users")
}

// Task model
model Task {
  id          String   @id @default(cuid())
  title       String   @map("task_title")
  description String?  @map("task_description")
  completed   Boolean  @default(false) @map("is_completed")
  priority    Priority @default(MEDIUM) @map("task_priority")
  status      TaskStatus @default(PENDING) @map("task_status")
  userId      String   @map("user_id")
  createdAt   DateTime @default(now()) @map("created_at")
  updatedAt   DateTime @default(now()) @updatedAt @map("updated_at")

  // Relations
  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("tasks")
  @@index([userId])
}

// Session model
model Session {
  id        String   @id @default(cuid())
  userId    String   @map("user_id")
  expiresAt DateTime @map("expires_at")
  createdAt DateTime @default(now()) @map("created_at")

  // Relations
  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("sessions")
  @@index([userId])
}

// Enums
enum Priority {
  HIGH
  MEDIUM
  LOW
}

enum TaskStatus {
  PENDING
  IN_PROGRESS
  COMPLETED
}
```

## Indexes and Performance

### Primary Indexes
- User.id (clustered index)
- Task.id (clustered index)
- Session.id (clustered index)

### Secondary Indexes
- User.email (unique index for fast lookups)
- Task.userId (for user-specific queries)
- Task.createdAt (for chronological ordering)
- Session.expiresAt (for cleanup operations)

### Query Patterns
- **User Tasks**: SELECT * FROM Task WHERE userId = ? ORDER BY createdAt DESC
- **Task Filtering**: SELECT * FROM Task WHERE userId = ? AND status = ?
- **Session Lookup**: SELECT * FROM Session WHERE id = ? AND expiresAt > NOW()
- **User Lookup**: SELECT * FROM User WHERE email = ?

## API Data Models (Pydantic)

### Request Models
```python
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Complete project documentation",
                "description": "Write comprehensive docs for the API",
                "priority": "HIGH",
                "status": "PENDING"
            }
        }

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[Priority] = None
    status: Optional[TaskStatus] = None
```

### Response Models
```python
class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    completed: bool
    priority: Priority
    status: TaskStatus
    userId: str
    createdAt: datetime
    updatedAt: datetime
```

## Data Validation Rules

### Business Logic Constraints
- Users can only access/modify their own tasks
- Task titles must be between 1-255 characters
- Descriptions must be under 1000 characters
- Completed tasks should have status "COMPLETED"
- Task status should align with completed boolean flag
- Sessions automatically expire after defined duration