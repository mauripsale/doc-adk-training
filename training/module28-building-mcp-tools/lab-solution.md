---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 28 Solution: Building a "Shopping Cart" MCP Server

## Goal

This file contains the complete code for both the `cart_server.py` and the `agent.py` client script for the Shopping Cart MCP lab.

### `custom_mcp_server/cart_server.py`

```python
# Filename: cart_server.py
import asyncio
import json
from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# --- Server State ---
sidebar_position: 3
# In a real application, this would be a database. For this lab, a simple
# in-memory dictionary is enough to demonstrate statefulness.
SESSION_CARTS = {}

# --- MCP Server Setup ---
sidebar_position: 3
app = Server("shopping_cart_mcp_server")

@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    """Defines the 'menu' of tools our server offers."""
    print("[Server]: Client asked for the list of tools.")
    
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
        inputSchema={"type": "object", "properties": {}}, # No arguments needed
    )
    
    return [add_item_tool, view_cart_tool]

@app.call_tool()
async def call_mcp_tool(name: str, arguments: dict, session_id: str) -> list[mcp_types.Content]:
    """Handles the execution of our tools."""
    print(f"[Server]: Client called tool '{name}' for session '{session_id}'.")

    # Ensure a cart exists for the current session
    if session_id not in SESSION_CARTS:
        SESSION_CARTS[session_id] = []

    # --- Tool Logic ---
sidebar_position: 3
    if name == "add_item_to_cart":
        item = arguments.get("item")
        if item:
            SESSION_CARTS[session_id].append(item)
            response_text = json.dumps({"status": "success", "message": f"Added '{item}' to the cart."}) 
        else:
            response_text = json.dumps({"status": "error", "message": "No item provided."})
        
        return [mcp_types.TextContent(type="text", text=response_text)]

    elif name == "view_cart":
        cart_contents = SESSION_CARTS[session_id]
        response_text = json.dumps({"status": "success", "cart": cart_contents})
        return [mcp_types.TextContent(type="text", text=response_text)]

    else:
        response_text = json.dumps({"status": "error", "message": f"Tool '{name}' not found."}) 
        return [mcp_types.TextContent(type="text", text=response_text)]

# --- MCP Server Runner ---
sidebar_position: 3
async def run_mcp_stdio_server():
    """Runs the server, listening for connections over standard input/output."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        print("[Server]: Waiting for a client to connect...")
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(server_name=app.name, server_version="0.1.0"),
        )
        print("[Server]: Client disconnected.")

if __name__ == "__main__":
    print("[Server]: Starting Shopping Cart MCP Server...")
    try:
        asyncio.run(run_mcp_stdio_server())
    except KeyboardInterrupt:
        print("\n[Server]: Shutting down.")
```

### `custom_mcp_server/agent.py`

```python
# Filename: agent.py
import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# Get the absolute path to our server script.
PATH_TO_SERVER = os.path.abspath("./cart_server.py")

root_agent = LlmAgent(
    model='gemini-3.5-flash',
    name='shopping_agent',
    instruction='You are a shopping assistant. Help the user by adding items to their cart and showing them their cart contents.',
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='python3',
                    args=[PATH_TO_SERVER],
                ),
            ),
        )
    ],
)
```

### Self-Reflection Answers

1.  **In our `cart_server.py`, we used a global dictionary `SESSION_CARTS` to store the state. Why is this approach not suitable for a production environment with multiple server instances? What would be a better solution?**
    *   **Answer:** A global in-memory dictionary like `SESSION_CARTS` will not work in a production environment with multiple server instances (e.g., if you scale your server to handle more traffic). Each server instance would have its own independent copy of `SESSION_CARTS`, leading to inconsistent state. If a user adds an item to their cart through one server instance and then views their cart through another, the second instance wouldn't see the added item. A better solution is to use an external, centralized, and persistent data store (e.g., Redis, a SQL database, or a NoSQL database) that all server instances can access, ensuring a single source of truth for the state.

2.  **The `call_tool` handler receives a `session_id`. Why is this ID crucial for managing state in a multi-user environment?**
    *   **Answer:** The `session_id` is crucial for **user isolation** and enabling **stateful conversations** in a multi-user environment. It acts as a unique identifier for each client's ongoing interaction with the MCP server. Without `session_id`, the server wouldn't know which shopping cart belongs to which user, and all users would end up sharing a single, chaotic cart. By using the `session_id`, the server can correctly associate and manage each user's individual state (their cart) across multiple `call_tool` requests.

3.  **By building an MCP server, you have decoupled your tool's logic from the agent. What are the long-term benefits of this separation for maintaining and scaling your application?**
    *   **Answer:** Decoupling provides significant benefits:
        *   **Independent Scalability:** You can scale the agent and the tool server independently based on their specific workloads. If the shopping cart gets heavy traffic, you can scale *only* the MCP server without affecting the agent.
        *   **Modular Maintenance:** You can update and redeploy the tool's logic (e.g., change how items are added to the cart) without needing to redeploy or even restart the agent.
        *   **Reusability:** The MCP server can be consumed by *any* MCP-compliant client, not just your ADK agent. This promotes sharing and reuse of business logic across different applications.
        *   **Technology Agnosticism:** The MCP server could even be written in a different programming language (e.g., Go, Java) if that's better suited for the tool's logic, as long as it adheres to the MCP protocol. This allows teams to use the best tool for the job.