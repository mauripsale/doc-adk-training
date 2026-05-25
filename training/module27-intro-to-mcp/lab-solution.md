---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 27 Solution: Using a Stateful File System Tool

## Goal

This file contains the complete code for the `agent.py` script in the Stateful File System Tool lab, aligned with the standard `adk web` workflow.

### `mcp_agent/agent.py`

```python
import os # Required for path operations
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# -- Configuration --
# It's good practice to define paths dynamically if possible,
# or ensure the user understands the need for an ABSOLUTE path.
# For this example, we'll construct a path relative to this file,
# assuming 'test_files' is in the same directory as agent.py.
TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_files/")

# -- Agent Definition --
root_agent = LlmAgent(
    model='gemini-3.5-flash',
    name='filesystem_agent',
    instruction='You are a helpful assistant that can interact with a user\'s local file system. You can list files and read their content.',
    tools=[
        # This is the bridge to the external MCP server.
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    # The command to run the MCP server.
                    command='npx',
                    # Arguments for the command.
                    args=[
                        "-y",  # Auto-confirm 'npx' installation
                        "@modelcontextprotocol/server-filesystem", # The server package
                        # IMPORTANT: This MUST be an ABSOLUTE path to a folder the
                        # npx process can access.
                        os.path.abspath(TARGET_FOLDER_PATH), # The directory it should manage
                    ],
                ),
            ),
            # Optional: Filter which tools from the MCP server are exposed
            tool_filter=['list_directory', 'read_file']
        )
    ],
)
```

### `mcp_agent/__init__.py`

This file should be created and can be left empty. It is required for the ADK to discover the `agent.py` file as a Python module.

### Self-Reflection Answers

1.  **The `MCPToolset` dynamically discovers the tools from the server. What are the advantages of this approach compared to manually defining each tool on the agent side?**
    *   **Answer:** Dynamic discovery reduces boilerplate code and improves maintainability. You don't need to update your agent's code every time the MCP server adds, removes, or modifies a tool. It promotes a clean separation of concerns: the MCP server is responsible for defining its capabilities, and the agent client simply consumes them. This makes the system more flexible and scalable.

2.  **The file system server is "stateful" because it remembers the state of the `test_files` directory between tool calls. How does this differ from the stateless calculator tools you built in earlier modules?**
    *   **Answer:** Stateless tools (like the calculator functions) execute, return a result, and retain no memory of previous calls. Each invocation is entirely independent. A stateful tool, like the filesystem server, maintains an internal state (the actual files and directories on disk). Actions like `write_file` in one turn directly affect subsequent calls like `read_file` or `list_directory` in later turns. This persistence of external state is what allows for more complex, multi-turn interactions with external systems.

3.  **The `StdioConnectionParams` launches the MCP server as a subprocess. What are the security implications of this, and why is it important that the server is sandboxed to a specific `TARGET_FOLDER_PATH`?**
    *   **Answer:** Launching any external process, especially one that can interact with the file system, introduces significant security risks. If the MCP server itself (or its dependencies) were compromised or had a vulnerability, it could potentially gain access to the entire host system. Sandboxing the server to a `TARGET_FOLDER_PATH` is critical because it acts as a security boundary. It restricts the server's operations to *only* that specific directory, preventing it from reading, writing, or deleting files outside of its designated area. This minimizes the "blast radius" of any potential exploit and is a fundamental security practice for running external tools in a production environment.
