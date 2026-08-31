---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 35: Deploying an Agent to Agent Runtime Challenge

## Goal
In this lab, you will deploy the same multi-agent Customer Support system from Modules 32 and 33 to Google Cloud's Agent Runtime, using both the recommended Accelerated method and the manual Standard method — completing the "same application, three platforms" arc for Part 6.

### Prerequisites
*   A Google Cloud Project with billing enabled.
*   `gcloud` CLI installed and authenticated (`gcloud auth application-default login`).
*   A GCS bucket for the Standard Deployment part (`gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://YOUR_UNIQUE_BUCKET_NAME`).
*   **Python Environment:** A Python version between 3.9 and 3.13.
*   **UV Tool:** For managing the Python environment. See [Install UV](https://github.com/astral-sh/uv#installation).
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

This method uses the Agents CLI to add deployment artifacts to your existing ADK project and deploy it.

### Step 1: Prepare the Agent Project
1.  **Re-create the Customer Support Agent:** We'll use the same multi-agent Customer Support system from Modules 32 and 33. Create a fresh directory and the same three YAML files:
    ```shell
    mkdir support_agent
    cd support_agent
    ```

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

2.  **Navigate to the Parent Directory:** In your terminal, navigate to the parent directory that contains `support_agent/`.
3.  **Scaffold the Project:** Run the Agents CLI `scaffold enhance` command to add the required deployment files to your project. Pass `--agent-directory support_agent` so the CLI correctly detects your YAML config agent in `support_agent/` — without it, the CLI can't find your agent code and silently generates an unrelated generic stub agent instead.
    ```shell
    uvx google-agents-cli scaffold enhance -d agent_runtime --agent-directory support_agent
    ```
    The command should report `Found support_agent/root_agent.yaml (YAML config agent)` and generate a `support_agent/agent.py` shim (via `config_agent_utils.from_config(...)`) that loads your `router_agent` and its `billing_agent`/`tech_support_agent` sub-agents — that's how you know it picked up the right project.
4.  **Follow the Prompts:** The tool will ask you several questions. You can accept the defaults, but ensure you select a **supported region** for Agent Runtime (e.g., `us-central1`).

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
1.  **Ensure you are in the parent directory** (containing `support_agent/`).
2.  **Run the Deployment Command:** This command uses the files added by the Agents CLI to provision the cloud infrastructure and deploy your agent. This process can take several minutes.
    ```shell
    uvx google-agents-cli deploy
    ```
3.  **Find Your Agent:** Once the build is complete, navigate to **Agent Platform -> Agent Runtime** in the Cloud Console to find your deployed agent and its ID.

---

## Part 2: Standard Deployment (Manual)

This method involves writing a custom Python script to deploy the agent. Unlike Part 1, this script needs to `import` your `root_agent` directly as a Python object — so this part uses a **Python-code version** of the same Customer Support system, instead of the YAML config version.

### Step 1: Prepare the Agent Project
1.  **Create the Python version of the Customer Support agent:**
    ```shell
    mkdir deploy_manual
    cd deploy_manual
    mkdir support_agent
    touch support_agent/__init__.py
    ```
2.  **Action:** Create `support_agent/agent.py`, translating the same router + two specialists design from Module 32 into Python `Agent` objects (instead of YAML config). Use the skeleton below and fill in the `# TODO` sections.
    ```python
    # In support_agent/agent.py
    from google.adk import Agent

    # TODO: 1. Define billing_agent, an Agent with name="billing_agent",
    # the same model/description/instruction as billing_agent.yaml above.

    # TODO: 2. Define tech_support_agent, an Agent with name="tech_support_agent",
    # the same model/description/instruction as tech_support_agent.yaml above.

    # TODO: 3. Define root_agent, an Agent named "router_agent" with the same
    # instruction as root_agent.yaml, and sub_agents=[billing_agent, tech_support_agent].
    ```
3.  **Install Dependencies:**
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
    from support_agent.agent import root_agent # Make sure this import is correct

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
    app = agent_engines.AdkApp(agent=root_agent)

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
3.  Run the script to test your deployed agent — try a billing question and a technical question, and confirm each routes to the correct specialist, exactly like in Modules 32 and 33:
    ```shell
    python interact.py
    ```

### Cleanup (Important!)
Follow the cleanup instructions in `lab-solution.md` to delete the Agent Runtime instances and GCS buckets to avoid incurring costs.

### Self-Reflection Questions
- What are the primary advantages of using the Accelerated Deployment method with the Agents CLI compared to the Standard Deployment method for production use?
- Agent Runtime is a managed backend. How does this simplify the development of complex clients (e.g., web or mobile applications) that interact with your agent?
- For what scenarios might the Standard Deployment method (using `deploy.py` and the Vertex AI SDK) still be advantageous, even if Accelerated Deployment is generally recommended?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMzUtZGVwbG95bWVudC1hZ2VudC1ydW50aW1lL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module35-deployment-agent-runtime/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
