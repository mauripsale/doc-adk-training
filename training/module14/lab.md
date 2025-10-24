# Module 14: Managing Conversation State and Memory

## Lab 14: Remembering a User Across Sessions

### Goal

In this lab, you will build on the "Memory" agent from Module 8. You will modify it to use **user-scoped state** (`user:` prefix), allowing the agent to remember a user's name not just for one conversation, but across multiple, separate sessions. This demonstrates the power of persistent, user-level memory.

### Step 1: Create the Agent Project

We will start a new project to keep things clean.

1.  **Navigate to your training directory:**

    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Create the agent project:**

    ```shell
    adk create --type=config persistent-memory-agent
    ```

3.  **Navigate into the new directory:**

    ```shell
    cd persistent-memory-agent
    ```

### Step 2: Create the User-Aware Memory Tool

The tool's code will be very similar to the one from Module 8, but with a critical change: we will add the `user:` prefix to the state key.

1.  **Create the `tools` directory and `__init__.py` file:**

    ```shell
    mkdir tools
    touch tools/__init__.py
    ```

2.  **Create the `user_memory.py` file:**

    Inside the `tools` directory, create a file named `user_memory.py` and add the following code:

    ```python
    from google.adk.tools import ToolContext

    def remember_user_name(name: str, tool_context: ToolContext) -> dict:
        """Saves the user's name to the persistent user state."""
        # By adding the 'user:' prefix, this state is now tied to the user_id.
        tool_context.state['user:name'] = name
        return {"status": "success", "message": f"Got it. I'll remember your name is {name}."}

    def recall_user_name(tool_context: ToolContext) -> dict:
        """Recalls the user's name from the persistent user state."""
        # We read from the same 'user:name' key.
        user_name = tool_context.state.get('user:name')
        
        if user_name:
            return {"status": "success", "name": user_name}
        else:
            return {"status": "not_found", "message": "I don't believe I've learned your name yet."}
    ```

### Step 3: Configure the Agent

Now, let's configure the agent to use these tools and to read the user's name directly in its instruction.

1.  **Set up your `.env` file** with your API key or Vertex AI project.

2.  **Update the `root_agent.yaml` file:**

    Replace the contents of `root_agent.yaml` with the following:

    ```yaml
    # yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
    name: persistent_memory_agent
    model: gemini-1.5-flash
    description: An agent that can remember a user's name across sessions.
    instruction: |
      You are a friendly and personal assistant.
      Your goal is to get to know the user.

      # Use a placeholder with a '?' to handle the case where the name is not yet known.
      Your user's name is {user:name?}.

      - If the user tells you their name, you MUST use the `remember_user_name` tool.
      - If you already know the user's name, greet them by name.
      - If you don't know the user's name, ask them for it.
    tools:
      - name: tools.user_memory.remember_user_name
      - name: tools.user_memory.recall_user_name
    ```
    **Analysis:**
    *   The instruction now includes `{user:name?}`. The `?` makes the placeholder optional; if `user:name` is not in the state, the placeholder will be replaced with an empty string instead of causing an error. This is crucial for the first time a user interacts with the agent.

### Step 4: Test the Persistent Memory

This test will involve two separate sessions to confirm the memory persists.

1.  **Start the web server:** `adk web`

2.  **Interact with the agent - Session 1:**
    *   Open the Dev UI. By default, the UI uses a random session ID for each conversation.
    *   **User:** "Hi there."
    *   **Expected Response:** The agent should notice it doesn't know your name and ask for it (e.g., "Hello! I don't believe we've met. What's your name?").
    *   **User:** "My name is Alex."
    *   **Expected Response:** The agent should use the `remember_user_name` tool and confirm (e.g., "Got it. I'll remember your name is Alex.").
    *   **Check the State:** Go to the "State" tab. You will see the key `user:name` with the value `"Alex"`.

3.  **Interact with the agent - Session 2:**
    *   **Refresh the page.** This will clear the current chat and start a **new session**.
    *   **User:** "Hello again."
    *   **Expected Response:** The agent should now greet you by name! (e.g., "Hello Alex! Welcome back.").
    *   **How it works:** Even though this is a new session, the ADK uses the same default `user_id`. The `SessionService` loads the state associated with that `user_id`, finds the `user:name` key, and injects it into the agent's instruction.

### Lab Summary

You have successfully created an agent with persistent memory! This is a fundamental building block for creating personalized and intelligent assistants.

You have learned to:
*   Use the `user:` prefix to store and retrieve state that is tied to a specific user.
*   Build an agent that can remember information across different conversations.
*   Use the optional `?` syntax in instruction placeholders to handle cases where state may not yet exist.
