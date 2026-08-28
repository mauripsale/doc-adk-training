---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 34 Solution: Deploying the "Shopping Cart" Server

## Goal

This file contains the complete code for the `stateless_cart_server.py` and the `agent.py` client for the lab.

### `cloud_mcp_server/stateless_cart_server.py`

```python
# Filename: stateless_cart_server.py
import json
import os
from mcp.server.fastmcp import FastMCP, Context

# --- Configuration ---
# In a serverless environment, we can use the temporary filesystem for a simple demo.
# In a real app, this would be a Redis or database connection.
STATE_STORAGE_PATH = "/tmp/carts"
if not os.path.exists(STATE_STORAGE_PATH):
    os.makedirs(STATE_STORAGE_PATH)

# --- MCP Server Setup ---
mcp = FastMCP("stateless_shopping_cart_server")

def get_session_id(ctx: Context) -> str:
    # The MCP session ID arrives as a standard HTTP header, tracked by the
    # transport itself.
    return ctx.request_context.request.headers.get("mcp-session-id", "unknown")

# Helper functions to simulate an external state store
def get_cart(session_id: str) -> list:
    cart_file = os.path.join(STATE_STORAGE_PATH, f"{session_id}.json")
    if os.path.exists(cart_file):
        with open(cart_file, 'r') as f:
            return json.load(f)
    return []

def save_cart(session_id: str, cart: list):
    cart_file = os.path.join(STATE_STORAGE_PATH, f"{session_id}.json")
    with open(cart_file, 'w') as f:
        json.dump(cart, f)

@mcp.tool()
def add_item_to_cart(item: str, ctx: Context) -> dict:
    """Adds an item to the cart."""
    session_id = get_session_id(ctx)
    print(f"[Server]: Handling add_item_to_cart for session '{session_id}'")
    cart = get_cart(session_id)
    cart.append(item)
    save_cart(session_id, cart)
    return {"status": "success", "message": f"Added '{item}'."}

@mcp.tool()
def view_cart(ctx: Context) -> dict:
    """Views items in the cart."""
    session_id = get_session_id(ctx)
    print(f"[Server]: Handling view_cart for session '{session_id}'")
    cart = get_cart(session_id)
    return {"status": "success", "cart": cart}

# --- ASGI app for HTTP, suitable for Cloud Run ---
# FastMCP mounts the MCP endpoint at /mcp by default.
app = mcp.streamable_http_app()
```

### `cloud_mcp_server/agent.py`

```python
# Filename: agent.py
from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

# The URL of your deployed MCP server, including the /mcp path FastMCP mounts at.
# Replace this with the URL from your `gcloud run deploy` output.
MCP_SERVER_URL = "YOUR_CLOUD_RUN_SERVICE_URL/mcp"

root_agent = Agent(
    model='gemini-3.5-flash',
    name='cloud_shopping_agent',
    instruction='You are a shopping assistant. Help the user by adding items to their cart and showing them their cart contents.',
    tools=[
        McpToolset(
            # Use StreamableHTTPConnectionParams for remote servers
            connection_params=StreamableHTTPConnectionParams(
                url=MCP_SERVER_URL,
            ),
        )
    ],
)
```

### Self-Reflection Answers

1.  **Our stateless server uses the `/tmp` directory for storage. Why is this approach not truly persistent, and what could happen to a user's shopping cart if the Cloud Run service scales down and then back up?**
    *   **Answer:** Using the `/tmp` directory for storage in a Cloud Run container is not truly persistent because `/tmp` is part of the container's volatile filesystem. When Cloud Run scales a service to zero due to inactivity or recycles an instance, the container is terminated, and all data in `/tmp` is permanently lost. If a user's shopping cart were stored this way, and the service scaled down and then back up, their cart would be erased. This demonstrates the critical need for externalized state in serverless environments.

2.  **What are the advantages of using a managed service like Google Cloud Memorystore (Redis) for storing session state compared to the file-based approach used in this lab?**
    *   **Answer:** A managed in-memory service like Google Cloud Memorystore (Redis) offers several advantages over a file-based approach for production session state:
        *   **True Persistence:** Data survives container restarts and scales to zero.
        *   **High Performance:** In-memory key-value stores are extremely fast, providing low-latency access to session data.
        *   **Scalability & Consistency:** All Cloud Run instances connect to the same central data source, ensuring state consistency across a horizontally scaled service.
        *   **Operational Simplicity:** Managed services handle patching, backups, and scaling, reducing operational overhead.

3.  **The `MCPToolset` on the client side doesn't need to know *how* the server is storing its state. Why is this separation of concerns a key benefit of the MCP architecture?**
    *   **Answer:** This separation of concerns is a key benefit of the MCP architecture because it decouples the client (the ADK agent using `MCPToolset`) from the server's internal implementation details. The agent only needs to know the server's URL and the tool's schema (its name, description, and input arguments). It doesn't care whether the server stores state in memory, a file, Redis, or a database. This allows the server's backend to be changed or upgraded (e.g., migrating from file-based state to Redis) without requiring any changes or redeployment of the client agent, promoting modular maintenance, independent evolution, and system robustness.
