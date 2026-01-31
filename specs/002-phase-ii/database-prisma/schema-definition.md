# Database Schema & Migration Strategy

## 1. Schema Definition (`schema.prisma`)
**Context**: This file is located in `frontend/prisma/schema.prisma`. It controls the Neon Postgres instance.

### **Core Systems**
1.  **Identity System** (Better-Auth specific):
    - `User`, `Session`, `Account`, `Verification`.
    - These tables are rigid. Do not modify fields required by Better-Auth.
2.  **Business System** (Todo App):
    - `Task` model.
    - `Priority` (Enum: HIGH, MEDIUM, LOW).
    - `TaskStatus` (Enum: PENDING, IN_PROGRESS, COMPLETED).

### **Relations**
- **User -> Task**: One-to-Many (`User` has `tasks Task[]`).
- **Cascade Delete**: If a User is deleted, their Tasks MUST be deleted (`onDelete: Cascade`).

## 2. Migration & Push Strategy
**Prompt Directive**: "Only use `db push` for rapid prototyping. Use `migrate dev` for production-like changes."

### **Commands**
- **Apply Changes**: `npx prisma db push` (Use this for this Hackathon phase).
- **Generate Client**: `npx prisma generate` (Run this after ANY schema change).
- **Studio**: `npx prisma studio` (View data).

## 3. Neon Database Configuration
- **Connection String**: Provided via `DATABASE_URL` in `.env`.
- **Pooling**: Use the pooled connection string (`-pooler`) for serverless environments if available, though direct connection is fine for the persistent Backend server.

## 4. Constraint Rules
- **Foreign Keys**: Always use `@relation` attributes.
- **Indexes**: Index `userId` on the `Task` table (`@@index([userId])`) for performance.
- **Defaults**: Use `@default(cuid())` for IDs and `@default(now())` for timestamps.
