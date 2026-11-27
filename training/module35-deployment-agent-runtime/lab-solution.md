---
sidebar_position: 3
title: "Lab Solution"
---

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
