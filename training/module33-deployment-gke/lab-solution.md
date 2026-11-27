---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 33 Solution: Deploying Enterprise Agents to GKE Autopilot

## Goal

This solution provides the complete runnable Python code for **Part 1** (`support-ops-gke/app/agent.py` deployed via `agents-cli --deployment-target gke`) and **Part 2** (`gke_support_agent/support_agent/` deployed manually via `Dockerfile` + `deployment.yaml` + `kubectl`), along with expected outputs and troubleshooting guidance.

### Part 1 Solution: `support-ops-gke/app/agent.py` (`agents-cli` Golden Path)

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

### Part 2 Solution: Raw Manual GKE Package (`gke_support_agent/`)

#### `support_agent/__init__.py`

```python
from . import agent
```

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

#### `Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY support_agent/ /app/support_agent/
EXPOSE 8080
CMD ["adk", "api_server", "/app", "--host", "0.0.0.0", "--port", "8080"]
```

### Expected Outputs

#### Part 1: `agents-cli run` Against Live GKE Service
*   **A2A Mode (`--mode a2a`):** Resolves the agent card from `/a2a/app`, invokes `lookup_ticket("TCK-1042")`, `check_sla_policy("enterprise")`, and `escalate_ticket("TCK-1042", ...)`, and reports the `15 minutes` P1 SLA target and `24/7 P1 SRE Oncall` escalation queue.
*   **ADK SSE Mode (`--mode adk --app-name app`):** Creates an ADK session under `/apps/app/...`, streams SSE events from `/run_sse`, and returns the `enterprise` SLA policy targets (`15 minutes` P1, `1 hour` P2, `4 hours` P3).

#### Part 2: `kubectl apply` & `kubectl get service --watch`
```
deployment.apps/support-agent-deployment created
service/support-agent-service created
```
```
NAME                    TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)        AGE
support-agent-service   LoadBalancer   10.44.192.123   34.123.45.67    80:30123/TCP   2m30s
```

### Troubleshooting Common GKE Errors

*   **Passing `--cpu` / `--memory` / `--concurrency` on `agents-cli deploy` fails:**
    *   **Cause:** `agents-cli` rejects imperative container sizing flags for GKE targets.
    *   **Solution:** Edit pod resource requests/limits and `kubernetes_horizontal_pod_autoscaler_v2` settings declaratively in `deployment/terraform/single-project/service.tf` (and `cicd/service.tf`).
*   **`kubectl apply` fails with `metadata.name: Invalid value ... RFC 1123 label`:**
    *   **Cause:** Kubernetes resource names cannot contain underscores (`_`), even when your Python package (`support_agent`) uses underscores.
    *   **Solution:** Always use hyphens (`support-agent-deployment`, `support-agent-service`) in Kubernetes `metadata.name` fields.
*   **`CrashLoopBackOff` or `404 NOT_FOUND` on `gemini-3.8-flash`:**
    *   **Cause:** Missing `GOOGLE_GENAI_USE_ENTERPRISE=1` or `GOOGLE_CLOUD_LOCATION=global` in the pod environment, or mismatched `AGENTS_DIR` inside `Dockerfile`.
    *   **Solution:** Inspect pod logs with `kubectl logs deployment/<deployment-name>` and ensure `GOOGLE_GENAI_USE_ENTERPRISE="1"` and `GOOGLE_CLOUD_LOCATION="global"` are set.

### Self-Reflection Answers

1.  **Why does `agents-cli deploy` reject `--cpu`, `--memory`, and `--concurrency` flags when `--deployment-target gke` is configured, whereas Cloud Run and Agent Runtime accept them?**
    *   **Answer:** On GKE, pod resource requests/limits and replica scaling (`HorizontalPodAutoscaler` + `PodDisruptionBudget`) are governed declaratively by Kubernetes resources inside `deployment/terraform/`. Allowing ad-hoc CLI sizing flags during image deployment would create configuration drift between live Kubernetes cluster state and Terraform IaC, and could conflict with HPA target utilization metrics.
2.  **How does GKE Workload Identity (`app_sa` in `iam.tf`) eliminate the security risks of static service account JSON keys?**
    *   **Answer:** Workload Identity binds a Kubernetes `ServiceAccount` directly to a GCP IAM Service Account (`app_sa`) using `roles/iam.workloadIdentityUser`. GKE's metadata server automatically issues short-lived, auto-rotating OAuth credentials to pods running under that Kubernetes `ServiceAccount`, completely eliminating downloadable JSON key files that could be leaked or committed to Git.
3.  **In Part 2's `deployment.yaml`, what is the distinct role of the `Deployment` object versus the `Service` object, and why is `adk api_server` used in the `Dockerfile` instead of `adk web`?**
    *   **Answer:** The `Deployment` manages pod execution, desired replica counts, self-healing, and rolling updates/rollbacks, whereas the `Service` provides a stable IP and load balancer across ephemeral pod IPs. `adk api_server` exposes a lean, headless REST/SSE API suitable for production backends, whereas `adk web` bundles the developer debug UI — exposing internal agent prompts, tool definitions, and execution traces while consuming extra memory and CPU.
