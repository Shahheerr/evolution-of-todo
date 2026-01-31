# Phase II Architecture: Full-Stack Todo Application

## 1. System Overview
This project is a decoupled Monorepo application designed for high performance, type safety, and stateless authentication.

### **The Monorepo Structure**
```text
/ (Root)
├── frontend/             # Next.js 16+ (App Router)
│   ├── app/              # Routes & Pages
│   ├── lib/              # Auth Client & API Wrappers
│   └── prisma/           # Database Schema (Source of Truth)
│
├── backend/              # FastAPI (Python 3.13+)
│   ├── app/              # API Logic
│   ├── prisma/           # Generated Python Client (if used)
│   └── pyproject.toml    # UV Dependency Management
└── specs/                # Documentation & Truth Sources
```

## 2. Technology Stack & Role Definition

| Component | Technology | Responsibility |
|-----------|------------|----------------|
| **Frontend** | Next.js 16+, React 19, TailwindCSS | UI Rendering, Auth Initiation (Better-Auth), Session Management. |
| **Backend** | FastAPI, Uvicorn, Python 3.13 | Business Logic, Data processing, Heavy lifting. |
| **Database** | Neon (Serverless PostgreSQL) | Unified Data persistence. |
| **ORM** | Prisma (Schema & Clients) | Schema management, Migration, Type-safe DB access. |
| **Auth** | Better-Auth + JWT | Identity management (FE) & Stateless Verification (BE). |
| **Tooling** | `uv` (Python), `npm` (JS) | Strict package management. |

## 3. Communication Protocol

### **Frontend -> Backend**
- **Protocol:** REST JSON.
- **Authentication:** All protected endpoints MUST receive the JWT in the standard header:
  `Authorization: Bearer <better-auth-jwt-token>`
- **Network Boundary:**
  - Frontend runs on `http://localhost:3000`
  - Backend runs on `http://localhost:8000`
  - CORS must be configured on Backend to allow `localhost:3000` methods `["*"]`.

## 4. Key Architectural Constraints (STRICT)
1.  **State Isolation:** The Backend is stateless. It knows the user **only** by decoding the JWT. It does NOT check session cookies.
2.  **Schema Authority:** The `frontend/prisma/schema.prisma` file is the **Single Source of Truth** for the database structure. Any change there must be pushed/migrated to Neon, and clients regenerated.
3.  **No Direct DB from Client:** Next.js Client Components must NEVER access the DB directly. They talk to Next.js API Routes or the FastAPI Backend.

## 5. Resources & Documentation
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Neon Serverless Postgres](https://neon.tech/docs/introduction)
- [Turborepo (Monorepo Concepts)](https://turbo.build/repo/docs)
