---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 28: Building Custom MCP Tools — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 28: Building a "Shopping Cart" MCP Server Challenge

## Goal

In this lab, you will build your own standalone MCP server from scratch in Python. This server will manage a stateful shopping cart, allowing clients to add items and inspect the cart's contents across multiple conversation turns. You will then connect an ADK agent to your custom server.

### Step 1: Install MCP and Create the Agent Package

<Setup/>

1.  **Navigate to your `adk-training` workspace directory and install the `mcp` extra:**
    ```shell
    cd /path/to/your/adk-training
    uv add "google-adk[mcp]"
    ```
    Installing `mcp` via ADK's `[mcp]` extra guarantees a version compatible with `google-adk`, rather than an unconstrained standalone release.

2.  **Create the agent directory inside `adk-training`:**
    ```shell
    mkdir custom_mcp_server
    cd custom_mcp_server
    ```

### Step 2: Implement the MCP Server (`cart_server.py`)

> **Critical — Never write logs to `stdout` in a `stdio` MCP server!**
> When `mcp.server.stdio.stdio_server()` runs, your server communicates with the ADK client by sending JSON-RPC frames over **standard output (`stdout`)**. If you call a regular `print("...")` without `file=sys.stderr`, Python writes plain text straight into `stdout`, corrupting the JSON-RPC stream and crashing the MCP handshake! Always log to `sys.stderr` (`print(..., file=sys.stderr, flush=True)`).

**Exercise:** Inside `custom_mcp_server/`, create a file named `cart_server.py` and implement the `@app.list_tools()` and `@app.call_tool()` handlers by completing `# TODO: 1` through `# TODO: 4`.

```python
# custom_mcp_server/cart_server.py (Starter Code)
import asyncio
import json
import sys
from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# --- Server State ---
# In production, persist state in a database (e.g., Redis or Firestore) keyed by
# user/session. Here, an in-memory list demonstrates cross-turn statefulness.
CART = []

# --- MCP Server Setup ---
app = Server("shopping_cart_mcp_server")

@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    """Defines the 'menu' of tools our server offers."""
    print("[Server]: Client asked for the list of tools.", file=sys.stderr, flush=True)

    # TODO: 1. Define the `add_item_to_cart` tool using `mcp_types.Tool(...)`.
    # Provide:
    # - name: "add_item_to_cart"
    # - description: Clear description of what the tool does
    # - inputSchema: JSON Schema object with a required string property "item"
    add_item_tool = mcp_types.Tool(...)

    # TODO: 2. Define the `view_cart` tool using `mcp_types.Tool(...)`.
    # Provide a name, description, and an empty object inputSchema
    # ({"type": "object", "properties": {}}).
    view_cart_tool = mcp_types.Tool(...)

    return [add_item_tool, view_cart_tool]

@app.call_tool()
async def call_mcp_tool(name: str, arguments: dict) -> list[mcp_types.Content]:
    """Handles the execution of our tools."""
    print(f"[Server]: Client called tool '{name}'.", file=sys.stderr, flush=True)

    # TODO: 3. Implement the logic for "add_item_to_cart":
    # - Read `item = arguments.get("item")`.
    # - If present, append `item` to `CART` and return a JSON status message
    #   wrapped in `[mcp_types.TextContent(type="text", text=response_text)]`.

    # TODO: 4. Implement the logic for "view_cart":
    # - Return a JSON payload containing `"cart": CART` wrapped in
    #   `[mcp_types.TextContent(type="text", text=response_text)]`.

    response_text = json.dumps({"status": "error", "message": f"Tool '{name}' not implemented."})
    return [mcp_types.TextContent(type="text", text=response_text)]

# --- MCP Server Runner (Provided for you) ---
async def run_mcp_stdio_server():
    """Runs the server, listening for JSON-RPC connections over stdio."""
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

### Step 3: Create the ADK Client Agent (`agent.py`)

1.  **Complete `custom_mcp_server/agent.py`:**
    Create `agent.py` inside `custom_mcp_server/` and connect to `cart_server.py` using `McpToolset` and `StdioConnectionParams`.
    > **Why `sys.executable` instead of `'python3'`?** Hardcoding `command='python3'` resolves to whatever global `python3` binary appears first on the OS `PATH`, which often lacks your project's `.venv` packages and crashes with `ModuleNotFoundError: No module named 'mcp'`. Using `sys.executable` guarantees the subprocess launches with the exact `.venv` Python interpreter running ADK!

    ```python
    # custom_mcp_server/agent.py (Starter Code)
    import pathlib
    import sys
    from google.adk import Agent
    from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
    from mcp import StdioServerParameters

    # TODO: 1. Compute the absolute path to 'cart_server.py' relative to this file
    # (pathlib.Path(__file__).parent / "cart_server.py") — do NOT use os.getcwd(),
    # because `uv run adk web` is launched from the parent `adk-training` folder!
    PATH_TO_SERVER = ...

    # TODO: 2. Define `root_agent` and configure `McpToolset` with `StdioConnectionParams`
    # and `StdioServerParameters(command=sys.executable, args=[PATH_TO_SERVER])`.
    root_agent = Agent(
        model='gemini-3.8-flash',
        name='shopping_agent',
        instruction='You are a shopping assistant. Help the user by adding items to their cart and showing them their cart contents.',
        tools=[
            McpToolset(...)
        ],
    )
    ```

2.  **Create `custom_mcp_server/__init__.py`:**
    Expose `agent` so ADK discovers `custom_mcp_server` as an agent package:
    ```shell
    echo "from . import agent as agent" > __init__.py
    ```

3.  **Configure `custom_mcp_server/.env`:**
    Create a `.env` file inside `custom_mcp_server/` matching your preferred Gemini backend:

    *   **Option A — Google AI Studio (API Key):**
        ```text
        GOOGLE_API_KEY=<your_google_ai_studio_api_key>
        ```
    *   **Option B — Google Cloud Vertex AI (ADC):**
        ```text
        GOOGLE_GENAI_USE_ENTERPRISE=1
        GOOGLE_CLOUD_PROJECT=<your_gcp_project>
        GOOGLE_CLOUD_LOCATION=global
        ```

### Step 4: Test the Full System

1.  **Return to the parent `adk-training` directory and start the ADK Dev UI:**
    ```shell
    cd ..
    uv run adk web
    ```
2.  **Open the Dev UI (`http://127.0.0.1:8000`)** and select `custom_mcp_server` from the agent dropdown.
3.  **Interact with your stateful shopping cart across multiple turns:**
    *   *"Please add 'milk' to my cart."*
    *   *"Also add 'eggs'."*
    *   *"What is in my shopping cart?"*
4.  **Inspect the terminal logs:** Watch your `[Server]: ...` diagnostic lines stream cleanly via `stderr` in the terminal as `list_tools` and `call_tool` execute without interfering with the `stdout` JSON-RPC channel!

### Having Trouble?
If you get stuck, you can find the complete, working code in `lab-solution.md` or unlock the Solution Vault below.

### Lab Summary
You have built and consumed your own stateful MCP server in Python:
*   Implemented `@app.list_tools()` using `from mcp.server.lowlevel import Server` to advertise JSON Schema tool definitions.
*   Implemented `@app.call_tool()` to mutate and read server-side state across turns.
*   Kept `stdio` JSON-RPC framing intact by routing server logs to `sys.stderr`, and used `sys.executable` so subprocesses inherit the active `.venv`.

### Self-Reflection Questions
- In our `cart_server.py`, we used a global list `CART` to store the state. Why is this approach not suitable for a production environment with multiple server instances or multiple concurrent users? What would be a better solution?
- The server declares `capabilities` in its `InitializationOptions`. What role does this capability negotiation play during the MCP handshake, and what might happen if a client expects a capability the server never declared?
- By building an MCP server, you have decoupled your tool's logic from the agent. What are the long-term benefits of this separation for maintaining and scaling your application?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="28">

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

</SolutionVault>
