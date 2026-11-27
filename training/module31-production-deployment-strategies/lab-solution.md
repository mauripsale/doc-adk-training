---
sidebar_position: 3
title: "Lab Solution"
---

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
