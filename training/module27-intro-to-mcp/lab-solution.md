---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 27 Solution: Using a Stateful File System Tool

## Goal

This file contains the complete code for the `mcp_agent/agent.py` script in the Stateful File System Tool lab, aligned with running `uv run adk web` from the parent `adk-training` workspace directory.

### `mcp_agent/agent.py`

```python
import os  # Required for path operations
from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

# -- Configuration --
# Define the sandboxed folder dynamically relative to this agent.py file
# so it resolves to an absolute path even when `uv run adk web` is launched
# from the parent `adk-training` directory.
TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_files")

# -- Agent Definition --
root_agent = Agent(
    model='gemini-3.8-flash',
    name='filesystem_agent',
    instruction='You are a helpful assistant that can interact with a user\'s local file system. You can list files and read their content.',
    tools=[
        # Bridge to the external MCP server subprocess.
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='npx',
                    args=[
                        "-y",  # Auto-confirm 'npx' package execution
                        "@modelcontextprotocol/server-filesystem",
                        # IMPORTANT: Must be an absolute path to the sandbox folder.
                        os.path.abspath(TARGET_FOLDER_PATH),
                    ],
                ),
            ),
            # Restrict exposed tools to read-only directory listing and file reading.
            tool_filter=['list_directory', 'read_file'],
        )
    ],
)
```

### `mcp_agent/__init__.py`

Generated automatically by `uv run adk create mcp_agent` (`from . import agent as agent`), enabling ADK to discover `mcp_agent` when `uv run adk web` runs from the parent `adk-training` directory.

### Self-Reflection Answers

1.  **The `McpToolset` dynamically discovers the tools from the server. What are the advantages of this approach compared to manually defining each tool on the agent side?**
    *   **Answer:** Dynamic discovery reduces boilerplate code and improves maintainability. You don't need to update your agent's code every time the MCP server adds, removes, or modifies a tool. It promotes a clean separation of concerns: the MCP server is responsible for defining its capabilities, and the agent client simply consumes them. This makes the system more flexible and scalable.

2.  **The file system server is "stateful" because it remembers the state of the `test_files` directory between tool calls. How does this differ from the stateless calculator tools you built in earlier modules?**
    *   **Answer:** Stateless tools (like the calculator functions) execute, return a result, and retain no memory of previous calls. Each invocation is entirely independent. A stateful tool, like the filesystem server, maintains an internal or external state across turns. Actions in one turn directly affect subsequent calls in later turns, enabling richer multi-turn workflows with external systems.

3.  **The `StdioConnectionParams` launches the MCP server as a subprocess. What are the security implications of this, and why is it important that the server is sandboxed to a specific `TARGET_FOLDER_PATH`?**
    *   **Answer:** Launching any external process, especially one that can interact with the file system, introduces significant security risks. If the MCP server or prompt input were abused without boundaries, it could read or modify sensitive host files (like `.env` or SSH keys). Sandboxing the server to `TARGET_FOLDER_PATH` and filtering exposed tools via `tool_filter` restricts operations strictly to that designated directory and read-only actions, minimizing the blast radius.
