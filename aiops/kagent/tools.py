"""
Kagent Remediation Tools

This module provides autonomous remediation tools for common Kubernetes issues.
Tools are designed to safely diagnose and fix problems without human intervention.
"""

import logging
from typing import Optional

from kubernetes import client, config
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)


class KubernetesRemediationTools:
    """Autonomous Kubernetes remediation tools."""

    def __init__(self, namespace: str = "todo-app"):
        """Initialize Kubernetes client and namespace."""
        try:
            config.load_kube_config()
        except Exception:
            try:
                config.load_incluster_config()
            except Exception:
                logger.warning("Could not load Kubernetes configuration")

        self.namespace = namespace
        self.corev1 = client.CoreV1Api()
        self.appsV1 = client.AppsV1Api()

    def restart_pod(self, pod_name: str) -> dict:
        """
        Restart a specific pod by deleting it (Deployment will recreate it).

        Args:
            pod_name: Name of the pod to restart

        Returns:
            dict: Result of the restart operation
        """
        try:
            # Check if pod is owned by a Deployment
            pod = self.corev1.read_namespaced_pod(pod_name, self.namespace)

            owner_references = pod.metadata.owner_references or []
            deployment_owner = next(
                (ref for ref in owner_references if ref.kind == "ReplicaSet"),
                None
            )

            if deployment_owner:
                # Find the deployment
                replicaset = self.corev1.read_namespaced_replica_set(
                    deployment_owner.name, self.namespace
                )
                deployment_ref = next(
                    (ref for ref in replicaset.metadata.owner_references or [] if ref.kind == "Deployment"),
                    None
                )

                if deployment_ref:
                    # Perform rollout restart on the deployment
                    self.appsV1.rollback_namespaced_deployment_rollout(
                        name=deployment_ref.name,
                        namespace=self.namespace
                    )
                    return {
                        "status": "success",
                        "action": "deployment_restart",
                        "deployment": deployment_ref.name,
                        "message": f"Restarted deployment {deployment_ref.name} (will recreate pod {pod_name})"
                    }

            # If not owned by deployment, delete the pod directly
            self.corev1.delete_namespaced_pod(pod_name, self.namespace)
            return {
                "status": "success",
                "action": "pod_delete",
                "pod": pod_name,
                "message": f"Deleted pod {pod_name}"
            }

        except ApiException as e:
            return {
                "status": "error",
                "action": "restart_failed",
                "pod": pod_name,
                "message": str(e)
            }

    def analyze_logs(self, pod_name: str, container: Optional[str] = None, tail_lines: int = 100) -> dict:
        """
        Fetch and analyze pod logs for common error patterns.

        Args:
            pod_name: Name of the pod
            container: Container name (if multiple containers)
            tail_lines: Number of lines to fetch

        Returns:
            dict: Analysis results with detected issues
        """
        try:
            logs = self.corev1.read_namespaced_pod_log(
                name=pod_name,
                namespace=self.namespace,
                container=container,
                tail_lines=tail_lines
            )

            # Common error patterns
            error_patterns = {
                "OutOfMemory": ["OutOfMemory", "OOM", "memory limit"],
                "DatabaseConnection": ["connection refused", "could not connect", "database", "postgres"],
                "MissingSecret": ["secret", "not found", "no such file"],
                "ImagePullError": ["ImagePullBackOff", "ErrImagePull", "pull access denied"],
                "CrashLoop": ["exited with code", "entrypoint", "command not found"],
            }

            detected_issues = []

            for issue, patterns in error_patterns.items():
                for pattern in patterns:
                    if pattern.lower() in logs.lower():
                        detected_issues.append({
                            "issue": issue,
                            "pattern": pattern,
                            "suggestion": self._get_suggestion_for_issue(issue)
                        })
                        break

            return {
                "status": "success",
                "pod": pod_name,
                "issues_detected": detected_issues,
                "log_sample": logs[-500:] if len(logs) > 500 else logs
            }

        except ApiException as e:
            return {
                "status": "error",
                "pod": pod_name,
                "message": str(e)
            }

    def _get_suggestion_for_issue(self, issue: str) -> str:
        """Get remediation suggestion for a detected issue."""
        suggestions = {
            "OutOfMemory": "Increase memory limits in deployment or optimize application memory usage",
            "DatabaseConnection": "Verify DATABASE_URL is correct and database is accessible",
            "MissingSecret": "Ensure required secrets are created in the namespace",
            "ImagePullError": "Verify image name/tag is correct and registry is accessible",
            "CrashLoop": "Check application logs for startup errors, verify entrypoint command"
        }
        return suggestions.get(issue, "Review logs for specific error details")

    def validate_config(self, deployment_name: str) -> dict:
        """
        Validate deployment configuration and detect common issues.

        Args:
            deployment_name: Name of the deployment

        Returns:
            dict: Validation results with detected issues
        """
        issues = []

        try:
            deployment = self.appsV1.read_namespaced_deployment(deployment_name, self.namespace)

            # Check resource limits
            for container in deployment.spec.template.spec.containers:
                if not container.resources:
                    issues.append({
                        "container": container.name,
                        "issue": "NoResourceLimits",
                        "severity": "warning",
                        "message": f"Container {container.name} has no resource limits defined"
                    })
                else:
                    limits = container.resources.limits or {}
                    requests = container.resources.requests or {}

                    # Check if requests exceed limits
                    for resource in requests:
                        if resource in limits:
                            req_value = self._parse_resource(requests[resource])
                            limit_value = self._parse_resource(limits[resource])
                            if req_value > limit_value:
                                issues.append({
                                    "container": container.name,
                                    "issue": "RequestsExceedLimits",
                                    "severity": "error",
                                    "message": f"{resource} request ({requests[resource]}) exceeds limit ({limits[resource]})"
                                })

            # Check image tags
            for container in deployment.spec.template.spec.containers:
                image = container.image
                if ":latest" in image:
                    issues.append({
                        "container": container.name,
                        "issue": "UsingLatestTag",
                        "severity": "warning",
                        "message": f"Container {container.name} uses :latest tag, use specific version instead"
                    })

            # Check probe configuration
            for container in deployment.spec.template.spec.containers:
                if not container.liveness_probe and not container.readiness_probe:
                    issues.append({
                        "container": container.name,
                        "issue": "NoHealthChecks",
                        "severity": "warning",
                        "message": f"Container {container.name} has no liveness or readiness probes"
                    })

            return {
                "status": "success",
                "deployment": deployment_name,
                "issues": issues,
                "valid": len(issues) == 0
            }

        except ApiException as e:
            return {
                "status": "error",
                "deployment": deployment_name,
                "message": str(e)
            }

    def _parse_resource(self, value: str) -> float:
        """Parse Kubernetes resource string to numeric value."""
        value = value.strip()
        if value.endswith("m"):
            return float(value[:-1]) / 1000
        elif value.endswith("Mi"):
            return float(value[:-2]) / 1024
        elif value.endswith("Gi"):
            return float(value[:-2])
        else:
            return float(value)

    def scale_deployment(self, deployment_name: str, replicas: int) -> dict:
        """
        Scale a deployment to specified replica count.

        Args:
            deployment_name: Name of the deployment
            replicas: Desired number of replicas

        Returns:
            dict: Result of the scale operation
        """
        try:
            deployment = self.appsV1.read_namespaced_deployment(deployment_name, self.namespace)

            current_replicas = deployment.spec.replicas or 0
            deployment.spec.replicas = replicas

            self.appsV1.patch_namespaced_deployment(
                name=deployment_name,
                namespace=self.namespace,
                body=deployment
            )

            return {
                "status": "success",
                "deployment": deployment_name,
                "previous_replicas": current_replicas,
                "new_replicas": replicas,
                "message": f"Scaled {deployment_name} from {current_replicas} to {replicas} replicas"
            }

        except ApiException as e:
            return {
                "status": "error",
                "deployment": deployment_name,
                "message": str(e)
            }

    def get_pod_events(self, pod_name: str) -> dict:
        """
        Get events for a specific pod.

        Args:
            pod_name: Name of the pod

        Returns:
            dict: Pod events
        """
        try:
            events = self.corev1.list_namespaced_event(
                namespace=self.namespace,
                field_selector=f"involvedObject.name={pod_name}"
            )

            event_list = []
            for event in events.items:
                event_list.append({
                    "type": event.type,
                    "reason": event.reason,
                    "message": event.message,
                    "timestamp": event.last_timestamp.isoformat() if event.last_timestamp else None
                })

            return {
                "status": "success",
                "pod": pod_name,
                "events": event_list
            }

        except ApiException as e:
            return {
                "status": "error",
                "pod": pod_name,
                "message": str(e)
            }


# Convenience functions for direct use
def restart_pod(pod_name: str, namespace: str = "todo-app") -> dict:
    """Restart a pod by deleting it (Deployment will recreate it)."""
    tools = KubernetesRemediationTools(namespace)
    return tools.restart_pod(pod_name)


def analyze_logs(pod_name: str, namespace: str = "todo-app", tail_lines: int = 100) -> dict:
    """Analyze pod logs for common error patterns."""
    tools = KubernetesRemediationTools(namespace)
    return tools.analyze_logs(pod_name, tail_lines=tail_lines)


def validate_config(deployment_name: str, namespace: str = "todo-app") -> dict:
    """Validate deployment configuration."""
    tools = KubernetesRemediationTools(namespace)
    return tools.validate_config(deployment_name)
