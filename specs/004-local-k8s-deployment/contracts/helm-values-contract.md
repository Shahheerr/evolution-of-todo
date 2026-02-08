# Helm Values Contract

**Phase**: IV - Local Kubernetes Deployment
**Component**: Helm Chart Configuration
**Status**: Specification

## Overview

This contract defines the Helm chart values schema for deploying the TaskFlow application. It specifies configurable parameters, environment-specific overrides, and validation requirements.

## Values Schema

### Root Level Values

```yaml
# Global settings
global:
  # Kubernetes namespace where all resources are deployed
  namespace: string (default: "todo-app")

# Image configuration
image:
  # Pull policy for all images
  pullPolicy: "IfNotPresent" | "Always" | "Never"

  # Frontend image specification
  frontend:
    repository: string (default: "todo-frontend")
    tag: string (default: "local")
    pullPolicy: string (override global)

  # Backend image specification
  backend:
    repository: string (default: "todo-backend")
    tag: string (default: "local")
    pullPolicy: string (override global)

# Replica count for deployments
replicaCount:
  frontend: number (default: 1, min: 1, max: 3)
  backend: number (default: 1, min: 1, max: 3)

# Resource limits and requests
resources:
  # Frontend resources
  frontend:
    limits:
      cpu: string (default: "500m")
      memory: string (default: "512Mi")
    requests:
      cpu: string (default: "250m")
      memory: string (default: "256Mi")

  # Backend resources
  backend:
    limits:
      cpu: string (default: "500m")
      memory: string (default: "512Mi")
    requests:
      cpu: string (default: "250m")
      memory: string (default: "256Mi")

# Environment variables
env:
  # External database connection string
  databaseUrl: string (required)

  # JWT secret for authentication
  betterAuthSecret: string (required)

  # Frontend URL for CORS
  frontendUrl: string (default: "http://localhost:3000")

  # OpenAI API key for AI features (optional)
  openaiApiKey: string (optional)

  # AI model name
  aiModel: string (default: "gpt-4o-mini")

# Service configuration
service:
  # Frontend service
  frontend:
    type: "ClusterIP" | "NodePort" | "LoadBalancer" (default: "NodePort")
    port: number (default: 3000)
    targetPort: number (default: 3000)
    nodePort: number (optional, for NodePort type)
    annotations: object (optional)

  # Backend service
  backend:
    type: "ClusterIP" | "NodePort" | "LoadBalancer" (default: "ClusterIP")
    port: number (default: 8000)
    targetPort: number (default: 8000)
    annotations: object (optional)

# Ingress configuration
ingress:
  enabled: boolean (default: false)
  className: string (default: "nginx")
  host: string (default: "localhost")
  path: string (default: "/")
  annotations: object (optional)

# Health check configuration
healthCheck:
  # Frontend health check
  frontend:
    enabled: boolean (default: true)
    path: string (default: "/")
    initialDelaySeconds: number (default: 5)
    periodSeconds: number (default: 10)
    timeoutSeconds: number (default: 5)
    failureThreshold: number (default: 3)

  # Backend health check
  backend:
    enabled: boolean (default: true)
    path: string (default: "/health")
    initialDelaySeconds: number (default: 10)
    periodSeconds: number (default: 10)
    timeoutSeconds: number (default: 5)
    failureThreshold: number (default: 3)

# Pod anti-affinity rules (optional)
podAntiAffinity:
  # Prefer not to schedule frontend pods on same node
  frontend:
    enabled: boolean (default: false)
    weight: number (default: 100)

  # Prefer not to schedule backend pods on same node
  backend:
    enabled: boolean (default: false)
    weight: number (default: 100)

# Security context (security hardening)
securityContext:
  # Run as non-root user
  runAsUser: number (default: 65532)
  runAsGroup: number (default: 65532)
  fsGroup: number (default: 65532)

  # Read-only root filesystem
  readOnlyRootFilesystem: boolean (default: true)

  # Drop all capabilities
  capabilities:
    drop:
      - "ALL"
    add:
      - "NET_BIND_SERVICE"

# AIOps configuration (optional)
aiops:
  # kubectl-ai integration
  kubectlAi:
    enabled: boolean (default: false)
    model: string (default: "gpt-4")

  # Kagent integration
  kagent:
    enabled: boolean (default: false)
    mcpServer: string (default: "http://localhost:8000/mcp")
```

## Environment-Specific Values

### Development (values-dev.yaml)

```yaml
# Development overrides for local Minikube deployment

# Reduce replica count for resource conservation
replicaCount:
  frontend: 1
  backend: 1

# Conservative resource limits for Minikube
resources:
  frontend:
    limits:
      cpu: 250m
      memory: 256Mi
    requests:
      cpu: 125m
      memory: 128Mi
  backend:
    limits:
      cpu: 250m
      memory: 256Mi
    requests:
      cpu: 125m
      memory: 128Mi

# NodePort for local access
service:
  frontend:
    type: NodePort
    nodePort: 30000

# Ingress disabled for local development
ingress:
  enabled: false

# Pod anti-affinity disabled (single node cluster)
podAntiAffinity:
  frontend:
    enabled: false
  backend:
    enabled: false
```

### Production (values-prod.yaml)

```yaml
# Production overrides for cloud deployment

# Higher replica count for availability
replicaCount:
  frontend: 2
  backend: 2

# Higher resource limits for production workload
resources:
  frontend:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 500m
      memory: 512Mi
  backend:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 500m
      memory: 512Mi

# LoadBalancer for production
service:
  frontend:
    type: LoadBalancer
    annotations:
      service.beta.kubernetes.io/aws-load-balancer-type: "nlb"

# Enable ingress with TLS
ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"

# Pod anti-affinity enabled for high availability
podAntiAffinity:
  frontend:
    enabled: true
  backend:
    enabled: true

# Enable AIOps
aiops:
  kubectlAi:
    enabled: true
  kagent:
    enabled: true
```

## Secrets Management

### Required Secrets

The following secrets must be created before deployment:

```bash
# Database credentials
kubectl create secret generic database-creds \
  --from-literal=database-url="postgresql://user:pass@host:5432/db" \
  -n todo-app

# Authentication secret
kubectl create secret generic backend-secrets \
  --from-literal=better-auth-secret="<your-secret-key>" \
  -n todo-app

# OpenAI API key (optional)
kubectl create secret generic openai-creds \
  --from-literal=openai-api-key="sk-..." \
  -n todo-app
```

### Secret Reference in Values

Secrets are referenced in values.yaml using the format:

```yaml
env:
  databaseUrl: "ref+secret://database-creds#database-url"
  betterAuthSecret: "ref+secret://backend-secrets#better-auth-secret"
  openaiApiKey: "ref+secret://openai-creds#openai-api-key"
```

This Helm convention injects secret values into environment variables at deployment time.

## Validation Rules

### Resource Limits Validation

**Total Memory Calculation**:
```
Total Memory = (Frontend Requests + Backend Requests) + System Overhead
           = 256Mi + 256Mi + 500Mi
           = 1012Mi (within 2GB Minikube default)
```

**Resource Limit Validation**:
- `requests.cpu` must be ≤ `limits.cpu`
- `requests.memory` must be ≤ `limits.memory`
- Total requests for all pods must fit on a single node

### Port Configuration Validation

| Service | Port | TargetPort | Protocol | Purpose |
|---------|------|-----------|----------|---------|
| Frontend | 3000 | 3000 | TCP | HTTP/WebSocket |
| Backend | 8000 | 8000 | TCP | HTTP API |

### Health Check Validation

**Frontend**:
- Path `/` must return 200 OK
- Response must be served within 5 seconds
- Must handle graceful shutdown on SIGTERM

**Backend**:
- Path `/health` must return JSON with `{"status": "healthy"}`
- Response must be served within 5 seconds
- Database connectivity must be verified

## Deployment Verification

### Pre-Deploy Validation

```bash
# Verify images exist
minikube image list | grep todo

# Verify namespace exists or create
kubectl create namespace todo-app --dry-run=client

# Verify secrets exist
kubectl get secrets -n todo-app

# Dry-run install
helm install todo-local ./charts/todo-app \
  --namespace todo-app \
  --dry-run --debug
```

### Post-Deploy Validation

```bash
# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-app-frontend -n todo-app --timeout=300s
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-app-backend -n todo-app --timeout=300s

# Verify services
kubectl get svc -n todo-app

# Test connectivity
kubectl exec -n todo-app deployment/frontend -- curl http://backend-service:8000/health
```

## Rollback Procedures

### Manual Rollback

```bash
# List releases
helm list -n todo-app

# Rollback to previous revision
helm rollback todo-local -n todo-app

# Verify rollback
helm status todo-local -n todo-app
```

### Automated Rollback (Future)

```yaml
# Deployment policy (not implemented in Phase IV)
deploymentStrategy:
  rollingUpdate:
    maxUnavailable: 0
    maxSurge: 1
  rollback:
    autoRollback: true
    timeout: 5m
```

## Upgrade Strategy

### Version Upgrade Process

```bash
# Update image tag
helm upgrade todo-local ./charts/todo-app \
  --namespace todo-app \
  --set image.backend.tag=v1.1.0

# Wait for rollout to complete
kubectl rollout status deployment/backend -n todo-app -w
```

### Canary Deployment (Future)

Not implemented in Phase IV, but supported via Helm plugins:
```bash
helm upgrade todo-local ./charts/todo-app \
  --set canary.enabled=true \
  --set canary.image.tag=v1.1.0
```

---

**Contract Version**: 1.0.0
**Last Modified**: 2026-02-06
