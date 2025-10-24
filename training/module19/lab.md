# Module 19: Deployment to Google Kubernetes Engine (GKE)

## Lab 19: Manually Deploying an Agent to GKE

### Goal

In this lab, you will learn the fundamental, manual process of deploying an ADK agent to Google Kubernetes Engine (GKE). While the ADK provides helper commands, walking through the manual steps of creating a `Dockerfile`, building a container, and writing Kubernetes manifests provides a much deeper understanding of the deployment process.

You will deploy the simple "Echo" agent from Module 3.

### Prerequisites

*   A Google Cloud Project with billing enabled.
*   Google Cloud CLI installed and authenticated.
*   **`kubectl` command-line tool:** If you don't have it, install it by running `gcloud components install kubectl`.
*   **Docker:** You need Docker running on your local machine to build the container image.

### Step 1: Enable APIs and Set Up Your Project

1.  **Navigate to your training directory:**

    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Copy the Echo Agent:**
    We'll make a fresh copy of the `echo-agent` from Module 3 to prepare it for containerization.

    ```shell
    cp -r echo-agent/ gke-echo-agent/
    cd gke-echo-agent/
    ```

3.  **Set Environment Variables:**
    In your terminal, set these variables to make the following commands easier. Replace `YOUR_PROJECT_ID` with your actual GCP Project ID.

    ```shell
    export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
    export GOOGLE_CLOUD_LOCATION=us-central1
    ```

4.  **Enable Required APIs:**
    Run this command to ensure the necessary cloud services are enabled.

    ```shell
    gcloud services enable \
        container.googleapis.com \
        artifactregistry.googleapis.com \
        cloudbuild.googleapis.com
    ```

### Step 2: Containerize the Agent

We need to create a `Dockerfile` to tell Docker how to package our agent.

1.  **Create a `requirements.txt` file:**
    Our container will need to install the ADK.

    ```shell
    echo "google-adk" > requirements.txt
    ```

2.  **Create the `Dockerfile`:**
    Create a file named `Dockerfile` (no extension) in the `gke-echo-agent` directory and add the following content:

    ```dockerfile
    # Use an official lightweight Python image.
    FROM python:3.11-slim

    # Set the working directory in the container.
    WORKDIR /app

    # Copy the requirements file and install dependencies.
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    # Copy the rest of the agent's code into the container.
    COPY . .

    # The ADK server runs on port 8080 by default.
    EXPOSE 8080

    # The command to run when the container starts.
    # This starts the ADK web server, making the agent and UI available.
    CMD ["adk", "web", "--host", "0.0.0.0"]
    ```

### Step 3: Build and Push the Container Image

1.  **Create an Artifact Registry Repository:**
    This is a private registry to store your container images.

    ```shell
    gcloud artifacts repositories create adk-images \
        --repository-format=docker \
        --location=$GOOGLE_CLOUD_LOCATION
    ```

2.  **Build the image with Cloud Build:**
    This command will package your code, send it to Google Cloud Build, which will then build the Docker image and push it to your new repository.

    ```shell
    gcloud builds submit \
        --tag ${GOOGLE_CLOUD_LOCATION}-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/adk-images/echo-agent:v1
    ```

### Step 4: Create and Deploy to a GKE Cluster

1.  **Create a GKE Autopilot Cluster:**
    This command creates a managed, serverless GKE cluster. This may take 5-10 minutes.

    ```shell
    gcloud container clusters create-auto adk-cluster \
        --location=$GOOGLE_CLOUD_LOCATION
    ```

2.  **Get Cluster Credentials:**
    This configures `kubectl` to connect to your new cluster.

    ```shell
    gcloud container clusters get-credentials adk-cluster \
        --location=$GOOGLE_CLOUD_LOCATION
    ```

3.  **Create the Kubernetes Manifest (`deployment.yaml`):**
    This YAML file tells Kubernetes what to deploy. Create a file named `deployment.yaml` and add the following, making sure to replace `YOUR_PROJECT_ID` with your project ID.

    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: echo-agent-deployment
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: echo-agent
      template:
        metadata:
          labels:
            app: echo-agent
        spec:
          containers:
          - name: echo-agent
            # IMPORTANT: Replace YOUR_PROJECT_ID with your actual project ID
            image: ${GOOGLE_CLOUD_LOCATION}-docker.pkg.dev/YOUR_PROJECT_ID/adk-images/echo-agent:v1
            ports:
            - containerPort: 8080
            env:
              - name: GOOGLE_GENAI_USE_VERTEXAI
                value: "1"
              - name: GOOGLE_CLOUD_PROJECT
                value: "YOUR_PROJECT_ID" # Replace this too
              - name: GOOGLE_CLOUD_LOCATION
                value: "us-central1"
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: echo-agent-service
    spec:
      type: LoadBalancer
      selector:
        app: echo-agent
      ports:
      - protocol: TCP
        port: 80
        targetPort: 8080
    ```

4.  **Deploy the application:**
    Apply the manifest to your cluster using `kubectl`.

    ```shell
    kubectl apply -f deployment.yaml
    ```

### Step 5: Test Your Deployed Agent

1.  **Get the External IP Address:**
    It can take a few minutes for GKE to provision a public IP address for your service. Run the following command and wait until an "EXTERNAL-IP" is displayed.

    ```shell
    kubectl get service echo-agent-service --watch
    ```
    Once you see an IP, press `Ctrl+C` to exit.

2.  **Access the Agent:**
    Copy the external IP address and paste it into your web browser. You should see the ADK Dev UI.

3.  **Test the Agent:**
    Interact with your Echo agent. It is now running in a pod on your GKE cluster, fully orchestrated by Kubernetes.

### Lab Summary

Congratulations! You have successfully completed the manual deployment of an agent to GKE. This is a significant achievement and provides a deep understanding of how containerized applications are run in a production environment.

You have learned to:
*   Write a `Dockerfile` to containerize an ADK agent.
*   Build and push a container image to Google Artifact Registry using Cloud Build.
*   Create a GKE cluster.
*   Write a Kubernetes `Deployment` manifest to run your container.
*   Write a Kubernetes `Service` manifest to expose your agent to the internet.
*   Use `kubectl` to deploy and inspect your application.

In the final module, you will learn how to monitor your deployed agents using Google Cloud's observability tools.
