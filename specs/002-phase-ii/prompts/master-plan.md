# Master Plan & Implementation Prompts

## 1. The "Meta-Prompt" for AI Agents
When initializing a new chat with an AI coder (like Claude Code), paste this entire block first:

> "You are acting as a Senior Full-Stack Engineer implementing Phase II of the Todo Monorepo.
> **Constraint 1**: You MUST read the `specs/` directory before writing code.
> **Constraint 2**: You MUST use the `context7` MCP tool to verify library syntax.
> **Constraint 3**: Use `uv` for Python and `npm` for Node.
> **Constraint 4**: Follow the directory structure in `specs/architecture/system-overview.md` exactly.
>
> **Current Task**: [Insert Task Here]"

## 2. Implementation Checklist
Use this checklist to ensure completeness.

### **Phase A: Foundation**
- [ ] Verify `frontend/prisma/schema.prisma` matches `specs/database-prisma/schema-definition.md`.
- [ ] Verify `.env` files share the same `BETTER_AUTH_SECRET`.
- [ ] Run `npx prisma db push` to sync Neon.

### **Phase B: Backend Core**
- [ ] Initialize `uv` project.
- [ ] Implement `app/core/security.py` with HS256 JWT verification (See `specs/backend-fastapi`).
- [ ] Implement `get_current_user` dependency.
- [ ] Create Pydantic models in `app/models/`.

### **Phase C: Frontend Core**
- [ ] Configure Better-Auth in `lib/auth.ts` (No Plugins!).
- [ ] Implement `/api/auth/token` route (Manual Minting).
- [ ] Build `lib/api.ts` client wrapper.

### **Phase D: Feature Integration**
- [ ] Build Dashboard UI.
- [ ] Connect "Create Task" Form -> `POST /api/tasks`.
- [ ] Connect "List Tasks" -> `GET /api/tasks`.
