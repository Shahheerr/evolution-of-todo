# Tasks: Local Kubernetes Deployment with AI-Native Operations

**Input**: Design documents from `/specs/004-local-k8s-deployment/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT required for this phase - the focus is on infrastructure artifacts, not application code changes.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Dockerfiles**: `frontend/Dockerfile`, `backend/Dockerfile`
- **Helm Chart**: `charts/todo-app/` directory at repository root
- **AIOps**: `aiops/` directory at repository root
- **Documentation**: `specs/004-local-k8s-deployment/` and repository root READMEs

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create charts/todo-app directory structure at repository root
- [X] T002 [P] Create aiops/kubectl-ai directory for AI configuration
- [X] T003 [P] Create aiops/kagent directory for autonomous agent

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Container Image Foundation

- [X] T004 [P] Create frontend/.dockerignore to exclude unnecessary files from build context
- [X] T005 [P] Create backend/.dockerignore to exclude unnecessary files from build context
- [X] T006 Create frontend/Dockerfile with multi-stage build (builder + runtime stages)
- [X] T007 Create backend/Dockerfile with multi-stage build (builder + runtime stages using UV)
- [X] T008 Verify non-root user UID 65532 in both Dockerfiles (security requirement)
- [X] T009 Verify no `latest` tags in Dockerfiles (specific versions only)

### Helm Chart Foundation

- [X] T010 Create charts/todo-app/Chart.yaml with chart metadata (name: todo-app, version: 1.0.0)
- [X] T011 Create charts/todo-app/values.yaml with default configuration values
- [X] T012 Create charts/todo-app/values-dev.yaml with Minikube-specific overrides
- [X] T013 [P] Create charts/todo-app/values-prod.yaml with production-specific overrides
- [X] T014 Create charts/todo-app/templates/_helpers.tpl with template helper functions

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - One-Command Local Deployment (Priority: P1) 🎯 MVP

**Goal**: Deploy the entire TaskFlow application to Minikube with a single Helm command

**Independent Test**: Run `helm install todo-local ./charts/todo-app --namespace todo-app --values charts/todo-app/values-dev.yaml` and verify pods reach Running status within 3 minutes

### Kubernetes Resource Templates

- [X] T015 [P] [US1] Create charts/todo-app/templates/frontend-deployment.yaml with Deployment spec
- [X] T016 [P] [US1] Create charts/todo-app/templates/backend-deployment.yaml with Deployment spec
- [X] T017 [P] [US1] Create charts/todo-app/templates/frontend-service.yaml with NodePort service spec
- [X] T018 [P] [US1] Create charts/todo-app/templates/backend-service.yaml with ClusterIP service spec
- [X] T019 [P] [US1] Create charts/todo-app/templates/frontend-configmap.yaml with ConfigMap for NEXT_PUBLIC_API_URL
- [X] T020 [P] [US1] Create charts/todo-app/templates/backend-configmap.yaml with ConfigMap for FRONTEND_URL and AI_MODEL
- [X] T021 [P] [US1] Create charts/todo-app/templates/backend-secret.yaml with Secret references for DATABASE_URL and BETTER_AUTH_SECRET
- [X] T022 [P] [US1] Create charts/todo-app/templates/frontend-secret.yaml with Secret references for DATABASE_URL and BETTER_AUTH_SECRET

### Health Checks and Probes

- [X] T023 [US1] Add liveness and readiness probes to frontend-deployment.yaml (path: /, port: 3000)
- [X] T024 [US1] Add liveness and readiness probes to backend-deployment.yaml (path: /health, port: 8000)

### Resource Limits and Deployment Strategy

- [X] T025 [US1] Configure resource limits and requests in both deployment templates (CPU/memory per values-dev.yaml)
- [X] T026 [US1] Configure rolling update strategy with maxUnavailable: 0, maxSurge: 1 in deployment templates

### Validation and Testing

- [X] T027 [US1] Run `helm lint charts/todo-app` to validate chart syntax
- [ ] T028 [US1] Run `helm install todo-local ./charts/todo-app --namespace todo-app --dry-run --debug` to pre-flight check
- [ ] T029 [US1] Deploy to Minikube and verify pods reach Running status with `kubectl get pods -n todo-app`
- [ ] T030 [US1] Verify frontend-to-backend communication by creating a task through the UI

**Checkpoint**: At this point, User Story 1 should be fully functional - complete deployment works with single command

---

## Phase 4: User Story 2 - Secure Container Images (Priority: P1)

**Goal**: Ensure container images follow security best practices (minimal size, non-root user, zero vulnerabilities)

**Independent Test**: Build images, run `trivy image todo-frontend:local` and `trivy image todo-backend:local`, verify 0 Critical/High vulnerabilities

### Image Build Validation

- [ ] T031 [P] [US2] Build frontend image with `docker build -t todo-frontend:local -f frontend/Dockerfile ./frontend`
- [ ] T032 [P] [US2] Build backend image with `docker build -t todo-backend:local -f backend/Dockerfile ./backend`
- [ ] T033 [P] [US2] Verify frontend image size ≤200MB with `docker images todo-frontend`
- [ ] T034 [P] [US2] Verify backend image size ≤500MB with `docker images todo-backend`

### Security Scanning

- [ ] T035 [P] [US2] Run Trivy scan on frontend: `trivy image todo-frontend:local --severity CRITICAL,HIGH`
- [ ] T036 [P] [US2] Run Trivy scan on backend: `trivy image todo-backend:local --severity CRITICAL,HIGH`
- [ ] T037 [US2] Verify non-root user in frontend container with `docker run --rm todo-frontend:local id`
- [ ] T038 [US2] Verify non-root user in backend container with `docker run --rm todo-backend:local id`

### Local Testing

- [ ] T039 [US2] Run frontend container locally with `docker run -p 3000:3000 todo-frontend:local` and verify health
- [ ] T040 [US2] Run backend container locally with `docker run -p 8000:8000 todo-backend:local` and verify /health endpoint
- [ ] T041 [US2] Load images into Minikube with `minikube image load todo-frontend:local` and `minikube image load todo-backend:local`

**Checkpoint**: At this point, User Story 2 is complete - both images are hardened, scanned, and ready for deployment

---

## Phase 5: User Story 3 - AI-Assisted Operations and Troubleshooting (Priority: P2)

**Goal**: Use kubectl-ai and Kagent for natural language cluster queries and autonomous remediation

**Independent Test**: Trigger a failure (e.g., invalid env var) and use kubectl-ai to diagnose

### kubectl-ai Configuration

- [X] T042 [P] [US3] Create aiops/kubectl-ai/config.yaml with AI query patterns and model configuration
- [ ] T043 [US3] Document kubectl-ai installation in specs/004-local-k8s-deployment/quickstart.md
- [X] T044 [US3] Create example queries in aiops/kubectl-ai/examples.md (e.g., "Why is backend crashing?")

### Kagent MCP Server

- [X] T045 [P] [US3] Create aiops/kagent/server.py with FastMCP server implementation
- [X] T046 [P] [US3] Create aiops/kagent/tools.py with remediation tools (restart-pod, analyze-logs, config-validator)
- [X] T047 [P] [US3] Create aiops/kagent/requirements.txt for MCP dependencies
- [X] T048 [US3] Implement pod-restart tool in tools.py that executes kubectl rollout restart
- [X] T049 [US3] Implement log-analyzer tool in tools.py that fetches and analyzes pod logs
- [X] T050 [US3] Implement config-validator tool in tools.py that validates Kubernetes resource configurations

### Integration and Testing

- [ ] T051 [US3] Test kubectl-ai with query "Show me all pods in todo-app namespace"
- [ ] T052 [US3] Test kubectl-ai with query "Why is the backend pod crashing?" (after triggering crash loop)
- [ ] T053 [US3] Test Kagent pod-restart tool by restarting a deployment

**Checkpoint**: At this point, User Story 3 is complete - AI tools can diagnose and remediate cluster issues

---

## Phase 6: User Story 4 - Environment-Specific Configuration Management (Priority: P2)

**Goal**: Deploy the same Helm chart to different environments with different configurations

**Independent Test**: Deploy with values-dev.yaml, then with values-prod.yaml, verify different configs apply

### Environment Configuration

- [X] T054 [P] [US4] Update charts/todo-app/values-dev.yaml with Minikube-optimized settings (1 replica, NodePort, low resources)
- [X] T055 [P] [US4] Update charts/todo-app/values-prod.yaml with production settings (2-3 replicas, LoadBalancer, higher resources)
- [ ] T056 [US4] Create charts/todo-app/templates/ingress.yaml with Ingress resource (disabled by default, enabled in prod)

### Validation

- [ ] T057 [US4] Deploy with values-dev.yaml and verify 1 replica per deployment
- [ ] T058 [US4] Deploy with values-prod.yaml and verify 2-3 replicas per deployment
- [ ] T059 [US4] Verify Ingress is created when using values-prod.yaml
- [ ] T060 [US4] Verify service type changes (NodePort in dev, LoadBalancer in prod)

**Checkpoint**: At this point, User Story 4 is complete - same chart deploys to different environments

---

## Phase 7: User Story 5 - Zero-Downtime Rolling Updates (Priority: P3)

**Goal**: Deploy new versions without disrupting active users

**Independent Test**: Deploy v1.0, then v1.1, verify pods replace gradually with no downtime

### Rolling Update Configuration

- [ ] T061 [US5] Verify rollingUpdate strategy in deployment templates (maxUnavailable: 0, maxSurge: 1)
- [ ] T062 [US5] Add readiness probes with appropriate initialDelaySeconds to prevent premature traffic
- [ ] T063 [US5] Add preStop hook to both deployments for graceful shutdown

### Update and Rollback Testing

- [ ] T064 [US5] Deploy v1.0, then upgrade to v1.1 with `helm upgrade todo-local ./charts/todo-app --set image.backend.tag=v1.1.0`
- [ ] T065 [US5] Monitor rollout with `kubectl rollout status deployment/backend -n todo-app -w`
- [ ] T066 [US5] Test rollback with `helm rollback todo-local -n todo-app`
- [ ] T067 [US5] Verify rollback completes within 2 minutes and restores full functionality

**Checkpoint**: At this point, User Story 5 is complete - rolling updates work with zero downtime

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T068 [P] Update README.md at repository root with Phase IV deployment instructions
- [X] T069 [P] Update frontend/README.md with container build instructions
- [X] T070 [P] Update backend/README.md with container build instructions
- [X] T071 [P] Create charts/todo-app/README.md with Helm chart documentation
- [X] T072 Add troubleshooting section to specs/004-local-k8s-deployment/quickstart.md
- [X] T073 Add cleanup procedures to specs/004-local-k8s-deployment/quickstart.md
- [X] T074 Document all environment variables in charts/todo-app/README.md
- [ ] T075 Run complete quickstart.md validation to ensure end-to-end deployment works

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 and US2 can proceed in parallel (both P1, independent)
  - US3 and US4 can proceed after US1/US2 (both P2, independent of each other)
  - US5 can proceed after US1 (P3, depends on working deployment)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independent of US1, can run in parallel
- **User Story 3 (P2)**: Can start after US1 (needs working deployment for testing)
- **User Story 4 (P2)**: Can start after US1 (needs working deployment)
- **User Story 5 (P3)**: Can start after US1 (needs working deployment)

### Within Each User Story

- Templates marked [P] can be created in parallel
- Health checks depend on deployment templates
- Validation tasks depend on template creation
- Integration tests depend on all resources being deployed

### Parallel Opportunities

- All Setup tasks (T001-T003) can run in parallel
- All .dockerignore and Dockerfile tasks (T004-T009) can run in parallel after Setup
- All Helm values files (T011-T013) can run in parallel after Chart.yaml
- All Kubernetes resource templates in US1 (T015-T022) can run in parallel
- Image builds in US2 (T031-T032, T033-T034) can run in parallel
- Security scans in US2 (T035-T036) can run in parallel
- kubectl-ai and Kagent tasks in US3 can run in parallel
- Environment config in US4 (T054-T055) can run in parallel
- All documentation tasks in Polish (T068-T071) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all Kubernetes resource templates together:
Task: "Create charts/todo-app/templates/frontend-deployment.yaml with Deployment spec"
Task: "Create charts/todo-app/templates/backend-deployment.yaml with Deployment spec"
Task: "Create charts/todo-app/templates/frontend-service.yaml with NodePort service spec"
Task: "Create charts/todo-app/templates/backend-service.yaml with ClusterIP service spec"
Task: "Create charts/todo-app/templates/frontend-configmap.yaml with ConfigMap"
Task: "Create charts/todo-app/templates/backend-configmap.yaml with ConfigMap"
Task: "Create charts/todo-app/templates/backend-secret.yaml with Secret references"
Task: "Create charts/todo-app/templates/frontend-secret.yaml with Secret references"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T014) - CRITICAL
3. Complete Phase 3: User Story 1 (T015-T030)
4. Complete Phase 4: User Story 2 (T031-T041)
5. **STOP and VALIDATE**: Test deployment and security independently
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 + User Story 2 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 3 → Test AI operations → Deploy/Demo
4. Add User Story 4 → Test environment switching → Deploy/Demo
5. Add User Story 5 → Test rolling updates → Deploy/Demo
6. Polish → Full Phase IV complete

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Kubernetes templates)
   - Developer B: User Story 2 (Container images and security)
3. After US1/US2 complete:
   - Developer A: User Story 3 (AIOps integration)
   - Developer B: User Story 4 (Environment configuration)
4. Developer C (or A/B): User Story 5 (Rolling updates)
5. All: Polish and documentation

---

## Task Summary

| Phase | Task Range | Count | Focus |
|-------|-----------|-------|-------|
| Setup | T001-T003 | 3 | Directory structure |
| Foundational | T004-T014 | 11 | Dockerfiles + Helm base |
| US1: Deployment | T015-T030 | 16 | Kubernetes resources |
| US2: Security | T031-T041 | 11 | Image hardening + scanning |
| US3: AIOps | T042-T053 | 12 | kubectl-ai + Kagent |
| US4: Config | T054-T060 | 7 | Environment-specific values |
| US5: Updates | T061-T067 | 7 | Rolling updates |
| Polish | T068-T075 | 8 | Documentation |
| **Total** | **T001-T075** | **75** | **Full Phase IV** |

**MVP Tasks (US1 + US2)**: T001-T041 = 41 tasks

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- US1 and US2 are both P1 and can be developed in parallel after Foundational phase
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Tests are NOT required for this infrastructure phase - validation is done via deployment and security scanning
