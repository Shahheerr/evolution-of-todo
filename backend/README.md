# TaskFlow Backend

This is the FastAPI backend for the TaskFlow application with JWT authentication and async PostgreSQL support.

## Getting Started (Local Development)

### Prerequisites

- Python 3.11+
- UV package manager ([Install UV](https://docs.astral.sh/uv/))
- PostgreSQL database (Neon recommended)

### Installation

```bash
# Install dependencies
uv sync

# Run the development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open [http://localhost:8000](http://localhost:8000) for the API.
Open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive API documentation (Swagger UI).

## Container Build (Kubernetes Deployment)

### Build the Docker Image

```bash
docker build -t todo-backend:local .
```

### Build Specifications

- **Base Image**: `python:3.13-slim` (SHA256-pinned)
- **Multi-Stage Build**: Builder stage + Runtime stage
- **Non-Root User**: UID 65532 (appuser)
- **Exposed Port**: 8000
- **Image Size**: Target ≤500MB
- **Package Manager**: UV (fast Python dependency installer)

### Build Stages

1. **Builder Stage** (`python:3.13-slim`)
   - Installs UV package manager
   - Copies `pyproject.toml` and `uv.lock`
   - Installs dependencies with `uv pip install --system`

2. **Runtime Stage** (`python:3.13-slim`)
   - Creates non-root user (UID 65532)
   - Copies Python dependencies from builder
   - Copies application code
   - Serves with uvicorn

### Security Features

- Non-root user execution (UID 65532)
- Specific version tags (no `latest`)
- Slim Debian base image (for UV compatibility)
- Health check on `/health` endpoint

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | Yes | JWT verification secret (must match frontend) |
| `FRONTEND_URL` | Yes | CORS allowed origin |
| `OPENAI_API_KEY` | Optional | OpenAI API key for AI chat features |
| `AI_MODEL` | No | AI model name (default: gpt-4o-mini) |

### Health Check

The container includes a Docker health check:
```bash
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
```

### Health Endpoint Response

```json
{
  "status": "healthy",
  "database": "healthy",
  "app": "Todo API"
}
```

### Scan for Vulnerabilities

```bash
trivy image todo-backend:local --severity CRITICAL,HIGH
```

## Deploy on Kubernetes

### Using Helm

```bash
helm install todo-local ../charts/todo-app \
  --namespace todo-app \
  --set image.backend.tag=local
```

### Manual Deployment

```bash
# Load image into Minikube
minikube image load todo-backend:local

# Create deployment
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: todo-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: todo-backend:local
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: backend-secrets
              key: database-url
        - name: BETTER_AUTH_SECRET
          valueFrom:
            secretKeyRef:
              name: backend-secrets
              key: better-auth-secret
EOF
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   ├── config.py        # Environment configuration
│   │   ├── database.py      # Database connection pool
│   │   └── security.py      # JWT verification
│   ├── models/
│   │   ├── auth.py          # Authentication models
│   │   └── task.py          # Task models
│   └── routes/
│       ├── __init__.py
│       ├── auth.py          # Authentication endpoints
│       ├── chat.py          # AI chat endpoints
│       └── tasks.py         # Task CRUD endpoints
├── tests/
│   ├── unit/
│   └── integration/
├── .env                     # Environment variables (not in container)
├── Dockerfile               # Container image definition
├── pyproject.toml           # Python dependencies
└── uv.lock                  # Dependency lock file
```

## API Documentation

### Authentication (JWT Required)

All endpoints (except `/health`) require a valid JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check (no auth required) |
| GET | `/api/tasks` | List tasks (with filters) |
| POST | `/api/tasks` | Create task |
| GET | `/api/tasks/{id}` | Get task by ID |
| PUT | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |
| POST | `/api/chat` | AI chat (optional, requires OPENAI_API_KEY) |

## Development Workflow

### Add New Dependency

```bash
uv add <package-name>
```

### Run Tests

```bash
uv run pytest
```

### Database Migration

Database schema is managed by the frontend Prisma client. Backend uses the same database connection.

## Deployment Documentation

- [Kubernetes Deployment Quickstart](../specs/004-local-k8s-deployment/quickstart.md)
- [Helm Chart Documentation](../charts/todo-app/README.md)
