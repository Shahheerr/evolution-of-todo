# Research & Technology Decisions

**Feature**: Local Kubernetes Deployment with AI-Native Operations
**Date**: 2026-02-06
**Status**: Complete

## Overview

This document consolidates research findings and technology decisions for Phase IV: Local Kubernetes Deployment. All research was conducted to resolve the technical requirements specified in the feature specification and inform the implementation plan.

## Decision Summaries

| Category | Decision | Justification |
|----------|----------|---------------|
| **Frontend Base Image** | `node:20-alpine` | Minimal Alpine-based Node.js, supports Next.js 16, small footprint |
| **Backend Base Image** | `python:3.13-slim` | Official Python with UV compatibility, reasonable size |
| **Non-Root User** | UID 65532 | Distroless-compatible, standard unprivileged user |
| **Image Registry** | Minikube internal (local load) | No external infrastructure, faster iteration |
| **Helm Structure** | Unified single chart | Atomic deployments, simpler dependency management |
| **Security Scanner** | Trivy | Open-source, comprehensive, Docker-native |
| **Container Runtime** | containerd | Minikube default, stable, performant |
| **Service Mesh** | Out of scope (Phase IV) | Adds unnecessary complexity for local deployment |

## Frontend Containerization Research

### Base Image Selection

**Options Evaluated**:

1. **node:20-alpine** ✅ SELECTED
   - Size: ~180MB base
   - Pros: Minimal Alpine base, official Node.js image, good Next.js compatibility
   - Cons: Slightly larger than distroless alternatives
   - Verdict: Optimal balance of size, compatibility, and maintainability

2. **node:20-slim**
   - Size: ~220MB base
   - Pros: Debian-based, good package ecosystem
   - Cons: Larger than Alpine, includes unnecessary packages
   - Verdict: Rejected due to size

3. **node:20 (full)**
   - Size: ~900MB base
   - Pros: Complete package ecosystem
   - Cons: Extremely large, bloated with unnecessary tools
   - Verdict: Rejected due to size

4. **distroless/nodejs**
   - Size: ~50MB base
   - Pros: Minimal, highly secure
   - Cons: Difficult to debug, limited debugging tools, incompatible with some Next.js build requirements
   - Verdict: Rejected due to debugging complexity

**Multi-Stage Build Strategy**:

```
Stage 1 (Build): node:20-alpine
  - Install all dependencies
  - Build Next.js application
  - Optimize production bundle

Stage 2 (Runtime): node:20-alpine
  - Copy built artifacts from Stage 1
  - Set non-root user (UID 65532)
  - Expose port 3000
  - Start Next.js server
```

**Rationale**: Multi-stage builds reduce final image size by excluding build tools (npm, node_modules for development, TypeScript compiler) from the runtime image. This improves security, deployment speed, and storage requirements.

### Security Considerations

1. **Non-Root User**: Run as UID 65532 (standard distroless user)
2. **Read-Only Root Filesystem**: Prevent runtime modifications
3. **Minimal Attack Surface**: Only include runtime dependencies
4. **Specific Version Tags**: Use `node:20-alpine@sha256:...` for reproducibility
5. **No Build Secrets**: Don't include build secrets in final image
6. **Vulnerability Scanning**: Run Trivy before deployment

## Backend Containerization Research

### Base Image Selection

**Options Evaluated**:

1. **python:3.13-slim** ✅ SELECTED
   - Size: ~130MB base
   - Pros: Official Python image, UV compatibility, reasonable size
   - Cons: Slightly larger than Alpine variant
   - Verdict: Best balance for UV support and stability

2. **python:3.13-alpine**
   - Size: ~50MB base
   - Pros: Minimal Alpine base
   - Cons: UV package manager has known compatibility issues with musl libc, many Python packages require glibc
   - Verdict: Rejected due to UV and package compatibility issues

3. **python:3.13**
   - Size: ~1GB base
   - Pros: Complete package ecosystem
   - Cons: Extremely large, includes unnecessary tools
   - Verdict: Rejected due to size

4. **distroless/python**
   - Size: ~30MB base
   - Pros: Minimal, highly secure
   - Cons: Difficult to debug, no package manager, incompatible with UV
   - Verdict: Rejected due to debugging difficulty and UV incompatibility

**Multi-Stage Build Strategy**:

```
Stage 1 (Builder): python:3.13-slim
  - Install UV package manager
  - Copy pyproject.toml and uv.lock
  - Install dependencies with UV
  - Create virtual environment

Stage 2 (Runtime): python:3.13-slim
  - Copy Python virtual environment from Stage 1
  - Copy application code
  - Set non-root user (UID 65532)
  - Expose port 8000
  - Start FastAPI with uvicorn
```

**Rationale**: Multi-stage builds with UV provide fast dependency resolution and a smaller runtime image. The slim variant offers glibc compatibility for all Python packages while maintaining a reasonable size.

### UV Package Manager Integration

**Why UV?**
- Speed: 10-100x faster than pip for dependency installation
- Determinism: Lock files guarantee reproducible builds
- Compatibility: Works with standard Python packaging (PyPI)
- Security: Validates package integrity during installation

**UV Configuration**:
```dockerfile
# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies
RUN uv pip install --system -r pyproject.toml
```

### Security Considerations

1. **Non-Root User**: Run as UID 65532 (consistent with frontend)
2. **Read-Only Root**: Prevent runtime modifications to system files
3. **Minimal Packages**: Only install runtime dependencies
4. **Secrets from Environment**: Inject DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY via Kubernetes Secrets
5. **Health Check Endpoint**: `/health` for liveness/readiness probes
6. **Graceful Shutdown**: Handle SIGTERM for zero-downtime deployments

## Kubernetes Deployment Research

### Deployment Strategy

**Replica Count**:
- Development (Minikube): 1 replica each (resource conservation)
- Production: 2-3 replicas each (high availability)

**Resource Limits** (for Minikube default 2CPUs, 2GB RAM):
```
Frontend:
  Requests: 250m CPU, 256Mi RAM
  Limits: 500m CPU, 512Mi RAM

Backend:
  Requests: 250m CPU, 256Mi RAM
  Limits: 500m CPU, 512Mi RAM
```

**Rationale**: Conservative limits prevent Minikube exhaustion while ensuring sufficient resources for application functioning. Requests are set at 50% of limits to allow multiple pods on a single node.

### Health Check Probes

**Liveness Probe**: Detects and restarts deadlocked containers
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

**Readiness Probe**: Holds traffic until container is ready
```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

**Rationale**: Separate liveness and readiness probes ensure that containers are restarted when deadlocked but not removed from service during slow startups.

### Rolling Update Strategy

**Configuration**:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 0  # Zero downtime
    maxSurge: 1          # One extra pod during update
```

**Rationale**: `maxUnavailable: 0` ensures zero downtime during updates. `maxSurge: 1` allows one extra pod to spin up before old pods are terminated, maintaining capacity.

### Service Discovery

**Internal Communication**:
- Frontend → Backend: `http://backend-service:8000/api`
- Backend → Database: External Neon PostgreSQL via environment variable

**Service Types**:
- Backend: ClusterIP (internal only)
- Frontend: NodePort (external access via Minikube tunnel)

**Rationale**: ClusterIP for backend follows the principle of least privilege—frontend can access backend, but backend is not directly exposed outside the cluster. NodePort for frontend allows external access for local development.

## Helm Chart Research

### Chart Structure Decision

**Options Evaluated**:

1. **Unified Single Chart** ✅ SELECTED
   - Structure: One `todo-app` chart with both deployments
   - Pros: Atomic deployments, simpler dependency management, consistent versioning
   - Cons: Larger chart, coupled deployments
   - Verdict: Best for local development and atomic updates

2. **Multi-Chart Architecture**
   - Structure: Separate `frontend` and `backend` charts
   - Pros: Independent deployments, smaller charts
   - Cons: Dependency management complexity, inconsistent versioning
   - Verdict: Rejected due to complexity

3. **Kustomize**
   - Structure: Base YAML overlays for different environments
   - Pros: GitOps-friendly, declarative
   - Cons: No package management, more manual work
   - Verdict: Rejected due to lack of packaging features

### Values File Organization

**Hierarchy**:
```
values.yaml           # Defaults (production-ready)
├── values-dev.yaml   # Development overrides (Minikube)
└── values-prod.yaml  # Production overrides (cloud)
```

**Development Overrides**:
- Replica count: 1
- Resource limits: Conservative (fit in Minikube)
- Service type: NodePort (for local access)
- Ingress: Disabled

**Production Overrides**:
- Replica count: 2-3
- Resource limits: Higher (for cloud workloads)
- Service type: LoadBalancer
- Ingress: Enabled (with TLS)

### Template Conventions

**Naming Conventions**:
- Resource names: `{{ include "todo-app.fullname" . }}-<resource>`
- Labels: `app.kubernetes.io/name: {{ include "todo-app.name" . }}`
- Selector match: Use `app.kubernetes.io/name` label

**Helper Functions**:
```yaml
# _helpers.tpl
{{- define "todo-app.name" -}}
{{- default .Chart.Name . }}
{{- end -}}

{{- define "todo-app.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "todo-app.name" .) -}}
{{- end -}}
```

## AIOps Integration Research

### kubectl-ai Integration

**Purpose**: Natural language interface to Kubernetes operations

**Configuration**:
```yaml
# kubectl-ai config
model: gpt-4
context: minikube
enabledCommands:
  - get
  - describe
  - logs
  - exec
```

**Use Cases**:
- "Why is the backend pod crashing?" → Analyzes logs and events
- "Show me pods with high memory usage" → Queries metrics
- "Restart the frontend deployment" → Executes rollout restart

**Rationale**: Reduces barrier to entry for Kubernetes operations. Developers can query cluster state without memorizing complex kubectl syntax.

### Kagent Integration

**Purpose**: Autonomous troubleshooting and remediation via MCP

**Architecture**:
```
Kagent (MCP Server)
├── Tools: pod-restart, log-analyzer, config-validator
├── Protocol: MCP (stdio or SSE)
└── Integration: Reads kubeconfig, executes kubectl commands
```

**Remediation Workflows**:
1. Detect issue (CrashLoopBackOff)
2. Collect data (logs, events, describe)
3. Analyze patterns (common failure modes)
4. Execute fix (restart, patch config, rollback)
5. Verify recovery

**Rationale**: Provides autonomous "hands" for cluster operations. Kagent can execute multi-step troubleshooting procedures without human intervention, reducing MTTR.

### Model Context Protocol (MCP)

**Server Implementation**:
```python
# kagent/server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("kagent-k8s")

@mcp.tool()
async def restart_pods(label: str) -> str:
    """Restart all pods matching a label selector."""
    # Execute kubectl rollout restart
    return f"Restarted pods with label {label}"

@mcp.tool()
async def analyze_pod_logs(pod_name: str) -> str:
    """Fetch and analyze logs from a pod."""
    # Get logs, analyze with AI
    return analysis
```

**Rationale**: MCP provides a standardized protocol for AI agent integration. Kagent exposes Kubernetes operations as tools that AI clients can invoke through the MCP protocol.

## Security Research

### Container Image Security

**Best Practices**:
1. **Multi-Stage Builds**: Exclude build tools from runtime
2. **Non-Root User**: Run as UID 65532
3. **Minimal Base Images**: Use Alpine-based images where possible
4. **Specific Versions**: Use digest-pinned tags (not `latest`)
5. **Vulnerability Scanning**: Scan with Trivy before deployment
6. **No Secrets in Images**: All secrets via environment variables

**Scanning Process**:
```bash
# Scan frontend image
trivy image todo-frontend:local

# Scan backend image
trivy image todo-backend:local

# Fail build if critical vulnerabilities found
trivy image --exit-code 1 --severity CRITICAL,HIGH todo-frontend:local
```

### Kubernetes Security

**Pod Security Policies**:
- Run as non-root (enforce via PSP or OPA Gatekeeper)
- Drop all capabilities (default deny)
- Read-only root filesystem
- Restrict seccomp profiles

**Network Policies**:
```yaml
# Frontend can only talk to backend
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: frontend-policy
spec:
  podSelector:
    matchLabels:
      app: frontend
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: backend
    ports:
    - protocol: TCP
      port: 8000
```

**Secrets Management**:
- Never store secrets in ConfigMaps or values files
- Use Kubernetes Secrets for sensitive data
- Inject secrets via environment variables
- Enable secret encryption at rest (etcd encryption)

## Performance Research

### Image Size Targets

**Frontend**:
- Base image (node:20-alpine): ~180MB
- Dependencies (node_modules): ~50MB
- Next.js build artifacts: ~20MB
- **Target: ≤250MB** ✅ ACHIEVABLE

**Backend**:
- Base image (python:3.13-slim): ~130MB
- Dependencies (site-packages): ~100MB
- Application code: ~10MB
- **Target: ≤500MB** ✅ ACHIEVABLE

### Resource Limits (Minikube Default)

**Available Resources**:
- CPUs: 2 cores
- RAM: 2GB (2048MB)
- Disk: 20GB

**Allocation Strategy**:
- System overhead: ~500MB
- Frontend pod: 512MB (256Mi request, 512Mi limit)
- Backend pod: 512MB (256Mi request, 512Mi limit)
- Total application: ~1GB
- **Headroom**: ~500MB** for system and other workloads

**Rationale**: Conservative resource allocation ensures Minikube remains responsive and the application doesn't crash the cluster. The 50% buffer (request = 50% of limit) allows the scheduler to place pods efficiently.

### Deployment Performance

**Image Build Time**:
- Frontend: ~2-3 minutes (multi-stage build)
- Backend: ~1-2 minutes (UV install is fast)

**Image Load Time**:
- Minikube image load: ~30 seconds per image

**Deployment Time**:
- Helm install: ~30 seconds
- Pod startup: ~60-90 seconds per pod
- Total time to running: **≤5 minutes** ✅ ACHIEVABLE

## Networking Research

### Service Discovery

**Internal DNS**:
```yaml
# Backend service (ClusterIP)
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
```

**Frontend Configuration**:
```env
# Frontend environment variable
NEXT_PUBLIC_API_URL=http://backend-service:8000/api
```

**Rationale**: Kubernetes provides internal DNS for service discovery. Services are accessible via `<service-name>.<namespace>.svc.cluster.local` or simply `<service-name>` within the same namespace.

### External Access

**Options Evaluated**:

1. **NodePort** ✅ SELECTED (for development)
   - Pros: Works out of box with Minikube, no additional setup
   - Cons: High port numbers, not suitable for production
   - Verdict: Best for local development

2. **Minikube Tunnel**
   - Pros: Exposes services via local IP, stable URLs
   - Cons: Requires running tunnel command, not persistent
   - Verdict: Alternative to NodePort

3. **Ingress (LoadBalancer)**
   - Pros: Production-ready, standard Kubernetes pattern
   - Cons: Requires additional setup (MetalLB, cloud provider)
   - Verdict: Out of scope for Phase IV

### Session Affinity

**Configuration**:
```yaml
spec:
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800  # 3 hours
```

**Rationale**: Session affinity ensures that AI chat conversations (which maintain state on the backend) are routed to the same pod for the duration of the session.

## Testing Strategy

### Container Image Testing

**Build Verification**:
```bash
# Test frontend container locally
docker run -p 3000:3000 todo-frontend:local

# Test backend container locally
docker run -p 8000:8000 todo-backend:local
```

**Health Check Verification**:
```bash
# Test health endpoint
curl http://localhost:8000/health
```

### Kubernetes Deployment Testing

**Pre-Flight Checks**:
```bash
# Verify Minikube is running
minikube status

# Check available resources
kubectl top nodes

# Verify images are loaded
minikube image list | grep todo
```

**Deployment Verification**:
```bash
# Deploy
helm install todo-local ./charts/todo-app

# Wait for readiness
kubectl wait --for=condition=ready pod -l app=frontend -n todo-app --timeout=300s

# Verify connectivity
kubectl exec -n todo-app deployment/frontend -- curl http://backend-service:8000/health
```

### Rollback Testing

```bash
# Deploy new version
helm upgrade todo-local ./charts/todo-app --set image.backend.tag=v1.1.0

# Simulate failure (crash loop)
kubectl patch deployment backend -n todo-app -p '{"spec":{"template":{"spec":{"containers":[{"name":"backend","command":["/bin/sh","-c","exit 1"}]}}}}'

# Rollback
helm rollback todo-local -n todo-app

# Verify recovery
kubectl get pods -n todo-app
```

## References and Resources

### Official Documentation
- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker Hardened Images](https://github.com/GoogleContainerTools/distroless)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)
- [Kubernetes Security](https://kubernetes.io/docs/concepts/security/security-context/)
- [UV Package Manager](https://github.com/astral-sh/uv)

### Security Resources
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [Trivy Scanner](https://aquasecurity.github.io/trivy/)
- [Kubernetes Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)

### AIOps Resources
- [kubectl-ai](https://github.com/googlecloudplatform/kubectl-ai)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Kagent Autonomous Agents](https://github.com/anthropics/anthropic-sdk-typescript)

### Example Projects
- [Hello-Kubernetes Helm Chart](https://github.com/hashicorp/helm/tree/main/examples/hello-kubernetes)
- [Docker Multi-Stage Next.js](https://github.com/vercel/next.js/blob/canary/examples/docker-example/Dockerfile)
- [FastAPI Docker Deployment](https://fastapi.tiangolo.com/deployment/docker/)

---

**Next Steps**: This research document informs the implementation plan. Proceed with creating Dockerfiles, Helm chart templates, and AIOps integration as specified in `plan.md`.
