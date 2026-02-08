# Data Model: Phase IV Kubernetes Deployment

**Feature**: Local Kubernetes Deployment with AI-Native Operations
**Date**: 2026-06-02
**Status**: Complete

## Overview

Phase IV introduces infrastructure artifacts rather than application data entities. This document describes the infrastructure data model for container images, Kubernetes resources, and Helm chart configuration.

## Infrastructure Entities

### ContainerImage

Immutable artifact containing application code, runtime dependencies, and execution environment.

**Attributes**:
| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| registry | string | Container registry (optional for local) | `docker.io`, empty for local |
| repository | string | Image repository name | `todo-frontend`, `todo-backend` |
| tag | string | Image version identifier | `local`, `v1.0.0`, `sha256:abc123...` |
| digest | string | Content-addressable hash | `sha256:abc123def456...` |
| size | number | Image size in bytes | `250000000` (250MB) |
| layers | array | Ordered list of layer digests | `["sha256:...", "sha256:..."]` |

**State Transitions**:
```
[Build] → [Scanned] → [Loaded into Minikube] → [Deployed]
  ↓         ↓            ↓                    ↓
Created   Verified     Available           Running
```

**Validation Rules**:
- `tag` must not be `latest` (specific version required)
- `size` must be ≤500MB for backend, ≤200MB for frontend
- `digest` must match the actual image content (integrity check)

### KubernetesDeployment

Declarative specification for pod replicas and update strategy.

**Attributes**:
| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| name | string | Deployment name | `frontend`, `backend` |
| namespace | string | Kubernetes namespace | `todo-app` |
| replicas | number | Desired replica count | `1`, `2`, `3` |
| strategy | string | Update strategy | `RollingUpdate` |
| template | object | Pod template | see PodTemplate |
| selector | object | Label selector | `{app: frontend}` |
| status | string | Deployment status | `Progressing`, `Available`, `ReplicaSet` |

**State Transitions**:
```
[Created] → [Progressing] → [Ready] → [Scaled]
   ↓           ↓              ↓         ↓
Pending    Updating      Healthy    Stable
```

**Validation Rules**:
- `replicas` must be ≥1
- `strategy` must be `RollingUpdate` (for zero downtime)
- `template` must include valid container specification

### KubernetesPod

Smallest deployable Kubernetes unit containing one or more containers.

**Attributes**:
| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| name | string | Pod name | `frontend-7d6f8c9k4-x`` |
| namespace | string | Kubernetes namespace | `todo-app` |
| phase | string | Pod lifecycle phase | `Pending`, `Running`, `Succeeded`, `Failed` |
| conditions | array | Pod readiness conditions | `[Ready: True]` |
| containers | array | Container specifications | see Container |
| nodeName | string | Node running the pod | `minikube` |

**State Transitions**:
```
[Pending] → [Running] → [Succeeded/Failed]
   ↓         ↓            ↓
Waiting   Ready        Terminated
```

### KubernetesService

Network abstraction that provides stable endpoints for pods.

**Attributes**:
| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| name | string | Service name | `backend-service`, `frontend` |
| namespace | string | Kubernetes namespace | `todo-app` |
| type | string | Service type | `ClusterIP`, `NodePort`, `LoadBalancer` |
| clusterIP | string | Internal cluster IP | `10.96.123.45` |
| externalIP | string | External IP (for LoadBalancer) | `192.168.49.2` |
| ports | array | Exposed ports | `[{port: 8000, targetPort: 8000}]` |
| selector | object | Label selector | `{app: backend}` |

**Service Types**:
- **ClusterIP**: Internal cluster access only (backend)
- **NodePort**: External access via node:port (frontend, dev)
- **LoadBalancer**: External load balancer (production, out of scope)

### KubernetesConfigMap

Non-sensitive configuration data injected into pods.

**Attributes**:
| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| name | string | ConfigMap name | `frontend-config`, `backend-config` |
| namespace | string | Kubernetes namespace | `todo-app` |
| data | object | Key-value pairs | `{API_URL: "http://..."}` |
| immutable | boolean | Whether ConfigMap is immutable | `false` |

**Frontend ConfigMap Data**:
```yaml
NEXT_PUBLIC_API_URL: "http://backend-service:8000/api"
NEXT_PUBLIC_APP_URL: "http://localhost:3000"
FRONTEND_URL: "http://localhost:3000"
```

**Backend ConfigMap Data**:
```yaml
FRONTEND_URL: "http://localhost:3000"
AI_MODEL: "gpt-4o-mini"
```

### KubernetesSecret

Sensitive configuration data (base64-encoded).

**Attributes**:
| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| name | string | Secret name | `backend-secrets`, `database-creds` |
| namespace | string | Kubernetes namespace | `todo-app` |
| type | string | Secret type | `Opaque` |
| data | object | Base64-encoded key-value pairs | `{DATABASE_URL: "cG9zdGdyZXN...=="}` |

**Backend Secret Data**:
```yaml
DATABASE_URL: "postgresql://user:pass@host:5432/db"
BETTER_AUTH_SECRET: "supersecretkey"
OPENAI_API_KEY: "sk-..."
```

### HelmChart

Package of Kubernetes resource templates and values.

**Attributes**:
| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| name | string | Chart name | `todo-app` |
| version | string | Chart version | `1.0.0` |
| description | string | Chart description | "TaskFlow Todo App" |
| templates | array | Kubernetes resource templates | `[deployment.yaml, service.yaml]` |
| values | object | Default configuration values | `{image: {...}}` |

**Values Schema**:
```yaml
image:
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
    limits: {cpu: 500m, memory: 512Mi}
    requests: {cpu: 250m, memory: 256Mi}
  backend:
    limits: {cpu: 500m, memory: 512Mi}
    requests: {cpu: 250m, memory: 256Mi}

env:
  databaseUrl: "postgresql://..."
  betterAuthSecret: "ref+secret://..."
  openaiApiKey: "ref+secret://..."

service:
  frontend: {type: NodePort, port: 3000}
  backend: {type: ClusterIP, port: 8000}

ingress:
  enabled: false
```

### AIOpsAgent

AI-powered service for cluster monitoring and remediation.

**Attributes**:
| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| name | string | Agent name | `kubectl-ai`, `kagent` |
| type | string | Agent type | `query`, `remediation` |
| protocol | string | Communication protocol | `mcp` (Model Context Protocol) |
| tools | array | Available operations | `[restart-pod, analyze-logs]` |

**kubectl-ai Agent**:
```yaml
name: kubectl-ai
type: query
tools:
  - get
  - describe
  - logs
  - exec
```

**Kagent Agent**:
```yaml
name: kagent
type: remediation
protocol: mcp
tools:
  - pod-restart
  - log-analyzer
  - config-validator
  - resource-check
```

## Relationships

```
ContainerImage ──┬──> KubernetesDeployment ──┬──> KubernetesPod ──┐
                   │                            │                      │
                   │                            ├──> KubernetesService ──┤
                   │                            │                      │
                   │                            └──> KubernetesConfigMap ─┤
                   │                            │                      │
                   └──────────────────────────────┴──> KubernetesSecret ──┘
                                                          │
                                           HelmChart ─────────┘
```

**Relationship Rules**:
1. **KubernetesDeployment** creates **KubernetesPods** based on its template
2. **KubernetesService** routes traffic to **KubernetesPods** via label selectors
3. **KubernetesConfigMap** injects configuration into **KubernetesPods**
4. **KubernetesSecret** injects secrets into **KubernetesPods**
5. **HelmChart** generates all Kubernetes resources from templates
6. **AIOpsAgent** monitors and modifies all Kubernetes resources

## Lifecycle Management

### Container Lifecycle

```
[Code] → [Dockerfile] → [Build] → [Image] → [Scan] → [Load] → [Deploy]
   ↓        ↓           ↓        ↓        ↓        ↓        ↓
Write   Define    Create   Push    Verify  Push    Run
```

### Deployment Lifecycle

```
[Helm Install] → [Pod Created] → [Container Started] → [Readiness Check] → [Ready]
      ↓               ↓                    ↓                     ↓
Chart Applied   Pod Running           Health Check          Serving Traffic
```

### Update Lifecycle

```
[Helm Upgrade] → [New Pod Created] → [Old Pod Terminated] → [Traffic Shifted] → [Complete]
      ↓                ↓                    ↓                     ↓
New Version    New Pod Running      Old Pod Removed      New Version Active
```

### Rollback Lifecycle

```
[Helm Rollback] → [Previous Revision Restored] → [New Pods Created] → [Old Pods Removed] → [Restored]
      ↓                      ↓                      ↓                     ↓
Rollback Command   Old Version Active      New Pods Removed    Previous Version Active
```

## State Transitions Summary

| Entity | States | Transition Triggers |
|--------|--------|-------------------|
| **Pod** | Pending → Running → Succeeded/Failed | Container startup, application exit |
| **Deployment** | Progressing → Available → ReplicaSet | Pod replica changes |
| **Service** | Type changes → Endpoint updates | Helm upgrade |
| **ConfigMap** | Created → Updated → Deleted | Helm upgrade, manual edits |
| **Secret** | Created → Updated → Deleted (recreated) | Helm upgrade, manual edits (Secrets are immutable) |

---

**Note**: Phase IV infrastructure entities describe deployment artifacts rather than application data. The application data model (User, Task, Session) remains unchanged from Phase III.
