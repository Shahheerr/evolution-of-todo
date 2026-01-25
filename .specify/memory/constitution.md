<!-- SYNC IMPACT REPORT:
Version change: N/A → 1.0.0
Modified principles: None (new constitution)
Added sections: All sections added
Removed sections: None
Templates requiring updates: ✅ Updated
Follow-up TODOs: None
-->
# The Evolution of Todo Constitution

## Core Principles

### I. The Iron Rule of Spec-Driven Development
All code implementation must originate from Spec-Kit Plus directives processed by Claude Code; Manual code writing is prohibited. If the code fails, we fix the Spec, not the Code.

### II. Specification Management & Versioning
All specifications must be stored sequentially in the `specs/` directory with strict numbering format (e.g., `specs/001-initial-setup`, `specs/002-basic-crud`, `specs/003-web-refactor`); Once a Spec is implemented and committed, that folder becomes immutable and locked. New features require a new numbered folder - never overwrite old specs.

### III. Git Workflow & Phase-Based Isolation
Use Phase Branches to prevent regression: `main` holds production-ready code of the completed previous phase, while `phase/I-console`, `phase/II-fullstack`, etc. serve as active development branches; Upon completion of each phase, create a git tag (e.g., `v1.0-phase-I-complete`) before merging.

### IV. Directory Evolution & Refactoring Protocol
Core business logic must be decoupled from interfaces to survive evolution from Phase I to Phase V; During phase transitions, do not delete existing logic - move Phase I code to `/backend/core` and initialize `/frontend` as a sibling during Phase II; Maintain the Great Migration rule to ensure continuity of business logic across all phases.

### V. Tech Stack Compliance
Each phase has an immutable technology stack: Phase I uses Python 3.13+ with In-Memory storage; Phase II implements Next.js, FastAPI, SQLModel, Neon DB; Phase III integrates OpenAI Agents SDK, MCP; Phases IV/V utilize Docker, Kubernetes, Kafka. Adherence to these stacks is mandatory for each respective phase.

### VI. Quality Assurance & Self-Correction
Before marking any task complete, all lints and tests must pass; Generate and maintain a `CLAUDE.md` file to store project-specific context for AI assistant continuity; All changes must be small, testable, and reference code precisely.

## Evolution Protocols
The project transitions through 5 distinct phases: from a simple In-Memory Python Console App (Phase I) to a Distributed Cloud-Native Microservices System on Kubernetes (Phase V). Each phase builds upon the previous while maintaining backward compatibility where possible. The system must evolve gracefully without breaking existing functionality.

## Development Standards
All implementation follows Spec-Driven Development methodology with Claude Code as the primary development agent. Specifications drive all code generation, and architectural decisions are documented in Architecture Decision Records (ADRs). Code quality is maintained through automated linting, testing, and peer review processes.

## Governance
This Constitution serves as the immutable "Supreme Law" governing all project activities; All team members must comply with these principles; Amendments require formal documentation and approval process; All pull requests and reviews must verify constitutional compliance; This document supersedes all other development practices and guidelines.

**Version**: 1.0.0 | **Ratified**: 2026-01-24 | **Last Amended**: 2026-01-24
