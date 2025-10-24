# Module 8: Advanced Tool Concepts: Tool Context

## Lab 8: Creating a "Memory" Agent with Tool Context

### Goal

In this lab, you will build an agent that can remember and recall a piece of information using a custom tool. You will learn how to use the `ToolContext` object to read from and write to the session's state, giving your tool "memory."

We will build an agent that can remember the user's name.

### Step 1: Create the Memory Agent Project

1.  **Navigate to your training directory:**

    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Create the agent project:**

    ```shell
    adk create --type=config memory-agent
    ```

3.  **Navigate into the new directory:**

    ```shell
    cd memory-agent
    ```

### Step 2: Write the State-Aware Tool Functions

We will create a Python module with two tools: one to remember the user's name and one to recall it.

1.  **Create the `tools` directory and `__init__.py` file:**

    ```shell
    mkdir tools
    touch tools/__init__.py
    ```

2.  **Create the `memory.py` file:**

    Inside the `tools` directory, create a file named `memory.py`. Add the following code:

    ```python
    from google.adk.tools import ToolContext

    def remember_name(name: str, tool_context: ToolContext) -> dict:
        """
        Remembers the user's name by saving it to the session state.

        Use this tool when the user tells you their name.

        Args:
            name: The user's name to remember.
            tool_context: The context object provided by the ADK.
        
        Returns:
            A dictionary confirming the name was saved.
        """
        # The 'state' object in the tool_context is a dictionary-like object.
        # We can write to it directly.
        tool_context.state['user_name'] = name
        
        return {"status": "success", "message": f"I will remember that your name is {name}."}

    def recall_name(tool_context: ToolContext) -> dict:
        """
        Recalls the user's name from the session state.

        Use this tool when the user asks you what their name is, or if you need
        to address them by name but don't have it in the immediate context.

        Args:
            tool_context: The context object provided by the ADK.

        Returns:
            A dictionary containing the user's name or a message if it's not known.
        """
        # We use .get() to safely access the state, providing a default value.
        user_name = tool_context.state.get('user_name')
        
        if user_name:
            return {"status": "success", "name": user_name}
        else:
            return {"status": "not_found", "message": "I don't believe you've told me your name yet."}

    ```
    **Analysis:**
    *   We import `ToolContext`.
    *   Both functions now include `tool_context: ToolContext` in their signature.
    *   `remember_name` **writes** to `tool_context.state` like a standard Python dictionary.
    *   `recall_name` **reads** from `tool_context.state` using the safe `.get()` method.

### Step 3: Configure the Agent

Now, let's update the agent's configuration to use these new stateful tools.

1.  **Set up your environment variables** in the `.env` file as you've done in previous labs.

2.  **Update the `root_agent.yaml` file:**

    Replace the contents of `root_agent.yaml` with the following:

    ```yaml
    # yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
    name: memory_agent
    model: gemini-2.5-flash
    description: An agent that can remember and recall the user's name.
    instruction: |
      You are a friendly assistant with a memory.
      - If the user tells you their name, you MUST use the `remember_name` tool to save it.
      - If the user asks you what their name is, you MUST use the `recall_name` tool to find it.
      - After recalling a name, address the user by their name.
    tools:
      - name: tools.memory.remember_name
      - name: tools.memory.recall_name
    ```

### Step 4: Test the Memory Agent

1.  **Start the web server:**

    From the `memory-agent` directory, run `adk web`.

2.  **Interact with the agent:**
    *   Open the Dev UI.
    *   **Turn 1: Tell the agent your name.**
        *   **User:** "Hi, my name is Alex."
        *   The agent should respond with something like, "I will remember that your name is Alex."
    *   **Turn 2: Ask the agent for your name.**
        *   **User:** "What is my name?"
        *   The agent should now respond with, "Your name is Alex."
    *   **Examine the Trace and State:**
        *   In the Trace view for the first turn, you'll see the `remember_name` tool being called.
        *   Click on the "State" tab. You will now see a key `user_name` with the value `"Alex"`. This confirms the tool successfully modified the session state.
        *   In the Trace view for the second turn, you'll see the `recall_name` tool being called, and its output containing your name.

### Lab Summary

You have now created a tool with "memory"! This is a critical step towards building more sophisticated, context-aware agents.

You have learned to:
*   Access the `ToolContext` by adding it to a tool function's signature.
*   Write data to the session `state` using `tool_context.state['key'] = value`.
*   Read data from the session `state` using `tool_context.state.get('key')`.
*   Build an agent that can carry information across multiple turns of a conversation.

In the next module, you'll explore how to integrate tools from third-party libraries, further expanding your agent's capabilities.
