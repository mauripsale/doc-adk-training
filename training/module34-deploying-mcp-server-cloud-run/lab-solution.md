---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 34 Solution: Deploying a Stateless MCP Server to Cloud Run & Connecting `agents-cli`

## Goal

This solution provides the complete runnable Python files for:
1.  `cloud_mcp_server/stateless_cart_server.py` (FastMCP Streamable HTTP server for Cloud Run)
2.  `cloud_mcp_server/agent.py` (Standalone ADK client agent tested via `uv run adk web`)
3.  `support-ops-agent/app/agent.py` (Canonical Part 6 `agents-cli` agent equipped with `McpToolset` + `StreamableHTTPConnectionParams`, tested via `agents-cli run` and `agents-cli playground`)

### 1. `cloud_mcp_server/stateless_cart_server.py`

```python
# Filename: stateless_cart_server.py
import json
import os
from mcp.server.fastmcp import FastMCP, Context

# --- Configuration ---
# In a serverless environment, we use /tmp/carts to simulate an external store.
# In production, replace get_cart/save_cart with Memorystore (Redis) or Firestore.
STATE_STORAGE_PATH = "/tmp/carts"
if not os.path.exists(STATE_STORAGE_PATH):
    os.makedirs(STATE_STORAGE_PATH)

# --- MCP Server Setup ---
mcp = FastMCP("stateless_shopping_cart_server")


def get_session_id(ctx: Context) -> str:
    # The MCP session ID arrives as a standard HTTP header tracked by the transport.
    return ctx.request_context.request.headers.get("mcp-session-id", "unknown")


def get_cart(session_id: str) -> list:
    cart_file = os.path.join(STATE_STORAGE_PATH, f"{session_id}.json")
    if os.path.exists(cart_file):
        with open(cart_file, "r") as f:
            return json.load(f)
    return []


def save_cart(session_id: str, cart: list) -> None:
    cart_file = os.path.join(STATE_STORAGE_PATH, f"{session_id}.json")
    with open(cart_file, "w") as f:
        json.dump(cart, f)


@mcp.tool()
def add_item_to_cart(item: str, ctx: Context) -> dict:
    """Adds an item to the session cart."""
    session_id = get_session_id(ctx)
    print(f"[Server]: Handling add_item_to_cart for session '{session_id}'")
    cart = get_cart(session_id)
    cart.append(item)
    save_cart(session_id, cart)
    return {"status": "success", "message": f"Added '{item}'."}


@mcp.tool()
def view_cart(ctx: Context) -> dict:
    """Views all items currently in the session cart."""
    session_id = get_session_id(ctx)
    print(f"[Server]: Handling view_cart for session '{session_id}'")
    cart = get_cart(session_id)
    return {"status": "success", "cart": cart}


# --- ASGI app for HTTP, suitable for Cloud Run ---
# FastMCP mounts the Streamable HTTP MCP endpoint at /mcp by default.
app = mcp.streamable_http_app()
```

### 2. Standalone ADK Client (`cloud_mcp_server/agent.py`)

```python
# Filename: cloud_mcp_server/agent.py
import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

# Base URL of your deployed Cloud Run MCP service (FastMCP mounts Streamable HTTP at /mcp)
MCP_SERVER_URL = os.environ.get(
    "MCP_SERVER_URL",
    "https://YOUR_CLOUD_RUN_SERVICE_URL",
).rstrip("/")

root_agent = Agent(
    model="gemini-3.8-flash",
    name="cloud_shopping_agent",
    instruction=(
        "You are a helpful shopping assistant. Add requested items to the user's cart "
        "and display current cart contents accurately using your remote MCP tools."
    ),
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=f"{MCP_SERVER_URL}/mcp",
            ),
        )
    ],
)
```

### 3. `agents-cli` Enterprise Project (`support-ops-agent/app/agent.py`)

```python
"""
Enterprise Support Operations Agent equipped with Remote Cloud Run MCP Toolset (`agents-cli`).
Built with Google ADK 2.0 (`gemini-3.8-flash`), stateful tools, MCP Streamable HTTP, and A2A serving.
"""

import os
from typing import Any, Dict

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from google.adk.tools.tool_context import ToolContext
from google.genai import types

MODEL = "gemini-3.8-flash"

MCP_SERVER_URL = os.environ.get(
    "MCP_SERVER_URL",
    "https://YOUR_CLOUD_RUN_SERVICE_URL",
).rstrip("/")
MCP_AUTH_TOKEN = os.environ.get("MCP_AUTH_TOKEN", "")
mcp_headers = {"Authorization": f"Bearer {MCP_AUTH_TOKEN}"} if MCP_AUTH_TOKEN else None

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


remote_cart_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=f"{MCP_SERVER_URL}/mcp",
        headers=mcp_headers,
    ),
)

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
        "4. Use `add_item_to_cart` and `view_cart` from your remote Cloud Run MCP toolset whenever the user asks to stage or inspect items in their cart.\n"
        "5. Summarize ticket status, SLA targets, escalations, and cart contents clearly."
    ),
    tools=[lookup_ticket, check_sla_policy, escalate_ticket, remote_cart_toolset],
)

# CRITICAL for agents-cli: App `name` MUST match `agent_directory: "app"` in agents-cli-manifest.yaml
app = App(
    root_agent=root_agent,
    name="app",
)
```

### Self-Reflection Answers

1.  **Our demo MCP server writes session files under `/tmp/carts`. Why is `/tmp` volatile on Cloud Run, and what happens to a user's cart when Cloud Run scales down to zero?**
    *   **Answer:** On Cloud Run, `/tmp` is an in-memory filesystem local to each individual container instance. If consecutive requests hit different horizontally scaled instances — or if Cloud Run scales the service down to zero during idle periods — the container's `/tmp` directory is destroyed and the user's cart disappears.
2.  **What advantages does Google Cloud Memorystore (Redis) provide over `/tmp` files for storing MCP session state?**
    *   **Answer:** Memorystore (Redis) provides true out-of-process persistence across container restarts and scale-to-zero events, sub-millisecond read/write latency for fast tool execution, and strong consistency across every Cloud Run container replica reading the same `Mcp-Session-Id`.
3.  **How does `StreamableHTTPConnectionParams(url=f"{MCP_SERVER_URL}/mcp", headers=...)` decouple `support-ops-agent` from the MCP server's internal storage implementation and authentication topology?**
    *   **Answer:** `McpToolset` communicates strictly over the standardized MCP `/mcp` HTTP protocol and JSON-RPC tool schemas while injecting authentication headers transparently at the transport layer. Platform teams can migrate the Cloud Run MCP backend from `/tmp` to Memorystore or enforce IAM/Bearer authentication without altering `support_ops_agent`'s reasoning or tool-calling logic.
