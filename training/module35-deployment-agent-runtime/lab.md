---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 35: Deploying to Agent Runtime — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 35: Deploying an Agent to Agent Runtime Challenge

## Goal
In this lab, you will deploy the same multi-agent Customer Support system from Modules 32 and 33 to Google Cloud's Agent Runtime, using both the recommended Accelerated method and the manual Standard method — completing the "same application, three platforms" arc for Part 6.

### Prerequisites
*   A Google Cloud Project with billing enabled.
*   `gcloud` CLI installed and authenticated (`gcloud auth application-default login`).
*   A GCS staging bucket in `us-central1` for Part 2 (`gcloud storage buckets create gs://YOUR_UNIQUE_BUCKET_NAME --project=YOUR_PROJECT_ID --location=us-central1`).
*   **Python Environment:** Python 3.10+.
*   **UV Tool:** For managing the Python environment and running `uvx google-agents-cli`. See [Install UV](https://docs.astral.sh/uv/getting-started/installation/).
*   **Required APIs:** Ensure the following APIs are enabled in your project:
    *   Vertex AI API (`aiplatform.googleapis.com`)
    *   Cloud Build API (`cloudbuild.googleapis.com`)
    *   Artifact Registry API (`artifactregistry.googleapis.com`)
    *   Cloud Resource Manager API (`cloudresourcemanager.googleapis.com`)
*   **Set GCP Project & Infrastructure Region:**
    ```shell
    export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
    export DEPLOY_REGION=us-central1
    gcloud config set project "$GOOGLE_CLOUD_PROJECT"
    ```

---

## Part 1: Accelerated Deployment (Recommended)

This method uses the Agents CLI to add deployment artifacts to your existing ADK project and deploy it.

### Step 1: Prepare the Agent Project

<Setup/>

1.  **Re-create the Customer Support Agent:** We'll use the same multi-agent Customer Support system from Modules 32 and 33. Create a fresh directory and the same three YAML files:
    ```shell
    mkdir support_agent
    cd support_agent
    ```

    *   **`billing_agent.yaml`:**
        ```yaml
        name: billing_agent
        model: gemini-3.8-flash
        description: "Handles questions about billing, invoices, and payments."
        instruction: "You are a billing support agent. Politely answer questions about billing and payment issues."
        ```
    *   **`tech_support_agent.yaml`:**
        ```yaml
        name: tech_support_agent
        model: gemini-3.8-flash
        description: "Handles technical support questions and troubleshooting."
        instruction: "You are a technical support agent. Help users troubleshoot technical issues and provide clear solutions."
        ```
    *   **`root_agent.yaml`:**
        ```yaml
        name: router_agent
        model: gemini-3.8-flash
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

2.  **Navigate to the Parent Directory:**
    ```shell
    cd ..
    ```
3.  **Scaffold the Project:** Run `uvx google-agents-cli scaffold enhance` from the parent directory containing `support_agent/`. Pass:
    *   `.` as the current project directory,
    *   `--adk` (shortcut for `--base-template adk`, required when enhancing a plain ADK folder that does not yet have an `agents-cli-manifest.yaml`),
    *   `-d agent_runtime` to select Vertex AI Agent Runtime as the deployment target, and
    *   `--agent-directory support_agent` so the CLI locates your YAML config agent in `support_agent/` rather than scaffolding a generic stub:
    ```shell
    uvx google-agents-cli scaffold enhance . \
      --adk \
      -d agent_runtime \
      --agent-directory support_agent \
      --region "$DEPLOY_REGION"
    ```
    The command detects `support_agent/root_agent.yaml` and generates a `Dockerfile`, `agents-cli-manifest.yaml`, Terraform IaC under `deployment/terraform/`, and a `support_agent/agent.py` shim (`config_agent_utils.from_config(...)`) that loads your `router_agent` and its specialists.
4.  **Follow the Prompts:** Accept the defaults or pass `-y` for non-interactive defaults, keeping `--region` set to a supported Agent Runtime infrastructure region (`us-central1`).

### Step 2: Verify Your Google Cloud Credentials
1.  **Confirm Application Default Credentials (ADC) and Active Project:**
    ```shell
    gcloud auth application-default login
    gcloud config set project "$GOOGLE_CLOUD_PROJECT"
    gcloud config get-value project
    ```

### Step 3: Deploy the Agent
1.  **Ensure you are in the project root directory** (containing `agents-cli-manifest.yaml` and `support_agent/`).
2.  **Run the Deployment Command (with Region Separation):** Deploy the Agent Runtime resource to `DEPLOY_REGION=us-central1` while passing `GOOGLE_CLOUD_LOCATION=global` into the container so `gemini-3.8-flash` Vertex AI calls hit the global endpoint without 404 region errors:
    ```shell
    uvx google-agents-cli deploy \
      --project "$GOOGLE_CLOUD_PROJECT" \
      --region "$DEPLOY_REGION" \
      --env-vars "GOOGLE_CLOUD_LOCATION=global" \
      --no-confirm-project
    ```
    > **Tip — Async Deployments (`--no-wait` / `--status`):** Agent Runtime container builds and rollouts typically take 5–10 minutes. To return control to your terminal immediately, start the rollout with `uvx google-agents-cli deploy --project "$GOOGLE_CLOUD_PROJECT" --region "$DEPLOY_REGION" --env-vars "GOOGLE_CLOUD_LOCATION=global" --no-confirm-project --no-wait`, then check progress anytime with `uvx google-agents-cli deploy --status`.
3.  **Inspect `deployment_metadata.json`:** When the deployment finishes (either synchronously or when `--status` detects completion), `agents-cli` writes `deployment_metadata.json` in your project root:
    ```json
    {
      "remote_agent_runtime_id": "projects/YOUR_PROJECT/locations/us-central1/reasoningEngines/ENGINE_ID",
      "deployment_target": "agent_runtime",
      "is_a2a": true,
      "agent_directory": "support_agent"
    }
    ```
    Keep this file! In **Module 36**, `uvx google-agents-cli publish gemini` automatically reads `deployment_metadata.json` to register your agent with Gemini Enterprise without needing manual runtime ID flags. You can also view your live agent under **Agent Platform -> Agent Runtime** in the Google Cloud Console.

---

## Part 2: Standard Deployment (Manual)

This method involves writing a custom Python script to deploy the agent. Unlike Part 1, this script needs to `import` your `root_agent` directly as a Python object — so this part uses a **Python-code version** of the same Customer Support system, instead of the YAML config version.

### Step 1: Prepare the Agent Project

<Setup/>

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
    from google.adk.agents import Agent

    # TODO: 1. Define billing_agent, an Agent with name="billing_agent",
    # model="gemini-3.8-flash", and the same description/instruction as billing_agent.yaml.

    # TODO: 2. Define tech_support_agent, an Agent with name="tech_support_agent",
    # model="gemini-3.8-flash", and the same description/instruction as tech_support_agent.yaml.

    # TODO: 3. Define root_agent, an Agent named "router_agent" with model="gemini-3.8-flash",
    # the same instruction as root_agent.yaml, and sub_agents=[billing_agent, tech_support_agent].
    ```
3.  **Install Dependencies with `uv`:**
    ```shell
    uv add "google-cloud-aiplatform[adk,agent_engines]>=1.129.0"
    ```

### Step 2: Create the Deployment Script
1.  In the `deploy_manual` directory, create a new file named `deploy.py`.
2.  **Action:** Write the Python code to deploy the agent. Use the skeleton below and fill in the `# TODO` sections:
    *   Initialize `vertexai.init(...)` with `DEPLOY_REGION = "us-central1"` for the Agent Runtime control plane and staging bucket.
    *   Wrap `root_agent` in `agent_engines.AdkApp`.
    *   Call `agent_engines.create(...)` passing `env_vars={"GOOGLE_GENAI_USE_ENTERPRISE": "1", "GOOGLE_CLOUD_LOCATION": "global"}` so `gemini-3.8-flash` uses the global Vertex AI endpoint inside the container (note: Agent Runtime injects `GOOGLE_CLOUD_PROJECT` automatically and reserves that variable name).

    ```python
    # In deploy.py
    import vertexai
    from vertexai import agent_engines
    from support_agent.agent import root_agent

    # TODO: Fill in these values for your project
    PROJECT_ID = "your-gcp-project-id"
    DEPLOY_REGION = "us-central1"
    STAGING_BUCKET = "gs://your-gcs-bucket-name"

    # Initialize the Vertex AI SDK in the infrastructure deployment region
    vertexai.init(
        project=PROJECT_ID,
        location=DEPLOY_REGION,
        staging_bucket=STAGING_BUCKET,
    )

    # Wrap the agent in an AdkApp object
    app = agent_engines.AdkApp(agent=root_agent)

    # TODO: Call agent_engines.create() to deploy `app`:
    # - agent_engine=app
    # - requirements=["google-cloud-aiplatform[adk,agent_engines]>=1.129.0"]
    # - env_vars={"GOOGLE_GENAI_USE_ENTERPRISE": "1", "GOOGLE_CLOUD_LOCATION": "global"}
    remote_app = None  # Replace this

    print("Deployment finished!")
    print(f"Resource Name: {remote_app.resource_name}")
    ```

### Step 3: Test Agent Locally (Optional but Recommended)
**Action:** Before deploying, run the `local_test.py` pattern from the **Reference Solution Vault** below to verify `AdkApp` locally and catch any routing or import issues before starting the 5–10 minute cloud build.

### Step 4: Deploy the Agent
Run the deployment script with `uv run python`. This will take several minutes:
```shell
uv run python deploy.py
```

### Step 5: Interact with the Deployed Agent
1.  Create an `interact.py` script (reference implementation available in the **Reference Solution Vault** below).
2.  **Action:** Configure the script with your `PROJECT_ID`, `DEPLOY_REGION` (`"us-central1"`), and the `AGENT_ENGINE_ID` printed by `deploy.py`.
3.  Run the script with `uv run python` to test your deployed agent — try a billing question and a technical question, and confirm each routes to the correct specialist, just like in Modules 32 and 33:
    ```shell
    uv run python interact.py
    ```

### Cleanup (Important!)
Follow the cleanup instructions in the **Reference Solution Vault** below to delete your Agent Runtime instances and GCS staging bucket so you do not incur ongoing charges.

### Self-Reflection Questions
- What are the primary advantages of using the Accelerated Deployment method with the Agents CLI compared to the Standard Deployment method for production use?
- Agent Runtime is a managed backend. How does this simplify the development of complex clients (e.g., web or mobile applications) that interact with your agent?
- For what scenarios might the Standard Deployment method (using `deploy.py` and the Vertex AI SDK) still be advantageous, even if Accelerated Deployment is generally recommended?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="35">

# Lab 35 Solution: Deploying an Agent to Agent Runtime

## Goal

This lab is a procedural tutorial. The solution for both parts is a successfully deployed Agent Runtime instance running the Customer Support system.

---

### Part 1: Accelerated Deployment Solution

After running `uvx google-agents-cli scaffold enhance . --adk -d agent_runtime --agent-directory support_agent --region "$DEPLOY_REGION"` followed by `uvx google-agents-cli deploy --project "$GOOGLE_CLOUD_PROJECT" --region "$DEPLOY_REGION" --env-vars "GOOGLE_CLOUD_LOCATION=global" --no-confirm-project` (or `--no-wait` + `--status`), a successful completion is the primary indicator of success.

**Expected Outcome:**
*   The `uvx google-agents-cli deploy` command completes without errors and writes `deployment_metadata.json` containing `remote_agent_runtime_id`.
*   A new agent appears in **Agent Platform -> Agent Runtime** in the Google Cloud Console (`us-central1`).
*   `deployment_metadata.json` is ready to be consumed directly by `uvx google-agents-cli publish gemini` in Module 36.

---

### Part 2: Standard Deployment Solution

This section contains the complete code for `support_agent/agent.py`, `deploy.py`, `interact.py`, and `local_test.py` used in the manual deployment part of the lab.

#### `support_agent/agent.py`

This file defines the same Customer Support system as Modules 32 and 33, but as Python `Agent` objects instead of YAML config — required because `deploy.py` needs to `import` `root_agent` directly.

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

#### `deploy.py`

This script initializes Vertex AI in `DEPLOY_REGION = "us-central1"` for the Agent Runtime control plane while injecting `GOOGLE_CLOUD_LOCATION=global` into the runtime container so `gemini-3.8-flash` resolves on the global endpoint (Agent Runtime automatically injects `GOOGLE_CLOUD_PROJECT`).

```python
import vertexai
from vertexai import agent_engines
from support_agent.agent import root_agent

# --- CONFIGURATION ---
PROJECT_ID = "your-gcp-project-id"
DEPLOY_REGION = "us-central1"
STAGING_BUCKET = "gs://your-unique-bucket-name"
AGENT_DISPLAY_NAME = "customer-support-agent"

def main():
    # Initialize Vertex AI SDK in the infrastructure deployment region
    vertexai.init(project=PROJECT_ID, location=DEPLOY_REGION, staging_bucket=STAGING_BUCKET)

    # 1. Wrap your agent in an AdkApp
    print("Wrapping agent in AdkApp...")
    app = agent_engines.AdkApp(agent=root_agent)

    # 2. Deploy to Agent Runtime (separating DEPLOY_REGION from GOOGLE_CLOUD_LOCATION=global)
    print(f"Deploying '{AGENT_DISPLAY_NAME}' to Agent Runtime in {DEPLOY_REGION}...")
    remote_app = agent_engines.create(
        agent_engine=app,
        display_name=AGENT_DISPLAY_NAME,
        requirements=["google-cloud-aiplatform[adk,agent_engines]>=1.129.0"],
        env_vars={
            "GOOGLE_GENAI_USE_ENTERPRISE": "1",
            "GOOGLE_CLOUD_LOCATION": "global",
        },
    )

    print(f"Deployment complete. Resource Name: {remote_app.resource_name}")
    print(f"Agent Runtime ID: {remote_app.resource_name.split('/')[-1]}")

if __name__ == "__main__":
    main()
```

> **Note:** Earlier versions of this lab passed `enable_tracing=True` to `AdkApp`. That parameter is deprecated — telemetry is controlled via the `GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY` environment variable or the Cloud Console toggle instead.

#### `interact.py`

```python
import asyncio
import vertexai
from vertexai import agent_engines

# --- CONFIGURATION ---
PROJECT_ID = "your-gcp-project-id"
DEPLOY_REGION = "us-central1"
# Replace with the ID printed by `uv run python deploy.py`
AGENT_ENGINE_ID = "YOUR_AGENT_ENGINE_ID"

async def main():
    vertexai.init(project=PROJECT_ID, location=DEPLOY_REGION)

    # Get a reference to the deployed agent
    remote_app = agent_engines.get(AGENT_ENGINE_ID)

    # Create a new session
    print("Creating new session...")
    remote_session = await remote_app.async_create_session(user_id="test-user-123")

    # Send a query and stream the response
    query = "I have a question about my invoice, it seems too high this month."
    print(f"\nUser: {query}")
    print("Agent: ", end="")

    final_response = ""
    async for event in remote_app.async_stream_query(
        user_id="test-user-123",
        session_id=remote_session["id"],
        message=query,
    ):
        # Look for the final text part in the model's response
        if (
            event.get("content", {}).get("parts", [{}])[0].get("text")
            and not event.get("content", {}).get("parts", [{}])[0].get("function_call")
        ):
            final_response = event["content"]["parts"][0]["text"]

    print(final_response)

if __name__ == "__main__":
    asyncio.run(main())
```

#### `local_test.py` (Optional)

This script shows the code for the optional local testing step. Note that `async_create_session` returns a plain `dict`, not an object — access the session ID with `session["id"]`, not `session.id`.

```python
import asyncio
from vertexai import agent_engines
from support_agent.agent import root_agent

async def main():
    # Wrap the agent in an AdkApp object
    app = agent_engines.AdkApp(agent=root_agent)

    # Create a local session to maintain conversation history
    session = await app.async_create_session(user_id="u_123")
    print(f"Local session created: {session['id']}")

    # Send a query to the agent
    events = []
    async for event in app.async_stream_query(
        user_id="u_123",
        session_id=session["id"],
        message="My app keeps crashing every time I open it.",
    ):
        events.append(event)

    # The full event stream shows the agent's thought process, including
    # which specialist it delegated to
    print("\n--- Full Event Stream ---")
    for event in events:
        print(event)

    # For quick tests, you can extract just the final text response
    final_text_responses = [
        e for e in events
        if e.get("content", {}).get("parts", [{}])[0].get("text")
        and not e.get("content", {}).get("parts", [{}])[0].get("function_call")
    ]
    if final_text_responses:
        print("\n--- Final Response ---")
        print(final_text_responses[0]["content"]["parts"][0]["text"])

if __name__ == "__main__":
    asyncio.run(main())
```

### Cleanup Commands

If you are not immediately continuing with the Part 1 Agent Runtime instance in Module 36, delete your deployed Agent Runtime resources and staging bucket when finished:

```shell
# Delete an Agent Runtime instance via Python one-liner (replace PROJECT_ID and ENGINE_ID)
uv run python -c "import vertexai; from vertexai import agent_engines; vertexai.init(project='YOUR_PROJECT_ID', location='us-central1'); agent_engines.delete('YOUR_AGENT_ENGINE_ID', force=True)"

# Delete the GCS staging bucket used in Part 2
gcloud storage rm -r gs://YOUR_UNIQUE_BUCKET_NAME
```

### Self-Reflection Answers

1.  **What are the primary advantages of using the Accelerated Deployment method with the Agents CLI compared to the Standard Deployment method for production use?**
    *   **Answer:** The Accelerated Deployment method with the Agents CLI is significantly more robust and recommended for production due to several advantages:
        *   **Infrastructure as Code (IaC):** The Agents CLI generates Terraform configurations, ensuring that your cloud infrastructure is provisioned in a reproducible, auditable, and version-controlled manner. The Standard method requires manual `gcloud` commands or custom scripting for infrastructure.
        *   **Built-in CI/CD:** The Agents CLI includes pre-configured Cloud Build pipelines for automated testing, building, and deploying. This streamlines development workflows and enforces best practices for continuous integration and delivery.
        *   **Best Practices:** It incorporates Google Cloud and ADK best practices for security (e.g., IAM roles, service accounts), reliability, and scalability from the start.
        *   **Reduced Manual Effort & Errors:** It minimizes manual configuration, reducing human error and accelerating time to market compared to the more involved Standard Deployment.

2.  **Agent Runtime is a managed backend. How does this simplify the development of complex clients (e.g., web or mobile applications) that interact with your agent?**
    *   **Answer:** As a managed backend, Agent Runtime significantly simplifies client development by abstracting away the complexities of server-side operations. This includes:
        *   **Automatic Scaling & Concurrency:** Clients don't need to worry about the agent's backend scaling to handle thousands of concurrent users. Agent Runtime handles this automatically.
        *   **Stable API:** It provides a stable and consistent API endpoint that clients (whether web, mobile, or other services) can easily connect to without needing to understand the underlying agent's implementation details.
        *   **Separation of Concerns:** The client can focus solely on UI/UX, session management, and presenting information, while Agent Runtime handles the heavy lifting of agent orchestration, LLM interaction, tool execution, and state management.
        *   **Security:** Agent Runtime handles much of the backend security, allowing clients to focus on secure authentication with the managed service rather than managing complex server-side security.

3.  **For what scenarios might the Standard Deployment method (using `deploy.py` and the Vertex AI SDK) still be advantageous, even if Accelerated Deployment is generally recommended?**
    *   **Answer:** While Accelerated Deployment is the best practice for new production projects, the Standard Deployment method still has advantages for specific scenarios:
        *   **Learning & Understanding:** It provides a deeper understanding of the underlying Vertex AI SDK and Agent Runtime APIs, which is invaluable for debugging or custom integrations.
        *   **Customization:** For highly specialized deployment workflows that deviate significantly from the Agents CLI templates (e.g., integrating with existing, complex CI/CD systems or custom infrastructure), a manual script offers greater flexibility.
        *   **Modifying Existing Deployments:** If you need to programmatically update specific aspects of an already deployed Agent Runtime instance that aren't covered by the Agents CLI's `deploy` command, a custom script is often necessary.
        *   **Simplified Projects:** For very simple, one-off deployments or internal tools that don't require a full IaC/CI/CD setup, a direct script might be quicker to set up initially.

</SolutionVault>
