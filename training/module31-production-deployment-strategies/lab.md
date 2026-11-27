---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 31: Production Deployment Strategies — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 31: Prototyping, Testing & Evaluating with Google Agents CLI

## Goal

In this hands-on kickoff lab for Part 6, you will install **`google-agents-cli`**, scaffold our canonical enterprise **`support-ops-agent`** in prototype mode, implement stateful ticket triage and escalation tools in **`app/agent.py`** (`gemini-3.8-flash`), smoke-test multi-turn session persistence locally, run the **`agents-cli eval run` / `eval compare` Quality Flywheel**, and validate your architectural target selection across four enterprise scenarios.

Every subsequent Part 6 module (Cloud Run in Module 32, GKE in Module 33, Agent Runtime in Module 35, and Gemini Enterprise Governance in Module 36) builds directly on the `support-ops-agent` project you create here.

<Setup/>

### Prerequisites

* Python 3.10+ and [`uv`](https://docs.astral.sh/uv/) installed.
* Either a **Google Cloud Project** authenticated via `gcloud auth application-default login` (recommended — required for managed cloud-side grading in Step 4 and cloud deployments in Modules 32–36) or a `GEMINI_API_KEY` for local prototyping.

---

### Step 1: Install `agents-cli` & Scaffold the Prototype

1. **Install (or upgrade) `google-agents-cli` globally with `uv`:**

   ```shell
   uv tool install google-agents-cli
   # Already installed? Upgrade to the latest release:
   # uv tool upgrade google-agents-cli
   ```

2. **Sync the `agents-cli` AgentOps skills into your local coding agent configuration:**

   ```shell
   agents-cli setup --skip-auth
   ```

3. **Scaffold `support-ops-agent` in prototype mode from `adk-training/`:**
   Navigate to your `adk-training` workspace directory. **CRITICAL: Do NOT run `mkdir support-ops-agent` beforehand** — `agents-cli scaffold create` creates the directory automatically, and project names must be `<= 26` characters (lowercase letters, digits, and hyphens only):

   ```shell
   cd /path/to/your/adk-training

   agents-cli scaffold create support-ops-agent \
     --agent adk \
     --prototype \
     --agent-guidance-filename GEMINI.md

   cd support-ops-agent
   agents-cli info
   ```

4. **Inspect the generated project and align `agents-cli-manifest.yaml`:**
   Confirm that `agents-cli-manifest.yaml`, `GEMINI.md`, `app/agent.py`, `app/fast_api_app.py`, `app/app_utils/a2a.py`, and `tests/eval/` exist. Open `agents-cli-manifest.yaml` and verify `agent_directory: app` and set `root_agent_name: support_ops_agent` so it matches the agent you will build in Step 2.

5. **Configure `.env` in `support-ops-agent/.env`:**
   Configure **either** Gemini Enterprise / Vertex AI (recommended for Part 6 so `agents-cli eval run` and cloud deployments share one project) **or** a local Gemini API key:

   ```ini
   # Option A (Recommended for Part 6 & eval grading): Gemini Enterprise / Vertex AI
   GOOGLE_GENAI_USE_ENTERPRISE=1
   GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
   GOOGLE_CLOUD_LOCATION=global

   # Option B (Local AI Studio smoke testing only):
   # GOOGLE_GENAI_USE_ENTERPRISE=0
   # GEMINI_API_KEY=YOUR_GEMINI_API_KEY
   ```

---

### Step 2: Implement Stateful `support_ops_agent` in `app/agent.py`

Open `support-ops-agent/app/agent.py` and replace its contents with the starter skeleton below. Complete the **six `# TODO:` challenges** to implement stateful ticket triage, SLA lookup, and P1 incident escalation while obeying the `agents-cli` naming invariants:

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
    # TODO 1: Initialize `callback_context.state["user:customer_tier"] = "standard"`
    # and `callback_context.state["escalated_tickets"] = []` if those keys are not already present.
    pass


def lookup_ticket(ticket_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Looks up an enterprise support ticket by ID and syncs customer tier into state.

    Args:
        ticket_id: Ticket identifier such as 'TCK-1042' or 'TCK-2088'.
    """
    norm_id = ticket_id.strip().upper()
    # TODO 2: Look up `norm_id` in `TICKET_DB`.
    # - If missing, return a dict with `"status": "not_found"`, `"ticket_id": norm_id`,
    #   `"available_sample_tickets": sorted(TICKET_DB.keys())`, and an informative `"message"`.
    # - If found, store `record["tier"]` in `tool_context.state["user:customer_tier"]`,
    #   store `norm_id` in `tool_context.state["active_ticket_id"]`, and return
    #   `{"status": "found", "ticket_id": norm_id, **record}`.
    pass


def check_sla_policy(tier: str) -> Dict[str, Any]:
    """Returns response-time SLA targets for a customer tier ('enterprise' or 'standard').

    Args:
        tier: Customer support tier ('enterprise' or 'standard').
    """
    norm_tier = tier.strip().lower()
    # TODO 3: Look up `norm_tier` in `SLA_POLICIES`.
    # - If missing, return `{"status": "error", "message": ...}`.
    # - Otherwise return `{"status": "success", "tier": norm_tier, "sla_targets": policy}`.
    pass


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
    # TODO 4: Validate `norm_id` exists in `TICKET_DB` (return `{"status": "error", ...}` if unknown).
    # Append `norm_id` to `tool_context.state["escalated_tickets"]` (avoiding duplicates),
    # route `"enterprise"` tier tickets to `"24/7 P1 SRE Oncall"` (otherwise `"Tier-2 Engineering Queue"`),
    # and return `status`, `ticket_id`, `assigned_queue`, `reason`, and `session_escalated_tickets`.
    pass


# TODO 5: Define `root_agent = Agent(...)` with:
# - `name="support_ops_agent"` (matching `root_agent_name` in `agents-cli-manifest.yaml`)
# - `model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3))`
# - `before_agent_callback=initialize_support_state`
# - Clear operational `instruction` referencing `{user:customer_tier?}` that directs the agent to:
#   1. Call `lookup_ticket` first when given a ticket ID,
#   2. Call `check_sla_policy` for the ticket's customer tier,
#   3. Call `escalate_ticket` if severity is P1 or escalation is requested,
#   4. Summarize ticket status, SLA target, and escalation queue.
# - `tools=[lookup_ticket, check_sla_policy, escalate_ticket]`
root_agent = None  # Replace with Agent(...)

# TODO 6: Wrap `root_agent` in `app = App(root_agent=root_agent, name="app")`
# CRITICAL: `name="app"` MUST match `agent_directory: "app"` in `agents-cli-manifest.yaml`!
app = None  # Replace with App(...)
```

---

### Step 3: Local Iteration (`install`, `lint`, `run --start-server`, `playground`)

1. **Install project dependencies and lint your implementation:**

   ```shell
   agents-cli install
   agents-cli lint
   ```

2. **Run a stateful multi-turn CLI smoke test with a persistent local server:**
   Using `--start-server` keeps the FastAPI + in-memory session server warm across turns so `--session-id demo-1` preserves `user:customer_tier` and `escalated_tickets`:

   ```shell
   agents-cli run "Investigate ticket TCK-1042 and check its SLA." --start-server --session-id demo-1
   agents-cli run "Which customer tier was stored in my profile, and was TCK-1042 escalated?" --session-id demo-1
   agents-cli run "Stop" --stop-server
   ```
   Verify that Turn 1 looks up `TCK-1042`, checks the `enterprise` SLA (`15 minutes`), and escalates to `24/7 P1 SRE Oncall`, and Turn 2 recalls the `enterprise` tier and `TCK-1042` escalation from session state!

3. **Explore interactively in the Web Playground (Optional):**

   ```shell
   agents-cli playground
   ```
   *(Tip: When Google Cloud ADC is configured, passing `agents-cli playground --otel-to-cloud` exports OpenTelemetry spans directly to Cloud Trace while testing locally! Press `Ctrl+C` when finished.)*

---

### Step 4: The Quality Flywheel (`eval run` & `eval compare`)

Smoke testing proves one conversation worked once; **`agents-cli eval`** proves your agent generalizes across cases without regressions.

1. **Author the evaluation dataset in `tests/eval/datasets/basic-dataset.json`:**
   Replace the contents of `support-ops-agent/tests/eval/datasets/basic-dataset.json` with three representative support scenarios (P1 escalation, standard SLA lookup, and graceful unknown-ticket handling):

   ```json
   {
     "eval_cases": [
       {
         "eval_case_id": "p1_ticket_triage_and_escalation",
         "prompt": {
           "role": "user",
           "parts": [
             {
               "text": "Investigate ticket TCK-1042, check its SLA target, and escalate if required."
             }
           ]
         }
       },
       {
         "eval_case_id": "standard_ticket_sla_lookup",
         "prompt": {
           "role": "user",
           "parts": [
             {
               "text": "What is the current status and applicable SLA response target for ticket TCK-2088?"
             }
           ]
         }
       },
       {
         "eval_case_id": "unknown_ticket_graceful_handling",
         "prompt": {
           "role": "user",
           "parts": [
             {
               "text": "Please check the status of ticket TCK-9999."
             }
           ]
         }
       }
     ]
   }
   ```

2. **Execute your baseline evaluation run:**

   ```shell
   agents-cli eval run
   ```
   *(Note: Managed built-in metrics in `eval grade` call the Gemini platform Evaluation Service using your Google Cloud ADC project. Remember that `eval run` exits `0` regardless of metric scores — always inspect the printed scorecard!)*

3. **Inspect the HTML & JSON grade reports:**
   List `artifacts/grade_results/` to find your baseline `results_<timestamp>.html` and `results_<timestamp>.json`:

   ```shell
   ls -lt artifacts/grade_results/
   ```
   Open the `.html` report in your browser to inspect per-case rubric rationales and tool trajectories.

4. **Iterate and run `agents-cli eval compare`:**
   Refine your `root_agent` instruction in `app/agent.py` (for example, explicitly instructing the agent to list `available_sample_tickets` whenever `lookup_ticket` returns `"not_found"`), re-run `agents-cli eval run`, and diff your baseline JSON against the candidate JSON:

   ```shell
   agents-cli eval run
   agents-cli eval compare \
     artifacts/grade_results/<baseline>.json \
     artifacts/grade_results/<candidate>.json
   ```
   Confirm that target metrics improved or held steady with zero regressions across all three cases!

---

### Step 5: Architecture Target Selection Check

Before moving to Cloud Run deployment in Module 32, match each enterprise requirement below to its optimal `agents-cli` deployment target and protocol strategy (**`cloud_run`**, **`agent_runtime`**, **`gke`**, or **A2A on `cloud_run`**):

1. **Scenario 1 — Startup MVP:** A seed-stage startup needs to ship an e-commerce support agent for a pilot customer by Friday with zero Kubernetes staff, instant HTTPS, and scale-to-zero cost efficiency.
2. **Scenario 2 — Regulated Public-Sector Workload (FedRAMP):** A defense contractor needs a strictly auditable, FedRAMP-compliant internal compliance agent with zero-config managed sessions and OAuth 2.0 user consent in Gemini Enterprise.
3. **Scenario 3 — Quantitative FinTech Mesh (GPU + Custom `NetworkPolicy`):** A financial institution runs all workloads inside an existing Kubernetes platform requiring GPU node pools and strict pod-to-pod `NetworkPolicy` isolation.
4. **Scenario 4 — Cross-Organization Partner Integration:** Two external partner organizations need their autonomous procurement agents to discover your agent's capabilities dynamically via `/.well-known/agent-card.json` and invoke tasks over standard JSON-RPC HTTPS on serverless infrastructure.

Check your code and scenario selections against `lab-solution.md` or the **Reference Solution Vault** below!

### Lab Summary

You have established the complete local **Enterprise AgentOps** foundation with `google-agents-cli`:
* Installed `google-agents-cli`, synced coding-agent skills (`agents-cli setup --skip-auth`), and scaffolded `support-ops-agent` in `--prototype` mode without violating the 4 critical `agents-cli` rules.
* Built a stateful ADK 2.0 agent (`gemini-3.8-flash`) using `before_agent_callback`, `ToolContext`, and `App(root_agent=root_agent, name="app")`.
* Verified multi-turn state persistence via `agents-cli run --start-server --session-id demo-1` and closed the Quality Flywheel with `agents-cli eval run` and `agents-cli eval compare`.

### Self-Reflection Questions
* Why does changing `App(root_agent=root_agent, name="app")` to `name="support_ops_agent"` break `agents-cli run` and `agents-cli eval` when the code lives inside `app/agent.py`?
* Why should behavioral assertions (such as how an agent explains an unknown ticket or whether it cites SLA targets clearly) live in `agents-cli eval` datasets rather than `pytest` unit tests?
* Why does `agents-cli` recommend starting with `--prototype` and running `scaffold enhance` only after your core eval dataset passes?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="31">

# Lab 31 Solution: Prototyping, Testing & Evaluating with Google Agents CLI

## Goal

This reference solution contains the exact CLI workflow, complete runnable `app/agent.py` implementation, evaluation dataset, and architectural scenario answers for Module 31.

---

### Step 1: Scaffold & Environment Setup

```shell
uv tool install google-agents-cli
agents-cli setup --skip-auth

cd /path/to/your/adk-training
agents-cli scaffold create support-ops-agent \
  --agent adk \
  --prototype \
  --agent-guidance-filename GEMINI.md

cd support-ops-agent
agents-cli info
```

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

### `tests/eval/datasets/basic-dataset.json`

```json
{
  "eval_cases": [
    {
      "eval_case_id": "p1_ticket_triage_and_escalation",
      "prompt": {
        "role": "user",
        "parts": [
          {
            "text": "Investigate ticket TCK-1042, check its SLA target, and escalate if required."
          }
        ]
      }
    },
    {
      "eval_case_id": "standard_ticket_sla_lookup",
      "prompt": {
        "role": "user",
        "parts": [
          {
            "text": "What is the current status and applicable SLA response target for ticket TCK-2088?"
          }
        ]
      }
    },
    {
      "eval_case_id": "unknown_ticket_graceful_handling",
      "prompt": {
        "role": "user",
        "parts": [
          {
            "text": "Please check the status of ticket TCK-9999."
          }
        ]
      }
    }
  ]
}
```

---

### Steps 3 & 4: Verification & Quality Flywheel Commands

```shell
# Install & lint
agents-cli install
agents-cli lint

# Multi-turn stateful smoke test
agents-cli run "Investigate ticket TCK-1042 and check its SLA." --start-server --session-id demo-1
agents-cli run "Which customer tier was stored in my profile, and was TCK-1042 escalated?" --session-id demo-1
agents-cli run "Stop" --stop-server

# Run baseline evaluation & diff against a candidate run
agents-cli eval run
# After refining prompt/instructions and running `agents-cli eval run` a second time:
# agents-cli eval compare artifacts/grade_results/<baseline>.json artifacts/grade_results/<candidate>.json
```

---

### Step 5: Architecture Target Selection Answers

1. **Scenario 1 — Startup MVP → `cloud_run` (`agents-cli scaffold enhance . --deployment-target cloud_run`)**
   * **Justification:** Cloud Run delivers the fastest serverless container rollout with automatic HTTPS, IAM/IAP options, and scale-to-zero billing (`--min-instances 0` by default in dev) so the startup pays nothing during idle periods without managing Kubernetes clusters.
2. **Scenario 2 — Regulated Public-Sector Workload (FedRAMP) → `agent_runtime` (`agents-cli scaffold enhance . --deployment-target agent_runtime`)**
   * **Justification:** Agent Runtime in Gemini platform is the managed deployment target providing built-in **FedRAMP** compliance, automatic `VertexAiSessionService` persistence, CMEK support, and native **OAuth 2.0 user consent** when registered with Gemini Enterprise.
3. **Scenario 3 — Quantitative FinTech Mesh (GPU + Custom `NetworkPolicy`) → `gke` (`agents-cli scaffold enhance . --deployment-target gke`)**
   * **Justification:** GKE Autopilot (or Standard) integrates directly into an existing Kubernetes ecosystem while supporting custom GPU node pools, fine-grained Kubernetes `NetworkPolicy` rules, and full Pod-level resource and sidecar control.
4. **Scenario 4 — Cross-Organization Partner Integration → Built-in A2A on `cloud_run`**
   * **Justification:** Every Python ADK project scaffolded by `agents-cli` automatically exposes an A2A `AgentCard` (`/a2a/app/.well-known/agent-card.json`) and JSON-RPC endpoint via `app/app_utils/a2a.py`. Deploying that container to **Cloud Run** gives external partner agents standards-based cross-org discovery and invocation on elastic serverless infrastructure (and supports `--registration-type a2a` in Gemini Enterprise).

---

### Self-Reflection Answers

1. **Why does changing `App(root_agent=root_agent, name="app")` to `name="support_ops_agent"` break `agents-cli run` and `agents-cli eval` when the code lives inside `app/agent.py`?**
   * **Answer:** ADK's FastAPI server and `agents-cli`'s evaluation generator resolve `/apps/{app_name}/...` routes against the agent package directory (`agent_directory: "app"`). If `App.name` diverges from `"app"`, session creation and SSE invocation look up different application keys, resulting in `"Session not found"` errors.
2. **Why should behavioral assertions live in `agents-cli eval` datasets rather than `pytest` unit tests?**
   * **Answer:** `pytest` is deterministic and ideal for testing pure Python contracts (e.g., verifying `lookup_ticket("tck-1042")` normalizes casing), whereas LLM phrasing and multi-step tool trajectories are probabilistic. `agents-cli eval` uses rubric-based LLM judges (`final_response_quality`, `multi_turn_tool_use_quality`, `multi_turn_task_success`) that evaluate semantic correctness and tool usage without flaking on minor wording variations.
3. **Why does `agents-cli` recommend starting with `--prototype` and running `scaffold enhance` only after your core eval dataset passes?**
   * **Answer:** `--prototype` keeps the workspace focused on `app/agent.py` and `tests/eval/` while requirements and tool designs are still fluid. Once `agents-cli eval run` proves the agent meets its quality bar, `scaffold enhance` cleanly layers Terraform, CI/CD workflows, and load tests in place without premature DevOps overhead.

</SolutionVault>
