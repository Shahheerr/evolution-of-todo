# BACKEND CONTEXT & RULES (FastAPI)

## Tech Stack
- **Framework**: FastAPI.
- **Language**: Python 3.13+.
- **Package Manager**: `uv` (STRICT).
- **Database**: PostgreSQL (Neon).
- **ORM/Driver**: Prisma Client Python (preferred) OR AsyncPG with strict typing.

## Package Management (UV STRICT)
You are FORBIDDEN from using `pip install`.
- **Add Dependency**: `uv add <package_name>`
- **Run App**: `uv run uvicorn app.main:app --reload`
- **Sync**: `uv sync`

## Authentication & Security
1.  **JWT Dependency**: You must implement a `get_current_user` dependency in `app/core/security.py`.
2.  **Validation**:
    - Decode JWT using `BETTER_AUTH_SECRET` (from `.env`).
    - Algorithm: HS256.
    - Validate `exp` (Expiration).
3.  **Data Isolation**:
    - Extract `user_id` from the token `sub` claim.
    - **CRITICAL**: Every database query for Tasks must include `.where(userId=current_user.id)`. Failing to filter by user ID is a catastrophic security failure.

## Database Interaction (Prisma Python)
1.  If using Prisma Client Python:
    - Ensure `prisma` CLI is available.
    - Register the client in `app/core/db.py`.
2.  **Schema Sync**: The Backend treats the database schema as given. Do not run migrations from the backend unless explicitly instructed. Assume the Frontend/Root `schema.prisma` is the source of truth.

## Code Style
- Use Pydantic models for ALL schemas (Request & Response).
- Use Python Type Hints (`def my_func() -> str:`).
- Keep routes in `app/routes/`.
- Keep core config in `app/core/`.

## Commands
- Start Server: `uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- Add Pydantic: `uv add pydantic`
