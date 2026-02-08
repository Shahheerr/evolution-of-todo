# Feature Specification: Local Kubernetes Deployment with AI-Native Operations

**Feature Branch**: `004-local-k8s-deployment`
**Created**: 2026-02-06
**Status**: Draft
**Input**: User description: "make specification and ACT AS: Lead Platform Engineer & Cloud-Native Architect. CONTEXT: We are transitioning the 'Evolution of Todo' project from a local web application (Phase III) to a Local Kubernetes Deployment (Phase IV). This is not just a standard deployment; it is an AI-Native Operations (AIOps) implementation. We will use Minikube as our local cloud and leverage advanced AI agents (Gordon, kubectl-ai, Kagent) to manage the infrastructure."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One-Command Local Deployment (Priority: P1)

A developer or DevOps engineer wants to deploy the entire TaskFlow application (frontend, backend, and their dependencies) to a local Kubernetes environment with a single command. Instead of manually building containers, writing Kubernetes YAML manifests, configuring Services, Ingress, and environment variables, they run one deployment command that handles everything.

**Why this priority**: This is the foundation of the entire phase. Without a working deployment, no other scenarios can be tested. It delivers immediate value by eliminating the manual, error-prone process of setting up a local Kubernetes environment.

**Independent Test**: Can be fully tested by running the deployment command and verifying that both frontend and backend pods are running, accessible, and can communicate with each other. Delivers a fully functional local Kubernetes environment that mirrors production.

**Acceptance Scenarios**:

1. **Given** a fresh Minikube cluster is running, **When** the developer runs the deployment command (e.g., `helm install todo-local ./charts/todo-app`), **Then** all pods (frontend, backend) start successfully and reach "Running" status within 3 minutes
2. **Given** the application is deployed, **When** the developer accesses the frontend URL, **Then** the application loads and responds to user interactions without errors
3. **Given** both services are running, **When** a user creates a task through the frontend, **Then** the task is successfully stored and retrieved, proving frontend-to-backend communication works

---

### User Story 2 - Secure Container Images (Priority: P1)

A security-conscious developer wants to ensure that the container images running in the cluster follow security best practices. They need images that are minimal (small attack surface), run as non-root users, and use verified base images. They should be able to verify the security posture before deploying.

**Why this priority**: Security is non-negotiable for production readiness. Running containers as root or using bloated images with unnecessary packages creates significant vulnerabilities. This enables the deployment to pass security audits and be safely promoted to production environments.

**Independent Test**: Can be fully tested by building the images and running security scanning tools (e.g., `docker scan`, `trivy`) to verify no known vulnerabilities, non-root user execution, and minimal image size. Delivers hardened, production-ready container images.

**Acceptance Scenarios**:

1. **Given** a Dockerfile for the frontend or backend, **When** the image is built, **Then** the final image size is under 500MB for backend and under 200MB for frontend (multi-stage optimization)
2. **Given** a running container, **When** the user inside the container is inspected, **Then** the process runs as a non-root user (UID 65532 or similar unprivileged user)
3. **Given** the built image, **When** a vulnerability scan is performed, **Then** zero critical or high-severity vulnerabilities are reported in the final image

---

### User Story 3 - AI-Assisted Operations and Troubleshooting (Priority: P2)

A developer encounters an issue in the Kubernetes cluster (e.g., a pod keeps crashing, a service is unreachable, or performance is degraded). Instead of manually debugging with `kubectl logs`, `kubectl describe`, and searching documentation, they use AI tools to describe the problem in natural language and receive actionable diagnostics and automated fixes.

**Why this priority**: This establishes the AIOps workflow that differentiates this phase from standard deployments. While not required for basic functionality, it dramatically reduces mean-time-to-resolution (MTTR) for operational issues and enables autonomous cluster management.

**Independent Test**: Can be tested by intentionally triggering a failure scenario (e.g., setting invalid environment variables, requesting excessive resources) and using kubectl-ai to diagnose and resolve the issue. Delivers an intelligent operations layer that can understand and fix cluster problems autonomously.

**Acceptance Scenarios**:

1. **Given** a pod is in a CrashLoopBackOff state, **When** the developer asks kubectl-ai "Why is the backend pod crashing?", **Then** the AI analyzes logs and events, identifies the root cause, and provides specific fix instructions or executes the fix via Kagent
2. **Given** the cluster is running, **When** the developer queries "Show me all pods with high memory usage", **Then** kubectl-ai translates this to the appropriate kubectl command and displays the results
3. **Given** a service is unreachable, **When** the developer uses the AI troubleshooting interface, **Then** the AI checks service configuration, endpoints, and pod labels, then identifies the misconfiguration

---

### User Story 4 - Environment-Specific Configuration Management (Priority: P2)

A developer needs to deploy the same application to different environments (local Minikube for development, cloud-based Kubernetes for production) with different configurations (resource limits, service types, replica counts, external URLs). They want to manage these differences without duplicating entire Helm charts or manifests.

**Why this priority**: This enables the same deployment artifacts to be reused across environments, reducing duplication and drift. While local deployment can work with hardcoded values, environment-specific configuration is essential for a production-ready deployment pipeline.

**Independent Test**: Can be tested by creating separate `values-dev.yaml` and `values-prod.yaml` files, deploying with each, and verifying that the appropriate configurations are applied (e.g., NodePort for dev, LoadBalancer for prod). Delivers a flexible deployment system that adapts to different target environments.

**Acceptance Scenarios**:

1. **Given** a Helm chart with default values, **When** deploying with `--values values-dev.yaml`, **Then** the deployment uses development-specific settings (e.g., 1 replica, resource limits suitable for local machine)
2. **Given** the same Helm chart, **When** deploying with `--values values-prod.yaml`, **Then** the deployment uses production-specific settings (e.g., 3 replicas, higher resource limits, external ingress)
3. **Given** environment-specific values files, **When** the application is deployed to different environments, **Then** all environment variables, service configurations, and resource settings are correctly applied without manual modifications

---

### User Story 5 - Zero-Downtime Rolling Updates (Priority: P3)

A developer has made changes to the application code and wants to deploy the new version without disrupting active users. The deployment should gradually replace old pods with new ones, ensuring that the application remains available throughout the update process.

**Why this priority**: This is a production-grade capability that improves user experience but is not critical for initial local development. It enables continuous deployment practices and ensures high availability.

**Independent Test**: Can be tested by deploying an initial version, then deploying an updated version with a changed image tag, and verifying that pods are replaced one at a time while the application remains accessible. Delivers a deployment strategy that maintains service availability during updates.

**Acceptance Scenarios**:

1. **Given** the application is deployed with version 1.0, **When** a new deployment is triggered with version 1.1, **Then** old pods are terminated gradually and new pods start, maintaining at least one available pod throughout
2. **Given** a rolling update is in progress, **When** the update encounters a failure (new pod fails to start), **Then** the deployment pauses and rolls back to the previous stable version automatically
3. **Given** a user is actively using the application during an update, **When** pods are being replaced, **Then** the user experiences no interruption in service or loss of session data

---

### Edge Cases

- What happens when Minikube runs out of memory or disk space during deployment?
- How does the system handle image pull failures or invalid image references?
- What happens when the database connection string is missing or invalid?
- How does the system behave when resource limits are set higher than what Minikube can provide?
- What happens if the Helm chart installation fails midway through deployment?
- How does the system handle port conflicts (e.g., port 3000 or 8000 already in use on the host)?
- What happens when the frontend cannot reach the backend due to incorrect service name configuration?
- How does the system handle secrets (e.g., BETTER_AUTH_SECRET, OPENAI_API_KEY) that are not provided?
- What happens when kubectl-ai or Kagent tools are unavailable or misconfigured?
- How does the system recover from a complete cluster restart?

## Requirements *(mandatory)*

### Functional Requirements

#### Container Image Requirements
- **FR-001**: Frontend container image MUST use a multi-stage build process to minimize final image size
- **FR-002**: Backend container image MUST use UV package manager for Python dependencies
- **FR-003**: All container images MUST run as a non-root user with UID 65532 (or similar unprivileged user)
- **FR-004**: All container images MUST use specific version tags for base images (not `latest` tags)
- **FR-005**: Container images MUST include only necessary runtime dependencies (no build tools, debug tools, or development libraries)
- **FR-006**: Container images MUST pass security vulnerability scanning with zero critical or high-severity vulnerabilities
- **FR-007**: All images MUST expose only necessary ports (frontend: 3000, backend: 8000)
- **FR-008**: Container images MUST handle graceful shutdown (SIGTERM) to allow in-flight requests to complete

#### Kubernetes Deployment Requirements
- **FR-009**: System MUST deploy Frontend as a Kubernetes Deployment with configurable replica count
- **FR-010**: System MUST deploy Backend as a Kubernetes Deployment with configurable replica count
- **FR-011**: System MUST create a Kubernetes Service for Backend with type ClusterIP
- **FR-012**: System MUST create a Kubernetes Service for Frontend with type NodePort or LoadBalancer
- **FR-013**: All Deployments MUST have resource limits defined for CPU and memory (to prevent Minikube exhaustion)
- **FR-014**: All Deployments MUST have resource requests defined for CPU and memory (for proper scheduling)
- **FR-015**: All Deployments MUST use liveness and readiness probes to detect and recover from unhealthy pods
- **FR-016**: All Deployments MUST specify a replication strategy for rolling updates with configurable maxUnavailable and maxSurge
- **FR-017**: System MUST configure pod anti-affinity rules to prevent all frontend/backend pods from scheduling on the same node (if multiple nodes available)
- **FR-018**: All Deployments MUST use persistent volume claims for any data that must survive pod restarts

#### Helm Chart Requirements
- **FR-019**: System MUST provide a single Helm chart named `todo-app` that deploys both frontend and backend
- **FR-020**: Helm chart MUST use `values.yaml` to configure all deployment parameters (image tags, replica counts, resource limits)
- **FR-021**: Helm chart MUST support environment-specific values files (e.g., `values-dev.yaml`, `values-prod.yaml`)
- **FR-022**: Helm chart MUST verify Kubernetes API compatibility for Minikube's version (avoid invalid API versions)
- **FR-023**: Helm chart MUST include configurable environment variables for all secrets (database URL, auth secrets, API keys)
- **FR-024**: Helm chart MUST NOT hardcode any secrets or sensitive configuration
- **FR-025**: Helm chart MUST support Ingress configuration for external access (disabled by default for Minikube)
- **FR-026**: Helm chart MUST include namespace configuration (create namespace if it doesn't exist)
- **FR-027**: Helm chart MUST support health check endpoints that verify deployment success

#### Networking Requirements
- **FR-028**: Frontend MUST communicate with Backend via Kubernetes Service name (not localhost or hardcoded IPs)
- **FR-029**: Backend Service MUST be accessible via a stable DNS name within the cluster
- **FR-030**: Frontend Service MUST be accessible from the host machine via Minikube tunnel or NodePort
- **FR-031**: System MUST support external database connections via environment variables (for production scenarios)
- **FR-032**: All Services MUST use appropriate selectors to route traffic to correct pods
- **FR-033**: Services MUST use session affinity if required by the application (stateful conversations)
- **FR-034**: Network policies MUST restrict pod-to-pod communication (frontend can only talk to backend, backend to database)

#### Configuration Management Requirements
- **FR-035**: System MUST support environment variable injection from Kubernetes ConfigMaps or Secrets
- **FR-036**: Database connection string MUST be configurable via environment variable
- **FR-037**: BETTER_AUTH_SECRET MUST be injected from Kubernetes Secret (not hardcoded)
- **FR-038**: OPENAI_API_KEY MUST be injected from Kubernetes Secret (not hardcoded)
- **FR-039**: System MUST support different configurations for frontend API URL (development vs production)

#### AIOps Requirements
- **FR-040**: System MUST integrate with kubectl-ai for natural language cluster queries
- **FR-041**: System MUST support Kagent (autonomous troubleshooting agent) via Model Context Protocol (MCP)
- **FR-042**: System MUST log all deployment operations for AI analysis and troubleshooting
- **FR-043**: System MUST expose cluster metrics (CPU, memory, pod status) for AI monitoring
- **FR-044**: AI tools MUST be able to diagnose common failures (crash loops, image pull errors, OOMKilled)
- **FR-045**: System MUST support automated remediation via Kagent for known failure patterns
- **FR-046**: System MUST provide audit logs of all AI-initiated changes to the cluster

#### Operational Requirements
- **FR-047**: Developer MUST be able to deploy the entire application with a single Helm command
- **FR-048**: Developer MUST be able to update the application by changing image tags in values and running upgrade
- **FR-049**: Developer MUST be able to rollback to a previous deployment via Helm rollback command
- **FR-050**: System MUST provide pre-flight checks before deployment (verify Minikube is running, resources are available)
- **FR-051**: Deployment MUST complete within 5 minutes on a standard Minikube configuration
- **FR-052**: System MUST provide clear error messages if deployment fails (with actionable next steps)
- **FR-053**: Developer MUST be able to uninstall the entire application with a single Helm command
- **FR-054**: System MUST preserve data (if any) across deployments and upgrades

### Key Entities

- **Container Image**: A packaged, versioned artifact containing the application code, runtime dependencies, and execution environment. Images are identified by registry, repository, and tag (e.g., `todo-backend:v1.0.0`).
- **Kubernetes Deployment**: A declarative specification for pod replicas and update strategy. Deployments ensure that a specified number of pod replicas are running at any given time.
- **Kubernetes Pod**: The smallest deployable unit in Kubernetes, containing one or more containers that share storage and network resources.
- **Kubernetes Service**: An abstraction that defines a logical set of pods and a policy for accessing them. Services provide stable network endpoints (DNS names, IPs) for pod groups.
- **Kubernetes Ingress**: A collection of rules that allow inbound connections to reach cluster services, typically used for HTTP/HTTPS routing from external sources.
- **Helm Chart**: A collection of files that describe a related set of Kubernetes resources. Charts use templates to generate manifests and values files to provide configuration.
- **ConfigMap**: A Kubernetes API object used to store non-confidential data in key-value pairs for injection into pods as environment variables or command-line arguments.
- **Secret**: A Kubernetes API object used to store sensitive data (passwords, keys, tokens). Secrets are encoded (base64) and can be mounted as files or exposed as environment variables.
- **AIOps Agent**: An AI-powered service that can monitor, diagnose, and remediate infrastructure issues autonomously. Agents communicate via protocols like MCP (Model Context Protocol).
- **Resource Limits**: Constraints on the amount of CPU and memory that a pod can use. Limits prevent runaway processes from exhausting cluster resources.
- **Resource Requests**: The guaranteed amount of CPU and memory that a pod is allocated. The Kubernetes scheduler uses requests to place pods on nodes with sufficient capacity.
- **Liveness Probe**: A Kubernetes mechanism to determine if a container is running. If the probe fails, the kubelet restarts the container.
- **Readiness Probe**: A Kubernetes mechanism to determine if a container is ready to serve traffic. If the probe fails, the pod is removed from service endpoints.
- **Rolling Update**: A deployment strategy that gradually replaces old pods with new ones, ensuring that some pods remain available during the update.
- **NodePort**: A service type that exposes a service on each node's IP at a static port, allowing external access to the service.
- **LoadBalancer**: A service type that provisions an external load balancer (e.g., from cloud provider) to route external traffic to the service.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developer can deploy the complete application (frontend + backend) to Minikube with a single command within 5 minutes
- **SC-002**: All container images pass security vulnerability scanning with zero critical or high-severity vulnerabilities
- **SC-003**: All pods reach "Running" and "Ready" status within 3 minutes of deployment initiation
- **SC-004**: Frontend-to-backend communication works correctly (tasks can be created, retrieved, and updated) with zero manual configuration changes
- **SC-005**: Application remains accessible during rolling updates with zero downtime (no failed user requests during update)
- **SC-006**: kubectl-ai can diagnose and provide remediation for common failure scenarios (crash loops, missing environment variables) within 30 seconds
- **SC-007**: Deployment uses less than 4GB of RAM and 2 CPU cores on Minikube (leaving headroom for other workloads)
- **SC-008**: Developer can switch between development and production configurations by changing a single `values` file parameter
- **SC-009**: All secrets are stored in Kubernetes Secrets (never in ConfigMaps or hardcoded in manifests)
- **SC-010**: Rollback to previous version completes within 2 minutes and restores full functionality
- **SC-011**: Application handles Minikube cluster restart gracefully (pods recover automatically, data persists)
- **SC-012**: AI tools (kubectl-ai, Kagent) can successfully query cluster state and execute basic operations (list pods, check logs, describe services)

### User Experience Outcomes

- **SC-013**: Developer needs no prior Kubernetes knowledge to deploy the application locally (Helm handles everything)
- **SC-014**: Deployment failure messages are clear and actionable (developer knows exactly what to fix)
- **SC-015**: Application feels responsive and stable (no unexpected crashes, slow responses, or connection errors)
- **SC-016**: AIOps tools reduce troubleshooting time for common issues by at least 50% compared to manual kubectl debugging

### Operational Outcomes

- **SC-017**: Deployment artifacts (Helm chart, Dockerfiles) are production-ready and can be promoted to cloud environments without modifications
- **SC-018**: All resource limits are documented and reasonable for the application's actual needs (no over-provisioning that wastes resources or under-provisioning that causes crashes)
- **SC-019**: Deployment process is fully reproducible (same Helm chart + values produces identical deployments across runs)
- **SC-020**: Application observability is sufficient (logs, metrics, health checks) to diagnose issues without SSH-ing into pods

## Constraints & Assumptions

### Technical Constraints

- Deployment target is Minikube running on the developer's local machine (not a cloud provider)
- Minikube is configured with default settings (2 CPUs, 2GB RAM, 20GB disk) unless developer customizes
- Developer has Docker Desktop installed with WSL 2 integration enabled
- Developer has kubectl and helm installed and configured to communicate with Minikube
- External database (Neon PostgreSQL) remains the database (no database containerization in this phase)
- Kubernetes API version is compatible with Minikube's current version (v1.28+)

### Assumptions

- Developer is familiar with basic command-line operations but may not be a Kubernetes expert
- Minikube cluster is healthy and has sufficient resources to run the application
- Developer has valid credentials for external services (Neon database, OpenAI API if using AI features)
- Developer's machine has at least 8GB RAM and 4 CPU cores to run Minikube alongside other applications
- Network connectivity allows Minikube to pull images from Docker registry (local or remote)
- kubectl-ai and Kagent tools are properly configured and can communicate with the cluster
- Docker images are built locally and loaded into Minikube (not pushed to remote registry in this phase)

### Scope Boundaries

#### In Scope
- Containerization of Next.js frontend application with multi-stage Dockerfile
- Containerization of FastAPI backend application with UV package management
- Helm chart for deploying both frontend and backend to Minikube
- Kubernetes resource definitions (Deployment, Service, ConfigMap, Secret)
- Environment-specific configuration management (dev vs prod values)
- Integration with kubectl-ai for natural language cluster queries
- Integration with Kagent for autonomous troubleshooting
- Security hardening of container images (non-root users, minimal base images)
- Health checks and readiness probes for all services
- Rolling update strategy for zero-downtime deployments
- Documentation for deployment and troubleshooting procedures

#### Out of Scope
- Containerization of the Neon PostgreSQL database (continues to use external database)
- Cloud provider deployment (AWS EKS, Google GKE, Azure AKS) - focused on Minikube only
- Production ingress configuration (TLS certificates, domain names, external load balancers)
- Container image registry setup (Docker Hub, ECR, GCR) - images loaded locally into Minikube
- Continuous Integration/Continuous Deployment (CI/CD) pipeline configuration
- Monitoring and observability stack (Prometheus, Grafana, ELK stack)
- Service mesh implementation (Istio, Linkerd)
- Advanced Kubernetes features (Custom Resource Definitions, Operators)
- Multi-cluster or multi-region deployment
- Backup and disaster recovery procedures
- Cost optimization and resource usage analytics

## Dependencies

### External Dependencies

- **Docker Desktop**: Required for building container images on Windows/Mac
- **Minikube**: Required as the local Kubernetes cluster runtime
- **kubectl**: Required for direct cluster interaction and verification
- **Helm 3.x**: Required for chart-based deployment management
- **Neon PostgreSQL**: Required as the external database service
- **kubectl-ai**: Required for natural language cluster queries (AIOps layer)
- **Kagent**: Required for autonomous troubleshooting via MCP (AIOps layer)

### Internal Dependencies

- **Phase III Codebase**: Complete frontend (Next.js) and backend (FastAPI) applications from Phase III
- **Phase III Configuration**: All environment variables and secrets currently defined in `.env` files
- **Dockerfiles**: New Dockerfiles for frontend and backend that adhere to Docker Hardened Images principles
- **Helm Chart**: New Helm chart templates and values files for deployment

### Integration Points

- **Frontend Application**: Must be adapted to run in a container (no filesystem dependencies, proper signal handling)
- **Backend Application**: Must be adapted to run in a container (database URL from environment, proper health check endpoint)
- **Environment Variables**: All configuration must be externalized to Kubernetes ConfigMaps/Secrets
- **Service Discovery**: Frontend must use Kubernetes Service names to communicate with backend
- **AIOps Tools**: kubectl-ai and Kagent must be configured with proper kubeconfig and MCP connections

### Prerequisites for Deployment

| Prerequisite | Version | Verification Command |
|--------------|---------|----------------------|
| Docker Desktop | Latest | `docker --version` |
| Minikube | v1.28+ | `minikube version` |
| kubectl | v1.28+ | `kubectl version --client` |
| Helm | v3.0+ | `helm version` |
| Cluster Status | Running | `minikube status` |
| Available Memory | ≥4GB | `minikube status` (shows Allocatable) |
| Available CPU | ≥2 cores | `minikube status` (shows CPUs) |

## Success Metrics Summary

| Category | Metric | Target | Measurement Method |
|----------|--------|--------|-------------------|
| Deployment Time | Time to running pods | ≤5 minutes | `kubectl get pods -w` |
| Image Security | Critical/High vulnerabilities | 0 | `trivy image <image>` |
| Resource Usage | Total RAM consumed | ≤4GB | `kubectl top nodes` |
| Availability | Uptime during rolling update | 100% | Application testing during update |
| AIOps Effectiveness | Time to diagnose common issues | ≤30 seconds | kubectl-ai query timing |
| Reproducibility | Deployment success rate (consecutive runs) | 100% | Deploy/undeploy cycle test |
| Configuration Flexibility | Time to switch environments | ≤1 minute | Change values file and upgrade |

---

**Next Steps**: After approval of this specification, proceed to `/sp.plan` to create the implementation plan covering Dockerfile creation, Helm chart templates, values files, and AIOps integration.
