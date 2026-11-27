---
sidebar_position: 34
title: "Module 34: Deploying an MCP Server to Cloud Run"
pagination_label: "Module 34: Deploying MCP Server to Cloud Run — 📖 Theory & Overview"
---

# Module 34: Deploying an MCP Server to Cloud Run

## Theory

![Cloud-Native Stateless MCP Server Architecture (Light)](img/hero-light.webp#gh-light-mode-only)
![Cloud-Native Stateless MCP Server Architecture (Dark)](img/hero-dark.webp#gh-dark-mode-only)
*Figure: Deploying stateless serverless MCP servers on Cloud Run backed by externalized distributed cache and database stores.*

### The Challenge of State in a Serverless World

In Module 28, you built a stateful MCP server. Its state—the contents of the shopping cart—was a single global Python list: `CART = []`. That worked fine because the server ran over stdio, talking to exactly one client (your local agent) at a time — there was no notion of "whose cart is this" because there was only ever one.

Moving to Cloud Run over HTTP changes that completely: the server can now be talking to *many* clients concurrently, each of whom needs their own, isolated cart. A single global list would mean every user shares the exact same cart — a correctness bug, not just a scaling one. And even setting that aside, Cloud Run is a **stateless** and **serverless** environment, which introduces a second problem on top of the first:

*   **Stateless:** Each incoming request could be handled by a completely different container instance. An instance that handles a user's "add item" request might be shut down before the user makes a "view cart" request, which would then be routed to a brand new instance with no memory of the previous one. The in-memory cart data would be lost.
*   **Serverless:** You don't have a single, persistent "server." Cloud Run automatically starts and stops container instances based on traffic. It might run ten instances to handle a spike in traffic and then scale down to zero when idle.

If we deploy our simple, in-memory MCP server directly to Cloud Run, every user's shopping cart would be wiped out between requests. We need a new architecture.

### The Solution: Externalized State

The solution to this challenge is to **externalize the state**. Instead of storing the session data in the memory of the MCP server process, the server must save it to and load it from an external, persistent storage service that all of its instances can access.

This is a fundamental pattern in cloud-native application design. The application instances themselves remain stateless, which makes them easy to scale and replace, while the important data lives in a durable, centralized location.

**Common choices for an external state store include:**
*   **In-memory caches:** Services like **Redis** or **Google Cloud Memorystore**. These are extremely fast and are a perfect fit for session data that needs to be accessed quickly but may not need to be stored forever.
*   **Databases:** Services like **Firestore**, **DynamoDB**, or a traditional SQL database like **Cloud SQL**. These are better for data that needs to be stored permanently and queried in more complex ways.

### The New Architecture

![Stateless Serverless MCP Architecture (Light)](img/stateless-serverless-mcp-light.webp#gh-light-mode-only)
![Stateless Serverless MCP Architecture (Dark)](img/stateless-serverless-mcp-dark.webp#gh-dark-mode-only)
*Figure: Request lifecycle showing Agent HTTP request, Cloud Run auto-routing, Redis/Firestore state sync, and stateless response dispatch.*

With externalized state, the interaction flow for our MCP server on Cloud Run looks like this:

1.  An ADK agent (the client) sends a `call_tool` request (e.g., `add_item_to_cart`) to the Cloud Run service URL.
2.  Cloud Run starts or selects a container instance to handle the request.
3.  The MCP server code inside the container reads the `Mcp-Session-Id` HTTP header that the MCP transport itself tracks for the connection.
4.  Instead of appending to a global in-memory list, the server connects to the external state store (e.g., Redis), keyed by that session ID.
5.  It retrieves the shopping cart for the given session, performs the action (adds the new item), and saves the updated cart back to the external store.
6.  It sends the success response back to the ADK agent.

Now, if another request for the same `session_id` arrives a moment later, Cloud Run can send it to a completely different container instance. This new instance will follow the same process, connect to the same external store, and retrieve the correct, up-to-date shopping cart. The state is preserved.

### Connecting Standalone ADK Agents and `agents-cli` Projects

When an MCP server runs on Cloud Run over HTTP, your ADK agent replaces local `StdioConnectionParams` with a network transport parameter class from `google.adk.tools.mcp_tool`:

*   **`StreamableHTTPConnectionParams` (Recommended):** Connects over the modern MCP Streamable HTTP transport (mounted at `/mcp` by default in `FastMCP`), with optional `headers` (for Bearer tokens or API keys) and configurable timeouts.
*   **`SseConnectionParams` (Legacy HTTP+SSE):** Connects to older MCP servers that expose a separate Server-Sent Events endpoint.

Because `McpToolset` is a standard ADK toolset, the exact same wiring works both in standalone ADK packages (`uv run adk web`) and inside enterprise **`agents-cli`** projects (`support-ops-agent/app/agent.py`):

```python
import os
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "https://mcp-cart-server-xyz.a.run.app").rstrip("/")
MCP_AUTH_TOKEN = os.environ.get("MCP_AUTH_TOKEN", "")

mcp_headers = {"Authorization": f"Bearer {MCP_AUTH_TOKEN}"} if MCP_AUTH_TOKEN else None

remote_mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=f"{MCP_SERVER_URL}/mcp",
        headers=mcp_headers,
    )
)
```

Inside an `agents-cli` project, once `remote_mcp_toolset` is added to `root_agent.tools` in `app/agent.py` (with `app = App(root_agent=root_agent, name="app")` preserved), you can smoke-test remote Cloud Run MCP tool execution immediately from your terminal or browser before redeploying:

```bash
# Rapid CLI smoke test (with --start-server + --session-id to verify multi-turn MCP state)
agents-cli run "Add 'p1-incident-runbook' to my cart and inspect ticket TCK-1042." \
  --start-server --session-id ops-1

# Interactive web playground
agents-cli playground
```

### Production Considerations for MCP

When deploying MCP servers to production, security and safety become paramount. The ADK provides advanced features to handle these requirements.

#### Authentication

You must secure your MCP server (for example, deploying Cloud Run with `--no-allow-unauthenticated` or behind an API gateway) so only authorized agents can invoke its tools. `McpToolset` and `StreamableHTTPConnectionParams` support multiple authentication patterns:

*   **OAuth2 (`auth_scheme` + `auth_credential`):** Standard method for user-delegated or service-to-service production flows. ADK manages token acquisition and refresh automatically.
*   **HTTP Bearer / Cloud Run Identity Tokens (`headers` or `header_provider`):** Pass static headers via `StreamableHTTPConnectionParams(url=..., headers={"Authorization": "Bearer ..."})` or per-request dynamic tokens via `McpToolset(..., header_provider=...)`.
*   **API Keys & HTTP Basic Auth:** Supported via `auth_scheme` / `auth_credential` or custom HTTP headers.

#### Human-in-the-Loop (HITL)

When an MCP server provides powerful or destructive tools (e.g., `write_file`, `delete_database_entry`), it's crucial to have a human approval step to prevent accidental data loss or misuse.

You can enforce HITL in ADK either via `McpToolset(..., require_confirmation=True)` or by implementing a `before_tool_callback` on your `Agent`:
1.  Check if the tool being called is on a list of high-impact or destructive operations.
2.  Block or pause execution and prompt for explicit human approval before allowing the remote MCP call to proceed.

<KnowledgeCheck
  id="m34-stateless-mcp-cloud-run"
  question="Why must a stateful MCP server externalize its session data (for example, to Memorystore/Redis or Firestore) before being deployed to Cloud Run, and which ADK connection class connects to FastMCP's '/mcp' HTTP endpoint?"
  options={[
    "Cloud Run instances are stateless and ephemeral—requests may hit different containers or scale to zero—and the client connects via 'StreamableHTTPConnectionParams'",
    "Cloud Run blocks all outbound database connections and requires 'StdioConnectionParams' over SSH",
    "Global Python lists automatically replicate across all Cloud Run instances when 'SseConnectionParams' is used",
    "FastMCP automatically persists '/tmp' files across container termination without an external store"
  ]}
  correctIndex={0}
  hint="Think about what happens to in-memory or '/tmp' state when Cloud Run scales horizontally or scales down to zero, and how remote HTTP MCP servers are reached."
  explanation="Cloud Run containers are stateless: consecutive tool calls can land on separate container instances, and scaling to zero wipes container memory and '/tmp'. Externalizing state keyed by 'Mcp-Session-Id' keeps carts consistent across instances, while 'StreamableHTTPConnectionParams' connects 'McpToolset' to the remote '/mcp' endpoint."
/>

### Key Takeaways
- Serverless platforms like Cloud Run are **stateless**, meaning in-memory state is lost across horizontal scaling and scale-to-zero events.
- To deploy a stateful MCP server to Cloud Run, **externalize session state** (keyed by `Mcp-Session-Id`) into a shared backing store like **Memorystore (Redis)**, **Firestore**, or **Cloud SQL**.
- Connect both standalone ADK agents (`uv run adk web`) and enterprise **`agents-cli`** projects (`support-ops-agent/app/agent.py`) to remote FastMCP servers using `McpToolset(connection_params=StreamableHTTPConnectionParams(url=f"{MCP_SERVER_URL}/mcp", headers=...))`, verifying behavior rapidly with `agents-cli run` and `agents-cli playground`.
- **Separation of Concerns in MCP:** Because `McpToolset` only depends on the remote `/mcp` URL and tool schemas, you can upgrade the MCP server's persistence layer from a `/tmp` demo store to Redis or Firestore without changing a single line of agent code.
- **Persistence Caveat for `/tmp`:** Container `/tmp` storage lives in volatile memory on Cloud Run and disappears whenever an instance is recycled or scales down to zero — always use a managed external store in production.
