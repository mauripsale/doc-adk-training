---
sidebar_position: 2
title: "Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 27: Using a Stateful File System Tool Challenge

## Goal

In this lab, you will learn how to connect your ADK agent to an external, stateful tool using the Model Context Protocol (MCP). You will use the `McpToolset` to connect to a pre-built, open-source MCP server that provides file system operations. This will allow your agent to list files and read their contents from your local machine.

### Prerequisites

*   **Node.js and npx:** The MCP server we will use is a Node.js package. If you don't have it, install Node.js (which includes npx) from the [official website](https://nodejs.org/).

### Step 1: Create the Agent Project

<Setup/>

1.  **Navigate to your training directory:**
    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Create the agent project:**
    ```shell
    uv run adk create mcp_agent
    cd mcp_agent
    ```

3.  **Install the MCP extra.** `mcp` is not part of ADK's base install — it only comes in via ADK's `[mcp]` extra, which pins a compatible version:
    ```shell
    uv add "google-adk[mcp]"
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

Because the `McpToolset` requires Python code to configure the connection, we must define our agent in an `agent.py` file.

1.  **Create the `agent.py` file:**
    In the `mcp_agent` directory, create a file named `agent.py`.

2.  **Create the `__init__.py` file:**
    This empty file is crucial. It tells Python to treat the `mcp_agent` directory as a package, allowing `uv run adk web` to discover and load your `agent.py`.
    ```shell
    touch __init__.py
    ```

3.  **Complete the `agent.py` script:**
    **Exercise:** Open `agent.py` and complete the script by following the `# TODO` comments. Your goal is to define an agent and configure the `McpToolset` to launch and connect to the file system server.

    ```python
    import os
    # TODO: 1. Import the necessary classes:
    from google.adk import Agent
    from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    # -- Configuration --
    # TODO: 2. Define the TARGET_FOLDER_PATH.
    TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_files/")

    # -- Agent Definition --
    # TODO: 3. Define the root_agent.
    # Instantiate an Agent with the following properties:
    # - model: 'gemini-3.5-flash'
    # - name: 'filesystem_agent'
    # - instruction: 'You are a helpful assistant that can interact with a user\'s local file system. You can list files and read their content.'
    # - tools: A list containing one item: the McpToolset.
    
    # Inside the Agent's `tools` list, you will configure the McpToolset.
    # Follow this structure:
    #
    # McpToolset(
    #     connection_params=StdioConnectionParams(
    #         server_params=StdioServerParameters(
    #             # TODO: 4. Set the `command` to 'npx'.
    #             # TODO: 5. Set the `args` to a list containing:
    #             # "-y", "@modelcontextprotocol/server-filesystem", absolute path to TARGET_FOLDER_PATH
    #             command=...,
    #             args=[...],
    #         ),
    #     ),
    #     # TODO: 6. Optionally, filter specific tools: 'list_directory' and 'read_file'.
    #     tool_filter=[...]
    # )

    root_agent = ...
    ```

4.  **Set up your `.env` file** with your API key or Agent Platform project.

### Step 4: Test the Stateful Tool

1.  **Navigate to the parent directory** (`cd ..`) and start the Dev UI:
    ```shell
    uv run adk web
    ```
    When the server starts, you will see output in the console as `npx` downloads and runs the `@modelcontextprotocol/server-filesystem` package.

    > **Note:** if your very first request fails with an MCP session timeout, this is likely `npx` downloading the server package for the first time. Simply retry — it will be fast on every subsequent run since the package stays cached locally.

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
    *   In the trace for both turns, you will see `execute_tool` steps for `list_directory` and `read_file`. These tools were **dynamically discovered** by the `McpToolset`.

### Having Trouble?

If you get stuck, you can find the complete, working code in the `lab-solution.md` file.

### Lab Summary

You have successfully connected your ADK agent to a stateful, external tool using the Model Context Protocol.

You have learned to:
*   Understand the client-server architecture of MCP.
*   Use the `McpToolset` to connect to an MCP server.
*   Configure the `StdioConnectionParams` to automatically launch a local MCP server process directly within your agent definition.
*   Build an agent that can use tools provided by an external service without having to define them locally.

### Bonus: Connecting to a Remote MCP Server

So far you connected to a *local* MCP server launched as a subprocess (`StdioConnectionParams`). Most real-world integrations instead connect to a server already running somewhere else over HTTP, using `StreamableHTTPConnectionParams` — same `McpToolset`, different transport.

1.  **Get a free GitHub Personal Access Token:** create one at [github.com/settings/personal-access-tokens/new](https://github.com/settings/personal-access-tokens/new) with read-only repository access.

2.  **Set it as an environment variable** in your `.env` file:
    ```text
    GITHUB_TOKEN=YOUR_GITHUB_TOKEN
    ```

3.  **Create a second agent** (e.g. `github_agent/agent.py`):
    ```python
    import os
    from google.adk import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

    GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]

    root_agent = Agent(
        model="gemini-3.5-flash",
        name="github_agent",
        instruction="Help users get information from GitHub repositories.",
        tools=[
            McpToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url="https://api.githubcopilot.com/mcp/",
                    headers={
                        "Authorization": f"Bearer {GITHUB_TOKEN}",
                        "X-MCP-Readonly": "true",
                    },
                ),
            )
        ],
    )
    ```

4.  **Try it:** ask "What are the open issues on google/adk-python?" — no `npx`, no subprocess, no local sandboxing: the tool call goes straight over HTTPS to GitHub's servers.

A few things change when the server is remote instead of local: there's no subprocess lifecycle to manage (the server runs independently of your agent), network failures (timeouts, rate limits, an expired token) become a real possibility that a local stdio server never has, and the security surface shifts from "the subprocess has filesystem access" to "don't hardcode the credential in your header" — which is why the token above comes from `.env`, not a literal string.

### Self-Reflection Questions
- The `McpToolset` dynamically discovers the tools from the server. What are the advantages of this approach compared to manually defining each tool on the agent side?
- The file system server is "stateful" because it remembers the state of the `test_files` directory between tool calls. How does this differ from the stateless calculator tools you built in earlier modules?
- The `StdioConnectionParams` launches the MCP server as a subprocess. What are the security implications of this, and why is it important that the server is sandboxed to a specific `TARGET_FOLDER_PATH`?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMjctaW50cm8tdG8tbWNwL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module27-intro-to-mcp/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
