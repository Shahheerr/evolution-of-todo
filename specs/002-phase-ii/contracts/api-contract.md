# API Contracts: Phase-II Full-Stack Todo Application

## Overview
This document defines the API contracts between the Next.js frontend and FastAPI backend using JWT-based authentication. The contracts specify the endpoints, request/response formats, and authentication requirements.

## Authentication Contract

### JWT Token Exchange
- **Endpoint**: `GET /api/auth/token` (Next.js API route)
- **Purpose**: Convert Better-Auth session to JWT token for backend communication
- **Response**: Raw JWT token string for Authorization header
- **Required**: Same `BETTER_AUTH_SECRET` in both frontend and backend

### Authorization Header Format
- **Header**: `Authorization: Bearer <jwt-token>`
- **Requirement**: All authenticated endpoints require this header
- **Validation**: Backend verifies JWT signature using `BETTER_AUTH_SECRET`
- **Failure**: 401 Unauthorized response for invalid tokens

## API Endpoints

### Health Check
```
GET /
```

**Description**: Health check endpoint
**Authentication**: None required
**Response**: 200 OK with status message

### Protected Task Endpoints

#### Get User's Tasks
```
GET /tasks
```

**Description**: Retrieve all tasks belonging to the authenticated user
**Authentication**: Required (JWT Bearer token)
**Query Parameters**:
- `status` (optional): Filter by task status (PENDING, IN_PROGRESS, COMPLETED)
- `priority` (optional): Filter by priority (HIGH, MEDIUM, LOW)
- `limit` (optional): Limit number of results
- `offset` (optional): Offset for pagination
**Response**: 200 OK with array of Task objects
**Response Schema**:
```json
[
  {
    "id": "string",
    "title": "string",
    "description": "string",
    "completed": "boolean",
    "priority": "string",
    "status": "string",
    "userId": "string",
    "createdAt": "datetime",
    "updatedAt": "datetime"
  }
]
```

#### Create Task
```
POST /tasks
```

**Description**: Create a new task for the authenticated user
**Authentication**: Required (JWT Bearer token)
**Request Body**:
```json
{
  "title": "string (required)",
  "description": "string (optional)",
  "priority": "string (optional, default: MEDIUM)",
  "status": "string (optional, default: PENDING)"
}
```
**Response**: 201 Created with created Task object
**Response Schema**:
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "completed": "boolean",
  "priority": "string",
  "status": "string",
  "userId": "string",
  "createdAt": "datetime",
  "updatedAt": "datetime"
}
```

#### Get Specific Task
```
GET /tasks/{task_id}
```

**Description**: Retrieve a specific task by ID
**Authentication**: Required (JWT Bearer token)
**Parameters**: `task_id` (path parameter)
**Response**: 200 OK with Task object or 404 Not Found
**Response Schema**:
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "completed": "boolean",
  "priority": "string",
  "status": "string",
  "userId": "string",
  "createdAt": "datetime",
  "updatedAt": "datetime"
}
```

#### Update Task
```
PUT /tasks/{task_id}
```

**Description**: Update an existing task
**Authentication**: Required (JWT Bearer token)
**Parameters**: `task_id` (path parameter)
**Request Body** (all fields optional):
```json
{
  "title": "string (optional)",
  "description": "string (optional)",
  "completed": "boolean (optional)",
  "priority": "string (optional)",
  "status": "string (optional)"
}
```
**Response**: 200 OK with updated Task object or 404 Not Found
**Response Schema**:
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "completed": "boolean",
  "priority": "string",
  "status": "string",
  "userId": "string",
  "createdAt": "datetime",
  "updatedAt": "datetime"
}
```

#### Delete Task
```
DELETE /tasks/{task_id}
```

**Description**: Delete a specific task
**Authentication**: Required (JWT Bearer token)
**Parameters**: `task_id` (path parameter)
**Response**: 204 No Content or 404 Not Found

#### Toggle Task Completion
```
PATCH /tasks/{task_id}/toggle
```

**Description**: Toggle the completion status of a task
**Authentication**: Required (JWT Bearer token)
**Parameters**: `task_id` (path parameter)
**Response**: 200 OK with updated Task object or 404 Not Found
**Response Schema**:
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "completed": "boolean",
  "priority": "string",
  "status": "string",
  "userId": "string",
  "createdAt": "datetime",
  "updatedAt": "datetime"
}
```

## Error Response Contract

### Standard Error Format
All error responses follow this format:
```json
{
  "detail": "Human-readable error message"
}
```

### Common HTTP Status Codes
- **200 OK**: Successful GET, PUT, PATCH requests
- **201 Created**: Successful POST request
- **204 No Content**: Successful DELETE request
- **400 Bad Request**: Invalid request parameters or body
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Valid token but insufficient permissions
- **404 Not Found**: Requested resource does not exist
- **422 Unprocessable Entity**: Validation error in request data
- **500 Internal Server Error**: Unexpected server error

## Data Model Contracts

### Task Object Properties
| Property | Type | Required | Description |
|----------|------|----------|-------------|
| id | string | Yes | Unique identifier for the task |
| title | string | Yes | Task title (1-255 characters) |
| description | string | No | Optional task description (max 1000 characters) |
| completed | boolean | Yes | Whether the task is completed |
| priority | string | Yes | Task priority (HIGH, MEDIUM, LOW) |
| status | string | Yes | Task status (PENDING, IN_PROGRESS, COMPLETED) |
| userId | string | Yes | Owner user ID (extracted from JWT) |
| createdAt | datetime | Yes | Timestamp of creation |
| updatedAt | datetime | Yes | Timestamp of last update |

### Priority Enum Values
- `HIGH`: Highest priority task
- `MEDIUM`: Medium priority task (default)
- `LOW`: Lowest priority task

### Status Enum Values
- `PENDING`: Task is pending
- `IN_PROGRESS`: Task is in progress
- `COMPLETED`: Task is completed

## Security Contract

### Data Isolation
- Each user can only access tasks with their userId
- Backend extracts userId from JWT sub claim
- All queries filtered by userId from token
- 404 responses for tasks that don't belong to user

### Token Validation
- HS256 algorithm with shared secret
- Expired tokens rejected with 401
- Invalid signature tokens rejected with 401
- Token must contain valid sub claim with user ID

## Performance Contract

### Response Time Expectations
- All endpoints should respond within 200ms under normal load
- Health check should respond within 50ms
- Task operations should complete within 150ms

### Rate Limiting
- API endpoints may implement rate limiting (TBD)
- Clients should implement appropriate retry logic with exponential backoff