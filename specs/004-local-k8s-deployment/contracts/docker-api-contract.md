# Docker Build API Contract

**Phase**: IV - Local Kubernetes Deployment
**Component**: Container Image Build Process
**Status**: Specification

## Overview

This contract defines the Docker build process for both frontend and backend container images. It specifies build inputs, outputs, and validation requirements.

## Frontend Build Contract

### Build Inputs

| Input | Type | Description | Source |
|-------|------|-------------|--------|
| **Context** | Path | Build context directory | `./frontend/` |
| **Dockerfile** | File | Multi-stage Dockerfile | `./frontend/Dockerfile` |
| **.dockerignore** | File | Build exclusion patterns | `./frontend/.dockerignore` |
| **Node Version** | String | Node.js version | `20` (from base image) |
| **Next.js Version** | String | Next.js framework version | `16.1.6` (from package.json) |
| **Environment Variables** | Map | Build-time environment variables | `NEXT_PUBLIC_API_URL` |

### Build Process

```dockerfile
# Stage 1: Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Runtime
FROM node:20-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup -g 65532 -S nodejs
RUN adduser -S -u 65532 nodejs
COPY --from=builder --chown=65532:65532 /app/.next /app/.next
COPY --from=builder --chown=65532:65532 /app/public ./public
EXPOSE 3000
USER 65532
CMD ["npm", "start"]
```

### Build Outputs

| Output | Type | Description | Validation |
|--------|------|-------------|------------|
| **Image Tag** | String | Image identifier | `todo-frontend:local` |
| **Image Digest** | String | SHA256 content hash | Must be reproducible |
| **Image Size** | Number | Size in bytes | Must be ≤200MB |
| **Layer Count** | Number | Number of layers | Should be ≤10 layers |
| **Vulnerabilities** | ScanResult | Security scan result | 0 Critical/High |

### Non-Functional Requirements

| Requirement | Target | Measurement Method |
|-------------|--------|---------------------|
| Build Time | ≤3 minutes | `time docker build` |
| Image Size | ≤200MB | `docker images todo-frontend` |
| Startup Time | ≤30 seconds | `docker run --rm -p 3000:3000 todo-frontend` |
| Memory Usage | ≤256MB RSS | `docker stats` |
| Security Scan | 0 Critical/High | `trivy image todo-frontend:local` |

### Security Requirements

- [x] **Non-root User**: Process runs as UID 65532
- [x] **Read-Only Root**: Root filesystem is read-only
- [x] **No Secrets**: No secrets or credentials in image
- [x] **Minimal Base**: Alpine Linux base image
- [x] **Specific Tags**: No `latest` tags in Dockerfile
- [x] **Vulnerability Scan**: Passes Trivy with 0 Critical/High

### Environment Variables

| Variable | Type | Description | Default |
|----------|------|-------------|---------|
| `NODE_ENV` | String | Node environment | `production` |
| `PORT` | Number | Application port | `3000` |
| `NEXT_PUBLIC_API_URL` | String | Backend API URL | (from build args) |

### Health Check

```yaml
httpGet:
  path: /
  port: 3000
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

## Backend Build Contract

### Build Inputs

| Input | Type | Description | Source |
|-------|------|-------------|--------|
| **Context** | Path | Build context directory | `./backend/` |
| **Dockerfile** | File | Multi-stage Dockerfile | `./backend/Dockerfile` |
| **.dockerignore** | File | Build exclusion patterns | `./backend/.dockerignore` |
| **Python Version** | String | Python version | `3.13` (from base image) |
| **Package Manager** | String | Package manager tool | `uv` |
| **Dependencies** | File | Python dependencies | `pyproject.toml`, `uv.lock` |

### Build Process

```dockerfile
# Stage 1: Builder
FROM python:3.13-slim AS builder
WORKDIR /app
# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
# Copy dependency files
COPY pyproject.toml uv.lock ./
# Install dependencies
RUN uv pip install --system -r pyproject.toml

# Stage 2: Runtime
FROM python:3.13-slim AS runtime
WORKDIR /app
# Create non-root user
RUN groupadd -g 65532 appuser && \
    useradd -u 65532 -g appuser appuser
# Copy virtual environment from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
# Copy application code
COPY --chown=appuser:65532 . .
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build Outputs

| Output | Type | Description | Validation |
|--------|------|-------------|------------|
| **Image Tag** | String | Image identifier | `todo-backend:local` |
| **Image Digest** | String | SHA256 content hash | Must be reproducible |
| **Image Size** | Number | Size in bytes | Must be ≤500MB |
| **Layer Count** | Number | Number of layers | Should be ≤15 layers |
| **Vulnerabilities** | ScanResult | Security scan result | 0 Critical/High |

### Non-Functional Requirements

| Requirement | Target | Measurement Method |
|-------------|--------|---------------------|
| Build Time | ≤2 minutes | `time docker build` |
| Image Size | ≤500MB | `docker images todo-backend` |
| Startup Time | ≤30 seconds | `docker run --rm -p 8000:8000 todo-backend` |
| Memory Usage | ≤512MB RSS | `docker stats` |
| Security Scan | 0 Critical/High | `trivy image todo-backend:local` |

### Security Requirements

- [x] **Non-root User**: Process runs as UID 65532 (appuser)
- [x] **Read-Only Root**: Root filesystem is read-only
- [x] **No Secrets**: No secrets or credentials in image
- [x] **Slim Base**: Debian-based slim image (for UV compatibility)
- [x] **Specific Tags**: No `latest` tags in Dockerfile
- [x] **Vulnerability Scan**: Passes Trivy with 0 Critical/High

### Environment Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `DATABASE_URL` | String | Yes | PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | String | Yes | JWT signing secret (must match frontend) |
| `FRONTEND_URL` | String | Yes | CORS allowed origin |
| `OPENAI_API_KEY` | String | Optional | OpenAI API key for AI features |
| `AI_MODEL` | String | No | AI model name (default: gpt-4o-mini) |

### Health Check

```yaml
httpGet:
  path: /health
  port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

### Health Endpoint Response

```json
{
  "status": "healthy",
  "database": "healthy",
  "app": "Todo API"
}
```

## Build Commands

### Frontend Build

```bash
# Build frontend image
docker build \
  -f frontend/Dockerfile \
  -t todo-frontend:local \
  --build-arg NEXT_PUBLIC_API_URL=http://backend-service:8000/api \
  ./frontend

# Scan for vulnerabilities
trivy image todo-frontend:local

# Load into Minikube
minikube image load todo-frontend:local
```

### Backend Build

```bash
# Build backend image
docker build \
  -f backend/Dockerfile \
  -t todo-backend:local \
  ./backend

# Scan for vulnerabilities
trivy image todo-backend:local

# Load into Minikube
minikube image load todo-backend:local
```

## Build Verification Checklist

### Pre-Build Checks

- [ ] Docker Desktop is running
- [ ] Minikube is started (`minikube status`)
- [ ] Sufficient disk space for images (>2GB free)
- [ ] .env files are present (for reference only, not copied into images)
- [ ] No secrets in Dockerfiles or build context

### Post-Build Checks

- [ ] Image built successfully
- [ ] Image size within limits (frontend ≤200MB, backend ≤500MB)
- [ ] Image scan shows 0 Critical/High vulnerabilities
- [ ] Image loads into Minikube successfully
- [ ] Container starts and responds to health checks
- [ ] Non-root user verified (`id` command in container)

### Rollback Procedures

If build fails:
1. Check Docker daemon is running: `docker ps`
2. Check build logs for errors
3. Verify .dockerignore excludes unnecessary files
4. Clean build cache: `docker builder prune`
5. Retry build with `--no-cache` flag

If security scan fails:
1. Review vulnerability report from Trivy
2. Update base images to patched versions
3. Rebuild and rescan
4. If acceptable risk, document exception

## Integration with Kubernetes

### Image Registry Strategy

For local development:
1. Build images locally with Docker
2. Load images into Minikube: `minikube image load <image>`
3. Reference images in Helm values by local name

For production (future):
1. Build images with version tags
2. Push to container registry (Docker Hub, ECR, GCR)
3. Update Helm values to use registry images

### Image Tagging Convention

```
Development: todo-frontend:local, todo-backend:local
Production: todo-frontend:v1.0.0, todo-backend:v1.0.0
Testing: todo-frontend:dev, todo-backend:dev
```

---

**Contract Version**: 1.0.0
**Last Modified**: 2026-02-06
