---
sidebar_position: 3
title: "Lab Solution"
---

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
