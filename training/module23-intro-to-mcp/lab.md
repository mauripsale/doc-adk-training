# Module 23: Introduction to MCP & Stateful Tools

## Lab 23: Using a Stateful File System Tool

### Goal

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
    adk create --type=config mcp-agent
    cd mcp-agent
    ```

### Step 2: Create a Test Directory and File

The MCP file system server needs a directory to operate on. Let's create one.

1.  **Create a directory for the tool to access:**
    Inside your `mcp-agent` project, create a directory named `test_files`.

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
    In the `mcp-agent` directory, create a file named `agent.py`.

2.  **Add the following code to `agent.py`:**
    This code defines an agent and configures the `MCPToolset` to launch and connect to the file system server.

    ```python
    import os
    from google.adk.agents import LlmAgent
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    # -- Configuration --
    # Get the absolute path to the 'test_files' directory we created.
    # The MCP server needs an absolute path to know where to look.
    TARGET_FOLDER_PATH = os.path.abspath("./test_files")

    # -- Agent Definition --
    root_agent = LlmAgent(
        model='gemini-1.5-flash',
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
                            TARGET_FOLDER_PATH, # The directory it should manage
                        ],
                    ),
                ),
            )
        ],
    )
    ```

3.  **Delete the placeholder `root_agent.yaml`** file, as our agent is now defined in Python.

4.  **Set up your `.env` file** with your API key or Vertex AI project.

### Step 4: Test the Stateful Tool

1.  **Start the web server:**

    ```shell
    adk web
    ```
    When the server starts, you will see some output in the console as `npx` downloads and runs the `@modelcontextprotocol/server-filesystem` package. This is the `MCPToolset` launching the external tool server.

2.  **Interact with the agent:**
    *   Open the Dev UI in your browser.
    *   **Turn 1: List the files.**
        *   **User:** "What files are in my directory?"
        *   **Expected Response:** The agent should respond with a message indicating that it sees `hello.txt`.
    *   **Turn 2: Read the file.**
        *   **User:** "Great, can you read the content of hello.txt for me?"
        *   **Expected Response:** The agent should respond with the content of the file: "Hello from the MCP world!"

3.  **Examine the Trace View:**
    *   In the trace for both turns, you will see `execute_tool` steps.
    *   Expand them. You will see that the agent is calling tools like `list_directory` and `read_file`.
    *   These tools were not defined by you! They were **dynamically discovered** by the `MCPToolset` from the external server and made available to your agent.

### Lab Summary

You have successfully connected your ADK agent to a stateful, external tool using the Model Context Protocol.

You have learned to:
*   Understand the client-server architecture of MCP.
*   Use the `MCPToolset` to connect to an MCP server.
*   Configure the `StdioConnectionParams` to automatically launch a local MCP server process.
*   Build an agent that can use tools provided by an external service without having to define them locally.

This pattern is incredibly powerful for integrating with complex, pre-existing systems that offer an MCP interface. In the next module, you will take the next step and build your own simple MCP server from scratch.
