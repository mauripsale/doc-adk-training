---
sidebar_position: 36
title: "Module 36: Gemini Enterprise (formerly AgentSpace)"
pagination_label: "Module 36: Gemini Enterprise Publishing — 📖 Theory & Overview"
---

# Module 36: Gemini Enterprise (formerly AgentSpace)

![Gemini Enterprise Agent Ecosystem Banner (Light)](img/hero-light.webp#gh-light-mode-only)
![Gemini Enterprise Agent Ecosystem Banner (Dark)](img/hero-dark.webp#gh-dark-mode-only)

## Theory

### The Finale of the Part 6 `support-ops-agent` Arc

Across Part 6, you took a single stateful Python ADK application — **`support-ops-agent`** (`gemini-3.8-flash`, `agent_directory: "app"`, `App(name="app")`) — from prototype scaffolding and automated evaluation (Module 31) through serverless **Cloud Run** (Module 32), **GKE Autopilot** (Module 33), externalized **Cloud Run MCP** tooling (Module 34), and **Agent Runtime** (Module 35).

Now comes the final operational mile: **publishing `support-ops-agent` into Gemini Enterprise** (formerly Google AgentSpace) so employees across your organization can discover and invoke it inside a governed workspace, and **cataloging your entire agent and MCP fleet in Google Cloud Agent Registry**.

Think of the relationship like this:
*   **ADK + `agents-cli` = Engineering & Deployment**: How you build, evaluate, containerize, and roll out agents across Agent Runtime, Cloud Run, and GKE.
*   **Gemini Enterprise + Agent Registry = Enterprise Operations & Governance**: Where employees discover approved agents in the **Agent Gallery**, connect private enterprise data sources under strict RBAC, and audit every agent and MCP server across Google Cloud.

### Core Capabilities of Gemini Enterprise

*   **Agent Gallery:** A centralized internal marketplace where published ADK and A2A agents appear alongside pre-built Google agents (such as Deep Research) for authorized employees to discover and invoke.
*   **Enterprise Governance & RBAC:** Fine-grained identity, role-based access control, OAuth 2.0 user-scoped consent (`--authorization-id`), audit logging, and compliance boundaries (HIPAA, FedRAMP).
*   **Enterprise Data Connectors:** Secure, pre-built connectors for Google Drive, SharePoint, Jira, ServiceNow, Salesforce, and BigQuery—grounding agents in authoritative corporate records via Retrieval Augmented Generation (RAG).
*   **Agent Designer:** A governed no-code studio empowering business teams to compose lightweight workflow assistants while engineering teams focus on custom code-first ADK agents.

![Gemini Enterprise Integration Hub & Deployment Lifecycle (Light)](img/gemini-enterprise-hub-light.webp#gh-light-mode-only)
![Gemini Enterprise Integration Hub & Deployment Lifecycle (Dark)](img/gemini-enterprise-hub-dark.webp#gh-dark-mode-only)
*Figure: Enterprise data grounding, RBAC governance, and dual-mode ADK / A2A agent registration in Gemini Enterprise.*

---

### Publishing `support-ops-agent` with `agents-cli publish gemini`

Once a **text-based** agent is deployed and a Gemini app exists in your Google Cloud project, register it using `agents-cli publish gemini`:
*   **Discover Existing Gemini Apps:** Run `agents-cli publish gemini --list` to inspect the full `projects/<PROJECT_NUMBER>/locations/global/collections/default_collection/engines/<ENGINE_ID>` resource names in your project.
*   **Idempotent Updates:** Registration is **idempotent**—re-running `agents-cli publish gemini` updates your existing gallery entry in place without creating duplicates.
*   **Text-Based Agents Only:** Live bidirectional voice agents (`/run_live` bidi streaming) are **not supported** by the Gemini app (which has no `/run_live` transport, and Live agents omit their A2A card). Always register text-based agents like `support-ops-agent`.

#### Mode 1: ADK Native `:streamQuery` Registration (Default on Agent Runtime)

For ADK agents deployed to **Agent Runtime** in Module 35, `agents-cli deploy` wrote **`deployment_metadata.json`** (`remote_agent_runtime_id`, `deployment_target: "agent_runtime"`, `is_a2a: true`, `agent_directory: "app"`). When `deployment_metadata.json` is present in your working directory, `agents-cli publish gemini` **auto-detects** the reasoning engine ID and defaults `--registration-type` to **`adk`**.

In **ADK mode**, Gemini invokes your Agent Runtime instance natively over `:streamQuery`, authenticating end-to-end with Google Cloud IAM and supporting managed OAuth 2.0 user consent (`--authorization-id`):

```shell
# 1. Discover Gemini apps in your project
agents-cli publish gemini --list

# 2. Zero-flag metadata auto-detection (reads remote_agent_runtime_id from Module 35's deployment_metadata.json)
agents-cli publish gemini \
  --gemini-app-id "$GEMINI_APP_ID" \
  --display-name "Support Ops Agent" \
  --description "Triages tickets, checks SLAs, and escalates P1 incidents"

# 3. Interactive guided wizard (lists Gemini apps, offers metadata auto-detection, prompts for missing fields)
agents-cli publish gemini --interactive

# 4. Explicit programmatic mode for CI/CD pipelines (no metadata file required)
agents-cli publish gemini \
  --registration-type adk \
  --agent-runtime-id "$AGENT_RUNTIME_ID" \
  --gemini-app-id "$GEMINI_APP_ID" \
  --display-name "Support Ops Agent" \
  --description "Triages tickets, checks SLAs, and escalates P1 incidents" \
  --tool-description "Looks up enterprise support tickets, verifies SLA targets, and escalates P1 incidents"
```

> **Production Debugging Tip (`streaming_agent_run_with_events`):** Under the hood, Gemini's native `:streamQuery` call dispatches to `AdkApp`'s `streaming_agent_run_with_events` method on Agent Runtime. Whenever you diagnose an ADK invocation error after publishing, filter Cloud Logging's `reasoning_engine_stderr` stream for `streaming_agent_run_with_events` to pinpoint the exact Python traceback (and ensure Python projects run `google-cloud-aiplatform > 1.128.0` to avoid legacy `"Session not found"` bugs).

#### Mode 2: A2A Registration (Cloud Run & GKE Deployments from Modules 32 & 33)

**Cloud Run** and **GKE** do not expose a `ReasoningEngine` resource, so **A2A (`--registration-type a2a`)** is the default—and only—registration mode for those targets (as well as for any non-ADK framework).

Because our Python `support-ops-agent` is scaffolded with `agent_directory: "app"` and `App(name="app")`, its FastAPI container serves its live Agent Card at **`${SERVICE_URL}/a2a/app/.well-known/agent-card.json`** (whereas ADK Go projects serve `/.well-known/agent-card.json` at the root).

Before registering a private (`--no-allow-unauthenticated`) Cloud Run service, grant **`roles/run.servicesInvoker`** to the Discovery Engine service agent (`service-${PROJECT_NUMBER}@gcp-sa-discoveryengine.iam.gserviceaccount.com`):

```shell
export PROJECT_NUMBER=$(gcloud projects describe "$GOOGLE_CLOUD_PROJECT" --format="value(projectNumber)")

# 1. Authorize Gemini Enterprise (Discovery Engine SA) to invoke the Cloud Run service
gcloud run services add-iam-policy-binding support-ops-agent \
  --region="$DEPLOY_REGION" \
  --project="$GOOGLE_CLOUD_PROJECT" \
  --member="serviceAccount:service-${PROJECT_NUMBER}@gcp-sa-discoveryengine.iam.gserviceaccount.com" \
  --role="roles/run.servicesInvoker"

# 2. Register support-ops-agent via its live /a2a/app/.well-known/agent-card.json URL
agents-cli publish gemini \
  --registration-type a2a \
  --agent-card-url "${SERVICE_URL}/a2a/app/.well-known/agent-card.json" \
  --gemini-app-id "$GEMINI_APP_ID" \
  --display-name "Support Ops Agent (Cloud Run)" \
  --description "Triages tickets, checks SLAs, and escalates P1 incidents over A2A"
```

#### Registration Mode Comparison

| Aspect | Mode 1: ADK Registration (`adk`) | Mode 2: A2A Registration (`a2a`) |
| :--- | :--- | :--- |
| **Target Compute** | **Agent Runtime** (ADK projects only; default when `deployment_metadata.json` exists) | **Cloud Run**, **GKE**, or any non-ADK framework |
| **Wire Protocol** | Native `ReasoningEngine` `:streamQuery` (`streaming_agent_run_with_events`) | Standardized Agent-to-Agent (A2A) JSON-RPC via live Agent Card |
| **Auth & User Consent** | End-to-end IAM + managed OAuth 2.0 user consent (`--authorization-id`) | `roles/run.servicesInvoker` for `service-<PROJECT_NUMBER>@gcp-sa-discoveryengine.iam.gserviceaccount.com` |
| **Required Target Flag** | Auto-detected from `deployment_metadata.json` or `--agent-runtime-id` | `--agent-card-url "${SERVICE_URL}/a2a/app/.well-known/agent-card.json"` |

---

### Fleet Governance with Google Cloud Agent Registry (`gcloud agent-registry`)

While `agents-cli publish gemini` adds an agent to a specific Gemini app's user-facing gallery, **Google Cloud Agent Registry** provides a centralized, fleet-wide catalog of **every agent and MCP server** across your project and organization (managed with `roles/agentregistry.editor`):

*   **Auto-Registered Agent Runtime Agents:** Every agent deployed to Agent Runtime via `agents-cli deploy` (including Module 35's `support-ops-agent`) is **automatically registered** in Agent Registry—no extra CLI step required!
*   **Cataloging External Cloud Run MCP Servers:** External MCP servers (such as Module 34's stateful Cloud Run MCP server) are not auto-introspected; register them in a concrete single region (such as `us-central1`, not `us`/`eu` multi-regions) by uploading their `tools/list` specification (`toolspec.json`, up to 10 KB) via `gcloud agent-registry services create`:

```shell
# 1. Audit auto-registered Agent Runtime agents in your project and region
gcloud agent-registry agents list \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --location "$DEPLOY_REGION"

# 2. Register Module 34's Cloud Run MCP server in the enterprise fleet catalog
gcloud agent-registry services create support-mcp-server \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --location "$DEPLOY_REGION" \
  --mcp-server-spec-type=tool-spec \
  --mcp-server-spec-content=toolspec.json \
  --interfaces="url=${MCP_SERVER_URL}/mcp,protocolBinding=jsonrpc"
```
*(In Terraform-managed production environments, codify external MCP registrations declaratively with the `google_agent_registry_service` resource and an `mcp_server_spec` block.)*

<KnowledgeCheck
  id="m36-gemini-enterprise-publish"
  question="You deployed the Python 'support-ops-agent' (where 'agent_directory' is 'app' and 'App(name=app)') to Cloud Run in Module 32 and want to publish it to an existing Gemini Enterprise app. Which IAM binding and 'agents-cli publish gemini' command are required?"
  options={[
    "Grant 'roles/run.servicesInvoker' to 'service-<PROJECT_NUMBER>@gcp-sa-discoveryengine.iam.gserviceaccount.com', then run 'agents-cli publish gemini --registration-type a2a --agent-card-url \"${SERVICE_URL}/a2a/app/.well-known/agent-card.json\" --gemini-app-id \"$GEMINI_APP_ID\"'",
    "Run 'agents-cli publish gemini --registration-type adk --agent-runtime-id \"${SERVICE_URL}\"' with no IAM changes",
    "Convert 'support-ops-agent' to a '/run_live' voice agent so Gemini Enterprise auto-discovers it",
    "Copy 'deployment_metadata.json' into '/tmp' and run 'kubectl expose pod'"
  ]}
  correctIndex={0}
  hint="Cloud Run has no ReasoningEngine resource and deploys private by default ('--no-allow-unauthenticated'), while Python ADK scaffolds mount the A2A card under '/a2a/{agent_directory}/.well-known/agent-card.json'."
  explanation="On Cloud Run, Discovery Engine's service agent ('service-<PROJECT_NUMBER>@gcp-sa-discoveryengine.iam.gserviceaccount.com') needs 'roles/run.servicesInvoker', and 'agents-cli publish gemini' registers the Python ADK service over '--registration-type a2a' using '${SERVICE_URL}/a2a/app/.well-known/agent-card.json'."
/>

### Key Takeaways
- **Two Complementary Enterprise Catalogs:** **`agents-cli publish gemini`** registers text-based agents into a Gemini app's user-facing **Agent Gallery**, whereas **Google Cloud Agent Registry (`gcloud agent-registry`)** governs your organization-wide inventory of **agents and MCP servers**.
- **Mode 1 (`adk`) for Agent Runtime:** Leverages Module 35's `deployment_metadata.json` for zero-flag auto-detection, invoking `support-ops-agent` natively via `:streamQuery` (`streaming_agent_run_with_events` in `reasoning_engine_stderr`) with full OAuth 2.0 consent support (`--authorization-id`).
- **Mode 2 (`a2a`) for Cloud Run & GKE:** Connects serverless or Kubernetes deployments via `${SERVICE_URL}/a2a/app/.well-known/agent-card.json` after granting `roles/run.servicesInvoker` to `service-${PROJECT_NUMBER}@gcp-sa-discoveryengine.iam.gserviceaccount.com`.
- **Enterprise Grounding & Governance:** Combining Gemini Enterprise's RBAC, Data Connectors (RAG over private SharePoint, Salesforce, or BigQuery data), and Agent Registry fleet visibility turns isolated ADK containers into a secure, auditable enterprise AI platform.

This completes **Part 6: Deployment & Enterprise** — you can now scaffold, evaluate, containerize, deploy across Cloud Run, GKE, and Agent Runtime, publish to Gemini Enterprise, and govern agents and MCP servers at enterprise scale with `agents-cli`! In **Part 7**, you will bring every pattern from the curriculum together in full capstone architectures.
