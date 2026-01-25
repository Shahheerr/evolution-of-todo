---
id: 001
title: Evolution of Todo Constitution
stage: constitution
date: 2026-01-24
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: user
command: sp.constitution
labels: [constitution,spec-driven-development,evolution,todo]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
 - CLAUDE.md
tests:
---

## Prompt

**ACT AS:** Lead System Architect & DevOps Governor.

**CONTEXT:**
We are initiating a high-stakes hackathon project titled **"The Evolution of Todo"**. This is not a static project; it is an evolutionary system that will transition through 5 distinct phases, transforming from a simple In-Memory Python Console App (Phase I) to a Distributed Cloud-Native Microservices System on Kubernetes (Phase V).

**OBJECTIVE:**
Generate a comprehensive `CONSTITUTION.md` file that will serve as the immutable "Supreme Law" for this project. This document must govern how you (the AI) and I (the Architect) collaborate, manage code, handle state transitions, and ensure system integrity.

**CRITICAL REQUIREMENTS FOR THE CONSTITUTION:**

**Article I: The Iron Rule of Spec-Driven Development**
1.  **Zero Manual Edits:** Explicitly state that no code shall be written manually. All implementation comes from `Spec-Kit Plus` directives processed by Claude Code.
2.  **Spec Authority:** If the code fails, we fix the Spec, not the Code.

**Article II: Specification Management & Versioning**
1.  **Sequential History:** All specs must be stored in a `specs/` directory.
2.  **Naming Convention:** Enforce a strict numbering format: `specs/001-initial-setup`, `specs/002-basic-crud`, `specs/003-web-refactor`.
3.  **Immutability:** Once a Spec is implemented and committed, that folder is locked. New features require a new numbered folder. Never overwrite old specs.

**Article III: Git Workflow & Branching Strategy (The Safety Net)**
1.  **Phase-Based Isolation:** To prevent regression, mandate the use of Phase Branches.
    -   `main`: Holds the production-ready code of the completed previous phase.
    -   `phase/I-console`, `phase/II-fullstack`, etc.: Active development branches.
2.  **Tagging:** Upon completion of a phase, a git tag must be created (e.g., `v1.0-phase-I-complete`) before merging or evolving the directory structure.

**Article IV: Directory Evolution & Refactoring Protocol**
*This is the most critical section to prevent breaking changes during evolution.*
1.  **Phase I Structure:** Standard Python (`/src`, `main.py`).
2.  **The Great Migration (Phase II Rule):** Explicitly define how to handle the transition to Full Stack.
    -   Do not delete logic.
    -   Move Phase I code to `/backend/core`.
    -   Initialize `/frontend` as a sibling.
3.  **Refactoring Safety:** Require that core business logic (e.g., "Add Task") be decoupled from the Interface (CLI/Web/Chatbot) so the same logic survives from Phase I to Phase V.

**Article V: Tech Stack Compliance**
Define the immutable stack for each phase:
-   **Phase I:** Python 3.13+, In-Memory.
-   **Phase II:** Next.js, FastAPI, SQLModel, Neon DB.
-   **Phase III:** OpenAI Agents SDK, MCP.
-   **Phase IV/V:** Docker, Kubernetes, Kafka.

**Article VI: Quality Assurance & Self-Correction**
1.  Before marking a task complete, run lints/tests.
2.  Generate a `CLAUDE.md` alongside the Constitution to store project-specific context for your future self.

**OUTPUT INSTRUCTION:**
Draft the `CONSTITUTION.md` now. It should be professional, strict, and formatted for high readability.

## Response snapshot

Created the comprehensive constitution for "The Evolution of Todo" project based on the specified requirements. The constitution includes six core principles covering Spec-Driven Development, specification management, git workflow, directory evolution protocols, tech stack compliance, and quality assurance. Additionally, it defines evolution protocols, development standards, and governance rules. Also created the required CLAUDE.md file with project-specific context for the AI assistant.

## Outcome

- ✅ Impact: Created foundational constitution and CLAUDE.md for the Evolution of Todo project
- 🧪 Tests: No tests required for this task
- 📁 Files: Modified .specify/memory/constitution.md and created CLAUDE.md
- 🔁 Next prompts: Ready for specification development
- 🧠 Reflection: Constitution establishes clear governance for the project's evolution through 5 phases

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin with initial specification development