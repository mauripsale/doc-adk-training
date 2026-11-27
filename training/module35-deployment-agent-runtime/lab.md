---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 35: Deploying to Agent Runtime — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 35: Deploying `support-ops-agent` to Agent Runtime Challenge

## Goal
In this lab, you will deploy our canonical stateful Python **`support-ops-agent`** (`gemini-3.8-flash`) to Google Cloud's **Agent Runtime** using `agents-cli` — completing the "one production agent across Cloud Run, GKE, and Agent Runtime" deployment arc and generating `deployment_metadata.json` for zero-flag publishing in Module 36. In Part 2, you will also peek under the hood by deploying via the programmatic `vertexai.agent_engines` Python SDK.

### Prerequisites
*   A Google Cloud Project with billing enabled.
*   `gcloud` CLI installed and authenticated (`gcloud auth login` and `gcloud auth application-default login`).
*   **Python Environment:** Python 3.10+.
*   **`uv` & `agents-cli`:** Install `uv` ([guide](https://docs.astral.sh/uv/getting-started/installation/)) and install the Google Agents CLI globally so `agents-cli` is on your `PATH`:
    ```shell
    uv tool install google-agents-cli
    ```
*   A GCS staging bucket in `us-central1` for Part 2 (`gcloud storage buckets create gs://YOUR_UNIQUE_BUCKET_NAME --project=YOUR_PROJECT_ID --location=us-central1`).
*   **Required APIs:** Enable the required Google Cloud APIs:
    ```shell
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export DEPLOY_REGION="us-central1"
    gcloud config set project "$GOOGLE_CLOUD_PROJECT"

    gcloud services enable \
      aiplatform.googleapis.com \
      cloudbuild.googleapis.com \
      artifactregistry.googleapis.com \
      secretmanager.googleapis.com \
      cloudresourcemanager.googleapis.com \
      --project="$GOOGLE_CLOUD_PROJECT"
    ```

---

## Part 1: Accelerated Deployment of `support-ops-agent` with `agents-cli` (Recommended)

In Part 1, you will enhance our stateful `support-ops-agent` (featuring `before_agent_callback`, `ToolContext` state tracking across `lookup_ticket`, `check_sla_policy`, and `escalate_ticket`, and `App(name="app")`) for **Agent Runtime**, roll it out asynchronously, inspect `deployment_metadata.json`, and query the live managed endpoint over both native ADK `:streamQuery` and A2A!

### Step 1: Reuse or Fast-Bootstrap `support-ops-agent`

<Setup/>

If you already have `support-ops-agent/` from Module 31 or 32, `cd` directly into it. Otherwise, fast-bootstrap the exact canonical Part 6 project in 10 seconds (remember: **never `mkdir` before `scaffold create`**):

```shell
agents-cli scaffold create support-ops-agent --agent adk --prototype --agent-guidance-filename GEMINI.md
curl -fsSL https://mauripsale.github.io/doc-adk-training/samples/part6/agent.py -o support-ops-agent/app/agent.py
cd support-ops-agent
```

Take a moment to verify the two critical `agents-cli` invariants at the bottom of `app/agent.py`:
*   `root_agent = Agent(name="support_ops_agent", model=Gemini(model="gemini-3.8-flash", ...), ...)`
*   `app = App(root_agent=root_agent, name="app")` — **`App.name` matches `agent_directory: "app"`** in `agents-cli-manifest.yaml`, preventing `"Session not found"` errors locally and in the cloud.

### Step 2: Enhance for Agent Runtime & Sync Dependencies

1.  **Action:** From inside `support-ops-agent/`, enhance the prototype to add the Agent Runtime `Dockerfile`, FastAPI + `:streamQuery` + A2A entrypoint (`app/fast_api_app.py`), GitHub Actions CI/CD workflow, and Terraform IaC (`deployment/terraform/`), then sync project dependencies:
    ```shell
    # TODO: Run `agents-cli scaffold enhance .` with:
    #   --deployment-target agent_runtime
    #   --cicd-runner github_actions
    #   --region "$DEPLOY_REGION"
    # Then run `agents-cli install` to sync the environment.
    ```
    > **Critical Rule — Managed Sessions on Agent Runtime:** Do **not** pass `--session-type` (and clear any custom `session_type` setting if migrating from another target). At runtime, Agent Runtime injects `GOOGLE_CLOUD_AGENT_ENGINE_ID` and `app_utils/services.py` automatically upgrades `shared://session` to managed **`VertexAiSessionService`**.

    > **Tip — Enhancing a Plain Legacy `adk create` Folder:** If you ever need to enhance a plain ADK folder that was *not* created with `agents-cli` (no `agents-cli-manifest.yaml`) and keeps its code in a custom package such as `support_agent/`, pass `--adk` and `--agent-directory`:
    > ```shell
    > agents-cli scaffold enhance . --adk --deployment-target agent_runtime --agent-directory support_agent --region "$DEPLOY_REGION"
    > ```
    > Similarly, if your security team routes outbound agent traffic through an **Agent Gateway** with TLS inspection, run `agents-cli scaffold enhance . --agent-gateway` so the generated `Dockerfile` trusts `AGENT_GATEWAY_ROOT_CERTIFICATES`.

2.  **Quick Local Smoke Test:** Verify `support-ops-agent` locally before starting the cloud build:
    ```shell
    agents-cli run "Investigate ticket TCK-1042 and escalate if P1."
    ```

### Step 3: Deploy with Region Separation & Async `--no-wait` / `--status` Recovery

Agent Runtime builds your `Dockerfile` container remotely and provisions the managed `ReasoningEngine` resource, which takes **5–10 minutes**. Always separate:
*   `--region "$DEPLOY_REGION"` (`us-central1`) for the regional Agent Runtime infrastructure, and
*   `--env-vars "GOOGLE_GENAI_USE_ENTERPRISE=1,GOOGLE_CLOUD_LOCATION=global"` inside the container so `gemini-3.8-flash` resolves on Vertex AI's `global` endpoint.

1.  **Option A — Synchronous Deploy:**
    ```shell
    agents-cli deploy \
      --project "$GOOGLE_CLOUD_PROJECT" \
      --region "$DEPLOY_REGION" \
      --env-vars "GOOGLE_GENAI_USE_ENTERPRISE=1,GOOGLE_CLOUD_LOCATION=global" \
      --no-confirm-project
    ```

2.  **Option B — Non-Blocking Async Rollout & Status Recovery (Recommended for 5–10 min builds):**
    **Action:** Start the rollout asynchronously with `--no-wait`, poll progress with `--status`, and list active deployments in your project:
    ```shell
    # 1. Start the deployment and return immediately
    agents-cli deploy \
      --project "$GOOGLE_CLOUD_PROJECT" \
      --region "$DEPLOY_REGION" \
      --env-vars "GOOGLE_GENAI_USE_ENTERPRISE=1,GOOGLE_CLOUD_LOCATION=global" \
      --no-confirm-project \
      --no-wait

    # 2. Poll every ~60s until completion (automatically writes deployment_metadata.json when done!)
    agents-cli deploy --status

    # 3. List existing Agent Runtime deployments in your project and region
    agents-cli deploy --list --project "$GOOGLE_CLOUD_PROJECT" --region "$DEPLOY_REGION"
    ```
    *(Optional Enterprise Flags: In hardened environments, you can pass `--agent-identity`, `--agent-gateway-egress projects/PROJECT/locations/REGION/agentGateways/GATEWAY`, `--agent-gateway-ingress ...`, or `--key projects/KEY_PROJECT/locations/REGION/keyRings/RING/cryptoKeys/KEY` for CMEK at creation time.)*

3.  **Inspect `deployment_metadata.json`:** Once deployment completes, open `deployment_metadata.json` in your `support-ops-agent/` root and verify `"agent_directory": "app"`:
    ```json
    {
      "remote_agent_runtime_id": "projects/YOUR_PROJECT/locations/us-central1/reasoningEngines/ENGINE_ID",
      "deployment_target": "agent_runtime",
      "is_a2a": true,
      "agent_directory": "app",
      "deployment_timestamp": "2026-11-26T10:30:00.000+00:00"
    }
    ```
    **Keep this file intact!** In **Module 36**, `agents-cli publish gemini` reads `deployment_metadata.json` automatically to register `support-ops-agent` with Gemini Enterprise without requiring manual runtime ID or registration-type flags.

### Step 4: Test the Live Managed Agent Runtime Directly from `agents-cli run`

No custom Python client is needed to smoke-test your live cloud deployment! `agents-cli run --url` auto-detects Agent Runtime URLs, authenticates with your Google Cloud credentials, creates a managed `VertexAiSessionService` session, and streams the response.

**Action:** Construct `AGENT_RUNTIME_URL` from `deployment_metadata.json` and query your deployed `support-ops-agent` using **both** `--mode adk` (native `:streamQuery`) and `--mode a2a` (the `/api/a2a/app/...` passthrough):

```shell
export AGENT_RUNTIME_ID=$(python3 -c 'import json; print(json.load(open("deployment_metadata.json"))["remote_agent_runtime_id"])')
export AGENT_RUNTIME_URL="https://${DEPLOY_REGION}-aiplatform.googleapis.com/v1/${AGENT_RUNTIME_ID}"

# TODO 1: Query the live Agent Runtime endpoint using native ADK streaming (--mode adk)
# Prompt: "Investigate ticket TCK-1042 and escalate if P1."

# TODO 2: Query the same live Agent Runtime endpoint over the A2A protocol (--mode a2a)
# Prompt: "Check ticket TCK-2088 and summarize its SLA response target."
```
*(Tip: Append `-v` to print the full streamed JSON event payloads and observe `lookup_ticket`, `check_sla_policy`, and `escalate_ticket` executing inside Agent Runtime!)*

---

## Part 2: Under the Hood — Programmatic Python SDK (`vertexai.agent_engines`)

To understand what `agents-cli` and the reasoning engine adapter automate under the hood, you can also package and deploy a Python ADK `Agent` imperatively using `vertexai.agent_engines`.

### Step 1: Prepare a Standalone SDK Project

<Setup/>

1.  **Create a clean directory for the manual SDK experiment:**
    ```shell
    cd ..
    mkdir deploy_manual
    cd deploy_manual
    mkdir support_agent
    touch support_agent/__init__.py
    ```
2.  **Action:** Create `support_agent/agent.py` with a router and two specialist sub-agents (`billing_agent` and `tech_support_agent`) using `gemini-3.8-flash`. Fill in the `# TODO` sections:
    ```python
    # In support_agent/agent.py
    from google.adk.agents import Agent

    # TODO: 1. Define billing_agent, an Agent with name="billing_agent",
    # model="gemini-3.8-flash", and description/instruction for billing & invoice questions.

    # TODO: 2. Define tech_support_agent, an Agent with name="tech_support_agent",
    # model="gemini-3.8-flash", and description/instruction for technical troubleshooting.

    # TODO: 3. Define root_agent, an Agent named "router_agent" with model="gemini-3.8-flash"
    # that delegates billing questions to billing_agent and technical issues to tech_support_agent.
    ```
3.  **Install Dependencies with `uv`:**
    ```shell
    uv init --bare
    uv add "google-cloud-aiplatform[adk,agent_engines]>=1.129.0"
    ```

### Step 2: Create `deploy.py`
Create `deploy.py` in `deploy_manual/` and complete the `# TODO` call to `agent_engines.create(...)`:
*   Initialize `vertexai.init(...)` with `DEPLOY_REGION = "us-central1"` and your `STAGING_BUCKET`.
*   Wrap `root_agent` in `agent_engines.AdkApp(agent=root_agent)`.
*   Pass `env_vars={"GOOGLE_GENAI_USE_ENTERPRISE": "1", "GOOGLE_CLOUD_LOCATION": "global"}` so `gemini-3.8-flash` resolves on Vertex AI's global endpoint inside the runtime container.

```python
# In deploy.py
import vertexai
from vertexai import agent_engines
from support_agent.agent import root_agent

# TODO: Fill in these values for your project
PROJECT_ID = "your-gcp-project-id"
DEPLOY_REGION = "us-central1"
STAGING_BUCKET = "gs://your-unique-bucket-name"

vertexai.init(
    project=PROJECT_ID,
    location=DEPLOY_REGION,
    staging_bucket=STAGING_BUCKET,
)

app = agent_engines.AdkApp(agent=root_agent)

# TODO: Call agent_engines.create() to deploy `app`:
# - agent_engine=app
# - display_name="customer-support-agent"
# - requirements=["google-cloud-aiplatform[adk,agent_engines]>=1.129.0"]
# - env_vars={"GOOGLE_GENAI_USE_ENTERPRISE": "1", "GOOGLE_CLOUD_LOCATION": "global"}
remote_app = None  # Replace this

print(f"Deployment complete. Resource Name: {remote_app.resource_name}")
```

### Step 3: Local Pre-Flight, Deploy, Interact & Clean Up
1.  **(Recommended) Local Pre-Flight:** Run `local_test.py` (from the **Reference Solution Vault** below) to verify `AdkApp.async_stream_query(...)` locally before waiting on a cloud build. Note that `async_create_session` returns a Python `dict` (`session["id"]`).
2.  **Deploy:** Run `uv run python deploy.py` and record the printed `Agent Runtime ID`.
3.  **Interact:** Configure and run `uv run python interact.py` to create a remote session and stream events from the deployed `ReasoningEngine`.
4.  **Cleanup:** Run `uv run python cleanup.py` to delete the Part 2 manual SDK engine (keep your Part 1 `support-ops-agent` deployment alive if you are continuing immediately to Module 36!).

### Self-Reflection Questions
- Why must you omit or clear custom `session_type` overrides when enhancing `support-ops-agent` for `--deployment-target agent_runtime`?
- How do `agents-cli deploy --no-wait` and `agents-cli deploy --status` protect developer and CI workflows against 5–10 minute container build timeouts, and what file does `--status` write upon completion?
- When would an enterprise security team combine `--agent-identity`, `scaffold enhance . --agent-gateway` + `--agent-gateway-egress`, and `--key` on Agent Runtime?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="35">

# Lab 35 Solution: Deploying `support-ops-agent` to Agent Runtime

## Goal

This solution provides the complete verified `agents-cli` commands for Part 1 (deploying and testing our stateful `support-ops-agent` on Agent Runtime) and the complete Python SDK scripts (`support_agent/agent.py`, `deploy.py`, `interact.py`, `local_test.py`, and `cleanup.py`) for Part 2.

---

### Part 1: Accelerated Deployment of `support-ops-agent` (`agents-cli`)

#### 1. Bootstrap (or Reuse), Enhance & Install
```shell
# Fast-bootstrap if not reusing support-ops-agent/ from Module 31/32
agents-cli scaffold create support-ops-agent --agent adk --prototype --agent-guidance-filename GEMINI.md
curl -fsSL https://mauripsale.github.io/doc-adk-training/samples/part6/agent.py -o support-ops-agent/app/agent.py
cd support-ops-agent

# Enhance for Agent Runtime (do NOT set --session-type; Agent Runtime wires VertexAiSessionService automatically)
agents-cli scaffold enhance . \
  --deployment-target agent_runtime \
  --cicd-runner github_actions \
  --region "$DEPLOY_REGION"

agents-cli install

# Quick local smoke test
agents-cli run "Investigate ticket TCK-1042 and escalate if P1."
```

#### 2. Deploy with Region Separation & Async `--no-wait` / `--status`
```shell
# Start non-blocking rollout (container in us-central1, Gemini 3.8 Flash on global endpoint)
agents-cli deploy \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --region "$DEPLOY_REGION" \
  --env-vars "GOOGLE_GENAI_USE_ENTERPRISE=1,GOOGLE_CLOUD_LOCATION=global" \
  --no-confirm-project \
  --no-wait

# Poll rollout progress; writes deployment_metadata.json ("agent_directory": "app") when complete
agents-cli deploy --status

# Audit active Agent Runtime deployments
agents-cli deploy --list --project "$GOOGLE_CLOUD_PROJECT" --region "$DEPLOY_REGION"
```

#### 3. Live Cloud Verification via `agents-cli run --url` (`adk` & `a2a` Modes)
```shell
export AGENT_RUNTIME_ID=$(python3 -c 'import json; print(json.load(open("deployment_metadata.json"))["remote_agent_runtime_id"])')
export AGENT_RUNTIME_URL="https://${DEPLOY_REGION}-aiplatform.googleapis.com/v1/${AGENT_RUNTIME_ID}"

# Mode 1: Native ADK :streamQuery contract
agents-cli run "Investigate ticket TCK-1042 and escalate if P1." \
  --url "$AGENT_RUNTIME_URL" \
  --mode adk

# Mode 2: A2A JSON-RPC contract via Agent Runtime's /api HTTP passthrough
agents-cli run "Check ticket TCK-2088 and summarize its SLA response target." \
  --url "$AGENT_RUNTIME_URL" \
  --mode a2a
```

---

### Part 2: Under the Hood — Programmatic Python SDK Solution

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

#### `deploy.py`

This script initializes Vertex AI in `DEPLOY_REGION = "us-central1"` for the Agent Runtime control plane while injecting `GOOGLE_GENAI_USE_ENTERPRISE=1` and `GOOGLE_CLOUD_LOCATION=global` into the runtime container so `gemini-3.8-flash` resolves on the global endpoint (Agent Runtime injects `GOOGLE_CLOUD_PROJECT` automatically).

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

> **Note:** Earlier versions of `AdkApp` accepted `enable_tracing=True`. That parameter is deprecated — telemetry is controlled via the `GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY` environment variable or the Cloud Console toggle.

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

Note that `async_create_session` returns a plain `dict`, so access the session ID with `session["id"]`.

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

    print("\n--- Full Event Stream ---")
    for event in events:
        print(event)

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

#### `cleanup.py`

Run `cleanup.py` to delete the manual Part 2 Agent Runtime resource (keep Part 1's `support-ops-agent` running until you finish Module 36!).

```python
import vertexai
from vertexai import agent_engines

# --- CONFIGURATION ---
PROJECT_ID = "your-gcp-project-id"
DEPLOY_REGION = "us-central1"
AGENT_ENGINE_ID = "YOUR_AGENT_ENGINE_ID"

def main():
    vertexai.init(project=PROJECT_ID, location=DEPLOY_REGION)
    print(f"Deleting Agent Runtime resource '{AGENT_ENGINE_ID}'...")
    agent_engines.delete(AGENT_ENGINE_ID, force=True)
    print("Agent Runtime resource deleted successfully.")

if __name__ == "__main__":
    main()
```

```shell
# Also remove the Part 2 GCS staging bucket when finished
gcloud storage rm -r gs://YOUR_UNIQUE_BUCKET_NAME
```

### Self-Reflection Answers

1.  **Why must you omit or clear custom `session_type` overrides when enhancing `support-ops-agent` for `--deployment-target agent_runtime`?**
    *   **Answer:** On Agent Runtime, the platform injects `GOOGLE_CLOUD_AGENT_ENGINE_ID` into the container and `app_utils/services.py` automatically upgrades the `shared://session` URI to managed **`VertexAiSessionService`**. Setting a conflicting `session_type` is unnecessary and overridden by Agent Runtime's native session management.

2.  **How do `agents-cli deploy --no-wait` and `agents-cli deploy --status` protect developer and CI workflows against 5–10 minute container build timeouts, and what file does `--status` write upon completion?**
    *   **Answer:** `--no-wait` starts the server-side container build and `ReasoningEngine` rollout asynchronously and exits immediately so shells or agentic tool runners never hang or time out. Polling `agents-cli deploy --status` checks the operation server-side and, upon completion, writes **`deployment_metadata.json`** (`remote_agent_runtime_id`, `deployment_target`, `is_a2a`, `agent_directory: "app"`), ready for Module 36's `agents-cli publish gemini`.

3.  **When would an enterprise security team combine `--agent-identity`, `scaffold enhance . --agent-gateway` + `--agent-gateway-egress`, and `--key` on Agent Runtime?**
    *   **Answer:** Regulated workloads (finance, healthcare, public sector) often require dedicated per-agent workload principals (`--agent-identity`), centralized outbound TLS inspection and policy enforcement via an **Agent Gateway** (`scaffold enhance . --agent-gateway` injects `AGENT_GATEWAY_ROOT_CERTIFICATES` trust into the `Dockerfile` so `--agent-gateway-egress` can inspect outbound traffic), and customer-controlled cryptographic lifecycle with a Cloud KMS key (`--key` for CMEK at creation time).

</SolutionVault>
