---
sidebar_position: 35
title: "Module 35: Deploying to Agent Runtime"
pagination_label: "Module 35: Deploying to Agent Runtime — 📖 Theory & Overview"
---

# Module 35: Deploying to Agent Runtime

![Deploying to Agent Runtime Banner (Light)](img/hero-light.webp#gh-light-mode-only)
![Deploying to Agent Runtime Banner (Dark)](img/hero-dark.webp#gh-dark-mode-only)

## Theory

### From Local Prototype to Managed Agent Infrastructure

In Modules 32 and 33, you deployed our stateful Python **`support-ops-agent`** (`gemini-3.8-flash`) to serverless containers on Google Cloud Run and orchestrated pods on GKE Autopilot. **Google Cloud's Agent Runtime** (formerly Vertex AI Agent Engine) completes the Part 6 compute triad as a purpose-built, fully managed runtime in the Gemini Enterprise Agent Platform.

### Two Paths to Agent Runtime

1.  **Accelerated Container Deployment with `agents-cli` (Recommended Best Practice):**
    *   **Method:** Use **`google-agents-cli`** (`agents-cli scaffold enhance` + `agents-cli deploy`). Unlike legacy pickle-based packaging, `agents-cli` uses **container-based deployment**: it packages your project and Agent Runtime builds the container image directly from your project's `Dockerfile`—running the exact same unified `uvicorn app.fast_api_app:app` entrypoint that powers Cloud Run and GKE.
    *   **Key Features:** Automatic managed session wiring (`VertexAiSessionService`), built-in A2A + native `:streamQuery` serving, Terraform Infrastructure-as-Code (`google_vertex_ai_reasoning_engine` with `lifecycle.ignore_changes`), CI/CD pipelines (GitHub Actions or Cloud Build), and enterprise security controls (Agent Identity, Agent Gateway, CMEK).
    *   **Best For:** All production ADK agents, multi-environment GitOps workflows, and agents destined for Gemini Enterprise registration in Module 36.

2.  **Programmatic Python SDK Deployment (`vertexai.agent_engines`):**
    *   **Method:** Wrap a Python `Agent` in `agent_engines.AdkApp` and deploy imperatively with `vertexai.agent_engines.create(...)`.
    *   **Best For:** Understanding the underlying `ReasoningEngine` API mechanics, notebooks, or custom programmatic lifecycle scripts (`deploy.py`, `interact.py`, `cleanup.py`).

This module's lab walks you hands-on through both workflows.

---

### How Container-Based Agent Runtime Works

![Agent Runtime Architecture & Authorization Lifecycle (Light)](img/agent-runtime-auth-lifecycle-light.webp#gh-light-mode-only)
![Agent Runtime Architecture & Authorization Lifecycle (Dark)](img/agent-runtime-auth-lifecycle-dark.webp#gh-dark-mode-only)
*Figure: Managed container execution, automatic session persistence, and governed networking in Agent Runtime.*

#### 1. Unified `Dockerfile` & Dual-Protocol Surface
When you enhance `support-ops-agent` with `agents-cli scaffold enhance . --deployment-target agent_runtime`, `app/fast_api_app.py` configures a single FastAPI container (`get_fast_api_app`) that simultaneously serves:
*   **Native Reasoning Engine Contract (`/api/reasoning_engine` & `/api/stream_reasoning_engine`):** Added via `attach_reasoning_engine_routes(app)`, constructing an internal `AdkApp` adapter to handle native `:query` and `:streamQuery` invocations (used by the Cloud Console Playground, `agents-cli run --mode adk`, and Gemini Enterprise ADK registration).
*   **Built-in A2A & ADK HTTP Routes via `/api` Passthrough:** Agent Runtime exposes your container's HTTP routes externally under `https://{location}-aiplatform.googleapis.com/reasoningEngines/v1/{resource}/api/{container_path}`—making both `/run_sse` and your live A2A Agent Card (`/api/a2a/app/.well-known/agent-card.json`) reachable with standard Google Cloud IAM credentials (`agents-cli run --mode a2a`).

#### 2. Managed Sessions (`VertexAiSessionService`) — Do Not Override `session_type`!
On Cloud Run and GKE, you choose `--session-type` (`in_memory`, `cloud_sql`, or `agent_platform_sessions`). On **Agent Runtime**, sessions are managed natively by the platform:
*   At scaffold time, the project uses in-memory sessions locally (`shared://session`).
*   At cloud runtime, Agent Runtime injects `GOOGLE_CLOUD_AGENT_ENGINE_ID`, and `app_utils/services.py` **automatically upgrades the runner to `VertexAiSessionService`** (and upgrades artifacts to `GcsArtifactService` when `LOGS_BUCKET_NAME` is set).
*   **Critical Rule:** **Never hardcode or pass a custom `--session-type` / `session_type` override when targeting `agent_runtime`.** If migrating a project that sets `session_type`, clear it so Agent Runtime's managed session backend takes over cleanly.

#### 3. Non-Blocking Rollouts (`--no-wait` & `--status`) and `deployment_metadata.json`
Because Agent Runtime compiles your `Dockerfile` remotely and provisions managed infrastructure, deployments typically take **5–10 minutes**:
*   Pass `--no-wait` to start the rollout and return your terminal immediately, then poll progress with `agents-cli deploy --status` (and audit live instances anytime with `agents-cli deploy --list`).
*   Separate infrastructure region from model endpoint: deploy the engine in a concrete region (`--region us-central1`) while injecting `--env-vars "GOOGLE_GENAI_USE_ENTERPRISE=1,GOOGLE_CLOUD_LOCATION=global"` so `gemini-3.8-flash` resolves on the global endpoint.
*   When the rollout finishes (synchronously or via `--status`), `agents-cli` writes **`deployment_metadata.json`**:
    ```json
    {
      "remote_agent_runtime_id": "projects/PROJECT/locations/us-central1/reasoningEngines/ENGINE_ID",
      "deployment_target": "agent_runtime",
      "is_a2a": true,
      "agent_directory": "app",
      "deployment_timestamp": "2026-11-26T10:30:00.000+00:00"
    }
    ```
    In **Module 36**, `agents-cli publish gemini` reads this file automatically for **zero-flag ADK registration** into Gemini Enterprise!

---

### Enterprise Security & Governance Controls on Agent Runtime

Agent Runtime unlocks first-class enterprise security capabilities directly from `agents-cli`:

| Capability | CLI / Scaffold Flags | Operational Behavior & Requirements |
| :--- | :--- | :--- |
| **Agent Identity** | `agents-cli deploy --agent-identity` (or `--no-agent-identity`) | Assigns a dedicated, verifiable workload identity to the Agent Runtime resource instead of sharing a broad project default compute identity. Required before binding an Agent Gateway. |
| **Agent Gateway** | `agents-cli scaffold enhance . --agent-gateway` + `deploy --agent-gateway-egress <GW>` / `--agent-gateway-ingress <GW>` | Routes inbound (`CLIENT_TO_AGENT`) and/or outbound (`AGENT_TO_ANYWHERE`) traffic through a governed Agent Gateway (`projects/PROJECT/locations/REGION/agentGateways/GATEWAY`). Because an egress gateway performs TLS inspection, you **must** scaffold/enhance with `--agent-gateway` so the `Dockerfile` trusts the platform-injected `AGENT_GATEWAY_ROOT_CERTIFICATES` build arg. |
| **Customer-Managed Encryption (CMEK)** | `agents-cli deploy --key <KMS_KEY_RESOURCE>` | Encrypts the Agent Runtime instance at creation time using your single-region Cloud KMS key (`projects/KEY_PROJECT/locations/REGION/keyRings/RING/cryptoKeys/KEY`). Grant `roles/cloudkms.cryptoKeyEncrypterDecrypter` to both `service-PROJECT_NUMBER@gcp-sa-aiplatform.iam.gserviceaccount.com` and `service-PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com` first. For Terraform-managed staging/prod, configure `encryption_spec` in `service.tf` (keys are immutable after creation). |
| **Private VPC (PSC-I)** | `agents-cli deploy --network-attachment <ATTACHMENT>` | Enables private VPC egress via Private Service Connect interfaces (with optional `--dns-peering-domain`, `--dns-peering-project`, and `--dns-peering-network`). |

<KnowledgeCheck
  id="m35-agent-runtime-sessions-and-gateway"
  question="When deploying a scaffolded Python ADK agent ('support-ops-agent') to Agent Runtime using 'agents-cli', how are durable multi-turn sessions configured, and what is required before binding an outbound '--agent-gateway-egress'?"
  options={[
    "Do not set a custom 'session_type' because Agent Runtime automatically wires managed 'VertexAiSessionService' when 'GOOGLE_CLOUD_AGENT_ENGINE_ID' is injected; for '--agent-gateway-egress', enable '--agent-identity' and run 'agents-cli scaffold enhance . --agent-gateway' so the Dockerfile trusts 'AGENT_GATEWAY_ROOT_CERTIFICATES'",
    "Pass '--session-type sqlite_local' to 'agents-cli deploy' and disable TLS verification in Python",
    "Agent Runtime only supports stateless single-turn prompts and cannot use Dockerfiles",
    "Manually edit '/etc/hosts' inside the container and run 'gcloud compute ssh' into the reasoning engine"
  ]}
  correctIndex={0}
  hint="Recall how 'app_utils/services.py' upgrades 'shared://session' on Agent Runtime and why an egress Agent Gateway needs root CA trust in the Dockerfile."
  explanation="Agent Runtime automatically upgrades 'shared://session' to 'VertexAiSessionService' at runtime (so any custom 'session_type' should be omitted/cleared). Binding '--agent-gateway-egress' requires Agent Identity ('--agent-identity') plus 'scaffold enhance . --agent-gateway' so the Dockerfile consumes 'AGENT_GATEWAY_ROOT_CERTIFICATES' for outbound TLS inspection."
/>

### Key Takeaways
- **Container-Based Agent Runtime:** `agents-cli deploy` packages your repository and builds your root `Dockerfile` on Agent Runtime, serving `uvicorn app.fast_api_app:app` for both native `:streamQuery` (`--mode adk`) and `/api` HTTP passthrough A2A routes (`--mode a2a`).
- **Automatic Managed Sessions:** Agent Runtime automatically upgrades `shared://session` to `VertexAiSessionService` when `GOOGLE_CLOUD_AGENT_ENGINE_ID` is present—never hardcode custom `session_type` overrides when targeting `agent_runtime`.
- **Async Rollouts & Metadata Handoff:** Use `agents-cli deploy --no-wait` and `agents-cli deploy --status` to manage 5–10 minute container builds cleanly; completion writes `deployment_metadata.json` (`"agent_directory": "app"`), powering zero-flag Gemini Enterprise publishing in Module 36.
- **Enterprise Governance Ready:** First-class flags for `--agent-identity`, `--agent-gateway-egress` / `--agent-gateway-ingress` (paired with `--agent-gateway` at scaffold time), and CMEK (`--key`) let security teams enforce identity, governed network perimeter inspection, and customer-managed encryption without rewriting agent logic.
