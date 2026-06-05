---
sidebar_position: 27
title: "Module 27: Introduction to MCP & Stateful Tools"
---

# Module 27: Introduction to MCP & Stateful Tools

## Theory

### The Limits of Stateless Tools

The custom function tools you've built so far are powerful, but they have a fundamental limitation: they are **stateless**. Every time your agent calls a tool like `add(a, b)`, the tool executes from scratch, performs its calculation, returns a result, and then forgets everything.

This is perfect for many tasks, but it falls short for more complex, ongoing interactions where a tool needs to maintain its own memory or state across multiple turns of a conversation (e.g., managing a database connection, a multi-step booking process, or an interactive data analysis session).

### MCP: A Protocol for Stateful, Multi-turn Tools

To solve this problem, the ADK integrates with the **Model Context Protocol (MCP)**. MCP is an open standard designed to allow AI agents to have rich, stateful conversations with external tools. Instead of writing custom integrations for every service, you can connect to pre-built MCP servers from the community.

**Benefits**:

*   🔌 **Plug-and-Play**: Instantly connect to existing MCP servers for filesystems, databases, and popular APIs.
*   🌐 **Community Ecosystem**: Leverage a growing library of community-built tools.
*   🧩 **Standardized Interface**: Interact with all external tools through a consistent API.
*   🚀 **Extensible**: Build your own custom servers to expose proprietary systems to your agents.

### The MCP Architecture: Client and Server

MCP works on a client-server model:

1.  **The MCP Server:** A standalone application that exposes a set of stateful tools (e.g., a server that manages a filesystem).
2.  **The MCP Client:** The application that wants to use the tools. In our case, the **ADK agent acts as the MCP client**.

```text
+-----------------+      +----------------------+      +--------------------+
|   Agent Node    |----->|    MCPToolset        |----->|     MCP Server     |
|  (MCP Client)   |      | (ADK Wrapper/Client) |      | (e.g., Filesystem) |
+-----------------+      +----------------------+      +--------------------+
```

The `MCPToolset` is the bridge. It connects to an MCP server, discovers the tools it offers, and makes them available to your agent node. When your agent decides to use one of these tools, the `MCPToolset` proxies the call to the server, which executes the logic and maintains the state.

### MCP Connection Types

The ADK supports several ways to connect to an MCP server:

*   **`StdioConnectionParams`**: For running an MCP server as a local subprocess and communicating over standard input/output. This is the most common method for local development.
*   **`SseConnectionParams`**: For connecting to a remote server that uses Server-Sent Events (SSE) for real-time, streaming communication.
*   **`StreamableHTTPConnectionParams`**: For connecting to a remote server that supports bidirectional streaming over HTTP.

In the lab, you will use the `Stdio` connection to run a local filesystem server and give your agent the ability to interact with your files.

### Key Takeaways
- Standard function tools are **stateless**, which limits their ability to handle ongoing, multi-turn interactions.
- The **Model Context Protocol (MCP)** is an open standard that enables agents to connect to **stateful** external tools.
- The ADK acts as an MCP client, using the `MCPToolset` to connect to and consume tools from an MCP server.
- **Workflow Integration:** In ADK 2.0, an `Agent` node equipped with an `MCPToolset` becomes a powerful interface to external systems within your graph.
- **Security and Sandboxing:** Launching an MCP server as a subprocess (e.g., via `StdioConnectionParams`) grants the external code operational freedom. Always **sandbox** the server to a specific directory to minimize risk.