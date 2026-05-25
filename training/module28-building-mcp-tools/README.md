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
*   Managing any state associated with the `session_id`.
*   Returning a result to the client.

### Building an MCP Server in Python

The `mcp` Python library provides a `Server` class and decorators to simplify this process.

1.  **Install the library:** `pip install mcp`
2.  **Instantiate the Server:** `app = Server("my_mcp_server")`
3.  **Implement Handlers with Decorators:** You write `async` functions and use decorators to register them as handlers.
    *   `@app.list_tools()`: This decorates the function that will handle the `list_tools` request. It should return a list of `mcp.types.Tool` objects.
    *   `@app.call_tool()`: This decorates the function that will handle the `call_tool` request. It receives the tool name, arguments, and `session_id`.
4.  **Run the Server:** You use a runner function (e.g., `mcp.server.stdio.stdio_server`) to start the server and listen for connections.

In the lab, you will build a simple MCP server that exposes a stateful "shopping cart" tool, learning the fundamentals of implementing these handlers.

### Key Takeaways
- By building an MCP server, you become a **provider** of tools to any MCP-compliant client, not just your own agents.
- An MCP server must implement two core handlers: `list_tools` to advertise its capabilities, and `call_tool` to execute them.
- The `mcp` Python library simplifies server creation with a `Server` class and the `@app.list_tools()` and `@app.call_tool()` decorators.
- The `call_tool` handler receives a `session_id`, which is the key to managing state for different clients across multiple requests.
- **Benefits of Decoupling:** Building an MCP server decouples your tool's logic from the agent, which provides significant long-term benefits. It allows for independent scalability (you can scale the agent and the tool server separately based on their specific loads), modular maintenance (you can update and redeploy the tool logic without touching the agent), and reusability (the MCP server can be consumed by any MCP-compliant client, not just your ADK agent, and can even be written in a different programming language).
- **The Role of `session_id`:** The `session_id` is crucial in a multi-user environment because it provides user isolation and enables stateful conversations. It acts as a unique key to distinguish one user's context (e.g., their shopping cart) from another's, and it links a sequence of requests from a single user into a coherent, evolving transaction.
- **State Management in Production:** Using a global in-memory dictionary for state (like `SESSION_CARTS` in the lab) is not suitable for production. If you run multiple instances of your server for scalability or redundancy, each instance will have its own separate in-memory dictionary, leading to state inconsistency. The correct production solution is to use an external, centralized data store (e.g., a Redis cache, a SQL/NoSQL database) that all server instances can access, ensuring a single source of truth for the state.