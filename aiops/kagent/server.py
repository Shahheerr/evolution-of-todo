#!/usr/bin/env python3
"""
Kagent MCP Server for Kubernetes Autonomous Operations

This server provides Model Context Protocol (MCP) tools for autonomous
Kubernetes troubleshooting and remediation.
"""

import asyncio
import logging
from typing import Any

from mcp.server.fastmcp import FastMCP
from kubernetes import client, config
from kubernetes.client.rest import ApiException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("kagent-k8s")

# Load Kubernetes configuration
try:
    config.load_kube_config()
except Exception:
    # Fall back to in-cluster config if kubeconfig not available
    try:
        config.load_incluster_config()
    except Exception:
        logger.warning("Could not load Kubernetes configuration")

# Initialize Kubernetes clients
corev1 = client.CoreV1Api()
appsV1 = client.AppsV1Api()


def format_pod_info(pod: Any) -> str:
    """Format pod information for human-readable output."""
    return (
        f"Pod: {pod.metadata.name}\n"
        f"  Namespace: {pod.metadata.namespace}\n"
        f"  Status: {pod.status.phase}\n"
        f"  Node: {pod.spec.node_name}\n"
        f"  Restart Count: {sum(container.restart_count for container in (pod.status.container_statuses or []))}\n"
        f"  Ready: {sum(1 for cs in (pod.status.container_statuses or []) if cs.ready)}/{len(pod.spec.containers or [])}"
    )


def format_container_state(state: Any) -> str:
    """Format container state information."""
    if state.running:
        return f"Running since {state.running.started_at}"
    elif state.waiting:
        return f"Waiting: {state.waiting.reason} - {state.waiting.message or ''}"
    elif state.terminated:
        return f"Terminated: {state.terminated.reason} (exit code: {state.terminated.exit_code})"
    return "Unknown state"


@mcp.tool()
async def list_pods(namespace: str = "todo-app") -> str:
    """
    List all pods in a namespace with their status.

    Args:
        namespace: Kubernetes namespace (default: todo-app)
    """
    try:
        pods = corev1.list_namespaced_pod(namespace=namespace)
        if not pods.items:
            return f"No pods found in namespace '{namespace}'"

        result = [f"Pods in namespace '{namespace}':\n"]
        for pod in pods.items:
            result.append(format_pod_info(pod))
            result.append("")

        return "\n".join(result)
    except ApiException as e:
        return f"Error listing pods: {e}"


@mcp.tool()
async def get_pod_logs(pod_name: str, namespace: str = "todo-app", tail_lines: int = 100) -> str:
    """
    Fetch logs from a specific pod.

    Args:
        pod_name: Name of the pod
        namespace: Kubernetes namespace (default: todo-app)
        tail_lines: Number of lines from the end of logs (default: 100)
    """
    try:
        logs = corev1.read_namespaced_pod_log(
            name=pod_name,
            namespace=namespace,
            tail_lines=tail_lines
        )
        return f"Logs from pod '{pod_name}':\n\n{logs}"
    except ApiException as e:
        return f"Error fetching logs from pod '{pod_name}': {e}"


@mcp.tool()
async def describe_pod(pod_name: str, namespace: str = "todo-app") -> str:
    """
    Get detailed information about a pod including events.

    Args:
        pod_name: Name of the pod
        namespace: Kubernetes namespace (default: todo-app)
    """
    try:
        pod = corev1.read_namespaced_pod(name=pod_name, namespace=namespace)
        events = corev1.list_namespaced_event(namespace=namespace, field_selector=f"involvedObject.name={pod_name}")

        result = [
            f"Pod Details: {pod_name}",
            "=" * 50,
            format_pod_info(pod),
            "\nContainers:",
        ]

        for container in pod.spec.containers:
            result.append(f"  - {container.name}: {container.image}")

        # Container statuses
        if pod.status.container_statuses:
            result.append("\nContainer Statuses:")
            for cs in pod.status.container_statuses:
                result.append(f"  - {cs.name}:")
                result.append(f"    Ready: {cs.ready}")
                result.append(f"    Restarts: {cs.restart_count}")
                result.append(f"    State: {format_container_state(cs.state)}")

        # Events
        if events.items:
            result.append("\nRecent Events:")
            for event in events.items[:10]:
                result.append(f"  - {event.type}: {event.message} ({event.last_timestamp})")

        return "\n".join(result)
    except ApiException as e:
        return f"Error describing pod '{pod_name}': {e}"


@mcp.tool()
async def restart_deployment(deployment_name: str, namespace: str = "todo-app") -> str:
    """
    Restart a deployment by rolling out a restart.

    Args:
        deployment_name: Name of the deployment (e.g., 'backend', 'frontend')
        namespace: Kubernetes namespace (default: todo-app)
    """
    try:
        # Find the full deployment name (includes release name)
        deployments = appsV1.list_namespaced_deployment(namespace=namespace)
        target_deployment = None

        for deployment in deployments.items:
            if deployment_name.lower() in deployment.metadata.name.lower():
                target_deployment = deployment.metadata.name
                break

        if not target_deployment:
            available = [d.metadata.name for d in deployments.items]
            return f"Deployment '{deployment_name}' not found. Available deployments: {available}"

        # Perform rollout restart
        appsV1.rollback_namespaced_deployment_rollout(
            name=target_deployment,
            namespace=namespace
        )

        return f"Successfully restarted deployment '{target_deployment}' in namespace '{namespace}'"
    except ApiException as e:
        return f"Error restarting deployment '{deployment_name}': {e}"


@mcp.tool()
async def analyze_pod_failure(pod_name: str, namespace: str = "todo-app") -> str:
    """
    Analyze a failing pod and provide diagnostic information.

    Args:
        pod_name: Name of the pod
        namespace: Kubernetes namespace (default: todo-app)
    """
    try:
        pod = corev1.read_namespaced_pod(name=pod_name, namespace=namespace)
        events = corev1.list_namespaced_event(namespace=namespace, field_selector=f"involvedObject.name={pod_name}")

        result = [
            f"Failure Analysis for Pod: {pod_name}",
            "=" * 50,
        ]

        # Check pod phase
        if pod.status.phase == "Failed":
            result.append("Pod Status: FAILED")

        # Check container states
        if pod.status.container_statuses:
            result.append("\nContainer Analysis:")
            for cs in pod.status.container_statuses:
                if not cs.ready or cs.restart_count > 0:
                    result.append(f"\n  Container: {cs.name}")
                    result.append(f"  Ready: {cs.ready}")
                    result.append(f"  Restarts: {cs.restart_count}")

                    # Last termination state
                    if cs.last_state and cs.last_state.terminated:
                        ls = cs.last_state.terminated
                        result.append(f"  Last Exit Code: {ls.exit_code}")
                        result.append(f"  Last Reason: {ls.reason}")
                        if ls.message:
                            result.append(f"  Last Message: {ls.message[:200]}")

        # Check events
        if events.items:
            result.append("\nRecent Events:")
            for event in events.items:
                if event.type == "Warning" or event.type == "Error":
                    result.append(f"  - {event.type}: {event.message}")

        # Recommendations
        result.append("\nRecommendations:")

        if pod.status.container_statuses:
            high_restart = any(cs.restart_count > 3 for cs in pod.status.container_statuses)
            if high_restart:
                result.append("  - Pod has high restart count. Consider:")
                result.append("    * Checking application logs for errors")
                result.append("    * Verifying environment variables are correct")
                result.append("    * Ensuring database connectivity")
                result.append("    * Checking resource limits")

        # Get recent logs
        try:
            logs = corev1.read_namespaced_pod_log(name=pod_name, namespace=namespace, tail_lines=20)
            result.append("\nRecent Logs (last 20 lines):")
            result.append("---")
            result.append(logs)
        except Exception:
            result.append("\nUnable to fetch logs")

        return "\n".join(result)
    except ApiException as e:
        return f"Error analyzing pod '{pod_name}': {e}"


@mcp.tool()
async def validate_deployment(namespace: str = "todo-app") -> str:
    """
    Validate all deployments in a namespace and report issues.

    Args:
        namespace: Kubernetes namespace (default: todo-app)
    """
    try:
        deployments = appsV1.list_namespaced_deployment(namespace=namespace)
        result = [f"Deployment Validation for namespace '{namespace}':", "=" * 50]

        issues_found = False

        for deployment in deployments.items:
            result.append(f"\nDeployment: {deployment.metadata.name}")

            # Check replicas
            spec_replicas = deployment.spec.replicas or 0
            status_replicas = deployment.status.available_replicas or 0
            status_ready = deployment.status.ready_replicas or 0

            result.append(f"  Desired Replicas: {spec_replicas}")
            result.append(f"  Available Replicas: {status_replicas}")
            result.append(f"  Ready Replicas: {status_ready}")

            if spec_replicas != status_replicas:
                issues_found = True
                result.append("  ⚠️  WARNING: Replica count mismatch!")

            # Check conditions
            for condition in deployment.status.conditions or []:
                if condition.status != "True":
                    issues_found = True
                    result.append(f"  ⚠️  {condition.type}: {condition.reason}")
                    result.append(f"      Message: {condition.message}")

            # Check pod status
            pods = corev1.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"app={deployment.metadata.name.split('-')[-1]}"
            )

            for pod in pods.items:
                if pod.status.phase != "Running":
                    issues_found = True
                    result.append(f"  ⚠️  Pod {pod.metadata.name} is {pod.status.phase}")

                for cs in pod.status.container_statuses or []:
                    if cs.waiting and cs.waiting.reason in ["ImagePullBackOff", "ErrImagePull", "CrashLoopBackOff"]:
                        issues_found = True
                        result.append(f"  ⚠️  Container {cs.name}: {cs.waiting.reason}")

        if not issues_found:
            result.append("\n✅ All deployments are healthy!")
        else:
            result.append("\n⚠️  Issues found. Please review the warnings above.")

        return "\n".join(result)
    except ApiException as e:
        return f"Error validating deployments: {e}"


@mcp.tool()
async def get_resource_usage(namespace: str = "todo-app") -> str:
    """
    Get resource usage for all pods in a namespace.

    Args:
        namespace: Kubernetes namespace (default: todo-app)
    """
    try:
        # This requires metrics-server to be installed
        from kubernetes import config as k8s_config
        from kubernetes.client import CustomObjectsApi

        api = CustomObjectsApi()

        # Try to get metrics from metrics-server
        try:
            pods = api.list_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=namespace,
                plural="pods"
            )

            result = [f"Resource Usage for namespace '{namespace}':", "=" * 50]

            for item in pods.get("items", []):
                pod_name = item["metadata"]["name"]
                result.append(f"\nPod: {pod_name}")

                for container in item.get("containers", []):
                    container_name = container["name"]
                    cpu_usage = container["usage"].get("cpu", "N/A")
                    memory_usage = container["usage"].get("memory", "N/A")
                    result.append(f"  {container_name}:")
                    result.append(f"    CPU: {cpu_usage}")
                    result.append(f"    Memory: {memory_usage}")

            return "\n".join(result)
        except Exception as e:
            return f"Resource metrics not available. Ensure metrics-server is installed: {e}"
    except Exception as e:
        return f"Error getting resource usage: {e}"


def main():
    """Start the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
