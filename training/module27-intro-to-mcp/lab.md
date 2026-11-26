---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 27: Introduction to MCP & Stateful Tools — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 27: Using a Stateful File System Tool Challenge

## Goal

In this lab, you will learn how to connect your ADK agent to an external, stateful tool using the Model Context Protocol (MCP). You will use `McpToolset` to connect to a pre-built, open-source MCP server that provides file system operations, allowing your agent to list files and read their contents from a sandboxed local directory.

### Prerequisites

*   **Node.js and npx:** The MCP server we will use is distributed as a Node.js package. If you don't have it installed, install Node.js (which includes `npx`) from the [official website](https://nodejs.org/).

### Step 1: Create the Agent Project

<Setup/>

1.  **Navigate to your `adk-training` workspace directory:**
    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Install the MCP extra:** `mcp` is not part of ADK's base install — installing it via ADK's `[mcp]` extra pins a tested, compatible `mcp` SDK version in your workspace `.venv`:
    ```shell
    uv add "google-adk[mcp]"
    ```

3.  **Scaffold the agent project:**
    ```shell
    uv run adk create mcp_agent
    cd mcp_agent
    ```
    `uv run adk create mcp_agent` generates four files inside `mcp_agent/`:
    *   `__init__.py` (`from . import agent as agent`), which registers `mcp_agent` as a discoverable Python package for `adk web`.
    *   `agent.py`, a starter agent script that you will replace in Step 3.
    *   `.env`, containing the Google AI Studio (`GOOGLE_API_KEY`) or Vertex AI (`GOOGLE_GENAI_USE_ENTERPRISE=1`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`) credentials you selected during the prompt.
    *   `.gitignore`, ensuring `.env` and `.adk/` are excluded from version control.

### Step 2: Create a Sandboxed Test Directory and File

The MCP file system server requires an explicit directory path that acts as its sandbox boundary. Let's create one inside `mcp_agent/`.

1.  **Create a directory for the tool to access:**
    ```shell
    mkdir test_files
    ```

2.  **Create a sample file inside `test_files`:**
    ```shell
    echo "Hello from the MCP world!" > test_files/hello.txt
    ```

### Step 3: Configure the Agent to Use the MCP Toolset

1.  **Verify `__init__.py` and `.env`:**
    Confirm that `adk create` generated both `__init__.py` and `.env` inside `mcp_agent/`:
    ```shell
    ls -la __init__.py .env
    ```

2.  **Complete the `agent.py` script:**
    **Exercise:** Open `mcp_agent/agent.py`, replace the generated template with the starter skeleton below, and complete each `# TODO` section. Refer to the **MCP Connection Types** section in the Theory page if you need a refresher on the exact import paths.

    ```python
    import os
    from google.adk import Agent

    # TODO: 1. Import the required MCP classes:
    # - `McpToolset` and `StdioConnectionParams` from `google.adk.tools.mcp_tool`
    # - `StdioServerParameters` from `mcp`


    # -- Configuration --
    # TODO: 2. Define TARGET_FOLDER_PATH pointing to the `test_files` directory
    # next to this `agent.py` file (use os.path.dirname(os.path.abspath(__file__))).
    TARGET_FOLDER_PATH = ...

    # -- Agent Definition --
    # TODO: 3. Define `root_agent` as an Agent with:
    # - model: 'gemini-3.8-flash'
    # - name: 'filesystem_agent'
    # - instruction: 'You are a helpful assistant that can interact with a user\'s local file system. You can list files and read their content.'
    # - tools: A list containing a configured `McpToolset`.
    #
    # Inside `McpToolset(...)`:
    #   connection_params=StdioConnectionParams(
    #       server_params=StdioServerParameters(
    #           # TODO: 4. Set `command` to 'npx'.
    #           # TODO: 5. Set `args` to ["-y", "@modelcontextprotocol/server-filesystem", os.path.abspath(TARGET_FOLDER_PATH)].
    #           command=...,
    #           args=[...],
    #       ),
    #   ),
    #   # TODO: 6. Restrict exposed tools using `tool_filter` to ['list_directory', 'read_file'].
    #   tool_filter=[...]

    root_agent = ...
    ```

### Step 4: Test the Stateful Tool

1.  **Return to the parent `adk-training` workspace directory** and launch the ADK Dev UI:
    ```shell
    cd ..
    uv run adk web
    ```
    > **Important:** Always launch `uv run adk web` from the parent `adk-training` directory (not from inside `mcp_agent/`), so ADK discovers `mcp_agent` as an agent package and loads `mcp_agent/.env`.

    When the agent runs, `npx` will download and launch `@modelcontextprotocol/server-filesystem` as a local subprocess.
    > **Note:** If your very first request fails with an MCP session initialization timeout while `npx` downloads the package for the first time, simply send the message again — subsequent runs start immediately from your local npm cache.

2.  **Interact with the agent:**
    *   Open `http://127.0.0.1:8000` in your browser.
    *   Select `mcp_agent` from the agent dropdown in the top-left corner.
    *   **Turn 1 — List the files:**
        *   **User:** `"List the files in the directory you have access to."` (Or `"What files are in my directory?"` — if the model asks which path to check, reply `"the allowed directory"` or `"."`.)
        *   **Expected Response:** The agent calls `list_directory` (or `list_allowed_directories` if unfiltered) and reports `hello.txt`.
    *   **Turn 2 — Read the file:**
        *   **User:** `"Great, can you read the content of hello.txt for me?"`
        *   **Expected Response:** The agent calls `read_file` and returns `"Hello from the MCP world!"`.

3.  **Examine the Trace View:**
    *   Inspect the trace for both turns in the Dev UI. Notice the `execute_tool` spans for `list_directory` and `read_file` — tools that were **dynamically discovered** from the external Node.js MCP server via `McpToolset`.

### Having Trouble?

If you get stuck, check the complete reference implementation in `lab-solution.md` or unlock the Solution Vault at the bottom of this page.

### Lab Summary

You have connected an ADK agent to an external, stateful tool server over the Model Context Protocol:
*   Used `McpToolset` to dynamically discover and expose external MCP tools to an ADK `Agent`.
*   Configured `StdioConnectionParams` and `StdioServerParameters` to manage a local MCP server subprocess.
*   Sandboxed filesystem access to an explicit directory (`TARGET_FOLDER_PATH`) and restricted exposed capabilities with `tool_filter`.

### Bonus: Connecting to a Remote MCP Server (`github_agent`)

So far you connected to a *local* MCP server launched as a subprocess (`StdioConnectionParams`). Most production integrations instead connect to a remote MCP server over HTTPS using `StreamableHTTPConnectionParams` — the exact same `McpToolset`, just a different transport.

1.  **Create a GitHub Personal Access Token:** Generate a fine-grained token at [github.com/settings/personal-access-tokens/new](https://github.com/settings/personal-access-tokens/new) with read-only public repository access.

2.  **Scaffold `github_agent` from the parent `adk-training` workspace directory:**
    Make sure you are in `adk-training/` (not inside `mcp_agent/`), then run:
    ```shell
    cd /path/to/your/adk-training
    uv run adk create github_agent
    ```
    Just like before, `uv run adk create github_agent` automatically creates:
    *   `github_agent/__init__.py` (`from . import agent as agent`) so ADK discovers the package.
    *   `github_agent/.env` pre-populated with your Gemini backend configuration (`GOOGLE_API_KEY` or Vertex AI settings).
    *   `github_agent/agent.py` and `github_agent/.gitignore`.

3.  **Add `GITHUB_TOKEN` to `github_agent/.env`:**
    Append your GitHub token to `github_agent/.env` (keeping your existing Gemini credentials intact):
    ```text
    GITHUB_TOKEN=YOUR_GITHUB_TOKEN
    ```

4.  **Replace `github_agent/agent.py`:**
    ```python
    import os
    from google.adk import Agent
    from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

    GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]

    root_agent = Agent(
        model="gemini-3.8-flash",
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

5.  **Launch `adk web` from the parent `adk-training` directory and test it:**
    ```shell
    cd /path/to/your/adk-training
    uv run adk web
    ```
    Select `github_agent` from the Dev UI dropdown and ask: *"What are the open issues on google/adk-python?"* — no `npx`, no subprocess, and no local filesystem exposure; tool calls travel directly over HTTPS to GitHub's hosted MCP server.

Notice what shifts when moving from local `stdio` to remote HTTP: there is no subprocess lifecycle to manage, network failure modes (timeouts, rate limits, expired tokens) must be accounted for, and your primary security boundary moves from *directory sandboxing* to *least-privilege token scoping* (`X-MCP-Readonly: true` and loading `GITHUB_TOKEN` from `github_agent/.env` rather than hardcoding secrets).

### Self-Reflection Questions
- The `McpToolset` dynamically discovers the tools from the server. What are the advantages of this approach compared to manually defining each tool on the agent side?
- The file system server is "stateful" because it remembers the state of the `test_files` directory between tool calls. How does this differ from the stateless calculator tools you built in earlier modules?
- The `StdioConnectionParams` launches the MCP server as a subprocess. What are the security implications of this, and why is it important that the server is sandboxed to a specific `TARGET_FOLDER_PATH`?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="27">

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

</SolutionVault>
