---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 28 Solution: Building a "Shopping Cart" MCP Server

## Goal

This file contains the complete, working code for both `custom_mcp_server/cart_server.py` and `custom_mcp_server/agent.py`.

### `custom_mcp_server/cart_server.py`

```python
# Filename: cart_server.py
import asyncio
import json
import sys
from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# --- Server State ---
# In a real application, this would be a database. For this lab, a simple
# in-memory list is enough to demonstrate statefulness.
CART = []

# --- MCP Server Setup ---
app = Server("shopping_cart_mcp_server")

@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    """Defines the 'menu' of tools our server offers."""
    # Always log to stderr: stdout is reserved for MCP JSON-RPC frames!
    print("[Server]: Client asked for the list of tools.", file=sys.stderr, flush=True)

    add_item_tool = mcp_types.Tool(
        name="add_item_to_cart",
        description="Adds a single item to the user's shopping cart.",
        inputSchema={
            "type": "object",
            "properties": {
                "item": {"type": "string", "description": "The item to add to the cart."}
            },
            "required": ["item"],
        },
    )

    view_cart_tool = mcp_types.Tool(
        name="view_cart",
        description="Shows all the items currently in the user's shopping cart.",
        inputSchema={"type": "object", "properties": {}},  # No arguments needed
    )

    return [add_item_tool, view_cart_tool]

@app.call_tool()
async def call_mcp_tool(name: str, arguments: dict) -> list[mcp_types.Content]:
    """Handles the execution of our tools."""
    print(f"[Server]: Client called tool '{name}'.", file=sys.stderr, flush=True)

    # --- Tool Logic ---
    if name == "add_item_to_cart":
        item = arguments.get("item")
        if item:
            CART.append(item)
            response_text = json.dumps({"status": "success", "message": f"Added '{item}' to the cart."})
        else:
            response_text = json.dumps({"status": "error", "message": "No item provided."})

        return [mcp_types.TextContent(type="text", text=response_text)]

    elif name == "view_cart":
        response_text = json.dumps({"status": "success", "cart": CART})
        return [mcp_types.TextContent(type="text", text=response_text)]

    else:
        response_text = json.dumps({"status": "error", "message": f"Tool '{name}' not found."})
        return [mcp_types.TextContent(type="text", text=response_text)]

# --- MCP Server Runner ---
async def run_mcp_stdio_server():
    """Runs the server, listening for connections over standard input/output."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        print("[Server]: Waiting for a client to connect...", file=sys.stderr, flush=True)
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=app.name,
                server_version="0.1.0",
                capabilities=app.get_capabilities(NotificationOptions(), {}),
            ),
        )
        print("[Server]: Client disconnected.", file=sys.stderr, flush=True)

if __name__ == "__main__":
    print("[Server]: Starting Shopping Cart MCP Server...", file=sys.stderr, flush=True)
    try:
        asyncio.run(run_mcp_stdio_server())
    except KeyboardInterrupt:
        print("\n[Server]: Shutting down.", file=sys.stderr, flush=True)
```

### `custom_mcp_server/agent.py`

```python
# Filename: agent.py
import pathlib
import sys
from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

# Resolve cart_server.py relative to this file rather than os.getcwd(), because
# `uv run adk web` is launched from the parent `adk-training` directory.
PATH_TO_SERVER = str(pathlib.Path(__file__).parent / "cart_server.py")

root_agent = Agent(
    model='gemini-3.8-flash',
    name='shopping_agent',
    instruction='You are a shopping assistant. Help the user by adding items to their cart and showing them their cart contents.',
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    # Use sys.executable so the subprocess runs inside the active .venv
                    # where `google-adk[mcp]` is installed.
                    command=sys.executable,
                    args=[PATH_TO_SERVER],
                ),
            ),
        )
    ],
)
```

### Self-Reflection Answers

1.  **In our `cart_server.py`, we used a global list `CART` to store the state. Why is this approach not suitable for a production environment?**
    *   **Answer:** Multiple server instances would each have their own independent copy of the list, leading to inconsistent state, and every client connected to the same instance would share the exact same cart. A production solution uses an external, centralized data store such as Redis or Firestore keyed per user or session.

2.  **The server declares `capabilities` in its `InitializationOptions`. What role does capability negotiation play in the MCP handshake?**
    *   **Answer:** During initialization, the client and server exchange the protocol features they support (tools, prompts, resources, notifications). `app.get_capabilities(...)` advertises exactly what this server implements so unsupported requests fail cleanly during negotiation rather than mid-conversation.

3.  **What are the benefits of decoupling the tool logic from the agent?**
    *   **Answer:** Independent scalability, modular maintenance, and cross-client reusability. Any MCP-compliant host or agent can consume your shopping cart service without duplicating business logic.
