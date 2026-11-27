---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 36: Gemini Enterprise Publishing — 🧪 Challenge Lab"
---

# Lab 36: Publishing `support-ops-agent` to Gemini Enterprise & Governing Your Fleet

## Goal

Welcome to the finale of the Part 6 **`support-ops-agent`** arc! In this hands-on and architectural capstone lab, you will:
1. Discover Gemini Enterprise apps in your Google Cloud project using `agents-cli publish gemini --list`.
2. Publish your **Module 35 Agent Runtime** `support-ops-agent` via **Mode 1 — Native ADK `:streamQuery` Registration** (leveraging `deployment_metadata.json` auto-detection and learning how to trace `streaming_agent_run_with_events` in `reasoning_engine_stderr`).
3. Publish your **Module 32 / 33 Cloud Run or GKE** `support-ops-agent` via **Mode 2 — A2A Registration** (`${SERVICE_URL}/a2a/app/.well-known/agent-card.json`) with least-privilege Discovery Engine IAM access.
4. Audit auto-registered Agent Runtime agents and catalog **Module 34's Cloud Run MCP server** in **Google Cloud Agent Registry (`gcloud agent-registry`)**, followed by an enterprise RBAC & Data Connector governance blueprint.

### Prerequisites
*   A Google Cloud Project with a Gemini Enterprise app created in the Cloud Console (Discovery Engine) and **Discovery Engine Editor** + **Agent Registry Editor** (`roles/agentregistry.editor`) permissions.
*   `agents-cli` installed (`uv tool install google-agents-cli`) and authenticated (`gcloud auth login` & `gcloud auth application-default login`).
*   Your `support-ops-agent/` directory from Module 35 (containing `deployment_metadata.json` with `"agent_directory": "app"`) and/or your Cloud Run `SERVICE_URL` from Module 32.
*   **Note on Costs:** Gemini Enterprise and deployed runtime resources incur cloud charges; clean up unused test engines after completing the lab.

---

### Step 1: Discover Gemini Apps in Your Project

Before registering `support-ops-agent`, set your project environment variables and query the Gemini Enterprise apps available in your project:

```shell
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
export DEPLOY_REGION="us-central1"
export PROJECT_NUMBER=$(gcloud projects describe "$GOOGLE_CLOUD_PROJECT" --format="value(projectNumber)")

# TODO: Run `agents-cli publish gemini` with the flag that lists all Gemini apps in the current project and exits.
```

Copy the full Gemini app resource name (`projects/<PROJECT_NUMBER>/locations/global/collections/default_collection/engines/<ENGINE_ID>`) into `GEMINI_APP_ID`:

```shell
export GEMINI_APP_ID="projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/YOUR_GEMINI_ENGINE_ID"
```

---

### Step 2: Mode 1 — Native ADK `:streamQuery` Registration (From Module 35's `deployment_metadata.json`)

Navigate into your `support-ops-agent/` project directory from Module 35, where `agents-cli deploy` generated `deployment_metadata.json` *(if you started directly at Module 36 against an already-deployed Reasoning Engine, scaffold `support-ops-agent` first or pass `--registration-type adk --agent-runtime-id "projects/$GOOGLE_CLOUD_PROJECT/locations/$DEPLOY_REGION/reasoningEngines/YOUR_ENGINE_ID"` explicitly)*:

```shell
cd support-ops-agent
cat deployment_metadata.json
```

Because `deployment_metadata.json` records `remote_agent_runtime_id`, `deployment_target: "agent_runtime"`, and `agent_directory: "app"`, `agents-cli publish gemini` automatically selects **Mode 1 (`--registration-type adk`)** and reads the reasoning engine ID for you!

**Your Tasks:**
1.  **Zero-Flag Metadata Publish:** Run `agents-cli publish gemini` passing `--gemini-app-id "$GEMINI_APP_ID"`, `--display-name "Support Ops Agent"`, and `--description "Triages tickets, checks SLAs, and escalates P1 incidents"`:
    ```shell
    # TODO: Register support-ops-agent with Gemini using deployment_metadata.json auto-detection
    ```
2.  **Interactive Wizard Exploration:** Know how to launch the guided terminal prompt mode (`agents-cli publish gemini --interactive`) when onboarding teammates interactively.
3.  **Production Observability Check (`streaming_agent_run_with_events`):** Write the `gcloud logging read` command that searches `reasoning_engine_stderr` on `aiplatform.googleapis.com/ReasoningEngine` for `streaming_agent_run_with_events` — the exact `AdkApp` method invoked when Gemini calls your agent via `:streamQuery`:
    ```shell
    # TODO: Write the `gcloud logging read` command filtering reasoning_engine_stderr for streaming_agent_run_with_events
    ```

---

### Step 3: Mode 2 — A2A Registration (From Module 32/33's Cloud Run or GKE Deployment)

Now suppose your SRE organization hosts a regional instance of `support-ops-agent` on **Cloud Run** (from Module 32) at `SERVICE_URL="https://support-ops-agent-xyz-uc.a.run.app"`. Cloud Run has no `ReasoningEngine` resource and deploys with `--no-allow-unauthenticated` by default.

**Your Tasks:**
1.  **Grant Discovery Engine Invoker Access:** Grant `roles/run.servicesInvoker` on the `support-ops-agent` Cloud Run service to `service-${PROJECT_NUMBER}@gcp-sa-discoveryengine.iam.gserviceaccount.com`:
    ```shell
    export SERVICE_URL="https://support-ops-agent-xyz-uc.a.run.app"

    # TODO: Run `gcloud run services add-iam-policy-binding` granting roles/run.servicesInvoker
    # to service-${PROJECT_NUMBER}@gcp-sa-discoveryengine.iam.gserviceaccount.com
    ```
2.  **Register via the Live A2A Agent Card:** Because `support-ops-agent` is a Python ADK project with `agent_directory: "app"` and `App(name="app")`, its live Agent Card is served at `${SERVICE_URL}/a2a/app/.well-known/agent-card.json`. Run `agents-cli publish gemini` in `a2a` mode:
    ```shell
    # TODO: Run `agents-cli publish gemini` with:
    #   --registration-type a2a
    #   --agent-card-url "${SERVICE_URL}/a2a/app/.well-known/agent-card.json"
    #   --gemini-app-id "$GEMINI_APP_ID"
    #   --display-name "Support Ops Agent (Cloud Run)"
    #   --description "Triages tickets, checks SLAs, and escalates P1 incidents over A2A"
    ```

---

### Step 4: Fleet Governance in Google Cloud Agent Registry (`gcloud agent-registry`)

Publishing to a Gemini app populates one workspace's Agent Gallery, whereas **Google Cloud Agent Registry** governs your entire cloud fleet of agents and MCP servers.

**Your Tasks:**
1.  **Audit Auto-Registered Agent Runtime Agents:** Run `gcloud agent-registry agents list` in `$DEPLOY_REGION` (`us-central1`) to verify that Module 35's `support-ops-agent` was auto-registered upon deployment:
    ```shell
    # TODO: List auto-registered agents in Google Cloud Agent Registry for $GOOGLE_CLOUD_PROJECT and $DEPLOY_REGION
    ```
2.  **Catalog Module 34's External Cloud Run MCP Server:** Create a compact `toolspec.json` file (representing the MCP `tools/list` schema, max 10 KB) for Module 34's Cloud Run MCP server (`MCP_SERVER_URL`), then register it in Agent Registry using `gcloud agent-registry services create`:
    ```shell
    cat << 'EOF' > toolspec.json
    {
      "tools": [
        {
          "name": "lookup_incident_runbook",
          "description": "Fetches approved SRE runbook steps for P1/P2 production alerts.",
          "inputSchema": {
            "type": "object",
            "properties": {
              "service": {"type": "string"}
            },
            "required": ["service"]
          }
        }
      ]
    }
    EOF

    export MCP_SERVER_URL="https://support-mcp-server-xyz-uc.a.run.app"

    # TODO: Run `gcloud agent-registry services create support-mcp-server` with:
    #   --project "$GOOGLE_CLOUD_PROJECT"
    #   --location "$DEPLOY_REGION"
    #   --mcp-server-spec-type=tool-spec
    #   --mcp-server-spec-content=toolspec.json
    #   --interfaces="url=${MCP_SERVER_URL}/mcp,protocolBinding=jsonrpc"
    ```

---

### Step 5: Enterprise Governance, RBAC & Data Connectors Blueprint

To complete your enterprise rollout plan around `support-ops-agent`, define the organizational guardrails for three departments sharing your Gemini Enterprise app (**Support & SRE**, **Sales**, and **HR**):
1.  **Data Connectors:** Which Gemini Enterprise connectors (e.g., Jira/ServiceNow, Salesforce, SharePoint) ground `support-ops-agent`, a `Lead Qualifier Agent`, and an `HR Policy Assistant` in live corporate records?
2.  **Least-Privilege RBAC:** Which Google Groups should have **User** vs. **Editor/Manager** access to `support-ops-agent`, and why should Marketing or HR users never get raw access to the P1 incident escalation connector?
3.  **SLOs & Cost Governance:** Define one operational alert (based on `streaming_agent_run_with_events` errors or escalation latency) and one departmental budget guardrail.

---

### Self-Reflection Questions
- Why does `agents-cli publish gemini` default to `--registration-type adk` (`:streamQuery`) for ADK agents on Agent Runtime instead of A2A, even though the Agent Runtime container also serves an A2A card?
- Why is the A2A Agent Card URL for `support-ops-agent` on Cloud Run `/a2a/app/.well-known/agent-card.json` rather than `/.well-known/agent-card.json`?
- How do Gemini Enterprise's **Agent Gallery** and **Google Cloud Agent Registry (`gcloud agent-registry`)** complement each other in a large enterprise?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="36">

# Lab 36 Solution: Publishing `support-ops-agent` to Gemini Enterprise & Governing Your Fleet

## Goal

This solution provides the complete, verified `agents-cli publish gemini` and `gcloud agent-registry` commands for publishing `support-ops-agent` across Agent Runtime and Cloud Run/GKE, cataloging Module 34's MCP server, and structuring enterprise RBAC and data grounding.

---

### Step 1: Discover Gemini Apps in Your Project

```shell
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
export DEPLOY_REGION="us-central1"
export PROJECT_NUMBER=$(gcloud projects describe "$GOOGLE_CLOUD_PROJECT" --format="value(projectNumber)")

# List all Gemini Enterprise apps in the current project
agents-cli publish gemini --list

export GEMINI_APP_ID="projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/YOUR_GEMINI_ENGINE_ID"
```

---

### Step 2: Mode 1 — Native ADK `:streamQuery` Registration (Agent Runtime)

From inside `support-ops-agent/` (where Module 35 wrote `deployment_metadata.json` with `remote_agent_runtime_id`, `deployment_target: "agent_runtime"`, and `agent_directory: "app"`):

```shell
cd support-ops-agent

# 1. Zero-flag auto-detection from deployment_metadata.json (defaults to --registration-type adk)
agents-cli publish gemini \
  --gemini-app-id "$GEMINI_APP_ID" \
  --display-name "Support Ops Agent" \
  --description "Triages tickets, checks SLAs, and escalates P1 incidents"

# 2. Optional interactive wizard for guided onboarding
agents-cli publish gemini --interactive

# 3. Optional explicit CI/CD invocation (when running without deployment_metadata.json)
export AGENT_RUNTIME_ID=$(python3 -c 'import json; print(json.load(open("deployment_metadata.json"))["remote_agent_runtime_id"])')
agents-cli publish gemini \
  --registration-type adk \
  --agent-runtime-id "$AGENT_RUNTIME_ID" \
  --gemini-app-id "$GEMINI_APP_ID" \
  --display-name "Support Ops Agent" \
  --description "Triages tickets, checks SLAs, and escalates P1 incidents" \
  --tool-description "Looks up enterprise tickets, verifies SLA targets, and escalates P1 incidents"

# 4. Trace native :streamQuery invocations in Cloud Logging via streaming_agent_run_with_events
gcloud logging read \
  'resource.type="aiplatform.googleapis.com/ReasoningEngine" AND logName:"reasoning_engine_stderr" AND textPayload:"streaming_agent_run_with_events"' \
  --project="$GOOGLE_CLOUD_PROJECT" \
  --limit=20
```

---

### Step 3: Mode 2 — A2A Registration (Cloud Run / GKE Deployment)

```shell
export SERVICE_URL="https://support-ops-agent-xyz-uc.a.run.app"

# 1. Grant Discovery Engine service agent permission to invoke the private Cloud Run service
gcloud run services add-iam-policy-binding support-ops-agent \
  --region="$DEPLOY_REGION" \
  --project="$GOOGLE_CLOUD_PROJECT" \
  --member="serviceAccount:service-${PROJECT_NUMBER}@gcp-sa-discoveryengine.iam.gserviceaccount.com" \
  --role="roles/run.servicesInvoker"

# 2. Publish over A2A using /a2a/app/.well-known/agent-card.json (matching agent_directory: "app")
agents-cli publish gemini \
  --registration-type a2a \
  --agent-card-url "${SERVICE_URL}/a2a/app/.well-known/agent-card.json" \
  --gemini-app-id "$GEMINI_APP_ID" \
  --display-name "Support Ops Agent (Cloud Run)" \
  --description "Triages tickets, checks SLAs, and escalates P1 incidents over A2A"
```

---

### Step 4: Fleet Governance in Google Cloud Agent Registry (`gcloud agent-registry`)

```shell
# 1. Inspect auto-registered Agent Runtime agents in your project and region
gcloud agent-registry agents list \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --location "$DEPLOY_REGION"

# Describe a specific registered agent (replace AGENT_NAME from list output)
# gcloud agent-registry agents describe AGENT_NAME --project "$GOOGLE_CLOUD_PROJECT" --location "$DEPLOY_REGION"

# 2. Register Module 34's external Cloud Run MCP server with its tools/list specification (max 10 KB)
cat << 'EOF' > toolspec.json
{
  "tools": [
    {
      "name": "lookup_incident_runbook",
      "description": "Fetches approved SRE runbook steps for P1/P2 production alerts.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "service": {"type": "string"}
        },
        "required": ["service"]
      }
    }
  ]
}
EOF

export MCP_SERVER_URL="https://support-mcp-server-xyz-uc.a.run.app"

gcloud agent-registry services create support-mcp-server \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --location "$DEPLOY_REGION" \
  --mcp-server-spec-type=tool-spec \
  --mcp-server-spec-content=toolspec.json \
  --interfaces="url=${MCP_SERVER_URL}/mcp,protocolBinding=jsonrpc"
```

---

### Step 5: Enterprise Governance, RBAC & Data Connectors Blueprint (Reference Architecture)

*   **Data Connectors & Grounding:**
    *   **`Support Ops Agent` (ADK on Agent Runtime):** Connected to **Jira / ServiceNow** and **Confluence** connectors (plus OAuth 2.0 `--authorization-id` so ticket escalations execute under the authenticated engineer's identity).
    *   **`Lead Qualifier Agent` (ADK on Agent Runtime):** Grounded in the **Salesforce Connector** for account tier and pipeline scoring.
    *   **`HR Policy Assistant` (ADK or Agent Designer):** Grounded in the **SharePoint / Google Drive Connector** for authoritative employee handbook RAG.
*   **Least-Privilege RBAC Policy:**
    *   **`Support Ops Agent`:** Invocable by `support-tier1@company.com` and `sre-oncall@company.com`; managed exclusively by `platform-ai-eng@company.com`. Marketing and general employee groups do not receive invoker access to P1 SRE paging tools.
    *   **`HR Policy Assistant`:** Invocable by `all-employees@company.com`; managed by `hr-ops@company.com`.
*   **SLOs, Alerting & Cost Governance:**
    *   **Operational Alert:** Configure a Cloud Monitoring log-based alert firing if `reasoning_engine_stderr` logs containing `streaming_agent_run_with_events` exceed a 2% error rate over 15 minutes.
    *   **Cost Guardrail:** Assign per-department project/label budgets (using `agents-cli deploy --labels "cost-center=support-ops,env=prod"`) with automated threshold alerts at 80% of monthly spend.

---

### Self-Reflection Answers

1.  **Why does `agents-cli publish gemini` default to `--registration-type adk` (`:streamQuery`) for ADK agents on Agent Runtime instead of A2A, even though the Agent Runtime container also serves an A2A card?**
    *   **Answer:** Native ADK registration invokes the `ReasoningEngine` directly via `:streamQuery` (`streaming_agent_run_with_events`), providing first-party end-to-end Google Cloud IAM authentication, managed `VertexAiSessionService` continuity, and native support for OAuth 2.0 user consent (`--authorization-id`) without extra network hops.

2.  **Why is the A2A Agent Card URL for `support-ops-agent` on Cloud Run `/a2a/app/.well-known/agent-card.json` rather than `/.well-known/agent-card.json`?**
    *   **Answer:** In Python ADK projects scaffolded by `agents-cli`, `fast_api_app.py` mounts A2A routes per application directory under `/a2a/{agent_directory}/.well-known/agent-card.json`. Because `support-ops-agent` uses the default `agent_directory: "app"` (matching `App(name="app")`), its card path is `/a2a/app/.well-known/agent-card.json` (whereas ADK Go scaffolds mount `/.well-known/agent-card.json` at the root).

3.  **How do Gemini Enterprise's Agent Gallery and Google Cloud Agent Registry (`gcloud agent-registry`) complement each other in a large enterprise?**
    *   **Answer:** The **Agent Gallery** (`agents-cli publish gemini`) is the workspace consumption portal where authorized employees discover and chat with approved assistants inside a specific Gemini Enterprise app. **Google Cloud Agent Registry** (`gcloud agent-registry`) is the cloud platform governance plane where architects and security teams inventory, describe, and audit *all* deployed agents (auto-registered from Agent Runtime) and MCP tool servers (`toolspec.json`) across projects and regions.

</SolutionVault>
