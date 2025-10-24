# Module 24: Building a Custom MCP Tool

## Theory

### Becoming a Tool Provider

In the previous module, you acted as a **consumer** of an MCP tool. Your ADK agent was the client, and it connected to a pre-built MCP server. Now, we will flip the roles. You will become a **provider** by building your own simple, standalone MCP server from scratch.

This is a powerful concept. By exposing your application's capabilities via the Model Context Protocol, you are making them available not just to your own ADK agents, but to *any* MCP-compliant client, including agents built with other frameworks like Genkit, or even custom applications. It turns your service into a reusable, AI-addressable component in a larger ecosystem.

### The Anatomy of an MCP Server

An MCP server is an application that listens for connections from MCP clients and responds to their requests according to the protocol. At its core, an MCP server must implement handlers for two fundamental methods:

#### 1. `list_tools()`
When a client first connects, it will call the `list_tools()` method. The server's job is to respond with a list of all the tools it provides. For each tool, it must provide a detailed schema, including:
*   The tool's `name`.
*   A `description` of what it does.
*   An `inputSchema` that defines the arguments the tool expects, including their names, types, and whether they are required.

This is the "menu" that the server presents to the client. The client's LLM will use this menu to decide which tool to call.

#### 2. `call_tool()`
Once the client's LLM decides to use a tool, the client will send a `call_tool()` request. This request includes the `name` of the tool to execute and a dictionary of `arguments`.

The server's `call_tool()` handler is responsible for:
*   Receiving the request.
*   Finding the corresponding function or logic for the requested tool name.
*   Executing that logic with the provided arguments.
*   Formatting the result into an MCP-compliant response and sending it back to the client.

### Building an MCP Server in Python

While you could implement an MCP server from scratch by handling the raw protocol messages, the `mcp` Python library makes this much simpler. It provides a `Server` class that you can use to quickly build a compliant server.

The process looks like this:

1.  **Install the library:** `pip install mcp`
2.  **Instantiate the Server:** Create an instance of the `mcp.server.lowlevel.Server`.
3.  **Implement Handlers with Decorators:** You write standard Python `async` functions and use decorators to register them as handlers for the MCP methods.
    *   `@app.list_tools()`: The function decorated with this will handle the `list_tools` request.
    *   `@app.call_tool()`: The function decorated with this will handle the `call_tool` request.
4.  **Run the Server:** You use a runner function (e.g., `mcp.server.stdio.stdio_server`) to start the server and listen for connections.

### Exposing ADK Tools via MCP

A common and powerful pattern is to use an MCP server as a "wrapper" or "adapter" for your existing ADK tools. You can take a `FunctionTool` that you've already built for an ADK agent and expose it to the outside world through an MCP server.

The ADK provides helper utilities to make this easy:
*   `adk_to_mcp_tool_type()`: This function takes an ADK `FunctionTool` and automatically converts its schema into the format required by MCP for the `list_tools` handler.

This allows you to write your core tool logic once and then use it both internally within your ADK agents and expose it externally to any other MCP client, promoting code reuse and interoperability.

In the lab, you will build a simple MCP server that exposes a "shopping cart" tool, learning the fundamentals of implementing the `list_tools` and `call_tool` handlers.
