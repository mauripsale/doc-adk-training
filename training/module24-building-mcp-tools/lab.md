# Module 24: Building a Custom MCP Tool

## Lab 24: Building a "Shopping Cart" MCP Server

### Goal

In this lab, you will build your own simple, standalone MCP server from scratch. This server will manage a stateful shopping cart, allowing clients to add items and view the cart's contents. You will then create an ADK agent that acts as a client to your custom server, demonstrating the full end-to-end interaction.

### Prerequisites

*   You have completed Module 23.
*   You have `pip` installed in your virtual environment.

### Step 1: Install the MCP Server Library

The `mcp` library provides the tools needed to build an MCP server in Python.

1.  **Navigate to your training directory:**

    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Install the library:**

    ```shell
    pip install mcp
    ```

### Step 2: Create the Custom MCP Server

We will create a single Python script that will act as our server.

1.  **Create a new project directory for this lab:**

    ```shell
    mkdir custom-mcp-server
    cd custom-mcp-server
    ```

2.  **Create the `cart_server.py` file:**
    This file will contain all the logic for our stateful shopping cart server.

    ```python
    # Filename: cart_server.py
    import asyncio
    import json
    from mcp import types as mcp_types
    from mcp.server.lowlevel import Server, NotificationOptions
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio

    # --- Server State ---
    # In a real application, this would be a database or a more robust
    # session management system. For this lab, a simple dictionary is enough.
    # This will store the shopping cart for each session.
    SESSION_CARTS = {}

    # --- MCP Server Setup ---
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
            # Handle unknown tools
            response_text = json.dumps({"status": "error", "message": f"Tool '{name}' not found."})
            return [mcp_types.TextContent(type="text", text=response_text)]

    # --- MCP Server Runner ---
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

### Step 3: Create the ADK Client Agent

Now, let's create an ADK agent that will connect to and use our new server.

1.  **Create the `agent.py` file** in the same `custom-mcp-server` directory.
2.  **Add the following code:**

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
        model='gemini-1.5-flash',
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
3.  **Create an empty `__init__.py` file:** `touch __init__.py`
4.  **Create and configure your `.env` file.**

### Step 4: Test the Full System

1.  **Start the ADK web server:**
    From the `custom-mcp-server` directory, run `adk web`.

2.  **Check the console logs:**
    You will see the log messages from your `cart_server.py` script as the `MCPToolset` starts it as a subprocess. You'll see it waiting for a connection and then logging when the ADK client connects and asks for the list of tools.

3.  **Interact with the agent:**
    *   Open the Dev UI.
    *   **Turn 1: Add an item.**
        *   **User:** "Please add 'apples' to my shopping cart."
        *   **Expected Response:** The agent should confirm that 'apples' have been added.
    *   **Turn 2: Add another item.**
        *   **User:** "Also add 'bread'."
        *   **Expected Response:** The agent should confirm that 'bread' have been added.
    *   **Turn 3: View the cart.**
        *   **User:** "What's in my cart now?"
        *   **Expected Response:** The agent should list the items: `['apples', 'bread']`.

4.  **Examine the server logs:**
    Go back to the terminal running `adk web`. You will see the log messages from your `cart_server.py` script, showing the tool calls it received and confirming that it's managing the state for the session.

### Lab Summary

You have successfully built and consumed your own stateful, multi-turn tool using the Model Context Protocol!

You have learned to:
*   Install and use the `mcp` library to create a server.
*   Implement the `@app.list_tools()` handler to define the "menu" of tools your server provides.
*   Implement the `@app.call_tool()` handler to provide the logic for your tools.
*   Manage state on the server side, tied to a `session_id`.
*   Connect an ADK agent to your custom-built MCP server.

This is a powerful, advanced pattern that allows you to create highly capable and reusable tools for your AI agents.
