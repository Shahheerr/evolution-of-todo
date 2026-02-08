# Quickstart Guide: Local Kubernetes Deployment

**Phase**: IV - Local Kubernetes Deployment with AI-Native Operations
**Date**: 2026-02-06
**Audience**: Developers, DevOps engineers

## Overview

This guide provides step-by-step instructions for deploying the TaskFlow application to a local Minikube cluster using Helm charts. This is the fastest way to get the application running locally with containerization and Kubernetes orchestration.

## Prerequisites

### Software Requirements

| Tool | Version | Installation Check |
|------|---------|-------------------|
| Docker Desktop | Latest | `docker --version` |
| Minikube | v1.28+ | `minikube version` |
| kubectl | v1.28+ | `kubectl version --client` |
| Helm | v3.0+ | `helm version` |
| Trivy (optional) | Latest | `trivy --version` |

### Hardware Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 4GB | 8GB |
| CPU | 2 cores | 4 cores |
| Disk | 20GB | 30GB |

### Verify Prerequisites

```bash
# Check Docker
docker ps

# Check Minikube
minikube status

# If Minikube is not running, start it
minikube start

# Check kubectl can connect to Minikube
kubectl config current-context
kubectl get nodes

# Check Helm
helm version
```

## Quick Start (5 Minutes)

### Step 1: Build Container Images

```bash
# Navigate to project root
cd /mnt/d/web\ development/evolution-of-todo

# Build frontend image (~2-3 minutes)
cd frontend
docker build -t todo-frontend:local .

# Build backend image (~1-2 minutes)
cd ../backend
docker build -t todo-backend:local .
```

### Step 2: Load Images into Minikube

```bash
# Load both images into Minikube's internal registry (~30 seconds total)
minikube image load todo-frontend:local
minikube image load todo-backend:local

# Verify images are loaded
minikube image list | grep todo
```

### Step 3: Deploy with Helm

```bash
# Navigate to charts directory
cd /mnt/d/web\ development/evolution-of-todo

# Create namespace
kubectl create namespace todo-app

# Install the chart
helm install todo-local ./charts/todo-app \
  --namespace todo-app \
  --values charts/todo-app/values-dev.yaml

# Wait for pods to be ready (~2 minutes)
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-app-frontend -n todo-app --timeout=300s
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-app-backend -n todo-app --timeout=300s
```

### Step 4: Access the Application

```bash
# Get frontend URL
minikube service todo-frontend -n todo-app

# Or use port forwarding
kubectl port-forward svc/todo-frontend -n todo-app 3000:3000

# Open browser to http://localhost:3000
```

### Step 5: Verify Deployment

```bash
# Check all pods
kubectl get pods -n todo-app

# Check services
kubectl get svc -n todo-app

# Test health endpoints
kubectl exec -n todo-app deployment/backend -- curl http://localhost:8000/health
```

## Common Operations

### View Logs

```bash
# Frontend logs
kubectl logs -n todo-app deployment/frontend -l app=frontend

# Backend logs
kubectl logs -n todo-app deployment/backend -l app=backend

# Follow logs (streaming)
kubectl logs -f -n todo-app deployment/backend -l app=backend
```

### Shell into Container

```bash
# Frontend shell
kubectl exec -it -n todo-app deployment/frontend -- sh

# Backend shell
kubectl exec -it -n todo-app deployment/backend -- sh
```

### Restart Services

```bash
# Restart frontend
kubectl rollout restart deployment/frontend -n todo-app

# Restart backend
kubectl rollout restart deployment/backend -n todo-app
```

### Scale Replicas

```bash
# Scale frontend to 2 replicas
kubectl scale deployment/frontend -n todo-app --replicas=2

# Scale backend to 2 replicas
kubectl scale deployment/backend -n todo-app --replicas=2
```

## Update and Rollback

### Update Application

```bash
# Build new image version
cd frontend
docker build -t todo-frontend:v1.1.0 .

# Load into Minikube
minikube image load todo-frontend:v1.1.0

# Upgrade deployment
cd ../charts
helm upgrade todo-local ./charts/todo-app \
  --namespace todo-app \
  --set image.frontend.tag=v1.1.0
```

### Rollback Update

```bash
# Rollback to previous version
helm rollback todo-local -n todo-app

# Rollback to specific revision
helm rollback todo-local -n todo-app --revision 2

# View rollback history
helm history todo-local -n todo-app
```

## Troubleshooting

### Pods Not Starting

**Problem**: Pods stuck in Pending or CrashLoopBackOff state

```bash
# Check pod status
kubectl get pods -n todo-app

# Describe pod for events
kubectl describe pod <pod-name> -n todo-app

# Check pod logs
kubectl logs <pod-name> -n todo-app

# Check previous container logs (if crashed)
kubectl logs <pod-name> -n todo-app --previous
```

**Common causes**:
- Image pull errors: Verify images are loaded with `minikube image list | grep todo`
- Resource limits: Check `kubectl describe node` for available resources
- Missing secrets: Verify secrets exist with `kubectl get secrets -n todo-app`
- ConfigMap errors: Check `kubectl get configmap -n todo-app` for values

### Services Not Accessible

**Problem**: Cannot access application via browser or API

```bash
# Check service endpoints
kubectl get endpoints -n todo-app

# Check service configuration
kubectl describe svc todo-local-frontend -n todo-app

# Test service from within cluster
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -n todo-app -- curl http://todo-local-backend:8000/health

# Check port forwarding
kubectl port-forward svc/todo-local-frontend -n todo-app 3000:3000
```

**Common causes**:
- Wrong NodePort: Verify service type is NodePort for frontend
- Pod selector mismatch: Check pod labels match service selectors
- Network policies: Verify no policies blocking traffic

### Database Connection Issues

**Problem**: Backend cannot connect to PostgreSQL

```bash
# Check backend logs for database errors
kubectl logs -n todo-app -l app=backend --tail=50

# Verify DATABASE_URL in secret
kubectl get secret todo-local-backend-secrets -n todo-app -o jsonpath='{.data.database-url}' | base64 -d

# Test database connectivity from pod
kubectl exec -it -n todo-app <backend-pod> -- python -c "import asyncpg; asyncio.run(asyncpg.connect('<DATABASE_URL>'))"
```

**Common fixes**:
- Update DATABASE_URL in values.yaml or secret
- Verify database is accessible from cluster
- Check firewall rules allowing outbound connections

### Image Pull Errors

**Problem**: Pods stuck in ImagePullBackOff or ErrImagePull

```bash
# Verify images are loaded in Minikube
minikube image list | grep todo

# Rebuild and load images
cd frontend && docker build -t todo-frontend:local . && minikube image load todo-frontend:local
cd ../backend && docker build -t todo-backend:local . && minikube image load todo-backend:local

# Verify image references in deployment
kubectl get deployment todo-local-frontend -n todo-app -o jsonpath='{.spec.template.spec.containers[0].image}'
```

### Resource Issues

**Problem**: Pods killed due to OOMKilled or CPU throttling

```bash
# Check node resources
kubectl top nodes

# Check pod resource usage
kubectl top pods -n todo-app

# Describe resource quota
kubectl describe resourcequota -n todo-app

# Check pod limits
kubectl get pod <pod-name> -n todo-app -o jsonpath='{.spec.containers[0].resources}'
```

**Fixes**:
- Increase resource limits in values.yaml
- Upgrade Minikube memory: `minikube config set memory 4096`
- Scale down replicas: `kubectl scale deployment/todo-local-backend -n todo-app --replicas=1`

### Helm Install/Upgrade Failures

**Problem**: Helm command fails with errors

```bash
# Debug Helm install
helm install todo-local ./charts/todo-app --namespace todo-app --dry-run --debug

# Check Helm status
helm status todo-local -n todo-app

# View Helm history
helm history todo-local -n todo-app

# Uninstall and retry
helm uninstall todo-local -n todo-app
helm install todo-local ./charts/todo-app --namespace todo-app --values charts/todo-app/values-dev.yaml
```

## Cleanup

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n todo-app

# Describe pod for events
kubectl describe pod <pod-name> -n todo-app

# Check pod logs
kubectl logs <pod-name> -n todo-app
```

### Services Not Accessible

```bash
# Check service endpoints
kubectl get endpoints -n todo-app

# Test service from within cluster
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -n todo-app -- curl http://backend-service:8000/health
```

### Resource Issues

```bash
# Check node resources
kubectl top nodes

# Check pod resource usage
kubectl top pods -n todo-app

# Describe resource quotas
kubectl describe resourcequota -n todo-app
```

### Image Pull Issues

```bash
# Verify images are loaded in Minikube
minikube image list | grep todo

# Reload image if needed
minikube image load todo-frontend:local
```

## Cleanup

### Uninstall Application

```bash
# Uninstall the Helm release
helm uninstall todo-local -n todo-app

# Delete namespace
kubectl delete namespace todo-app

# Remove images from Minikube
minikube image rm todo-frontend:local todo-backend:local
```

### Complete Cleanup

```bash
# Stop Minikube
minikube stop

# Delete Minikube cluster (careful!)
minikube delete

# Remove Docker images
docker rmi todo-frontend:local todo-backend:local
```

## AIOps Operations

### Using kubectl-ai for Natural Language Queries

```bash
# Install kubectl-ai (if not already installed)
go install github.com/googlecloudplatform/kubectl-ai@latest

# Query cluster state
kubectl-ai "Show me all pods with high memory usage"
kubectl-ai "Why is the backend pod crashing?"
kubectl-ai "List all services in todo-app namespace"
```

### Using Kagent for Autonomous Remediation

```bash
# Install Kagent (if configured)
npm install -g @kagent/cli

# Start Kagent MCP server
cd aiops/kagent
python server.py

# Connect kubectl-ai to Kagent
kubectl-ai config set mcp-server http://localhost:8000/mcp

# Troubleshoot with AI
kubectl-ai "Fix the failing backend pod"
```

## Tips and Tricks

### Faster Iteration

```bash
# Build and load in one command (frontend)
cd frontend && docker build -t todo-frontend:local . && minikube image load todo-frontend:local &

# Build and load in one command (backend)
cd backend && docker build -t todo-backend:local . && minikube image load todo-backend:local &
```

### Resource Monitoring

```bash
# Watch pod status in real-time
kubectl get pods -n todo-app -w

# Watch deployment rollout
kubectl rollout status deployment/backend -n todo-app -w
```

### Debugging

```bash
# Port-forward to localhost
kubectl port-forward svc/todo-backend -n todo-app 8000:8000

# Access backend API locally
curl http://localhost:8000/health
```

## Production Deployment (Future)

For cloud deployment (AWS EKS, Google GKE, Azure AKS), see `values-prod.yaml` and the production deployment guide (to be created in Phase V).

## Support

For issues or questions:
- Check the main README: `/README.md`
- Check Phase IV specification: `specs/004-local-k8s-deployment/spec.md`
- Check the implementation plan: `specs/004-local-k8s-deployment/plan.md`

---

**Version**: 1.0.0
**Last Updated**: 2026-02-06
