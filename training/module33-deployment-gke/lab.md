---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 33: Deployment to GKE — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 33: Manually Deploying an Agent to GKE Challenge

## Goal

In this lab, you will learn the fundamental process of deploying an ADK agent to Google Kubernetes Engine (GKE), by deploying the same multi-agent Customer Support system from Module 32 — this time to GKE instead of Cloud Run. Walking through the manual steps of creating a `Dockerfile`, building a container, and writing Kubernetes manifests provides a deep understanding of the deployment process, and seeing the same application move between platforms makes the trade-offs concrete.

### Prerequisites

*   A Google Cloud Project with billing enabled.
*   Google Cloud CLI installed and authenticated.
*   `kubectl` command-line tool installed (`gcloud components install kubectl`).
*   Docker running on your local machine.

### Step 1: Prepare Your Project

<Setup/>

1.  **Create the Customer Support Agent Package:**
    We'll deploy the same multi-agent Customer Support architecture (`router_agent` delegating to `billing_agent` and `tech_support_agent`) inside a dedicated `support_agent/` Python package subdirectory. Placing the agent inside `support_agent/` ensures that when `adk api_server /app` runs in the container, it discovers the subdirectory name and mounts routes at `/apps/support_agent/...`:
    ```shell
    mkdir -p gke_support_agent/support_agent
    cd gke_support_agent
    ```

    *   **`support_agent/__init__.py`:**
        ```python
        from . import agent
        ```

    *   **`support_agent/agent.py`:** Complete the `# TODO` sections below to define the two specialist agents and the root router agent using `gemini-3.8-flash`:
        ```python
        from google.adk.agents import Agent

        # TODO: 1. Define `billing_agent` (name="billing_agent", model="gemini-3.8-flash")
        # to politely handle questions about billing, invoices, and payments.
        billing_agent = None

        # TODO: 2. Define `tech_support_agent` (name="tech_support_agent", model="gemini-3.8-flash")
        # to troubleshoot technical issues and provide clear solutions.
        tech_support_agent = None

        # TODO: 3. Define `root_agent` (name="router_agent", model="gemini-3.8-flash")
        # that delegates billing questions to `billing_agent` and technical problems
        # to `tech_support_agent` via `sub_agents=[billing_agent, tech_support_agent]`.
        root_agent = None
        ```

2.  **Set Environment Variables (Separating Infrastructure Region from Model Location):**
    In your terminal, export your project ID and `DEPLOY_REGION=us-central1` for Artifact Registry and the GKE cluster. Inside the Kubernetes pod manifest later, we will separately set `GOOGLE_CLOUD_LOCATION=global` so Vertex AI calls to `gemini-3.8-flash` hit the global endpoint instead of 404ing in `us-central1`. **Replace `YOUR_PROJECT_ID` with your actual GCP Project ID.**
    ```shell
    export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
    export DEPLOY_REGION=us-central1
    ```

3.  **Enable APIs:**
    ```shell
    gcloud services enable \
        aiplatform.googleapis.com \
        container.googleapis.com \
        artifactregistry.googleapis.com \
        cloudbuild.googleapis.com
    ```

### Step 2: Containerize the Agent

1.  **Create `requirements.txt`:**
    ```shell
    echo "google-adk" > requirements.txt
    ```

2.  **Create the `Dockerfile`:**
    Create a file named `Dockerfile` in `gke_support_agent/`. Notice how we copy `support_agent/` into `/app/support_agent/` (preserving `/app/support_agent/__init__.py` and `/app/support_agent/agent.py`) and pass `/app` as the `AGENTS_DIR` to `adk api_server`. If you copied files flat into `/app`, `adk api_server` would register the app name as `app` (`/apps/app/...`) instead of `support_agent` (`/apps/support_agent/...`)!
    ```dockerfile
    FROM python:3.11-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY support_agent/ /app/support_agent/
    EXPOSE 8080
    CMD ["adk", "api_server", "/app", "--host", "0.0.0.0", "--port", "8080"]
    ```

### Step 3: Build and Push the Container Image

1.  **Create an Artifact Registry Repository:**
    ```shell
    gcloud artifacts repositories create adk-images \
        --repository-format=docker \
        --location=$DEPLOY_REGION
    ```

2.  **Build and Push with Cloud Build:**
    ```shell
    gcloud builds submit \
        --tag ${DEPLOY_REGION}-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/adk-images/support-agent:v1
    ```

### Step 4: Create and Deploy to a GKE Cluster

1.  **Create a GKE Autopilot Cluster:** (This may take 5-10 minutes)
    ```shell
    gcloud container clusters create-auto adk-cluster \
        --location=$DEPLOY_REGION
    ```

2.  **Get Cluster Credentials:**
    ```shell
    gcloud container clusters get-credentials adk-cluster \
        --location=$DEPLOY_REGION
    ```

3.  **Create the Kubernetes Manifest (`deployment.yaml`):**
    Create a file named `deployment.yaml`. **Note the region separation:** the container image comes from `${DEPLOY_REGION}-docker.pkg.dev/...`, while inside the container `GOOGLE_GENAI_USE_ENTERPRISE="1"` and `GOOGLE_CLOUD_LOCATION="global"` ensure ADK 2.0's `google-genai` client routes `gemini-3.8-flash` requests to the global Vertex AI endpoint. Kubernetes resource names can't contain underscores, which is why `metadata.name` uses hyphens even though the Python package (`support_agent`) uses underscores.
    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: support-agent-deployment
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: support-agent
      template:
        metadata:
          labels:
            app: support-agent
        spec:
          containers:
          - name: support-agent
            image: ${DEPLOY_REGION}-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/adk-images/support-agent:v1
            ports:
            - containerPort: 8080
            env:
              - name: GOOGLE_GENAI_USE_ENTERPRISE
                value: "1"
              - name: GOOGLE_CLOUD_PROJECT
                value: "${GOOGLE_CLOUD_PROJECT}"
              - name: GOOGLE_CLOUD_LOCATION
                value: "global"
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: support-agent-service
    spec:
      type: LoadBalancer
      selector:
        app: support-agent
      ports:
      - protocol: TCP
        port: 80
        targetPort: 8080
    ```

4.  **Deploy the application:**
    This command substitutes `${DEPLOY_REGION}` and `${GOOGLE_CLOUD_PROJECT}` in your manifest and applies it to your cluster.
    ```shell
    envsubst < deployment.yaml | kubectl apply -f -
    ```
    *   **Note on `envsubst`:** This command substitutes shell environment variables (`DEPLOY_REGION`, `GOOGLE_CLOUD_PROJECT`) directly into `deployment.yaml` before `kubectl` applies it, while keeping `GOOGLE_CLOUD_LOCATION` pinned to `"global"`.

### Step 5: Test Your Deployed Agent

1.  **Get the External IP Address:**
    Run this command and wait until an `EXTERNAL-IP` is displayed. This can take a few minutes.
    ```shell
    kubectl get service support-agent-service --watch
    ```
    Once you see an IP, press `Ctrl+C` to exit and store it in a shell variable:
    ```shell
    export EXTERNAL_IP=$(kubectl get service support-agent-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    ```

2.  **Access the Agent via `curl`:**
    Unlike Module 32's `--with_ui` deployment, this container's `Dockerfile` runs `adk api_server` with no UI flag — opening `http://$EXTERNAL_IP` in a browser shows a bare `{"detail":"Not Found"}`, exactly as intended for a headless production service. Test the routing logic with `curl` against `/apps/support_agent/...`:
    ```shell
    # 1. Create session s1 for user u1 on support_agent
    curl -X POST "http://${EXTERNAL_IP}/apps/support_agent/users/u1/sessions/s1" \
      -H "Content-Type: application/json" \
      -d '{}'

    # 2. Send a billing inquiry via SSE streaming (routes to billing_agent)
    curl -X POST "http://${EXTERNAL_IP}/run_sse" \
      -H "Content-Type: application/json" \
      -d '{
        "app_name": "support_agent",
        "user_id": "u1",
        "session_id": "s1",
        "new_message": {
          "role": "user",
          "parts": [{"text": "I have a question about my invoice."}]
        }
      }'
    ```
    Repeat step 2 with `"My app keeps crashing."` to verify delegation to `tech_support_agent`.

### Lab Summary
You have successfully deployed the same multi-agent Customer Support system to GKE that you deployed to Cloud Run in Module 32. You learned to:
*   Package an ADK agent inside `/app/support_agent/` and serve `/app` with `adk api_server` so `/apps/support_agent/...` routes resolve cleanly.
*   Separate infrastructure region (`DEPLOY_REGION=us-central1`) from Vertex AI model inference location (`GOOGLE_CLOUD_LOCATION=global`).
*   Build and push a container image using Cloud Build and Artifact Registry.
*   Write Kubernetes `Deployment` and `Service` manifests and apply them with `envsubst` and `kubectl`.

### Bonus: The Automated Way

Now that you understand what happens under the hood, compare it to the ADK CLI shortcut that automates Steps 2-4 (containerization, push to Artifact Registry, manifest generation, and `kubectl apply`) in a single command:
```shell
uv run adk deploy gke \
    --project "$GOOGLE_CLOUD_PROJECT" \
    --cluster_name adk-cluster \
    --region "$DEPLOY_REGION" \
    --service_type=LoadBalancer \
    support_agent/
```
*(Or use `uvx google-agents-cli scaffold enhance . --adk -d gke --agent-directory support_agent` followed by `uvx google-agents-cli deploy` for full Terraform-managed Autopilot infrastructure.)*

### Cleanup (Important!)

GKE clusters can incur significant costs if left running. It is crucial to delete the resources you created after completing the lab.

1.  **Delete the GKE Cluster:**
    ```shell
    gcloud container clusters delete adk-cluster \
        --location=$DEPLOY_REGION \
        --async # Runs in background
    ```

2.  **Delete the Artifact Registry Repository:**
    ```shell
    gcloud artifacts repositories delete adk-images \
        --location=$DEPLOY_REGION \
        --async # Runs in background
    ```

3.  **Delete the `gke_support_agent` directory:**
    ```shell
    cd ..
    rm -rf gke_support_agent
    ```

### Self-Reflection Questions
- This lab was much more complex than the Cloud Run deployment. What are the key trade-offs you are making (in terms of complexity vs. control) when choosing GKE over Cloud Run?
- In the `deployment.yaml` file, what is the purpose of the `Deployment` object versus the `Service` object? Why do you need both?
- The `Dockerfile` uses `CMD ["adk", "api_server", ...]`. Why is it important to use `api_server` here instead of `web` for a production deployment?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="33">

# Lab 33 Solution: Manually Deploying an Agent to GKE

## Goal

This solution provides the complete `support_agent` Python package, container `Dockerfile`, and expected outputs for deploying the Customer Support agent on a GKE Autopilot cluster.

### Agent Package Solution

#### `support_agent/__init__.py`

```python
from . import agent
```

#### `support_agent/agent.py`

```python
from google.adk.agents import Agent

billing_agent = Agent(
    name="billing_agent",
    model="gemini-3.8-flash",
    description="Handles questions about billing, invoices, and payments.",
    instruction="You are a billing support agent. Politely answer questions about billing and payment issues.",
)

tech_support_agent = Agent(
    name="tech_support_agent",
    model="gemini-3.8-flash",
    description="Handles technical support questions and troubleshooting.",
    instruction="You are a technical support agent. Help users troubleshoot technical issues and provide clear solutions.",
)

root_agent = Agent(
    name="router_agent",
    model="gemini-3.8-flash",
    description="The main customer support router.",
    instruction="""
You are the customer support router.
Your job is to understand the user's request and delegate it to the correct specialist agent.
- If the user has a question about billing, delegate to the `billing_agent`.
- If the user has a technical problem, delegate to the `tech_support_agent`.
""",
    sub_agents=[billing_agent, tech_support_agent],
)
```

#### `Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY support_agent/ /app/support_agent/
EXPOSE 8080
CMD ["adk", "api_server", "/app", "--host", "0.0.0.0", "--port", "8080"]
```

### Expected Outputs

#### `gcloud builds submit`
After a successful build, the output will confirm the image was created and pushed, showing the image name and creation time.

#### `kubectl apply`
When you apply the manifest, you should see a confirmation that the deployment and service were created:
```
deployment.apps/support-agent-deployment created
service/support-agent-service created
```

#### `kubectl get service --watch`
This command will first show `<pending>` under the `EXTERNAL-IP` column. After a few minutes, GKE will provision a load balancer and the output will change to show a public IP address:
```
NAME                    TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)        AGE
support-agent-service   LoadBalancer   10.44.192.123   34.123.45.67    80:30123/TCP   2m30s
```
The `EXTERNAL-IP` is the public address of your agent.

### Expected Behavior

Navigating to `http://<EXTERNAL-IP>` in a browser returns a bare `{"detail":"Not Found"}` -- unlike Module 32's `--with_ui` Cloud Run deployment, this container's `Dockerfile` runs a headless `adk api_server` with no UI attached, which is exactly the point for a production deployment (see this module's Key Takeaways). Interact with the Customer Support system via `curl` instead: create a session against `/apps/support_agent/users/<id>/sessions/<id>`, then send a message via `/run_sse`. A billing question routes to `billing_agent`, a technical question routes to `tech_support_agent` — but this time it's running on your own GKE cluster instead of Cloud Run.

### Troubleshooting Common GKE Errors

*   **`kubectl apply` fails with `metadata.name: Invalid value ... a lowercase RFC 1123 label must consist of lower case alphanumeric characters or '-'`:**
    *   **Problem:** Kubernetes resource names (`metadata.name` on a `Deployment` or `Service`) cannot contain underscores — only lowercase letters, numbers, and hyphens. This is why `deployment.yaml` uses `support-agent-deployment`, not `support_agent-deployment`, even though the agent's own name (`router_agent`) and the container image tag (`support-agent:v1`) can use underscores freely — those live in different naming systems with different rules.
    *   **Solution:** Use hyphens, not underscores, in any `metadata.name` field.

*   **`ImagePullBackOff` or `ErrImagePull`:**
    *   **Problem:** The GKE cluster cannot pull the container image from Artifact Registry. This is almost always a permissions issue.
    *   **Solution:** Ensure the Artifact Registry API is enabled. Verify that the GKE node service account has the `Artifact Registry Reader` role. GKE Autopilot clusters usually handle this automatically, but Standard clusters may require manual configuration. Also, double-check that the image path in your `deployment.yaml` is exactly correct.

*   **`CrashLoopBackOff`:**
    *   **Problem:** The container is starting and then immediately crashing. This is an error within the container itself.
    *   **Solution:** Use `kubectl logs deployment/support-agent-deployment` to view the logs from the crashing pod. The logs will show the error message from the `adk api_server` command (e.g., a missing environment variable, a syntax error in an agent file, or — a common one — the agent directory argument not matching where the files actually landed inside the image).

*   **Service IP remains `<pending>`:**
    *   **Problem:** GKE is having trouble creating the external load balancer. This can happen due to project quota issues or incorrect network configurations.
    *   **Solution:** Use `kubectl describe service support-agent-service` to see the events associated with the service. The "Events" section at the bottom will usually contain a detailed error message from the cloud load balancer controller explaining the problem.

### Self-Reflection Answers

1.  **This lab was much more complex than the Cloud Run deployment. What are the key trade-offs you are making (in terms of complexity vs. control) when choosing GKE over Cloud Run?**
    *   **Answer:** The primary trade-off is **Control vs. Complexity**. GKE offers maximum control over underlying infrastructure (nodes, networking, specific hardware like GPUs), fine-grained security policies, and custom configurations. This flexibility comes at the cost of significantly higher operational complexity, requiring knowledge of Kubernetes concepts (Pods, Deployments, Services, etc.), YAML manifests, and `kubectl`. Cloud Run, conversely, prioritizes simplicity and ease of use, abstracting away most infrastructure concerns but offering less granular control. For simple, stateless agents, Cloud Run's low complexity and rapid deployment are highly advantageous; for complex microservices with specific infrastructure needs, GKE's control outweighs its complexity. Note that we deployed the *exact same agent* both times — the trade-off is purely about the platform, not the application.

2.  **In the `deployment.yaml` file, what is the purpose of the `Deployment` object versus the `Service` object? Why do you need both?**
    *   **Answer:**
        *   **`Deployment`:** The `Deployment` object is responsible for managing the *execution* of your application. It defines which container image to run, how many replicas (Pods) to maintain, and ensures that the desired number of agent instances are always running. It handles updates, rollbacks, and self-healing in case of failures.
        *   **`Service`:** The `Service` object is responsible for managing *access* to your application. It creates a stable network endpoint (like a public IP address) and a load balancer, routing external and internal traffic to the ephemeral Pods managed by the Deployment. Pods are transient and their IPs can change, so the Service provides a consistent way to reach the application.
        *   **Why both?** You need both because the Deployment ensures your agent is running reliably, while the Service ensures that clients can consistently *find and connect* to your running agent instances, abstracting away the dynamic nature of individual Pods.

3.  **The `Dockerfile` uses `CMD ["adk", "api_server", ...]`. Why is it important to use `api_server` here instead of `web` for a production deployment?**
    *   **Answer:** For a production deployment to GKE (or any backend service), it is critical to use `adk api_server` instead of `adk web`. The `api_server` command exposes a pure, headless REST API for programmatic consumption by other applications. In contrast, `adk web` includes the ADK Developer UI, which:
        *   **Security Risk:** Exposes sensitive internal information (e.g., agent's full instruction, tool definitions, detailed execution traces) that should not be publicly accessible in production.
        *   **Resource Overhead:** Adds unnecessary size to the container image and consumes additional memory and CPU resources, increasing operational costs for a service that will not be interacted with via a UI.
        Using `adk api_server` results in a leaner, more secure, and more efficient production deployment tailored for backend-to-backend communication.

</SolutionVault>
