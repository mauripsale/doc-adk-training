# Module 23: Introduction to MCP & Stateful Tools

## Theory

### The Limits of Stateless Tools

The custom function tools you've built so far are powerful, but they have a fundamental limitation: they are **stateless**. Every time your agent calls a tool like `add(a, b)`, the tool executes from scratch, performs its calculation, returns a result, and then forgets everything.

This is perfect for many tasks, but it falls short for more complex, ongoing interactions. Consider these scenarios:

*   **Connecting to a Database:** You wouldn't want to open a new database connection for every single query, run the query, and then immediately close the connection. This is inefficient and slow.
*   **A Multi-Step Booking Wizard:** Imagine booking a flight. The process involves several steps: searching for flights, selecting a seat, entering passenger details, and finally, payment. Each step depends on the previous ones.
*   **Interactive Data Analysis:** An agent might need to load a large dataset, then allow the user to ask multiple questions about it (filter, sort, aggregate) without reloading the data each time.

In all these cases, the tool needs to maintain a **state** across multiple turns of the conversation. It needs its own memory.

### MCP: A Protocol for Stateful, Multi-turn Tools

To solve this problem, the ADK integrates with the **Model Context Protocol (MCP)**. MCP is an open standard designed to allow LLMs and AI agents to have rich, stateful conversations with external tools.

Think of MCP as a specialized language that agents and tools can use to have a more complex dialogue than a simple one-off function call.

### The MCP Architecture: Client and Server

MCP works on a client-server model:

1.  **The MCP Server:** This is a standalone application that exposes a set of stateful tools. For example, you could have an MCP server that knows how to talk to your company's database. It manages the connection and keeps it open.
2.  **The MCP Client:** This is the application that wants to use the tools. In our case, the **ADK agent acts as the MCP client**.

### The `MCPToolset`: Your Agent's Bridge to MCP

The ADK provides a special tool called the `MCPToolset`. This tool acts as the bridge between your ADK agent and an external MCP server.

Here's how it works:

1.  **Connection:** When you add an `MCPToolset` to your agent, you provide it with the connection details for an MCP server (e.g., the command to start a local server or the URL of a remote one).
2.  **Tool Discovery:** The `MCPToolset` connects to the server and asks it, "What tools do you have?"
3.  **Adaptation:** The server responds with a list of its available tools and their schemas. The `MCPToolset` automatically converts these into a format that your ADK agent's LLM can understand.
4.  **Proxying:** To your `LlmAgent`, the MCP tools now look just like any other tool. When the agent decides to use one, it makes a normal function call. The `MCPToolset` intercepts this call, forwards it to the MCP server, waits for the response, and then passes the result back to the agent.

This powerful abstraction means you can connect your agent to complex, stateful, external systems without the agent's core logic needing to know the intricate details of the MCP protocol. It just sees a new set of tools it can use.

In the lab for this module, you will connect your agent to a pre-built MCP server that provides file system tools, allowing your agent to have a stateful interaction with your local files.
