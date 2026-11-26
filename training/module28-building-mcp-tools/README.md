---
sidebar_position: 28
title: "Module 28: Building a Custom MCP Tool"
pagination_label: "Module 28: Building Custom MCP Tools — 📖 Theory & Overview"
---

# Module 28: Building a Custom MCP Tool

## Theory

![Building Custom MCP Tool Providers (Light)](img/hero-light.webp#gh-light-mode-only)
![Building Custom MCP Tool Providers (Dark)](img/hero-dark.webp#gh-dark-mode-only)
*Figure: Developing custom MCP tool providers to expose stateful backend capabilities to the AI ecosystem.*

### Becoming a Tool Provider

In the previous module, you acted as a **consumer** of an MCP tool. Your ADK agent was the client connecting to a pre-built server. Now, we flip the roles. You will become a **provider** by building your own standalone MCP server from scratch.

By exposing your application's capabilities via the Model Context Protocol, you are making them available not just to your own ADK agents, but to *any* MCP-compliant client. It turns your service into a reusable, AI-addressable component in a larger ecosystem.

### The Anatomy of an MCP Server

An MCP server is an application that listens for connections from clients and responds to requests according to the protocol. A server must implement handlers for two fundamental methods:

![MCP Protocol Lifecycle (Light)](img/mcp-protocol-lifecycle-light.webp#gh-light-mode-only)
![MCP Protocol Lifecycle (Dark)](img/mcp-protocol-lifecycle-dark.webp#gh-dark-mode-only)
*Figure: The 2-phase Model Context Protocol lifecycle: Tool Discovery schema negotiation followed by stateful Tool Execution.*

#### 1. `list_tools()`
When a client first connects, it calls `list_tools()`. The server's job is to respond with a "menu" of all the tools it provides. For each tool, it must provide a detailed schema, including:
*   The tool's `name`.
*   A `description` of what it does.
*   An `inputSchema` (JSON Schema) that defines the arguments the tool expects (names, types, required fields).

The client's LLM uses this menu to decide which tool to call.

#### 2. `call_tool()`
Once the client's LLM decides to use a tool, it sends a `call_tool()` request containing the `name` of the tool and a dictionary of `arguments`.

The server's `call_tool()` handler is responsible for:
*   Receiving the request.
*   Executing the corresponding logic for the requested tool.
*   Managing any state the tool needs (e.g., an in-memory shopping cart or a database row).
*   Returning a list of MCP content blocks (such as `mcp_types.TextContent`) to the client.

### Building an MCP Server in Python

The `mcp` Python SDK provides a low-level `Server` class and decorators to wire up protocol handlers directly:

1.  **Install the library (via ADK's compatible extra):** `uv add "google-adk[mcp]"`
2.  **Import the low-level `Server` and protocol types:**
    Note that `Server` is imported from `mcp.server.lowlevel` (not top-level `mcp`):
    ```python
    import sys
    from mcp import types as mcp_types
    from mcp.server.lowlevel import Server, NotificationOptions
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio

    app = Server("my_mcp_server")
    ```
3.  **Implement Handlers with Decorators:** Write `async` functions and register them on `app`:
    *   `@app.list_tools()`: Returns a `list[mcp_types.Tool]` describing every exposed tool and its JSON Schema.
    *   `@app.call_tool()`: Receives `(name: str, arguments: dict)` and returns `list[mcp_types.Content]` (for example, `[mcp_types.TextContent(type="text", text=...)]`).
4.  **Run Over `stdio` Safely (Never Print to `stdout`!):**
    When you start a server with `mcp.server.stdio.stdio_server()`, **standard output (`stdout`) IS the JSON-RPC wire transport** between your server and the ADK client. Calling a plain `print("...")` writes raw text into `stdout`, which corrupts the JSON-RPC stream and causes the MCP client to fail with JSON parse errors! Always send server logs to **`sys.stderr`**:
    ```python
    print("[Server]: Tool called", file=sys.stderr, flush=True)
    ```
    Similarly, when launching a Python MCP server from `StdioServerParameters` on the client side, always pass `command=sys.executable` (rather than a hardcoded `'python3'`) so the subprocess runs inside the exact same `.venv` where `mcp` is installed.

In the lab, you will build a stateful "shopping cart" MCP server and connect an ADK `Agent` to it.

### Why Build an MCP Server?

Building an MCP server decouples your tool's logic from the agent, providing major architectural benefits:
1.  **Independent Scalability:** Scale the agent and the tool server independently.
2.  **Modular Maintenance:** Update tool logic without redeploying the agent.
3.  **Reusability:** Your MCP server can be consumed by *any* MCP-compliant client.
4.  **Workflow Integration:** In ADK 2.0, you can equip any `Agent` node with your custom MCP server across complex graph workflows.

### Going Further: Exposing a Whole Agent as an MCP Tool (Experimental)

This module builds a hand-written MCP server exposing granular tools (`add_item_to_cart`, `view_cart`) — no agent involved on the server side. ADK also offers the opposite direction: `to_mcp_server(agent)` (from `google.adk.tools.mcp_tool`, requires the `[mcp]` extra) wraps an *entire* ADK agent — its model loop and all of its own tools — as a single MCP tool that any MCP host can call, hiding the whole conversation behind one request/response. It is the MCP counterpart of `to_a2a` from Module 21, and is currently marked `@experimental` in ADK's source.

<KnowledgeCheck
  id="m28-stdio-jsonrpc-safety"
  question="Why must a Python MCP server running over mcp.server.stdio.stdio_server() write diagnostic logs to sys.stderr instead of calling standard print()?"
  options={[
    "Because stdio_server() uses stdout exclusively for JSON-RPC protocol frames, so plain print() output corrupts the MCP message stream",
    "Because Python disables stdout automatically inside async context managers",
    "Because ADK's McpToolset deletes any subprocess that writes to stderr",
    "Because mcp_types.TextContent automatically captures stdout instead of return values"
  ]}
  correctIndex={0}
  hint="Consider which file descriptors carry MCP protocol messages when using the stdio transport."
  explanation="Over the stdio transport, the MCP client reads JSON-RPC messages directly from the server subprocess's stdout stream. Writing plain log lines to stdout mixes non-JSON text into the protocol channel and breaks frame parsing, whereas stderr is left free for diagnostic logging."
/>

### Key Takeaways
- A custom Python MCP server uses `from mcp.server.lowlevel import Server` and implements `@app.list_tools()` (discovery) and `@app.call_tool()` (execution).
- Over `stdio_server()`, **`stdout` is reserved strictly for JSON-RPC frames** — always log with `print(..., file=sys.stderr, flush=True)`.
- When spawning a local Python MCP server from ADK via `StdioServerParameters`, use `command=sys.executable` so the child process inherits the active virtual environment's Python interpreter and installed `mcp` package.
- Decoupling stateful tools into standalone MCP servers makes capabilities reusable across any MCP-compliant host or agent framework.
