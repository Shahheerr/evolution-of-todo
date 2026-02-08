# kubectl-ai Example Queries

This document provides example queries for using kubectl-ai with the TaskFlow application.

## Installation

```bash
# Install kubectl-ai
go install github.com/googlecloudplatform/kubectl-ai@latest

# Or download from releases
curl -LO https://github.com/googlecloudplatform/kubectl-ai/releases/latest/download/kubectl-ai_linux_amd64
chmod +x kubectl-ai_linux_amd64
sudo mv kubectl-ai_linux_amd64 /usr/local/bin/kubectl-ai
```

## Usage

```bash
# Basic query
kubectl-ai "Show me all pods"

# Specify namespace
kubectl-ai "Show pods in todo-app namespace"

# Natural language queries
kubectl-ai "Why is the backend pod crashing?"
kubectl-ai "What's using the most memory?"
kubectl-ai "Are all services healthy?"
```

## Example Queries by Category

### Pod Status

| Query | Description |
|-------|-------------|
| "Show me all pods" | List all pods in the namespace |
| "Why is the backend pod crashing?" | Diagnose crash loops |
| "Show pods with high memory usage" | List pods by memory consumption |
| "Are all pods running?" | Check pod health status |

### Logs

| Query | Description |
|-------|-------------|
| "Show backend logs" | Stream backend logs |
| "Show recent frontend logs" | Get recent frontend logs |
| "Show logs from crashed pod" | Get logs from previous container |

### Services

| Query | Description |
|-------|-------------|
| "Show all services" | List all services |
| "Is the backend service accessible?" | Check service health |
| "What endpoints are available?" | Show service endpoints |

### Deployments

| Query | Description |
|-------|-------------|
| "Show deployment status" | Get deployment rollout status |
| "Is the rollout complete?" | Check if rollout finished |
| "Show deployment history" | List deployment revisions |

### Resources

| Query | Description |
|-------|-------------|
| "What's using the most CPU?" | Sort pods by CPU usage |
| "Show resource usage" | Display CPU and memory for all pods |
| "Are we hitting resource limits?" | Check resource constraints |

## Troubleshooting Scenarios

### Scenario: Backend Pod Keeps Restarting

```bash
kubectl-ai "Why is the backend pod crashing?"
```

**Expected actions:**
1. Show pod status
2. Display recent crash logs
3. Check resource limits
4. Suggest next steps

### Scenario: Service Unreachable

```bash
kubectl-ai "Why can't I reach the backend service?"
```

**Expected actions:**
1. Check service endpoints
2. Verify pod labels match service selectors
3. Show network policies
4. Test connectivity

### Scenario: High Memory Usage

```bash
kubectl-ai "Which pod is using the most memory?"
```

**Expected actions:**
1. Show top pods by memory
2. Display resource limits vs usage
3. Identify potential memory leaks

## Integration with Kagent

When Kagent MCP server is enabled, kubectl-ai can execute remediation actions:

```bash
# Automatic remediation
kubectl-ai "Fix the failing backend pod"

# This will:
# 1. Analyze the problem
# 2. Call Kagent's pod-restart tool
# 3. Verify the fix worked
```

## Configuration

Edit `aiops/kubectl-ai/config.yaml` to customize:
- Model selection (gpt-4, gpt-3.5-turbo)
- Namespace context
- Enabled commands
- Resource limits
- Safety settings
