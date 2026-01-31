# FastAPI Security & Data Isolation

## 1. Security Dependency (`app/core/security.py`)
**Prompt Directive**: "Implement a strict dependency that intercepts every request, validates the JWT signature, and returns a Pydantic User object."

### **Validation Logic**
1.  **Extract**: Get `Authorization: Bearer <token>` header.
2.  **Decode**: Use `jwt.decode` (PyJWT library).
3.  **Verify**:
    - Key: `settings.BETTER_AUTH_SECRET`
    - Algorithms: `["HS256"]`
    - Claims: `exp` (Expiration)
4.  **Error Handling**:
    - `ExpiredSignatureError` -> 401 "Token expired"
    - `InvalidTokenError` -> 401 "Invalid token"

```python
# CRITICAL IMPLEMENTATION
def verify_jwt_token(token: str) -> TokenPayload:
    payload = jwt.decode(
        token,
        settings.BETTER_AUTH_SECRET,
        algorithms=["HS256"],
        options={"verify_exp": True} # Do NOT verify aud/iss
    )
    return TokenPayload(**payload)
```

## 2. Data Isolation Strategy (Row Level Security via App Logic)
**Prompt Directive**: "The Backend is stateless. It relies 100% on the `sub` claim in the JWT to identify the data owner. You MUST filter every query."

### **The Golden Rule of CRUD**
Every single database query in `app/routes/tasks.py` MUST contain the user filter.

**CORRECT:**
```python
query = "SELECT * FROM task WHERE id = $1 AND \"userId\" = $2"
await db.fetchrow(query, task_id, current_user.id)
```

**FORBIDDEN (Security Vulnerability):**
```python
# DO NOT DO THIS
query = "SELECT * FROM task WHERE id = $1" 
await db.fetchrow(query, task_id) 
```

## 3. Pydantic Models (`app/models/task.py`)
Ensure strict validation of input data BEFORE it touches the database.
- `TaskCreate`: Title, Description, Status, Priority.
- `TaskResponse`: Must include `userId` to verify ownership in responses.
