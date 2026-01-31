# FRONTEND CONTEXT & RULES (Next.js)

## Tech Stack
- **Framework**: Next.js 16+ (App Router).
- **Language**: TypeScript (Strict Mode).
- **Styling**: TailwindCSS (Utility-first), Lucide-React (Icons).
- **Auth**: Better-Auth (Client & Server components).
- **API Client**: Native `fetch` with strict typing.

## Authentication Rules (Better-Auth)
1.  **Client Setup**: You must create a `lib/auth-client.ts` that exports `signIn`, `signOut`, and `useSession` from `createAuthClient`.
2.  **Middleware**: Protect `/dashboard` routes using Next.js Middleware or Layout guards. Redirect unauthenticated users to `/auth/login`.
3.  **Token Retrieval**:
    - Users authenticate via Better-Auth.
    - You must fetch a signed JWT (for the backend) from your internal API (`/api/auth/token`).
    - **DO NOT** try to read cookies manually to send to the backend. Use the explicit token exchange pattern.

## API Communication Rules
1.  **Authorization Header**: Every request to the FastAPI backend MUST include:
    `Authorization: Bearer <valid_jwt_token>`
2.  **Base URL**: Use environment variables (`NEXT_PUBLIC_API_URL`) for the backend address. Do not hardcode `localhost:8000`.
3.  **Type Safety**: Define TypeScript interfaces for ALL Request/Response bodies matching the Pydantic models in the backend.

## Architecture Strictness
1.  **NO DB in Client**: Never import `prisma` or `db` directly into `page.tsx` or `layout.tsx` unless it is a Server Component. Even then, prefer calling the Backend API for business logic (Tasks) to maintain the "Backend as Source of Truth" architecture.
2.  **UI Components**: Use small, reusable components. Keep `page.tsx` clean.

## Commands
- Run Dev: `npm run dev`
- Install: `npm install <package>`
- Prisma Gen: `npx prisma generate`
