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
|   ADK Agent     |----->|    MCPToolset        |----->|     MCP Server     |
| (MCP Client)    |      | (ADK Wrapper/Client) |      | (e.g., Filesystem) |
+-----------------+      +----------------------+      +--------------------+
```

The `MCPToolset` is the bridge. It connects to an MCP server, discovers the tools it offers, and makes them available to your agent. When your agent decides to use one of these tools, the `MCPToolset` proxies the call to the server, which executes the logic and maintains the state.

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
- This architecture allows you to leverage a growing ecosystem of pre-built, community-maintained MCP tools for common tasks like filesystem and database access.
- The `StdioConnectionParams` are used to connect to an MCP server running as a local subprocess, which is ideal for development.
- **Security and Sandboxing:** Launching an MCP server as a subprocess (e.g., via `StdioConnectionParams`) has security implications, as it grants the external code operational freedom on the host system. This is why **sandboxing** is critical. By restricting the server's access to a specific, sandboxed directory (the `TARGET_FOLDER_PATH`), you ensure that even if the server were compromised, it could not access or modify files outside of its designated area. This is a fundamental security practice for running external processes in a production environment.
- **Stateful vs. Stateless Tools:** Unlike the stateless calculator tools from previous modules (where each call is an independent transaction), MCP tools are often stateful. The MCP server maintains the state of the external system (e.g., the filesystem). This means that an action taken in one turn (like `write_file`) persists and affects the outcome of subsequent actions in later turns (like `read_file`), enabling more complex, multi-turn interactions.
- **Advantage of Dynamic Discovery:** The MCP's "plug-and-play" nature, where tools are dynamically discovered from the server, offers significant advantages over manual tool definition. It reduces maintenance, as changes to the server's tools are automatically reflected in the agent without requiring code changes. It also promotes a clean separation of concerns, where the tool's logic is completely decoupled from the agent's reasoning logic, and enhances reusability, as the same agent can connect to different MCP servers with minimal modification.