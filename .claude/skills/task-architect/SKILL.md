---
name: task-architect
description: This skill assists with navigating the Phase II Full-Stack Todo Application architecture. USE IT whenever the user asks about project structure, authentication flow, database schema, or how to implement new features within this Monorepo. It ensures strict adherence to the defined specifications.
disable-model-invocation: false
---

# Task Architect Skill

This skill provides expert guidance on the proprietary architecture of the Phase II Todo Application. It serves as the bridge between the high-level specifications and the implementation code.

## 🤖 When to Use This Skill
Active this skill when the user asks about:
1.  **Project Structure**: "Where is the auth logic?", "How are frontend and backend connected?", "Explain the monorepo".
2.  **Authentication**: "How does login work?", "Where is the JWT generated?", "What is the Better-Auth secret?".
3.  **Database**: "Where is the schema?", "How do I add a new table?", "What is the relation between User and Task?".
4.  **Implementation**: "How do I add a new API route?", "Create a new frontend page".

## 📚 Core Knowledge Sources
You are strictly bound by the `specs/` directory.
- **Architecture**: `specs/architecture/system-overview.md`
- **Authentication**: `specs/better-auth/server-config.md` & `specs/backend-fastapi/security-dependency.md`
- **Database**: `specs/database-prisma/schema-definition.md`
- **Frontend**: `specs/frontend-nextjs/api-client.md`

## 🛠️ Implementation Protocols

### 1. The "Research First" Protocol
Before answering *any* implementation question, you must first read the relevant spec file.
- If asked about **Auth**, read `specs/auth-flow.md` (or equivalent in new structure).
- If asked about **DB**, read `specs/database.md`.

### 2. The "Hallucination Check" Protocol
- **NEVER** suggest installing standard libraries if a custom implementation exists (e.g., standard Better-Auth plugins are BANNED; use Manual JWT).
- **NEVER** suggest using `pip`. ALWAYS use `uv`.
- **NEVER** suggest direct DB calls in Client Components.

## 🚀 Common Workflows

### Workflow A: Adding a New Backend Feature
1.  **Define Model**: Create Pydantic schema in `backend/app/models/`.
2.  **Define Route**: Create route in `backend/app/routes/`.
3.  **Inject Security**: Use `Depends(get_current_user)` for ALL protected routes.
4.  **Isolate Data**: Filter by `current_user.id`.

### Workflow B: Adding a New Frontend Page
1.  **Create Page**: `frontend/app/new-page/page.tsx`.
2.  **Auth Guard**: Use `useSession()` or Middleware.
3.  **Fetch Data**: Use `lib/api.ts` (Typed Wrapper).
4.  **Render**: Use Tailwind components.

## ⚠️ Critical Constraints
1.  **Port 3000** (Frontend) <-> **Port 8000** (Backend).
2.  `BETTER_AUTH_SECRET` must be identical in both `.env` files.
3.  Frontend `schema.prisma` is the **MASTER**. Backend follows.

## 🧪 Verification
After generating code, ask yourself:
1.  Did I usage `uv` for Python?
2.  Did I use `Authorization: Bearer`?
3.  Did I filter SQL by `userId`?
