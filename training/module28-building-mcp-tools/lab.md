---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 28: Building a "Shopping Cart" MCP Server Challenge

## Goal

In this lab, you will build your own simple, standalone MCP server from scratch. This server will manage a stateful shopping cart, allowing clients to add items and view the cart's contents. You will then connect an ADK agent to your custom server.

### Step 1: Install MCP and Create Project

1.  **Install the `mcp` library (via the ADK's compatible extra):**
    ```shell
    uv add "google-adk[mcp]"
    ```
    Installing `mcp` as a separate, unconstrained package (e.g. `pip install mcp`) can resolve a newer `mcp` release than the one ADK expects. Installing it through ADK's `[mcp]` extra guarantees a compatible version.

2.  **Create a new project directory:**
    ```shell
    mkdir custom_mcp_server
    cd custom_mcp_server
    ```

### Step 2: Implement the MCP Server

**Exercise:** Create a file named `cart_server.py`. Inside this file, your task is to implement the `list_tools` and `call_tool` handlers for the shopping cart server. Use the `# TODO` comments as your guide.

```python
# In cart_server.py (Starter Code)
import asyncio
import json
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
    print("[Server]: Client asked for the list of tools.")
    
    # TODO: 1. Define the `add_item_to_cart` tool. It needs a name, a
    # description, and an inputSchema for a required string property "item".
    add_item_tool = mcp_types.Tool(...)

    # TODO: 2. Define the `view_cart` tool. It needs a name, a description,
    # and an empty inputSchema since it takes no arguments.
    view_cart_tool = mcp_types.Tool(...)
    
    return [add_item_tool, view_cart_tool]

@app.call_tool()
async def call_mcp_tool(name: str, arguments: dict) -> list[mcp_types.Content]:
    """Handles the execution of our tools."""
    print(f"[Server]: Client called tool '{name}'.")

    # TODO: 3. Implement the logic for the "add_item_to_cart" tool.
    # - Get the "item" from the `arguments`.
    # - Append it to `CART`.
    # - Return a success message.

    # TODO: 4. Implement the logic for the "view_cart" tool.
    # - Return the current contents of `CART`.
    
    # Remember to return your response as a JSON string inside a
    # `mcp_types.TextContent` object.
    response_text = json.dumps({"status": "error", "message": "Not implemented."})
    return [mcp_types.TextContent(type="text", text=response_text)]

# --- MCP Server Runner (Provided for you) ---
async def run_mcp_stdio_server():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        print("[Server]: Waiting for a client to connect...")
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=app.name,
                server_version="0.1.0",
                capabilities=app.get_capabilities(NotificationOptions(), {}),
            ),
        )

if __name__ == "__main__":
    print("[Server]: Starting Shopping Cart MCP Server...")
    try:
        asyncio.run(run_mcp_stdio_server())
    except KeyboardInterrupt:
        print("\n[Server]: Shutting down.")
```

### Step 3: Create the ADK Client Agent

Create an `agent.py` file and complete the code to connect to your server using the ADK 2.0 `Agent` class and an `McpToolset`.

```python
# In agent.py
import pathlib
from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

# TODO: Get the absolute path to your 'cart_server.py'.
# Base it on this file's own location (pathlib.Path(__file__).parent), not on
# os.getcwd() — the process's working directory won't be this folder when
# 'adk web'/'adk run' is launched from the parent directory in Step 4.
PATH_TO_SERVER = ...

# TODO: Define the root Agent node and configure the McpToolset
# - command: 'python3'
# - args: [PATH_TO_SERVER]
root_agent = Agent(
    model='gemini-3.5-flash',
    name='shopping_agent',
    instruction='You are a shopping assistant.',
    tools=[
        McpToolset(...)
    ],
)
```
Also create an empty `__init__.py` and a `.env` file with `MODEL="gemini-3.5-flash"`.

### Step 4: Test the Full System

1.  **Navigate to the parent directory and start the ADK web server**, pointing it at the `custom_mcp_server` folder you created in Step 1:
    ```shell
    cd ..
    uv run adk web custom_mcp_server
    ```
2.  **Check the console logs:** You should see logs from your `cart_server.py` as it starts up.
3.  **Interact with the agent** in the Dev UI:
    *   "Please add 'milk' to my cart."
    *   "Also add 'eggs'."
    *   "What is in my shopping cart?"
4.  **Examine the server logs** in the console to see the `call_tool` requests being received and processed by your custom server.

### Having Trouble?
If you get stuck, you can find the complete, working code in the `lab-solution.md` file.

### Lab Summary
You have successfully built and consumed your own stateful MCP tool. You have learned to:
*   Implement the `@app.list_tools()` handler to define a server's tool schema.
*   Implement the `@app.call_tool()` handler to provide tool logic.
*   Manage state on the server side across multiple tool calls.
*   Connect an ADK agent to your custom-built MCP server.

### Self-Reflection Questions
- In our `cart_server.py`, we used a global list `CART` to store the state. Why is this approach not suitable for a production environment with multiple server instances or multiple concurrent users? What would be a better solution?
- The server declares `capabilities` in its `InitializationOptions`. What role does this capability negotiation play during the MCP handshake, and what might happen if a client expects a capability the server never declared?
- By building an MCP server, you have decoupled your tool's logic from the agent. What are the long-term benefits of this separation for maintaining and scaling your application?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMjgtYnVpbGRpbmctbWNwLXRvb2xzL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module28-building-mcp-tools/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
