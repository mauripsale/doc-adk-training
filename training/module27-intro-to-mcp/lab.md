---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 27: Using a Stateful File System Tool Challenge

## Goal

In this lab, you will learn how to connect your ADK agent to an external, stateful tool using the Model Context Protocol (MCP). You will use the `MCPToolset` to connect to a pre-built, open-source MCP server that provides file system operations. This will allow your agent to list files and read their contents from your local machine.

### Prerequisites

*   **Node.js and npx:** The MCP server we will use is a Node.js package. If you don't have it, install Node.js (which includes npx) from the [official website](https://nodejs.org/).

### Step 1: Create the Agent Project

1.  **Navigate to your training directory:**
    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Create the agent project:**
    ```shell
    adk create mcp_agent
    cd mcp_agent
    ```

### Step 2: Create a Test Directory and File

The MCP file system server needs a directory to operate on. Let's create one.

1.  **Create a directory for the tool to access:**
    Inside your `mcp_agent` project, create a directory named `test_files`.
    ```shell
    mkdir test_files
    ```

2.  **Create a sample file:**
    Inside `test_files`, create a file named `hello.txt`.
    ```shell
    echo "Hello from the MCP world!" > test_files/hello.txt
    ```

### Step 3: Configure the Agent to Use the MCP Toolset

Because the `MCPToolset` requires Python code to configure the connection, we must define our agent in an `agent.py` file.

1.  **Create the `agent.py` file:**
    In the `mcp_agent` directory, create a file named `agent.py`.

2.  **Create the `__init__.py` file:**
    This empty file is crucial. It tells Python to treat the `mcp_agent` directory as a package, allowing `adk web` to discover and load your `agent.py`.
    ```shell
    touch __init__.py
    ```

3.  **Complete the `agent.py` script:**
    **Exercise:** Open `agent.py` and complete the script by following the `# TODO` comments. Your goal is to define an agent and configure the `MCPToolset` to launch and connect to the file system server.

    ```python
    import os
    # TODO: 1. Import the necessary classes:
    # LlmAgent from google.adk.agents
    # MCPToolset from google.adk.tools.mcp_tool.mcp_toolset
    # StdioConnectionParams from google.adk.tools.mcp_tool.mcp_session_manager
    # StdioServerParameters from mcp

    # -- Configuration --
    # TODO: 2. Define the TARGET_FOLDER_PATH.
    # It's good practice to define paths dynamically if possible,
    # or ensure the user understands the need for an ABSOLUTE path.
    # For this example, construct a path relative to this file,
    # assuming 'test_files' is in the same directory as agent.py.
    TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_files/")

    # -- Agent Definition --
    # TODO: 3. Define the root_agent.
    # Instantiate an LlmAgent with the following properties:
    # - model: 'gemini-2.5-flash'
    # - name: 'filesystem_agent'
    # - instruction: 'You are a helpful assistant that can interact with a user\'s local file system. You can list files and read their content.'
    # - tools: A list containing one item: the MCPToolset.
    root_agent = None # Replace this

    # Inside the LlmAgent's `tools` list, you will configure the MCPToolset.
    # Follow this structure:
    #
    # MCPToolset(
    #     connection_params=StdioConnectionParams(
    #         server_params=StdioServerParameters(
    #             # TODO: 4. Set the `command` to 'npx'.
    #             command=...,
    #             # TODO: 5. Set the `args` to a list containing:
    #             # "-y"
    #             # "@modelcontextprotocol/server-filesystem"
    #             # The absolute path to the TARGET_FOLDER_PATH variable you defined above.
    #             args=[...],
    #         ),
    #     ),
    #     # TODO: 6. Optionally, filter specific tools. For this lab, let\'s allow 'list_directory' and 'read_file'.
    #     tool_filter=['list_directory', 'read_file']
    # )
    ```

4.  **Set up your `.env` file** with your API key or Vertex AI project.

### Step 4: Test the Stateful Tool

1.  **Navigate to the parent directory** (`cd ..`) and start the Dev UI:
    ```shell
    adk web
    ```
    When the server starts, you will see output in the console as `npx` downloads and runs the `@modelcontextprotocol/server-filesystem` package.

2.  **Interact with the agent:**
    *   Open the Dev UI in your browser.
    *   Select the `filesystem_agent` from the dropdown.
    *   **Turn 1: List the files.**
        *   **User:** "What files are in my directory?"
        *   **Expected Response:** The agent should respond with a message indicating that it sees `hello.txt`.
    *   **Turn 2: Read the file.**
        *   **User:** "Great, can you read the content of hello.txt for me?"
        *   **Expected Response:** The agent should respond with the content of the file: "Hello from the MCP world!"

3.  **Examine the Trace View:**
    *   In the trace for both turns, you will see `execute_tool` steps for `list_directory` and `read_file`. These tools were **dynamically discovered** by the `MCPToolset`.

### Having Trouble?

If you get stuck, you can find the complete, working code in the `lab-solution.md` file.

### Lab Summary

You have successfully connected your ADK agent to a stateful, external tool using the Model Context Protocol.

You have learned to:
*   Understand the client-server architecture of MCP.
*   Use the `MCPToolset` to connect to an MCP server.
*   Configure the `StdioConnectionParams` to automatically launch a local MCP server process directly within your agent definition.
*   Build an agent that can use tools provided by an external service without having to define them locally.

### Self-Reflection Questions
- The `MCPToolset` dynamically discovers the tools from the server. What are the advantages of this approach compared to manually defining each tool on the agent side?
- The file system server is "stateful" because it remembers the state of the `test_files` directory between tool calls. How does this differ from the stateless calculator tools you built in earlier modules?
- The `StdioConnectionParams` launches the MCP server as a subprocess. What are the security implications of this, and why is it important that the server is sandboxed to a specific `TARGET_FOLDER_PATH`?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMjctaW50cm8tdG8tbWNwL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module27-intro-to-mcp/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
