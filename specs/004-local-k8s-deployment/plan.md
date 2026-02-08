# Implementation Plan: Local Kubernetes Deployment with AI-Native Operations

**Branch**: `004-local-k8s-deployment` | **Date**: 2026-02-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-local-k8s-deployment/spec.md`

## Summary

Phase IV transforms the TaskFlow application from a local web development setup to a containerized deployment on local Kubernetes (Minikube). The primary goal is to create production-ready container images for both the Next.js frontend and FastAPI backend, package them into a unified Helm chart, and establish an AI-Native Operations (AIOps) workflow for intelligent cluster management.

The implementation follows Docker Hardened Images (DHI) principles with multi-stage builds, non-root user execution, and minimal attack surfaces. The Helm chart enables environment-specific configuration (dev/prod) while maintaining a single source of truth. Integration with kubectl-ai and Kagent provides natural language cluster queries and autonomous troubleshooting capabilities via the Model Context Protocol (MCP).

## Technical Context

**Language/Version**: Docker (containerization), Helm 3.x (package management), YAML (Kubernetes manifests)
**Primary Dependencies**:
- Container: Docker Desktop, Docker BuildKit
- Orchestration: Minikube v1.28+, Kubernetes v1.28+
- Package Management: Helm 3.x
- AIOps: kubectl-ai, Kagent, MCP (Model Context Protocol)
- Security: Trivy (vulnerability scanning), non-root users

**Storage**: External Neon PostgreSQL (no database containerization in this phase)
**Testing**: Helm test hooks, Kubernetes liveness/readiness probes, container security scanning
**Target Platform**: Local Minikube cluster (Linux containers on WSL 2)
**Project Type**: Web application (frontend + backend monorepo structure)

**Performance Goals**:
- Deployment completion: ≤5 minutes from command to running pods
- Pod startup time: ≤3 minutes to "Ready" status
- Rolling update: 100% uptime (zero failed requests during update)
- AIOps diagnosis: ≤30 seconds to identify common failures

**Constraints**:
- Minikube resource limits: ≤4GB RAM, ≤2 CPU cores total
- Image size limits: Frontend ≤200MB, Backend ≤500MB
- Zero critical/high security vulnerabilities in scanned images
- No hardcoded secrets in manifests (use Kubernetes Secrets)
- Specific version tags only (no `latest` tags)

**Scale/Scope**:
- Deployments: 2 (Frontend, Backend)
- Replica count: 1-3 per deployment (configurable via values)
- Services: 2 (ClusterIP for backend, NodePort for frontend)
- ConfigMaps: 2 (frontend config, backend config)
- Secrets: 2 (frontend secrets, backend secrets)
- Helm templates: ~8 (deployment, service, configmap, secret, ingress, etc.)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development ✅ PASS

- All implementation will originate from this specification (specs/004-local-k8s-deployment/spec.md)
- No manual code writing without spec directives
- Plan created via `/sp.plan` command following Spec-Kit Plus workflow

### Principle II: Specification Management ✅ PASS

- New numbered spec folder: `specs/004-local-k8s-deployment/`
- Sequential numbering follows existing pattern (001-phase-i, 002-phase-ii, 003-ai-chatbot)
- This folder will become immutable after implementation

### Principle III: Git Workflow & Phase-Based Isolation ✅ PASS

- Feature branch created: `004-local-k8s-deployment`
- Will create git tag `v1.0-phase-IV-complete` upon completion
- Main branch holds production-ready Phase III code

### Principle IV: Directory Evolution Protocol ✅ PASS

- New artifacts added at repository root: `charts/` directory
- Existing frontend/ and backend/ directories remain unchanged
- Dockerfiles added alongside existing code (no deletion of Phase III logic)

### Principle V: Tech Stack Compliance ✅ PASS

- Phase IV stack: Docker, Kubernetes, Helm
- Uses UV for Python package management (from Phase III)
- Integrates OpenAI Agents SDK and MCP (from Phase III)
- Adherence to constitution-mandated stack

### Principle VI: Quality Assurance ✅ PASS

- Security scanning before image deployment
- Liveness/readiness probes for health monitoring
- Pre-flight checks before deployment
- Documentation generated for all artifacts

**Constitution Gate Result**: ✅ **ALL GATES PASSED** - No violations, no justifications required

## Project Structure

### Documentation (this feature)

```text
specs/004-local-k8s-deployment/
├── spec.md              # Feature specification (created)
├── plan.md              # This file (/sp.plan output)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   ├── docker-api-contract.md
│   └── helm-values-contract.md
└── tasks.md             # Phase 2 output (/sp.tasks - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Existing structure (Option 2: Web application)
backend/
├── app/                 # Existing FastAPI application
├── Dockerfile           # NEW: Container image definition
├── .dockerignore        # NEW: Build context optimization
└── .env                 # Existing environment config

frontend/
├── app/                 # Existing Next.js application
├── Dockerfile           # NEW: Container image definition
├── .dockerignore        # NEW: Build context optimization
├── .env                 # Existing environment config
└── prisma/              # Existing database schema

# NEW: Helm chart directory
charts/
└── todo-app/           # Helm chart for the full application
    ├── Chart.yaml       # Chart metadata
    ├── values.yaml      # Default configuration values
    ├── values-dev.yaml  # Development environment overrides
    ├── values-prod.yaml # Production environment overrides
    └── templates/       # Kubernetes resource templates
        ├── _helpers.tpl # Template helper functions
        ├── deployment.yaml  # Deployment template
        ├── service.yaml     # Service template
        ├── configmap.yaml  # ConfigMap template
        ├── secret.yaml     # Secret template
        └── ingress.yaml    # Ingress template (optional)

# NEW: AIOps configuration
aiops/
├── kubectl-ai/         # kubectl-ai configuration
│   └── config.yaml     # AI query patterns and responses
└── kagent/             # Kagent autonomous agent
    ├── server.py       # MCP server for cluster interaction
    └── tools.py        # Remediation tools
```

**Structure Decision**: Option 2 (Web application) - Maintains existing frontend/backend monorepo structure while adding containerization and Helm chart artifacts. This aligns with the Phase III architecture and supports independent scaling of frontend and backend components.

## Phase 0: Research & Technology Decisions

### Research Tasks

| Topic | Decision | Rationale | Alternatives Considered |
|-------|----------|-----------|-------------------------|
| Frontend Base Image | `node:20-alpine` | Minimal Alpine-based Node.js image, supports Next.js 16 | `node:20-slim` (larger), `node:20` (much larger), custom-built base (more maintenance) |
| Backend Base Image | `python:3.13-slim` | Official Python image with UV support, reasonable size | `python:3.13-alpine` (UV compatibility issues), `python:3.13` (too large), `distroless/python` (debugging difficulty) |
| Multi-Stage Build Strategy | Separate build vs runtime stages | Minimizes final image size by excluding build tools | Single-stage (larger images), BuildKit only (less portable) |
| Non-Root User UID | 65532 (distroless-compatible) | Standard unprivileged UID, avoids security risks | Root user (insecure), UID 1000 (may conflict), random UID (unpredictable) |
| Helm Chart Structure | Single chart with multiple sub-charts considered, rejected in favor of unified chart | Simplifies deployment, atomic updates | Multi-chart (more complex), Kustomize (less package management) |
| Service Mesh Integration | Out of scope for Phase IV | Adds complexity beyond local deployment needs | Istio, Linkerd (overkill for local Minikube) |
| Container Runtime | containerd (Minikube default) | Standard Kubernetes runtime, good performance | Docker (deprecated), CRI-O (not needed locally) |
| Image Registry Strategy | Local Minikube image load | No remote registry needed for local development | Docker Hub, GitHub CR, local registry (additional infrastructure) |
| Security Scanner | Trivy | Open-source, comprehensive, Docker integration | Clair (deprecated), Snyk (paid), Grype (less mature) |
| Helm Version | 3.x | Current stable release, improved security over 2.x | 2.x (EOL), 4.x (not yet stable) |

### Technology Stack Details

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Container Runtime | Docker | Latest | Build and run containers |
| Container Registry | Minikube internal | N/A | Local image storage |
| Kubernetes Distribution | Minikube | v1.28+ | Local cluster runtime |
| Package Manager | Helm | v3.0+ | Deployment automation |
| Template Engine | Go Template | (Helm bundled) | YAML manifest generation |
| Security Scanner | Trivy | Latest | Vulnerability scanning |
| AI Query Interface | kubectl-ai | Latest | Natural language kubectl |
| AI Automation | Kagent | Latest | Autonomous troubleshooting |
| Agent Protocol | MCP | v1.0 | Model Context Protocol |

### Best Practices Research

| Area | Best Practice | Implementation |
|-------|---------------|----------------|
| Image Size | Multi-stage builds, Alpine base, .dockerignore | Frontend ≤200MB, Backend ≤500MB |
| Security | Non-root user, scan before deploy, no latest tags | UID 65532, Trivy scan, specific versions |
| Resource Management | Requests + Limits, health checks | Prevents cluster exhaustion |
| Configuration | Environment-specific values, no secrets in manifests | values-dev.yaml, values-prod.yaml |
| Networking | Service names for internal communication | `http://backend-service:8000` |
| Updates | Rolling updates, readiness probes | Zero-downtime deployments |
| Observability | Structured logging, health endpoints | Diagnosability via AIOps |

### Resolved Clarifications

| Question | Answer | Source |
|----------|--------|--------|
| Database containerization? | No - continue using external Neon PostgreSQL | Spec scope boundaries |
| Cloud provider deployment? | No - focused on Minikube local only | Spec scope boundaries |
| Image registry setup? | No - local Minikube image load | Spec assumptions |
| CI/CD pipeline? | No - out of scope for Phase IV | Spec scope boundaries |

## Phase 1: Design & Contracts

### Data Model

No new data entities are introduced in Phase IV. The deployment artifacts (Dockerfiles, Helm charts, Kubernetes resources) describe infrastructure, not data structures.

#### Infrastructure Entities (for documentation)

**ContainerImage**: Immutable artifact containing application code and runtime
- Attributes: registry, repository, tag, digest, size, layers
- Relationships: Built from Dockerfile, deployed via Kubernetes Deployment

**KubernetesDeployment**: Declarative pod specification
- Attributes: name, replicas, selector, template, strategy, revisionHistoryLimit
- Relationships: Creates Pods, controlled by HorizontalPodAutoscaler

**KubernetesService**: Network abstraction for pods
- Attributes: name, type, selector, ports, clusterIP
- Relationships: Routes to Pods via selectors, exposes Deployments

**KubernetesConfigMap**: Non-sensitive configuration data
- Attributes: name, data (key-value pairs)
- Relationships: Injected into Pods as environment variables or files

**KubernetesSecret**: Sensitive configuration data
- Attributes: name, type (Opaque/tls/docker-registry), data (base64-encoded)
- Relationships: Injected into Pods as environment variables or files

**HelmChart**: Package of Kubernetes resource templates
- Attributes: name, version, description, keywords, maintainers
- Relationships: Contains templates, generates Kubernetes resources via `helm install/upgrade`

### API Contracts

#### Docker Build API Contract

```yaml
# Frontend Build Contract
build:
  context: ./frontend
  dockerfile: Dockerfile
  args:
    NEXT_PUBLIC_API_URL: http://backend-service:8000/api
  target: production
  tags:
    - todo-frontend:local
    - todo-frontend:v1.0.0

# Backend Build Contract
build:
  context: ./backend
  dockerfile: Dockerfile
  target: production
  tags:
    - todo-backend:local
    - todo-backend:v1.0.0
```

#### Helm Values Contract

```yaml
# values.yaml Contract Structure
image:
  pullPolicy: IfNotPresent
  frontend:
    repository: todo-frontend
    tag: local
  backend:
    repository: todo-backend
    tag: local

replicaCount:
  frontend: 1
  backend: 1

resources:
  frontend:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 250m
      memory: 256Mi
  backend:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 250m
      memory: 256Mi

env:
  databaseUrl: "postgresql://..."
  betterAuthSecret: "ref+secret://..."  # Kubernetes Secret reference
  openaiApiKey: "ref+secret://..."     # Kubernetes Secret reference

service:
  frontend:
    type: NodePort
    port: 3000
  backend:
    type: ClusterIP
    port: 8000

ingress:
  enabled: false
  className: nginx
  host: localhost
```

#### Kubernetes API Contract

| Resource | API Version | Kind | Namespace |
|----------|------------|------|----------|
| Deployment | apps/v1 | Deployment | todo-app |
| Service | v1 | Service | todo-app |
| ConfigMap | v1 | ConfigMap | todo-app |
| Secret | v1 | Secret | todo-app |
| Ingress | networking.k8s.io/v1 | Ingress | todo-app (optional) |

### Configuration Model

#### Environment Variables (Frontend)

| Variable | Source | Description | Default |
|----------|--------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | ConfigMap | Backend API base URL | `http://backend-service:8000/api` |
| `NEXT_PUBLIC_APP_URL` | ConfigMap | Frontend application URL | `http://localhost:3000` |
| `DATABASE_URL` | Secret | Prisma database connection | From external Neon |
| `BETTER_AUTH_SECRET` | Secret | JWT signing secret | Auto-generated |
| `BETTER_AUTH_URL` | ConfigMap | Better Auth base URL | `http://localhost:3000` |

#### Environment Variables (Backend)

| Variable | Source | Description | Default |
|----------|--------|-------------|---------|
| `DATABASE_URL` | Secret | PostgreSQL connection string | From external Neon |
| `BETTER_AUTH_SECRET` | Secret | JWT verification secret | Must match frontend |
| `FRONTEND_URL` | ConfigMap | CORS allowed origin | `http://localhost:3000` |
| `OPENAI_API_KEY` | Secret | OpenAI API key for AI chat | Optional |
| `AI_MODEL` | ConfigMap | AI model name | `gpt-4o-mini` |

#### Helm Values Hierarchy

```
values.yaml (defaults)
├── values-dev.yaml (local Minikube overrides)
└── values-prod.yaml (cloud production overrides)
```

### Quickstart Guide

**Phase IV Quickstart: Local Kubernetes Deployment**

This guide covers deploying the TaskFlow application to a local Minikube cluster with Helm charts.

## Prerequisites

Verify your environment:

```bash
# Check Docker
docker --version

# Check Minikube
minikube version

# Check kubectl
kubectl version --client

# Check Helm
helm version

# Verify Minikube is running
minikube status
```

## Step 1: Build Container Images

```bash
# Build frontend image (multi-stage, non-root)
cd frontend
docker build -t todo-frontend:local .

# Build backend image (UV, non-root)
cd ../backend
docker build -t todo-backend:local .
```

## Step 2: Load Images into Minikube

```bash
# Load both images into Minikube's registry
minikube image load todo-frontend:local
minikube image load todo-backend:local
```

## Step 3: Deploy with Helm

```bash
# Create namespace (optional)
kubectl create namespace todo-app

# Install the chart
helm install todo-local ./charts/todo-app \
  --namespace todo-app \
  --values charts/todo-app/values-dev.yaml

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=frontend -n todo-app --timeout=300s
kubectl wait --for=condition=ready pod -l app=backend -n todo-app --timeout=300s
```

## Step 4: Access the Application

```bash
# Get the frontend URL
minikube service todo-frontend -n todo-app

# Or use port forwarding
kubectl port-forward svc/todo-frontend -n todo-app 3000:3000
```

## Step 5: Verify Deployment

```bash
# Check all pods
kubectl get pods -n todo-app

# Check services
kubectl get svc -n todo-app

# Test the application
curl http://localhost:3000
```

## Upgrade and Rollback

```bash
# Upgrade with new image
helm upgrade todo-local ./charts/todo-app \
  --namespace todo-app \
  --set image.backend.tag=v1.1.0

# Rollback if needed
helm rollback todo-local -n todo-app
```

## Troubleshooting with AIOps

```bash
# Natural language query
kubectl-ai "Why is the backend pod crashing?"

# Get pod status
kubectl-ai "Show me all pods with high memory usage"

# Describe service
kubectl-ai "Is the backend service accessible?"
```

## Cleanup

```bash
# Uninstall the release
helm uninstall todo-local -n todo-app

# Delete namespace
kubectl delete namespace todo-app
```

## Architecture Decision Records

This section captures significant architectural decisions made during Phase IV planning. Each decision should be documented in a formal ADR if it has long-term implications.

### ADR-001: Multi-Stage Dockerfiles for Image Size Optimization

**Status**: Accepted
**Context**: Need to minimize container image sizes for faster deployment and reduced attack surface

**Decision**: Use multi-stage builds for both frontend and backend Dockerfiles
- Frontend: Build stage with full Node.js for Next.js compilation, runtime stage with minimal node:alpine
- Backend: Build stage with Python+UV for dependency installation, runtime stage with python:3.13-slim

**Rationale**:
- Reduces frontend image from ~1GB to <200MB
- Reduces backend image from ~800MB to <500MB
- Excludes build tools and development dependencies from runtime
- Improves security by minimizing attack surface

**Consequences**:
- (+) Faster image pulls and deployments
- (+) Reduced storage requirements
- (+) Smaller attack surface
- (-) More complex Dockerfile syntax
- (-) Longer build times due to multiple stages

**Alternatives Considered**:
1. Single-stage Dockerfiles → Rejected due to large image sizes
2. BuildKit only → Rejected due to portability concerns
3. Distroless images → Rejected due to debugging difficulty

### ADR-002: Non-Root User (UID 65532) for Security

**Status**: Accepted
**Context**: Containers running as root pose significant security risks

**Decision**: All containers run as non-root user with UID 65532
- Use USER 65532 in Dockerfiles
- Create user in build stage if needed
- Ensure application writes to writable directories

**Rationale**:
- Reduces privilege escalation attack surface
- Follows Docker Hardened Images (DHI) principles
- Compatible with distroless image conventions
- Prevents container breakout vulnerabilities

**Consequences**:
- (+) Enhanced security posture
- (+) Compliance with security best practices
- (-) Requires careful permission management
- (-) Potential issues with file permissions

**Alternatives Considered**:
1. Root user → Rejected due to security risks
2. UID 1000 → Rejected due to potential conflicts
3. Random UID → Rejected due to unpredictability

### ADR-003: Local Minikube Image Loading vs Remote Registry

**Status**: Accepted
**Context**: Need to make images available to Minikube for local development

**Decision**: Use `minikube image load` to push images directly to Minikube's internal registry

**Rationale**:
- No external registry setup required for local development
- Faster iteration (no push/pull latency)
- Works offline after initial load
- Simpler developer experience

**Consequences**:
- (+) No registry infrastructure needed
- (+) Faster local development cycles
- (-) Images don't persist across Minikube restarts
- (-) Not suitable for team development (each developer loads own images)

**Alternatives Considered**:
1. Docker Hub public registry → Rejected due to public exposure
2. Private registry (Docker Hub, GCR, ECR) → Rejected due to infrastructure overhead
3. Local registry (Docker Registry v2) → Rejected as overkill for single developer

### ADR-004: Unified Helm Chart vs Multi-Chart Architecture

**Status**: Accepted
**Context**: Need to package both frontend and backend for deployment

**Decision**: Single Helm chart (`todo-app`) with two Deployment resources

**Rationale**:
- Atomic deployments (both services update together)
- Simpler dependency management
- Single version control for deployment artifacts
- Easier rollback for the entire application

**Consequences**:
- (+) Simpler deployment workflow
- (+) Consistent versioning across services
- (-) Frontend and backend must deploy together
- (-) Larger Helm chart to maintain

**Alternatives Considered**:
1. Separate charts → Rejected due to dependency complexity
2. Parent chart with sub-charts → Rejected due to added complexity
3. Kustomize → Rejected due to less sophisticated package management

### ADR-005: AIOps Integration via kubectl-ai and Kagent

**Status**: Accepted
**Context**: Need intelligent operations layer for cluster management

**Decision**: Integrate kubectl-ai for natural language queries and Kagent for autonomous remediation

**Rationale**:
- Reduces mean-time-to-resolution (MTTR) for operational issues
- Enables natural language cluster interaction
- Provides autonomous troubleshooting capabilities
- Aligns with AI-Native Operations vision

**Consequences**:
- (+) Lower barrier to entry for Kubernetes operations
- (+) Faster incident response
- (-) Additional tool complexity
- (-) Requires AI model configuration

**Alternatives Considered**:
1. Manual kubectl only → Rejected due to steeper learning curve
2. Custom scripts → Rejected due to maintenance burden
3. Full observability stack (Prometheus/Grafana) → Rejected as overkill for local deployment

---

## Complexity Tracking

> **No violations requiring justification** - All constitution gates passed successfully. The architecture maintains simplicity while achieving Phase IV objectives within the constraints of the Spec-Driven Development methodology.
