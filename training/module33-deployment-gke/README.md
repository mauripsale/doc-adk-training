---
sidebar_position: 33
title: "Module 33: Deployment to Google Kubernetes Engine (GKE)"
---

# Module 33: Deployment to Google Kubernetes Engine (GKE)

## Theory

### When You Need More Control

In the previous module, you learned how to deploy your agent to Google Cloud Run, a serverless platform that is incredibly simple and cost-effective. For many use cases, Cloud Run is the perfect deployment target.

However, as your applications become more complex, you may find you need more control and flexibility than a serverless platform can offer. You might need to:
*   Deploy agents that have specific hardware requirements (like GPUs).
*   Have fine-grained control over networking and security policies.
*   Run other services alongside your agent in the same private network.
*   Manage complex, stateful workloads.

For these scenarios, the industry-standard solution is **Kubernetes**.

### What is Kubernetes?

Kubernetes (often abbreviated as K8s) is an open-source **container orchestration** platform. While a container platform like Docker runs a single container on a single machine, Kubernetes allows you to manage and run thousands of containers across a whole fleet of machines, known as a **cluster**.

It automates the deployment, scaling, and management of containerized applications. You tell Kubernetes the desired state of your application (e.g., "I want three copies of my agent container running at all times"), and Kubernetes works to maintain that state, automatically handling things like machine failures and load balancing.

### Google Kubernetes Engine (GKE)

Running and managing a Kubernetes cluster yourself can be incredibly complex. **Google Kubernetes Engine (GKE)** is a managed Kubernetes service provided by Google Cloud. It takes care of the heavy lifting of managing the cluster's infrastructure—like provisioning machines, managing the Kubernetes control plane, and handling upgrades—so you can focus on deploying your applications.

### Cloud Run vs. GKE: A Quick Comparison

| Feature | Google Cloud Run | Google Kubernetes Engine (GKE) |
| :--- | :--- | :--- |
| **Abstraction Level** | High (Serverless) | Medium (Managed Kubernetes) |
| **Control** | Less control, more automation | Full control over cluster configuration |
| **Use Case** | Stateless web apps, APIs, simple agents | Complex microservices, stateful apps, custom hardware |
| **Scaling** | Automatic, including scale-to-zero | Highly configurable auto-scaling |
| **Complexity** | Very low | Moderate to high |

In essence, Cloud Run prioritizes simplicity and ease of use, while GKE prioritizes flexibility and control.

### The Deployment Process to GKE

Deploying to GKE is a more involved process than deploying to Cloud Run, as it requires you to define your application's components using Kubernetes' own configuration language (which also uses YAML).

The general steps are:
1.  **Containerize your application:** Create a `Dockerfile` that specifies how to build a container image for your agent.
2.  **Build and Push the Image:** Build the container image and push it to a container registry (like Google Artifact Registry).
3.  **Create a GKE Cluster:** Provision a GKE cluster in your Google Cloud project.
4.  **Write Kubernetes Manifests:** Create YAML files that describe the desired state of your application to Kubernetes. This typically involves:
    *   A **Deployment:** Specifies which container image to run and how many replicas (copies) to maintain.
    *   A **Service:** Exposes your application to the internet by creating a public IP address and a load balancer.
5.  **Apply the Manifests:** Use the `kubectl` command-line tool to apply your manifest files to the GKE cluster, which triggers the deployment.

While the ADK provides the `adk deploy gke` command to automate some of these steps, understanding the underlying concepts is crucial for managing a production deployment on Kubernetes. In the lab, you will walk through the manual process to gain a deeper understanding of how GKE works.

### Key Takeaways
- **Google Kubernetes Engine (GKE)** is a managed container orchestration platform that provides more control and flexibility than serverless options like Cloud Run.
- GKE is the preferred choice for complex applications with specific hardware needs (like GPUs), fine-grained networking requirements, or for organizations already invested in the Kubernetes ecosystem.
- The deployment process to GKE is more involved, requiring you to containerize your application with a `Dockerfile` and define its desired state using Kubernetes **Manifests** (YAML files).
- Key Kubernetes objects include the **Deployment** (manages your application's running instances) and the **Service** (exposes your application to the network).
- You interact with a GKE cluster using the `kubectl` command-line tool.
- **`api_server` vs. `web` in Production:** It is critical to use `adk api_server` in a production `Dockerfile` instead of `adk web`. The `api_server` command exposes a pure, headless REST API for programmatic consumption, which is what's needed for a backend service. In contrast, `adk web` also includes the debug UI, which exposes sensitive internal information (like the agent's full instruction and reasoning trace) and adds unnecessary resource overhead, making it insecure and inefficient for production.
- **Deployment vs. Service Objects:** In Kubernetes, the `Deployment` and `Service` objects have distinct roles. The **Deployment** is responsible for the *execution* of the application; it defines which container image to run and how many replicas (Pods) to maintain, ensuring the agent is always running. The **Service** is responsible for *access*; it provides a stable network endpoint (like a public IP address) to the application, routing external traffic to the ephemeral Pods managed by the Deployment. You need both to run and expose an application.
- **GKE vs. Cloud Run Trade-off:** The primary trade-off between GKE and Cloud Run is **Control vs. Complexity**. GKE offers maximum control over nodes, networking, and hardware (like GPUs) but comes with higher operational complexity and slower deployment times. Cloud Run offers simplicity, rapid deployment, and a cost-effective pay-per-use model but provides less control. GKE is the right choice when the need for granular control outweighs the benefits of serverless simplicity.