---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 32: Deployment to Cloud Run — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 32: Deploying Support Ops Agent to Cloud Run with Google Agents CLI

## Goal

In this lab, you will carry **`support-ops-agent`** (`gemini-3.8-flash`) from its local prototype into production on **Google Cloud Run** using the **`agents-cli` Golden Path**: enhancing the project in place with Cloud Run Terraform & CI/CD scaffolding (`scaffold enhance`), deploying with clean infrastructure-vs-model region separation (`agents-cli deploy`), querying both its **built-in A2A** and **ADK SSE** endpoints live in the cloud, and grading evaluation traces generated directly from the deployed Cloud Run URL.

<Setup/>

### Prerequisites

* A Google Cloud Project with billing enabled and `Owner` or `Editor` permissions.
* Google Cloud CLI installed and authenticated:
  ```shell
  gcloud auth login
  gcloud auth application-default login
  gcloud config set project YOUR_PROJECT_ID
  ```
* Enable the required Google Cloud APIs in your project:
  ```shell
  gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    aiplatform.googleapis.com \
    secretmanager.googleapis.com \
    --project=YOUR_PROJECT_ID
  ```
* `google-agents-cli` installed (`uv tool install google-agents-cli`).

---

### Step 1: Prepare or Fast-Bootstrap `support-ops-agent`

* **Continuing from Module 31?** Simply enter your existing `support-ops-agent/` directory:
  ```shell
  cd /path/to/your/adk-training/support-ops-agent
  agents-cli info
  ```

* **Starting fresh at Module 32?** Run this 10-second standalone bootstrap from `adk-training/` (do **not** `mkdir support-ops-agent` beforehand) to pull the canonical `app/agent.py` and evaluation dataset:
  ```shell
  cd /path/to/your/adk-training
  agents-cli scaffold create support-ops-agent --agent adk --prototype --agent-guidance-filename GEMINI.md
  curl -fsSL https://mauripsale.github.io/doc-adk-training/samples/part6/agent.py -o support-ops-agent/app/agent.py
  curl -fsSL https://mauripsale.github.io/doc-adk-training/samples/part6/basic-dataset.json -o support-ops-agent/tests/eval/datasets/basic-dataset.json
  cd support-ops-agent
  ```

Verify that `app/agent.py` defines `root_agent` (`name="support_ops_agent"`, `MODEL = "gemini-3.8-flash"`) and `app = App(root_agent=root_agent, name="app")`, and that `root_agent_name: support_ops_agent` is set in `agents-cli-manifest.yaml`.

---

### Step 2: Enhance the Prototype for Cloud Run (`scaffold enhance`)

Upgrade `support-ops-agent` in place to add Cloud Run Terraform modules, GitHub Actions CI/CD workflows, and Locust load tests while leaving `app/agent.py` and `.env` completely intact:

1. **Export your project ID and Cloud Run region, then run `scaffold enhance`:**

   ```shell
   export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
   export DEPLOY_REGION=us-central1

   agents-cli scaffold enhance . \
     --deployment-target cloud_run \
     --cicd-runner github_actions \
     --region "$DEPLOY_REGION"

   agents-cli install
   ```

2. **Inspect the generated production artifacts:**
   * **`agents-cli-manifest.yaml`:** Confirm `deployment_target: cloud_run`, `cicd_runner: github_actions`, and `region: us-central1` are recorded.
   * **`deployment/terraform/single-project/service.tf`:** Inspect the `google_cloud_run_v2_service` definition, including `min_instance_count`, `max_instance_request_concurrency`, CPU/memory limits, and the runtime `app_sa` service account.
   * **`tests/load_test/load_test.py`:** Review the generated Locust load test used to benchmark concurrency and latency under load.
   * **`app/agent.py`:** Confirm your stateful `support_ops_agent` code was preserved untouched!

---

### Step 3: Deploy `support-ops-agent` to Cloud Run (`agents-cli deploy`)

Now package, build, and deploy the container to Cloud Run in `us-central1` while pointing `GOOGLE_CLOUD_LOCATION` inside the container to the **`global`** Gemini Enterprise / Vertex AI endpoint for `gemini-3.8-flash`.

1. **Preview the exact deployment command with `--dry-run`:**

   ```shell
   agents-cli deploy \
     --project "$GOOGLE_CLOUD_PROJECT" \
     --region "$DEPLOY_REGION" \
     --env-vars "GOOGLE_GENAI_USE_ENTERPRISE=1,GOOGLE_CLOUD_LOCATION=global" \
     --no-confirm-project \
     --dry-run
   ```
   Inspect the printed `gcloud` command to see how `agents-cli` configures `--memory 4Gi`, `--cpu 1`, `--concurrency 8`, `--min-instances 0`, and your runtime environment variables.

2. **Execute the live Cloud Run rollout:**

   ```shell
   agents-cli deploy \
     --project "$GOOGLE_CLOUD_PROJECT" \
     --region "$DEPLOY_REGION" \
     --env-vars "GOOGLE_GENAI_USE_ENTERPRISE=1,GOOGLE_CLOUD_LOCATION=global" \
     --no-confirm-project
   ```
   Wait 2–4 minutes while Cloud Build builds the `uv`-managed `Dockerfile`, pushes the image to Artifact Registry, and rolls out the Cloud Run revision.

---

### Step 4: Query & Evaluate the Live Cloud Run Service with `agents-cli`

1. **Capture the live Cloud Run `SERVICE_URL`:**

   ```shell
   SERVICE_URL=$(gcloud run services describe support-ops-agent \
     --region="$DEPLOY_REGION" \
     --project="$GOOGLE_CLOUD_PROJECT" \
     --format='value(status.url)')
   echo "Live Service URL: $SERVICE_URL"
   ```

2. **Test the live Agent-to-Agent (A2A) protocol endpoint (`--mode a2a`):**
   `agents-cli` automatically attaches your Google Cloud identity token, fetches `$SERVICE_URL/a2a/app/.well-known/agent-card.json`, and invokes the agent over A2A JSON-RPC:

   ```shell
   agents-cli run "Investigate ticket TCK-1042 and check SLA." \
     --url "$SERVICE_URL" \
     --mode a2a
   ```
   Verify that the cloud service looks up `TCK-1042`, cites the `15 minutes` enterprise P1 SLA, and escalates to `24/7 P1 SRE Oncall`!

3. **Test the live ADK SSE streaming endpoint (`--mode adk`):**

   ```shell
   agents-cli run "Check ticket TCK-2088." \
     --url "$SERVICE_URL" \
     --mode adk \
     --app-name app
   ```
   Verify that it returns the status (`investigating`) and standard P3 SLA (`24 business hours`) for Northwind Retail.

4. **Run remote cloud trace generation + automated grading against the live URL:**
   Drive the evaluation dataset from `tests/eval/datasets/basic-dataset.json` directly against your deployed Cloud Run container and grade the captured traces:

   ```shell
   agents-cli eval generate --url "$SERVICE_URL" --app-name app && agents-cli eval grade
   ```
   Inspect the printed score summary and the new `artifacts/grade_results/results_<timestamp>.html` report to confirm parity between local and cloud execution!

---

### Step 5: Under the Hood Reference & Revision Rollback

<details>
<summary><strong>Under the Hood Reference: <code>adk deploy cloud_run</code>, Instant Traffic Rollback &amp; Cleanup</strong></summary>

When working on standalone single-folder ADK experiments outside an `agents-cli` repository, the core ADK CLI also offers `uv run adk deploy cloud_run`, which synthesizes a temporary Dockerfile and runs `gcloud run deploy`:

```shell
# Standalone ADK CLI alternative (for non-scaffolded single-agent folders):
uv run adk deploy cloud_run \
  --project="$GOOGLE_CLOUD_PROJECT" \
  --region="$DEPLOY_REGION" \
  --env GOOGLE_CLOUD_LOCATION=global \
  app/
```

**Instant Cloud Run Revision Rollback (Zero-Commit Recovery):**
While GitOps rollback (reverting a commit on `main`) is the primary production strategy, Cloud Run keeps immutable revisions so you can shift 100% of traffic back to a known-good revision in seconds:

```shell
gcloud run revisions list \
  --service=support-ops-agent \
  --region="$DEPLOY_REGION" \
  --project="$GOOGLE_CLOUD_PROJECT"

gcloud run services update-traffic support-ops-agent \
  --to-revisions=REVISION_NAME=100 \
  --region="$DEPLOY_REGION" \
  --project="$GOOGLE_CLOUD_PROJECT"
```

**Optional Cost Cleanup:**
Because `agents-cli deploy` sets `--min-instances 0` by default, an idle service incurs zero compute cost (and keeping `support-ops-agent` live lets you register its A2A endpoint in Module 36!). Whenever you want to delete the Cloud Run service completely, run:

```shell
gcloud run services delete support-ops-agent \
  --region="$DEPLOY_REGION" \
  --project="$GOOGLE_CLOUD_PROJECT" \
  --quiet
```

</details>

### Having Trouble?
Check the troubleshooting guide and complete reference solution in `lab-solution.md` or unlock the **Reference Solution Vault** below.

### Lab Summary

Congratulations! You have promoted `support-ops-agent` to Google Cloud Run using the end-to-end `agents-cli` Golden Path:
* Upgraded a `--prototype` project in place via `agents-cli scaffold enhance . --deployment-target cloud_run` without modifying `app/agent.py`.
* Previewed (`--dry-run`) and deployed the container with regional separation (`--region us-central1` + `GOOGLE_CLOUD_LOCATION=global`).
* Invoked the live authenticated Cloud Run service over both **A2A (`--mode a2a`)** and **ADK SSE (`--mode adk --app-name app`)**, and ran `agents-cli eval generate --url ... && agents-cli eval grade` against production HTTP endpoints.

### Self-Reflection Questions
* Why does `agents-cli deploy` default to `--no-allow-unauthenticated` on Cloud Run, and how would you expose a browser-accessible internal tool safely to employees without writing custom login code?
* If load testing with `tests/load_test/load_test.py` triggers container OOM restarts when you raise `--concurrency` from `8` to `32`, which flag should you scale alongside `--concurrency` and why?
* What happens to active conversation history in `support-ops-agent` when a Cloud Run instance scales down to zero under the default `in_memory` session configuration, and which `scaffold enhance` flag solves this for stateful production apps?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="32">

# Lab 32 Solution: Deploying Support Ops Agent to Cloud Run with Google Agents CLI

## Goal

This reference solution provides the canonical `app/agent.py` implementation alongside the complete `agents-cli` Cloud Run enhancement, deployment, dual-protocol verification, remote evaluation, and troubleshooting reference for Module 32.

---

### `app/agent.py`

```python
"""
Enterprise Support Operations Agent — Canonical Part 6 End-to-End Agent (`agents-cli`).
Built with Google ADK 2.0 (`gemini-3.8-flash`), stateful tools, and built-in A2A serving.
"""

from typing import Any, Dict

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.tool_context import ToolContext
from google.genai import types

MODEL = "gemini-3.8-flash"

TICKET_DB: Dict[str, Dict[str, Any]] = {
    "TCK-1042": {
        "customer": "Acme Cloud Robotics",
        "tier": "enterprise",
        "severity": "P1",
        "status": "open",
        "summary": "Production payment webhook returning HTTP 503 timeouts in eu-west1.",
    },
    "TCK-2088": {
        "customer": "Northwind Retail",
        "tier": "standard",
        "severity": "P3",
        "status": "investigating",
        "summary": "CSV invoice export omits localized tax column.",
    },
}

SLA_POLICIES: Dict[str, Dict[str, str]] = {
    "enterprise": {
        "P1_response": "15 minutes",
        "P2_response": "1 hour",
        "P3_response": "4 hours",
        "dedicated_oncall": "Yes (24/7 SRE pager)",
    },
    "standard": {
        "P1_response": "2 hours",
        "P2_response": "8 hours",
        "P3_response": "24 business hours",
        "dedicated_oncall": "No (business-hours queue)",
    },
}


def initialize_support_state(callback_context: CallbackContext) -> None:
    """Initializes default session and user state keys before the first turn."""
    if "user:customer_tier" not in callback_context.state:
        callback_context.state["user:customer_tier"] = "standard"
    if "escalated_tickets" not in callback_context.state:
        callback_context.state["escalated_tickets"] = []


def lookup_ticket(ticket_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Looks up an enterprise support ticket by ID and syncs customer tier into state.

    Args:
        ticket_id: Ticket identifier such as 'TCK-1042' or 'TCK-2088'.
    """
    norm_id = ticket_id.strip().upper()
    record = TICKET_DB.get(norm_id)
    if not record:
        return {
            "status": "not_found",
            "ticket_id": norm_id,
            "available_sample_tickets": sorted(TICKET_DB.keys()),
            "message": f"Ticket '{norm_id}' was not found.",
        }

    tool_context.state["user:customer_tier"] = record["tier"]
    tool_context.state["active_ticket_id"] = norm_id
    return {"status": "found", "ticket_id": norm_id, **record}


def check_sla_policy(tier: str) -> Dict[str, Any]:
    """Returns response-time SLA targets for a customer tier ('enterprise' or 'standard').

    Args:
        tier: Customer support tier ('enterprise' or 'standard').
    """
    norm_tier = tier.strip().lower()
    policy = SLA_POLICIES.get(norm_tier)
    if not policy:
        return {
            "status": "error",
            "message": f"Unknown tier '{tier}'. Valid tiers: enterprise, standard.",
        }
    return {"status": "success", "tier": norm_tier, "sla_targets": policy}


def escalate_ticket(
    ticket_id: str,
    reason: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Escalates a high-severity support ticket to the incident engineering queue.

    Args:
        ticket_id: Ticket identifier to escalate (e.g., 'TCK-1042').
        reason: Concise technical justification for the escalation.
    """
    norm_id = ticket_id.strip().upper()
    if norm_id not in TICKET_DB:
        return {"status": "error", "message": f"Cannot escalate unknown ticket '{norm_id}'."}

    escalated = list(tool_context.state.get("escalated_tickets", []))
    if norm_id not in escalated:
        escalated.append(norm_id)
    tool_context.state["escalated_tickets"] = escalated

    tier = tool_context.state.get("user:customer_tier", TICKET_DB[norm_id]["tier"])
    queue = "24/7 P1 SRE Oncall" if tier == "enterprise" else "Tier-2 Engineering Queue"
    return {
        "status": "escalated",
        "ticket_id": norm_id,
        "assigned_queue": queue,
        "reason": reason.strip(),
        "session_escalated_tickets": escalated,
    }


# Keep name="support_ops_agent" in sync with root_agent_name in agents-cli-manifest.yaml
root_agent = Agent(
    name="support_ops_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    before_agent_callback=initialize_support_state,
    instruction=(
        "You are the Support Operations Agent (active customer tier: {user:customer_tier?}).\n"
        "Follow this exact operational workflow:\n"
        "1. When given a ticket ID, ALWAYS call `lookup_ticket` first.\n"
        "2. Call `check_sla_policy` for the ticket's customer tier so your answer cites exact SLA response times.\n"
        "3. If a ticket has P1 severity OR the user requests escalation, call `escalate_ticket` with a concise technical reason.\n"
        "4. Summarize the ticket status, applicable SLA target, and any escalation queue clearly."
    ),
    tools=[lookup_ticket, check_sla_policy, escalate_ticket],
)

# CRITICAL for agents-cli: App `name` MUST match `agent_directory: "app"` in agents-cli-manifest.yaml
app = App(
    root_agent=root_agent,
    name="app",
)
```

---

### Complete End-to-End Cloud Run Commands (Steps 1–4)

```shell
# Step 1: Fast-bootstrap (if not reusing Module 31 directory)
agents-cli scaffold create support-ops-agent --agent adk --prototype --agent-guidance-filename GEMINI.md
curl -fsSL https://mauripsale.github.io/doc-adk-training/samples/part6/agent.py -o support-ops-agent/app/agent.py
curl -fsSL https://mauripsale.github.io/doc-adk-training/samples/part6/basic-dataset.json -o support-ops-agent/tests/eval/datasets/basic-dataset.json
cd support-ops-agent

# Step 2: Enhance in place for Cloud Run
export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
export DEPLOY_REGION=us-central1

agents-cli scaffold enhance . \
  --deployment-target cloud_run \
  --cicd-runner github_actions \
  --region "$DEPLOY_REGION"
agents-cli install

# Step 3: Dry-run preview & live deploy
agents-cli deploy \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --region "$DEPLOY_REGION" \
  --env-vars "GOOGLE_GENAI_USE_ENTERPRISE=1,GOOGLE_CLOUD_LOCATION=global" \
  --no-confirm-project \
  --dry-run

agents-cli deploy \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --region "$DEPLOY_REGION" \
  --env-vars "GOOGLE_GENAI_USE_ENTERPRISE=1,GOOGLE_CLOUD_LOCATION=global" \
  --no-confirm-project

# Step 4: Live A2A test, ADK SSE test, and remote evaluation
SERVICE_URL=$(gcloud run services describe support-ops-agent \
  --region="$DEPLOY_REGION" \
  --project="$GOOGLE_CLOUD_PROJECT" \
  --format='value(status.url)')

agents-cli run "Investigate ticket TCK-1042 and check SLA." --url "$SERVICE_URL" --mode a2a
agents-cli run "Check ticket TCK-2088." --url "$SERVICE_URL" --mode adk --app-name app
agents-cli eval generate --url "$SERVICE_URL" --app-name app && agents-cli eval grade
```

---

### Troubleshooting Common Cloud Run Errors

* **`404 NOT_FOUND` calling `gemini-3.8-flash` at runtime:**
  * **Cause:** `GOOGLE_CLOUD_LOCATION` defaulted to `us-central1` instead of `global`.
  * **Fix:** Redeploy with `--env-vars "GOOGLE_GENAI_USE_ENTERPRISE=1,GOOGLE_CLOUD_LOCATION=global"`.
* **`403 Forbidden` when testing with raw `curl`:**
  * **Cause:** Cloud Run services deployed by `agents-cli` require IAM authentication (`roles/run.invoker`) by default.
  * **Fix:** Test via `agents-cli run --url "$SERVICE_URL" --mode a2a` (which attaches credentials automatically) or pass `-H "Authorization: Bearer $(gcloud auth print-identity-token)"` to `curl`.
* **`PERMISSION_DENIED` on Cloud Build or Artifact Registry:**
  * **Fix:** Ensure `run.googleapis.com`, `cloudbuild.googleapis.com`, `artifactregistry.googleapis.com`, and `aiplatform.googleapis.com` are enabled and your account holds `Editor`/`Owner` or Cloud Run/Cloud Build admin roles.
* **Inspecting container crash logs:**
  * **Fix:** Run `gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=support-ops-agent" --project="$GOOGLE_CLOUD_PROJECT" --limit=50 --format="table(timestamp,severity,textPayload)"`.

---

### Self-Reflection Answers

1. **Why does `agents-cli deploy` default to `--no-allow-unauthenticated` on Cloud Run, and how would you expose a browser-accessible internal tool safely to employees without writing custom login code?**
   * **Answer:** Leaving an LLM-backed endpoint unauthenticated on the public internet risks quota exhaustion (denial-of-wallet) and unauthorized tool execution. Requiring Cloud Run IAM authentication protects machine-to-machine callers, while passing `agents-cli deploy --iap` enables **Identity-Aware Proxy (IAP)** so authorized Google Workspace users can sign in through Google's zero-trust proxy with zero application auth code.
2. **If load testing with `tests/load_test/load_test.py` triggers container OOM restarts when you raise `--concurrency` from `8` to `32`, which flag should you scale alongside `--concurrency` and why?**
   * **Answer:** Scale **`--memory`** (e.g., `--memory 16Gi` alongside `--cpu 4 --concurrency 32`). Because Uvicorn serves concurrent requests inside a single async Python process while awaiting Gemini responses, every in-flight request holds its conversation state, tool outputs, and streaming buffers in memory simultaneously.
3. **What happens to active conversation history in `support-ops-agent` when a Cloud Run instance scales down to zero under the default `in_memory` session configuration, and which `scaffold enhance` flag solves this for stateful production apps?**
   * **Answer:** With `in_memory` sessions, scaling to zero (or landing on a different container replica) loses prior session state. Passing `--session-type cloud_sql` (managed PostgreSQL 15 with IAM authentication) or `--session-type agent_platform_sessions` to `agents-cli scaffold enhance` persists sessions durably across container restarts and horizontal autoscaling.

</SolutionVault>
