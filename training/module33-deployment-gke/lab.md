---
sidebar_position: 2
title: "Challenge Lab"
---

export const GOOGLE_CLOUD_LOCATION = '${GOOGLE_CLOUD_LOCATION}';
export const GOOGLE_CLOUD_PROJECT = '${GOOGLE_CLOUD_PROJECT}';

# Lab 33: Manually Deploying an Agent to GKE Challenge

## Goal

In this lab, you will learn the fundamental process of deploying an ADK agent to Google Kubernetes Engine (GKE). Walking through the manual steps of creating a `Dockerfile`, building a container, and writing Kubernetes manifests provides a deep understanding of the deployment process.

### Prerequisites

*   A Google Cloud Project with billing enabled.
*   Google Cloud CLI installed and authenticated.
*   `kubectl` command-line tool installed (`gcloud components install kubectl`).
*   Docker running on your local machine.

### Step 1: Prepare Your Project

1.  **Copy the Echo Agent:**
    Make a fresh copy of the `echo_agent` from Module 3.
    ```shell
    cp -r echo_agent/ gke_echo_agent/
    cd gke_echo_agent/
    ```

2.  **Update Agent Model:**
    Open `root_agent.yaml` and ensure the model is set to `gemini-3.5-flash`.
    ```yaml
    # In root_agent.yaml
    name: echo_agent
    model: gemini-3.5-flash # Ensure this is gemini-3.5-flash
    description: "An agent that repeats the user's input."
    instruction: "You are an echo agent. Your only job is to repeat the user's input back to them exactly as they wrote it."
    ```

3.  **Set Environment Variables:**
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
    Create a file named `Dockerfile` and add the following:
    ```dockerfile
    FROM python:3.11-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY . .
    EXPOSE 8080
    CMD ["adk", "api_server", "--host", "0.0.0.0", "echo_agent/"]
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
        --tag ${GOOGLE_CLOUD_LOCATION}-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/adk-images/echo_agent:v1
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
    Create a file named `deployment.yaml`. **Note the use of shell variables (`GOOGLE_CLOUD_LOCATION`, `GOOGLE_CLOUD_PROJECT`)**, which we will substitute in the next step.
    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: echo_agent-deployment
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: echo_agent
      template:
        metadata:
          labels:
            app: echo_agent
        spec:
          containers:
          - name: echo_agent
            image: ${GOOGLE_CLOUD_LOCATION}-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/adk-images/echo_agent:v1
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
      name: echo_agent-service
    spec:
      type: LoadBalancer
      selector:
        app: echo_agent
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
    kubectl get service echo_agent-service --watch
    ```
    Once you see an IP, press `Ctrl+C` to exit.

2.  **Access the Agent:**
    Copy the external IP address and paste it into your web browser. You should see the ADK Dev UI running on GKE.

### Lab Summary
You have successfully deployed an agent to GKE. You learned to:
*   Write a `Dockerfile` to containerize an ADK agent.
*   Build and push a container image using Cloud Build.
*   Create a GKE cluster.
*   Write Kubernetes `Deployment` and `Service` manifests.
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
    echo_agent/
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

3.  **Delete the `gke_echo_agent` directory:**
    ```shell
    cd ..
    rm -rf gke_echo_agent
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
