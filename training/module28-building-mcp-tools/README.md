---
sidebar_position: 28
title: "Module 28: Building a Custom MCP Tool"
---

# Module 28: Building a Custom MCP Tool

## Theory

### Becoming a Tool Provider

In the previous module, you acted as a **consumer** of an MCP tool. Your ADK agent was the client connecting to a pre-built server. Now, we flip the roles. You will become a **provider** by building your own simple, standalone MCP server from scratch.

By exposing your application's capabilities via the Model Context Protocol, you are making them available not just to your own ADK agents, but to *any* MCP-compliant client. It turns your service into a reusable, AI-addressable component in a larger ecosystem.

### The Anatomy of an MCP Server

An MCP server is an application that listens for connections from clients and responds to requests according to the protocol. A server must implement handlers for two fundamental methods:

#### 1. `list_tools()`
When a client first connects, it calls `list_tools()`. The server's job is to respond with a "menu" of all the tools it provides. For each tool, it must provide a detailed schema, including:
*   The tool's `name`.
*   A `description` of what it does.
*   An `inputSchema` that defines the arguments the tool expects (names, types, etc.).

The client's LLM uses this menu to decide which tool to call.

#### 2. `call_tool()`
Once the client's LLM decides to use a tool, it sends a `call_tool()` request containing the `name` of the tool and a dictionary of `arguments`.

The server's `call_tool()` handler is responsible for:
*   Receiving the request.
*   Executing the corresponding logic for the requested tool.
*   Managing any state the tool needs (e.g. an in-memory cart, a database row).
*   Returning a result to the client.

### Building an MCP Server in Python

The `mcp` Python library provides a `Server` class and decorators to simplify this process.

1.  **Install the library (via ADK's compatible extra):** `uv add "google-adk[mcp]"`
2.  **Instantiate the Server:** `app = Server("my_mcp_server")`
3.  **Implement Handlers with Decorators:** You write `async` functions and use decorators to register them as handlers.
    *   `@app.list_tools()`: This decorates the function that will handle the `list_tools` request. It should return a list of `mcp.types.Tool` objects.
    *   `@app.call_tool()`: This decorates the function that will handle the `call_tool` request. It receives the tool name and arguments.
4.  **Run the Server:** You use a runner function (e.g., `mcp.server.stdio.stdio_server`) to start the server and listen for connections.

In the lab, you will build a simple MCP server that exposes a stateful "shopping cart" tool, learning the fundamentals of implementing these handlers.

### Why build an MCP Server?

Building an MCP server decouples your tool's logic from the agent, which provides significant benefits:
1.  **Independent Scalability:** You can scale the agent and the tool server separately.
2.  **Modular Maintenance:** Update tool logic without redeploying the agent.
3.  **Reusability:** Your MCP server can be consumed by *any* MCP-compliant client.
4.  **Workflow Integration:** In ADK 2.0, you can equip any `Agent` node with your custom MCP server, allowing for complex, distributed graph execution.