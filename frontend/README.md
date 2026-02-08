# TaskFlow Frontend

This is the Next.js frontend for the TaskFlow application with Better Auth authentication and a modern dark theme UI.

## Getting Started (Local Development)

First, run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Container Build (Kubernetes Deployment)

### Build the Docker Image

```bash
docker build -t todo-frontend:local .
```

### Build Specifications

- **Base Image**: `node:20-alpine` (SHA256-pinned)
- **Multi-Stage Build**: Builder stage + Runtime stage
- **Non-Root User**: UID 65532 (nodejs)
- **Exposed Port**: 3000
- **Image Size**: Target ≤200MB

### Build Stages

1. **Builder Stage** (`node:20-alpine`)
   - Installs dependencies with `npm ci`
   - Generates Prisma client
   - Builds Next.js application with `npm run build`

2. **Runtime Stage** (`node:20-alpine`)
   - Copies only built artifacts from builder
   - Runs as non-root user (UID 65532)
   - Serves with `npm start`

### Security Features

- Non-root user execution (UID 65532)
- Specific version tags (no `latest`)
- Minimal Alpine base image
- Health check on port 3000

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NODE_ENV` | Node environment | `production` |
| `PORT` | Application port | `3000` |
| `NEXT_PUBLIC_API_URL` | Backend API URL | (from build args) |
| `NEXT_PUBLIC_APP_URL` | Frontend URL | (from build args) |
| `DATABASE_URL` | Prisma database | (from Kubernetes Secret) |
| `BETTER_AUTH_SECRET` | JWT signing secret | (from Kubernetes Secret) |

### Health Check

The container includes a Docker health check:
```bash
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"
```

### Scan for Vulnerabilities

```bash
trivy image todo-frontend:local --severity CRITICAL,HIGH
```

## Deploy on Kubernetes

### Using Helm

```bash
helm install todo-local ../charts/todo-app \
  --namespace todo-app \
  --set image.frontend.tag=local
```

### Manual Deployment

```bash
# Load image into Minikube
minikube image load todo-frontend:local

# Create deployment
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: todo-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: todo-frontend:local
        ports:
        - containerPort: 3000
EOF
```

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

## Deployment Documentation

- [Kubernetes Deployment Quickstart](../specs/004-local-k8s-deployment/quickstart.md)
- [Helm Chart Documentation](../charts/todo-app/README.md)
