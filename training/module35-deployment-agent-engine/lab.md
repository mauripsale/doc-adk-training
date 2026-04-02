---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 35: Deploying an Agent to Agent Engine Challenge

## Goal
In this lab, you will deploy an ADK agent to Google Cloud's Agent Engine using both the recommended Accelerated method and the manual Standard method.

### Prerequisites
*   A Google Cloud Project with billing enabled.
*   `gcloud` CLI installed and authenticated (`gcloud auth application-default login`).
*   A GCS bucket for the Standard Deployment part (`gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://YOUR_UNIQUE_BUCKET_NAME`).
*   **Python Environment:** A Python version between 3.9 and 3.13.
*   **UV Tool:** For managing the Python environment. See [Install UV](https://github.com/astral-sh/uv#installation).
*   **Make Tool:** A build automation tool, typically pre-installed on Unix-based systems.
*   **Required APIs:** Ensure the following APIs are enabled in your project:
    *   Vertex AI API
    *   Cloud Build API
    *   Artifact Registry API
    *   Cloud Resource Manager API
*   **Set GCP Project:** Before starting, ensure your `gcloud` CLI is configured to the correct project:
    ```shell
    gcloud config set project YOUR_PROJECT_ID
    ```

---

## Part 1: Accelerated Deployment (Recommended)

This method uses the Agent Starter Pack (ASP) to add deployment artifacts to your existing ADK project and deploy it.

### Step 1: Prepare the Agent Project
1.  **Get an Agent:** For this lab, we'll use the `multi_tool_agent` from the Python Quickstart. If you don't have it, create it now. These instructions assume your project is in a directory structure like `your-project-directory/multi_tool_agent/`.
2.  **Navigate to the Parent Directory:** In your terminal, navigate to the parent directory that contains your agent folder (e.g., `your-project-directory/`).
3.  **Enhance the Project:** Run the ASP `enhance` command to add the required deployment files to your project.
    ```shell
    uvx agent-starter-pack enhance --adk -d agent_engine
    ```
4.  **Follow the Prompts:** The tool will ask you several questions. You can accept the defaults, but ensure you select a **supported region** for Agent Engine (e.g., `us-central1`).

### Step 2: Connect to Your Google Cloud Project
1.  **Login to Google Cloud:**
    ```shell
    gcloud auth application-default login
    ```
2.  **Set Your Project ID:**
    ```shell
    gcloud config set project your-project-id-xxxxx
    ```
3.  **Verify the Project:**
    ```shell
    gcloud config get-value project
    ```

### Step 3: Deploy the Agent
1.  **Ensure you are in the parent directory** (e.g., `your-project-directory/`).
2.  **Run the Deployment Command:** This command uses the `Makefile` added by the ASP tool to provision the cloud infrastructure and deploy your agent. This process can take several minutes.
    ```shell
    make backend
    ```
3.  **Find Your Agent:** Once the build is complete, navigate to **Vertex AI -> Agent Engine** in the Cloud Console to find your deployed agent and its ID.

---
sidebar_position: 2

## Part 2: Standard Deployment (Manual)

This method involves writing a custom Python script to deploy the agent.

### Step 1: Prepare the Agent Project
1.  **Get an Agent:** Copy the `multi_tool_agent` project to a new directory named `deploy_manual`.
    ```shell
    cp -r /path/to/multi_tool_agent deploy_manual
    cd deploy_manual
    ```
2.  **Install Dependencies:**
    ```shell
    pip install "google-cloud-aiplatform[adk,agent_engines]>=1.111"
    ```

### Step 2: Create the Deployment Script
1.  In the `deploy_manual` directory, create a new file named `deploy.py`.
2.  **Action:** Write the Python code to deploy the agent. Use the skeleton below and fill in the `# TODO` sections. You will need to:
    *   Import `vertexai`, `agent_engines`, and your `root_agent`.
    *   Initialize the Vertex AI SDK with your project details.
    *   Wrap your `root_agent` in an `agent_engines.AdkApp`.
    *   Call `agent_engines.create` to deploy the app.

    ```python
    # In deploy.py
    import vertexai
    from vertexai import agent_engines
    from multi_tool_agent.agent import root_agent # Make sure this import is correct

    # TODO: Fill in these values for your project
    PROJECT_ID = "your-gcp-project-id"
    LOCATION = "us-central1"
    STAGING_BUCKET = "gs://your-gcs-bucket-name"

    # Initialize the Vertex AI SDK
    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET,
    )

    # Wrap the agent in an AdkApp object
    app = agent_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )

    # TODO: Call agent_engines.create() to deploy the app.
    # Pass the `app` object to the `agent_engine` parameter.
    # Also provide a `requirements` list: ["google-cloud-aiplatform[adk,agent_engines]"]
    remote_app = None # Replace this

    print(f"Deployment finished!")
    print(f"Resource Name: {remote_app.resource_name}")
    ```

### Step 3: Test Agent Locally (Optional but Recommended)
**Action:** Before deploying, add the local testing code from the `lab-solution.md` to your `deploy.py` script (before the deployment call) to test the `AdkApp` locally. This helps you catch errors before starting the lengthy deployment process.

### Step 4: Deploy the Agent
Run the deployment script. This will take several minutes.
```shell
python deploy.py
```

### Step 5: Interact with the Deployed Agent
1.  Create an `interact.py` script (code available in `lab-solution.md`).
2.  **Action:** Configure the script with your `PROJECT_ID`, `LOCATION`, and the `AGENT_ENGINE_ID` from the deployment output.
3.  Run the script to test your deployed agent:
    ```shell
    python interact.py
    ```

### Cleanup (Important!)
Follow the cleanup instructions in `lab-solution.md` to delete the Agent Engine instances and GCS buckets to avoid incurring costs.

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMzUtZGVwbG95bWVudC1hZ2VudC1lbmdpbmUvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module35-deployment-agent-engine/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
