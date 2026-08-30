---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 33: Manually Deploying an Agent to GKE Challenge

## Goal

In this lab, you will learn the fundamental process of deploying an ADK agent to Google Kubernetes Engine (GKE), by deploying the same multi-agent Customer Support system from Module 32 — this time to GKE instead of Cloud Run. Walking through the manual steps of creating a `Dockerfile`, building a container, and writing Kubernetes manifests provides a deep understanding of the deployment process, and seeing the same application move between platforms makes the trade-offs concrete.

### Prerequisites

*   A Google Cloud Project with billing enabled.
*   Google Cloud CLI installed and authenticated.
*   `kubectl` command-line tool installed (`gcloud components install kubectl`).
*   Docker running on your local machine.

### Step 1: Prepare Your Project

1.  **Re-create the Customer Support Agent:**
    We'll use the same multi-agent Customer Support system from Module 32. Let's create a fresh copy in its own directory.
    ```shell
    mkdir gke_support_agent
    cd gke_support_agent
    ```

    Create three YAML files, exactly as in Module 32:

    *   **`billing_agent.yaml`:**
        ```yaml
        name: billing_agent
        model: gemini-3.5-flash
        description: "Handles questions about billing, invoices, and payments."
        instruction: "You are a billing support agent. Politely answer questions about billing and payment issues."
        ```

    *   **`tech_support_agent.yaml`:**
        ```yaml
        name: tech_support_agent
        model: gemini-3.5-flash
        description: "Handles technical support questions and troubleshooting."
        instruction: "You are a technical support agent. Help users troubleshoot technical issues and provide clear solutions."
        ```

    *   **`root_agent.yaml`:**
        ```yaml
        name: router_agent
        model: gemini-3.5-flash
        description: "The main customer support router."
        instruction: |
          You are the customer support router.
          Your job is to understand the user's request and delegate it to the correct specialist agent.
          - If the user has a question about billing, delegate to the `billing_agent`.
          - If the user has a technical problem, delegate to the `tech_support_agent`.
        sub_agents:
          - config_path: billing_agent.yaml
          - config_path: tech_support_agent.yaml
        ```

2.  **Set Environment Variables:**
    In your terminal, set these variables. **Replace `YOUR_PROJECT_ID` with your actual GCP Project ID.**
    ```shell
    export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
    export GOOGLE_CLOUD_LOCATION=us-central1
    ```

3.  **Enable APIs:**
    ```shell
    gcloud services enable \
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
    Create a file named `Dockerfile` and add the following. Note that `.` is passed as the agent directory — since the YAML files are copied directly into `/app`, `/app` itself *is* the agent folder (there's no `support_agent/` subdirectory inside the image).
    ```dockerfile
    FROM python:3.11-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY . .
    EXPOSE 8080
    CMD ["adk", "api_server", "--host", "0.0.0.0", "--port=8080", "."]
    ```

### Step 3: Build and Push the Container Image

1.  **Create an Artifact Registry Repository:**
    ```shell
    gcloud artifacts repositories create adk-images \
        --repository-format=docker \
        --location=$GOOGLE_CLOUD_LOCATION
    ```

2.  **Build and Push with Cloud Build:**
    ```shell
    gcloud builds submit \
        --tag ${GOOGLE_CLOUD_LOCATION}-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/adk-images/support-agent:v1
    ```

### Step 4: Create and Deploy to a GKE Cluster

1.  **Create a GKE Autopilot Cluster:** (This may take 5-10 minutes)
    ```shell
    gcloud container clusters create-auto adk-cluster \
        --location=$GOOGLE_CLOUD_LOCATION
    ```

2.  **Get Cluster Credentials:**
    ```shell
    gcloud container clusters get-credentials adk-cluster \
        --location=$GOOGLE_CLOUD_LOCATION
    ```

3.  **Create the Kubernetes Manifest (`deployment.yaml`):**
    Create a file named `deployment.yaml`. **Note the use of shell variables (`GOOGLE_CLOUD_LOCATION`, `GOOGLE_CLOUD_PROJECT`)**, which we will substitute in the next step. Kubernetes resource names can't contain underscores, which is why these use hyphens even though the container image and agent names use underscores.
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
            image: ${GOOGLE_CLOUD_LOCATION}-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/adk-images/support-agent:v1
            ports:
            - containerPort: 8080
            env:
              - name: GOOGLE_GENAI_USE_VERTEXAI
                value: "1"
              - name: GOOGLE_CLOUD_PROJECT
                value: "${GOOGLE_CLOUD_PROJECT}"
              - name: GOOGLE_CLOUD_LOCATION
                value: "${GOOGLE_CLOUD_LOCATION}"
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
    This command substitutes the variables in your manifest and applies it to your cluster.
    ```shell
    envsubst < deployment.yaml | kubectl apply -f -
    ```
    *   **Note on `envsubst`:** This command is used to substitute the shell environment variables (like `GOOGLE_CLOUD_PROJECT`) directly into your `deployment.yaml` file before `kubectl` applies it.

### Step 5: Test Your Deployed Agent

1.  **Get the External IP Address:**
    Run this command and wait until an "EXTERNAL-IP" is displayed. This can take a few minutes.
    ```shell
    kubectl get service support-agent-service --watch
    ```
    Once you see an IP, press `Ctrl+C` to exit.

2.  **Access the Agent:**
    Copy the external IP address and paste it into your web browser. You should see the ADK Dev UI running on GKE. Test the same routing logic as in Module 32: a billing question should route to `billing_agent`, and a technical question should route to `tech_support_agent`.

### Lab Summary
You have successfully deployed the same multi-agent Customer Support system to GKE that you deployed to Cloud Run in Module 32. You learned to:
*   Write a `Dockerfile` to containerize an ADK agent.
*   Build and push a container image using Cloud Build.
*   Create a GKE cluster.
*   Write Kubernetes `Deployment` and `Service` manifests — and why their resource names can't use underscores.
*   Use `envsubst` and `kubectl` to deploy your application.

### Bonus: The Automated Way

Now that you understand what happens under the hood, compare it to the ADK CLI shortcut that automates Steps 2-4 (containerization, push to Artifact Registry, manifest generation, and `kubectl apply`) in a single command:
```shell
uv run adk deploy gke \
    --project $GOOGLE_CLOUD_PROJECT \
    --cluster_name adk-cluster \
    --region $GOOGLE_CLOUD_LOCATION \
    --service_type=LoadBalancer \
    --with_ui \
    .
```
You won't run this in the lab (you already deployed manually above), but knowing it exists — and now understanding exactly what it does for you — is valuable once you move past learning and into daily production work.

### Cleanup (Important!)

GKE clusters can incur significant costs if left running. It is crucial to delete the resources you created after completing the lab.

1.  **Delete the GKE Cluster:**
    ```shell
    gcloud container clusters delete adk-cluster \
        --location=$GOOGLE_CLOUD_LOCATION \
        --async # Runs in background
    ```

2.  **Delete the Artifact Registry Repository:**
    ```shell
    gcloud artifacts repositories delete adk-images \
        --location=$GOOGLE_CLOUD_LOCATION \
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

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMzMtZGVwbG95bWVudC1na2UvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module33-deployment-gke/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
