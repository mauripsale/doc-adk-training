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

<Setup/>

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

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="35">

# Lab 35 Solution: Deploying an Agent to Agent Runtime

## Goal

This lab is a procedural tutorial. The solution for both parts is a successfully deployed Agent Runtime instance running the Customer Support system.

---

### Part 1: Accelerated Deployment Solution

After running `uvx google-agents-cli deploy`, a successful run of the command is the primary indicator of success.

**Expected Outcome:**
*   The `uvx google-agents-cli deploy` command completes without errors in your terminal.
*   A new agent with the name you configured appears in the **Agent Platform -> Agent Runtime** section of the Google Cloud Console.
*   You can copy the **Agent Runtime ID** from the console to use with a client application.

---

### Part 2: Standard Deployment Solution

This section contains the complete code for `support_agent/agent.py`, `deploy.py`, and `interact.py` used in the manual deployment part of the lab.

#### `support_agent/agent.py`

This file defines the same Customer Support system as Modules 32 and 33, but as Python `Agent` objects instead of YAML config — required because `deploy.py` needs to `import` `root_agent` directly.

```python
from google.adk.agents import Agent

billing_agent = Agent(
    name="billing_agent",
    model="gemini-3.5-flash",
    description="Handles questions about billing, invoices, and payments.",
    instruction="You are a billing support agent. Politely answer questions about billing and payment issues.",
)

tech_support_agent = Agent(
    name="tech_support_agent",
    model="gemini-3.5-flash",
    description="Handles technical support questions and troubleshooting.",
    instruction="You are a technical support agent. Help users troubleshoot technical issues and provide clear solutions.",
)

root_agent = Agent(
    name="router_agent",
    model="gemini-3.5-flash",
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

This script uses the Vertex AI SDK to package and deploy the agent.

```python
import vertexai
from vertexai import agent_engines
from support_agent.agent import root_agent

# --- CONFIGURATION ---
PROJECT_ID = "your-gcp-project-id"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://your-unique-bucket-name"
AGENT_DISPLAY_NAME = "customer-support-agent"

def main():
    # Initialize Vertex AI SDK
    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

    # 1. Wrap your agent in an AdkApp
    print("Wrapping agent in AdkApp...")
    app = agent_engines.AdkApp(agent=root_agent)

    # 2. Deploy to Agent Runtime
    print(f"Deploying '{AGENT_DISPLAY_NAME}' to Agent Runtime...")
    remote_app = agent_engines.create(
        agent_engine=app,
        display_name=AGENT_DISPLAY_NAME,
        requirements=["google-cloud-aiplatform[adk,agent_engines]>=1.111"],
    )

    print(f"Deployment complete. Resource Name: {remote_app.resource_name}")
    print(f"Agent Runtime ID: {remote_app.resource_name.split('/')[-1]}")

if __name__ == "__main__":
    main()
```

> **Note:** earlier versions of this lab passed `enable_tracing=True` to `AdkApp`. That parameter is now deprecated — telemetry is controlled via the `GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY` environment variable or the Cloud Console toggle instead, so it's simply omitted here.

#### `interact.py`

```python
import asyncio
import vertexai
from vertexai import agent_engines

# --- CONFIGURATION ---
# Note: Replace these with your actual Google Cloud project details.
PROJECT_ID = "your-gcp-project-id"
LOCATION = "us-central1"
# Note: Replace this with the ID output by the deploy.py script.
AGENT_ENGINE_ID = "YOUR_AGENT_ENGINE_ID"

async def main():
    vertexai.init(project=PROJECT_ID, location=LOCATION)

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
import vertexai
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
