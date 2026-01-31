# Implementation Plan: Phase-II Full-Stack Todo Application

**Branch**: `002-phase-ii` | **Date**: 2026-01-26 | **Spec**: [specs/002-phase-ii/spec.md](specs/002-phase-ii/spec.md)
**Input**: Feature specification from `/specs/002-phase-ii/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation of Phase-II: Full-Stack Todo Application with Next.js frontend and FastAPI backend, implementing stateless authentication using Better-Auth and JWT tokens. The application maintains the same core functionality as Phase-I while providing a modern web interface with clean separation of concerns, following the decoupled monorepo architecture pattern. The backend provides REST API endpoints secured with JWT authentication, while the frontend provides a responsive user interface with premium dark mode design.

## Technical Context

**Language/Version**: Python 3.13+ (as specified in constitution and spec), Next.js 16+, React 19, TypeScript 5+
**Primary Dependencies**: FastAPI (0.115+), Pydantic (v2+), Next.js (16+), Better-Auth (v1.4+), Neon PostgreSQL, Prisma (v6+)
**Storage**: Neon Serverless PostgreSQL with Prisma ORM for database operations
**Testing**: pytest for backend unit/integration tests, Jest/React Testing Library for frontend tests
**Target Platform**: Web application (Chrome, Firefox, Safari, Edge browsers)
**Project Type**: Decoupled monorepo (frontend + backend as separate logical units)
**Performance Goals**: API endpoints respond within 200ms, frontend renders dashboard within 3 seconds of authentication, supports 10,000+ tasks per user without degradation
**Constraints**: Stateless authentication using JWT, data isolation by user ID, no direct DB access from frontend components, shared BETTER_AUTH_SECRET between systems
**Scale/Scope**: Multi-user SaaS application, individual task management up to 10,000 tasks per user, horizontal scaling via Neon serverless

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance Verification
- ✅ **Spec-Driven Development**: Following spec from `/specs/002-phase-ii/spec.md` as required by Constitution Article I
- ✅ **Specification Management**: Using sequential numbering format `specs/002-phase-ii` as required by Constitution Article II
- ✅ **Git Workflow**: Using feature branch `002-phase-ii` for isolation as required by Constitution Article III
- ✅ **Directory Evolution**: Following "Great Migration" rule - Phase I code preserved, new frontend/ and backend/ directories created as required by Constitution Article IV
- ✅ **Tech Stack Compliance**: Using Next.js, FastAPI, SQLModel, Neon DB as specified for Phase II in Constitution Article V
- ✅ **Quality Assurance**: Following testing and linting practices as required by Constitution Article VI
- ✅ **Architecture Pattern**: Implementing clean separation (Frontend/Backend with shared auth secret) as specified in requirements

## Project Structure

### Documentation (this feature)

```text
specs/002-phase-ii/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
/
├── frontend/                 # Next.js 16+ application
│   ├── app/                  # App Router pages and layouts
│   │   ├── api/              # Next.js API routes (auth/token endpoint)
│   │   ├── dashboard/        # Main dashboard page
│   │   ├── auth/             # Authentication pages
│   │   └── globals.css       # Global styles
│   ├── lib/                  # Shared utilities and auth client
│   │   ├── auth.ts           # Better-Auth client configuration
│   │   └── api.ts            # API client wrapper
│   ├── public/               # Static assets
│   ├── prisma/               # Database schema (master source of truth)
│   │   └── schema.prisma     # Prisma schema definition
│   ├── package.json          # NPM dependencies
│   ├── tsconfig.json         # TypeScript configuration
│   └── tailwind.config.ts    # Tailwind CSS configuration
├── backend/                  # FastAPI application
│   ├── app/                  # FastAPI application code
│   │   ├── main.py           # Application entry point
│   │   ├── core/             # Configuration and security
│   │   │   ├── config.py     # Settings and configuration
│   │   │   └── security.py   # JWT authentication dependencies
│   │   ├── models/           # Pydantic models for validation
│   │   │   ├── user.py       # User data models
│   │   │   ├── task.py       # Task data models
│   │   │   └── auth.py       # Authentication models
│   │   └── routes/           # API route handlers
│   │       ├── auth.py       # Authentication endpoints
│   │       ├── tasks.py      # Task management endpoints
│   │       └── users.py      # User management endpoints
│   ├── pyproject.toml        # UV project configuration
│   ├── .env                  # Environment variables
│   └── .python-version       # Python version specification
└── specs/                    # Specification and documentation
    └── 002-phase-ii/         # Phase II specifications
```

### Tests (repository root)

```text
tests/
├── backend/
│   ├── unit/
│   │   ├── test_models.py    # Pydantic model tests
│   │   ├── test_security.py  # Security/authorization tests
│   │   └── test_auth.py      # Authentication tests
│   ├── integration/
│   │   └── test_api.py       # API endpoint integration tests
│   └── contract/
│       └── test_auth_contract.py  # Auth contract tests
└── frontend/
    ├── unit/
    │   ├── __tests__/lib/auth.test.ts
    │   └── __tests__/components/task-list.test.tsx
    ├── integration/
    │   └── pages/dashboard.int.test.tsx
    └── e2e/
        └── auth-flow.e2e.test.ts
```

**Structure Decision**: Decoupled monorepo architecture following the specification requirements. The frontend uses Next.js App Router with Better-Auth for authentication and communicates with the FastAPI backend via REST API using JWT tokens. The database schema is maintained in the frontend/prisma directory as the master source of truth, with the backend trusting this structure. The shared BETTER_AUTH_SECRET enables the stateless authentication bridge between systems.
