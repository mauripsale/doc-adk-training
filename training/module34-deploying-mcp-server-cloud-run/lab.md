---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 34: Deploying MCP Server to Cloud Run — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 34: Deploying a Stateless MCP Server to Cloud Run & Connecting `agents-cli`

## Goal

In this lab, you will take the stateful MCP server pattern from Module 28, re-architect it into a **stateless FastMCP HTTP server**, containerize it with a `Dockerfile`, and deploy it to **Google Cloud Run**. Then, in Steps 4 and 5, you will connect to your live Cloud Run `/mcp` endpoint in **two ways**:

1.  **Standalone ADK Package (`cloud_mcp_server/agent.py`):** Launch `uv run adk web` from the parent `adk-training/` directory to test the remote MCP server interactively.
2.  **Enterprise `agents-cli` Project (`support-ops-agent/app/agent.py`):** Equip the canonical Part 6 `support_ops_agent` with `McpToolset(connection_params=StreamableHTTPConnectionParams(url=f"{MCP_SERVER_URL}/mcp", headers=...))` and test it immediately via `agents-cli run` and `agents-cli playground`.

**Note:** For lab simplicity, our server simulates externalized state using per-session JSON files in `/tmp/carts` keyed by the `Mcp-Session-Id` HTTP header. In production, you replace those two helper functions (`get_cart` / `save_cart`) with Google Cloud Memorystore (Redis) or Firestore.

### Prerequisites

*   A Google Cloud Project with billing enabled.
*   Google Cloud CLI (`gcloud`) installed and authenticated.
*   `uv` and `google-agents-cli` installed (`uv tool install google-agents-cli`).
*   **Required APIs:** Cloud Run, Cloud Build, Artifact Registry, and Vertex AI:
    ```shell
    export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
    export DEPLOY_REGION=us-central1
    gcloud config set project "$GOOGLE_CLOUD_PROJECT"
    gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com aiplatform.googleapis.com
    ```

---

### Step 1: Create the Stateless FastMCP Server

<Setup/>

1.  **Create a new `cloud_mcp_server` directory inside your `adk-training` workspace:**

    ```shell
    cd /path/to/your/adk-training
    mkdir cloud_mcp_server
    cd cloud_mcp_server
    ```

2.  **Create `stateless_cart_server.py`:**
    Using `mcp.server.fastmcp.FastMCP`, each tool call extracts the `mcp-session-id` HTTP header managed by the Streamable HTTP transport and reads/writes that session's isolated cart outside Python process globals:

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

### Step 2: Containerize the MCP Server

1.  **Create `requirements.txt`:**
    Pin `mcp<2` alongside `uvicorn` so `mcp.server.fastmcp.FastMCP` and `google-adk`'s `McpToolset` client stay aligned on the 1.x MCP SDK surface:

    ```shell
    printf "mcp<2\nuvicorn\n" > requirements.txt
    ```

2.  **Create `Dockerfile`:**

    ```dockerfile
    FROM python:3.11-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY stateless_cart_server.py .

    # Cloud Run injects PORT (defaults to 8080 locally).
    # Shell form is used so ${PORT:-8080} expands at container startup.
    CMD python -m uvicorn stateless_cart_server:app --host 0.0.0.0 --port ${PORT:-8080}
    ```

### Step 3: Build and Deploy the MCP Server to Cloud Run

1.  **Ensure an Artifact Registry Docker repository exists and submit the build:**

    ```shell
    gcloud artifacts repositories describe adk-images --location="$DEPLOY_REGION" >/dev/null 2>&1 || \
      gcloud artifacts repositories create adk-images \
        --repository-format=docker \
        --location="$DEPLOY_REGION"

    gcloud builds submit \
        --tag "${DEPLOY_REGION}-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/adk-images/mcp-cart-server:v1"
    ```

2.  **Deploy `mcp-cart-server` to Cloud Run and store `MCP_SERVER_URL`:**

    ```shell
    gcloud run deploy mcp-cart-server \
        --image="${DEPLOY_REGION}-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/adk-images/mcp-cart-server:v1" \
        --region="$DEPLOY_REGION" \
        --allow-unauthenticated

    export MCP_SERVER_URL=$(gcloud run services describe mcp-cart-server \
        --region="$DEPLOY_REGION" \
        --format='value(status.url)')
    echo "Deployed MCP Server Base URL: $MCP_SERVER_URL"
    ```

---

### Step 4: Connect Both a Standalone ADK Agent and Your `agents-cli` Project

#### Step 4A: Configure the Standalone ADK Client (`cloud_mcp_server/agent.py`)

1.  **Install the MCP client extra in your `adk-training` environment:**
    ```shell
    uv add "google-adk[mcp]"
    ```

2.  **Create `cloud_mcp_server/agent.py` and complete the `# TODO` block:**
    Notice that `MCP_SERVER_URL` holds the Cloud Run base URL, while `FastMCP` serves the Streamable HTTP endpoint at `f"{MCP_SERVER_URL}/mcp"`:

    ```python
    # Filename: cloud_mcp_server/agent.py
    import os
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

    MCP_SERVER_URL = os.environ.get(
        "MCP_SERVER_URL",
        "https://YOUR_CLOUD_RUN_SERVICE_URL",
    ).rstrip("/")

    # TODO: Define `root_agent` (name="cloud_shopping_agent", model="gemini-3.8-flash")
    # equipped with `McpToolset(connection_params=StreamableHTTPConnectionParams(url=f"{MCP_SERVER_URL}/mcp"))`.
    root_agent = None
    ```

3.  **Create `cloud_mcp_server/__init__.py` and `cloud_mcp_server/.env`:**
    ```python
    from . import agent
    ```
    Create `cloud_mcp_server/.env` (separating Cloud Run's `us-central1` region from `GOOGLE_CLOUD_LOCATION=global` for `gemini-3.8-flash`):
    ```ini
    GOOGLE_GENAI_USE_ENTERPRISE=1
    GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
    GOOGLE_CLOUD_LOCATION=global
    MCP_SERVER_URL=https://YOUR_CLOUD_RUN_SERVICE_URL
    ```

#### Step 4B: Equip Your `agents-cli` Project (`support-ops-agent/app/agent.py`)

Now connect the exact same Cloud Run MCP server into the canonical Part 6 **`agents-cli`** `support-ops-agent` project so your enterprise support agent can both triage tickets (`lookup_ticket`, `check_sla_policy`, `escalate_ticket`) and stage incident follow-up items in the remote Cloud Run MCP cart!

1.  **Open (or scaffold) `support-ops-agent` and add `google-adk[mcp]`:**
    ```shell
    cd /path/to/your/adk-training

    # If you don't already have support-ops-agent from earlier Part 6 modules, scaffold it now:
    if [ ! -d "support-ops-agent" ]; then
      agents-cli scaffold create support-ops-agent \
        --agent adk \
        --prototype \
        --region "$DEPLOY_REGION" \
        --agent-guidance-filename GEMINI.md
      curl -fsSL https://mauripsale.github.io/doc-adk-training/samples/part6/agent.py -o support-ops-agent/app/agent.py
    fi

    cd support-ops-agent
    uv add "google-adk[mcp]"
    agents-cli install
    ```

2.  **Update `support-ops-agent/app/agent.py` (complete the `# TODO` section):**
    Equip `support_ops_agent` with `McpToolset` using `StreamableHTTPConnectionParams(url=f"{MCP_SERVER_URL}/mcp", headers=mcp_headers)` (supporting an optional `MCP_AUTH_TOKEN` Bearer header when your Cloud Run MCP service uses `--no-allow-unauthenticated`), while keeping `app = App(root_agent=root_agent, name="app")` intact:

    ```python
    # Filename: support-ops-agent/app/agent.py
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

    # ... (keep TICKET_DB, SLA_POLICIES, initialize_support_state,
    #      lookup_ticket, check_sla_policy, and escalate_ticket from Part 6 agent.py) ...

    # TODO: Instantiate `remote_cart_toolset` using `McpToolset` and
    # `StreamableHTTPConnectionParams(url=f"{MCP_SERVER_URL}/mcp", headers=mcp_headers)`,
    # and attach it to `root_agent` alongside `[lookup_ticket, check_sla_policy, escalate_ticket]`.
    remote_cart_toolset = None
    ```

---

### Step 5: Test End-to-End with `adk web`, `agents-cli run`, and `agents-cli playground`

#### 5A: Test the Standalone ADK Package via `uv run adk web`

`adk web` must always be launched from the **parent directory** (`adk-training/`) containing `cloud_mcp_server/`:

```shell
cd /path/to/your/adk-training
export MCP_SERVER_URL=$(gcloud run services describe mcp-cart-server --region="$DEPLOY_REGION" --format='value(status.url)')
uv run adk web
```

*   Open `http://127.0.0.1:8000` in your browser and select **`cloud_mcp_server`** from the dropdown.
*   Ask the agent to add `'apples'` and `'bread'`, then ask `"What is in my cart?"` to confirm state persists across remote Cloud Run HTTP calls.
*   Press `Ctrl+C` when finished.

#### 5B: Test the `agents-cli` Project via `agents-cli run` and `agents-cli playground`

Switch into `support-ops-agent/` and verify the Cloud Run MCP toolset directly through `agents-cli`:

```shell
cd /path/to/your/adk-training/support-ops-agent
export GOOGLE_GENAI_USE_ENTERPRISE=1
export GOOGLE_CLOUD_LOCATION=global
export MCP_SERVER_URL=$(gcloud run services describe mcp-cart-server --region="$DEPLOY_REGION" --format='value(status.url)')
# Optional if mcp-cart-server was deployed privately without --allow-unauthenticated:
# export MCP_AUTH_TOKEN=$(gcloud auth print-identity-token)

# 1. Terminal smoke test across two turns on the same session (--start-server + --session-id)
agents-cli run "Investigate ticket TCK-1042, check enterprise SLA, and add 'P1-Pager-Bridge' to my cart." \
  --start-server \
  --session-id ops-mcp-demo

agents-cli run "View my cart and confirm which tickets were escalated." \
  --session-id ops-mcp-demo

# 2. Interactive visual debugging via agents-cli playground
agents-cli playground
```

Notice how seamlessly `support_ops_agent` combines local stateful Python tools (`lookup_ticket`, `check_sla_policy`, `escalate_ticket`) with remote Cloud Run MCP tools (`add_item_to_cart`, `view_cart`)!

---

### Cleanup (Important!)

Delete the Cloud Run service and Artifact Registry repository when finished to avoid ongoing storage or compute charges:

```shell
gcloud run services delete mcp-cart-server \
    --region="$DEPLOY_REGION" \
    --async

gcloud artifacts repositories delete adk-images \
    --location="$DEPLOY_REGION" \
    --async

cd /path/to/your/adk-training
rm -rf cloud_mcp_server
```

### Self-Reflection Questions
- Our demo MCP server writes session files under `/tmp/carts`. Why is `/tmp` volatile on Cloud Run, and what happens to a user's cart when Cloud Run scales down to zero?
- What advantages does Google Cloud Memorystore (Redis) provide over `/tmp` files for storing MCP session state?
- How does `StreamableHTTPConnectionParams(url=f"{MCP_SERVER_URL}/mcp", headers=...)` decouple `support-ops-agent` from the MCP server's internal storage implementation and authentication topology?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="34">

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

</SolutionVault>
