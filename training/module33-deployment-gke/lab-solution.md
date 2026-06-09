---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 33 Solution: Manually Deploying an Agent to GKE

## Goal

This lab is a procedural tutorial. The primary "solution" is a successfully deployed agent running on a GKE cluster, accessible via a public IP address.

### Expected Outputs

#### `gcloud builds submit`
After a successful build, the output will confirm the image was created and pushed, showing the image name and creation time.

#### `kubectl apply`
When you apply the manifest, you should see a confirmation that the deployment and service were created:
```
deployment.apps/echo_agent-deployment created
service/echo_agent-service created
```

#### `kubectl get service --watch`
This command will first show `<pending>` under the `EXTERNAL-IP` column. After a few minutes, GKE will provision a load balancer and the output will change to show a public IP address:
```
NAME                 TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)        AGE
echo_agent-service   LoadBalancer   10.44.192.123   34.123.45.67    80:30123/TCP   2m30s
```
The `EXTERNAL-IP` is the public address of your agent.

### Expected Behavior

When you navigate to the `http://<EXTERNAL-IP>` address in your browser, you should see the ADK Developer UI. You can interact with the "Echo" agent, and it will respond as it did locally.

### Troubleshooting Common GKE Errors

*   **`ImagePullBackOff` or `ErrImagePull`:**
    *   **Problem:** The GKE cluster cannot pull the container image from Artifact Registry. This is almost always a permissions issue.
    *   **Solution:** Ensure the Artifact Registry API is enabled. Verify that the GKE node service account has the `Artifact Registry Reader` role. GKE Autopilot clusters usually handle this automatically, but Standard clusters may require manual configuration. Also, double-check that the image path in your `deployment.yaml` is exactly correct.

*   **`CrashLoopBackOff`:**
    *   **Problem:** The container is starting and then immediately crashing. This is an error within the container itself.
    *   **Solution:** Use `kubectl logs deployment/echo_agent-deployment` to view the logs from the crashing pod. The logs will show the error message from the `uv run adk web` command (e.g., a missing environment variable, a syntax error in an agent file, etc.).

*   **Service IP remains `<pending>`:**
    *   **Problem:** GKE is having trouble creating the external load balancer. This can happen due to project quota issues or incorrect network configurations.
    *   **Solution:** Use `kubectl describe service echo_agent-service` to see the events associated with the service. The "Events" section at the bottom will usually contain a detailed error message from the cloud load balancer controller explaining the problem.

### Self-Reflection Answers

1.  **This lab was much more complex than the Cloud Run deployment. What are the key trade-offs you are making (in terms of complexity vs. control) when choosing GKE over Cloud Run?**
    *   **Answer:** The primary trade-off is **Control vs. Complexity**. GKE offers maximum control over underlying infrastructure (nodes, networking, specific hardware like GPUs), fine-grained security policies, and custom configurations. This flexibility comes at the cost of significantly higher operational complexity, requiring knowledge of Kubernetes concepts (Pods, Deployments, Services, etc.), YAML manifests, and `kubectl`. Cloud Run, conversely, prioritizes simplicity and ease of use, abstracting away most infrastructure concerns but offering less granular control. For simple, stateless agents, Cloud Run's low complexity and rapid deployment are highly advantageous; for complex microservices with specific infrastructure needs, GKE's control outweighs its complexity.

2.  **In the `deployment.yaml` file, what is the purpose of the `Deployment` object versus the `Service` object? Why do you need both?**
    *   **Answer:**
        *   **`Deployment`:** The `Deployment` object is responsible for managing the *execution* of your application. It defines which container image to run, how many replicas (Pods) to maintain, and ensures that the desired number of agent instances are always running. It handles updates, rollbacks, and self-healing in case of failures.
        *   **`Service`:** The `Service` object is responsible for managing *access* to your application. It creates a stable network endpoint (like a public IP address) and a load balancer, routing external and internal traffic to the ephemeral Pods managed by the Deployment. Pods are transient and their IPs can change, so the Service provides a consistent way to reach the application.
        *   **Why both?** You need both because the Deployment ensures your agent is running reliably, while the Service ensures that clients can consistently *find and connect* to your running agent instances, abstracting away the dynamic nature of individual Pods.

3.  **The `Dockerfile` uses `CMD ["uv", "run", "adk", "api_server", ...]`. Why is it important to use `api_server` here instead of `web` for a production deployment?**
    *   **Answer:** For a production deployment to GKE (or any backend service), it is critical to use `uv run adk api_server` instead of `uv run adk web`. The `api_server` command exposes a pure, headless REST API for programmatic consumption by other applications. In contrast, `uv run adk web` includes the ADK Developer UI, which:
        *   **Security Risk:** Exposes sensitive internal information (e.g., agent's full instruction, tool definitions, detailed execution traces) that should not be publicly accessible in production.
        *   **Resource Overhead:** Adds unnecessary size to the container image and consumes additional memory and CPU resources, increasing operational costs for a service that will not be interacted with via a UI.
        Using `uv run adk api_server` results in a leaner, more secure, and more efficient production deployment tailored for backend-to-backend communication.
