#!/bin/bash
# Build script for Phase IV container images
# This script builds and validates container images for local Kubernetes deployment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================="
echo "TaskFlow - Container Image Build Script"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Check if Docker is running
print_status "$YELLOW" "Checking Docker..."
if ! docker ps &> /dev/null; then
    print_status "$RED" "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi
print_status "$GREEN" "Docker is running."
echo ""

# Build frontend image
print_status "$YELLOW" "Building frontend image..."
cd "$PROJECT_ROOT/frontend"
docker build -t todo-frontend:local .
print_status "$GREEN" "Frontend image built successfully."
echo ""

# Build backend image
print_status "$YELLOW" "Building backend image..."
cd "$PROJECT_ROOT/backend"
docker build -t todo-backend:local .
print_status "$GREEN" "Backend image built successfully."
echo ""

# Verify image sizes
print_status "$YELLOW" "Verifying image sizes..."
FRONTEND_SIZE=$(docker images todo-frontend:local --format "{{.Size}}")
BACKEND_SIZE=$(docker images todo-backend:local --format "{{.Size}}")

echo "Frontend image size: $FRONTEND_SIZE"
echo "Backend image size: $BACKEND_SIZE"

# Check if Trivy is installed
if command -v trivy &> /dev/null; then
    print_status "$YELLOW" "Running security scans..."
    echo ""

    print_status "$YELLOW" "Scanning frontend image..."
    trivy image --severity CRITICAL,HIGH todo-frontend:local
    echo ""

    print_status "$YELLOW" "Scanning backend image..."
    trivy image --severity CRITICAL,HIGH todo-backend:local
    echo ""

    print_status "$GREEN" "Security scans complete."
else
    print_status "$YELLOW" "Trivy not found. Skipping security scans."
    print_status "$YELLOW" "Install Trivy from: https://aquasecurity.github.io/trivy/"
fi

# Check if Minikube is running
if command -v minikube &> /dev/null; then
    if minikube status &> /dev/null; then
        print_status "$YELLOW" "Loading images into Minikube..."
        minikube image load todo-frontend:local
        minikube image load todo-backend:local
        print_status "$GREEN" "Images loaded into Minikube."
    else
        print_status "$YELLOW" "Minikube is not running. Skipping image load."
    fi
else
    print_status "$YELLOW" "Minikube not found. Skipping image load."
fi

echo ""
print_status "$GREEN" "========================================="
print_status "$GREEN" "Build complete!"
print_status "$GREEN" "========================================="
echo ""
echo "Next steps:"
echo "1. Update values.yaml with your DATABASE_URL and BETTER_AUTH_SECRET"
echo "2. Create namespace: kubectl create namespace todo-app"
echo "3. Install chart: helm install todo-local ./charts/todo-app --namespace todo-app --values charts/todo-app/values-dev.yaml"
echo "4. Check pods: kubectl get pods -n todo-app"
echo ""
