# Module 22: Intercepting Execution with Callbacks

## Lab 22: Logging Tool Calls with a Callback

### Goal

In this lab, you will learn how to use a callback for observation. You will take the "Calculator" agent from Module 7 and add a `before_tool_callback` to it. This callback will print a log message to the console every time the agent is about to use one of its calculator tools, showing which tool is being called and with what arguments.

### Step 1: Prepare the Agent Project

1.  **Navigate to your training directory:**

    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Copy the Calculator Agent project:**
    We'll make a fresh copy to work with.

    ```shell
    cp -r module07-custom-function-tools/calculator-agent/ callback-calculator/
    cd callback-calculator/
    ```

### Step 2: Define and Register the Callback Function

Since callbacks are Python functions, we need to define our agent in a Python script (`agent.py`) rather than a YAML file.

1.  **Create the `agent.py` file:**
    Inside the `callback-calculator` directory, create a new file named `agent.py`.

2.  **Add the following code to `agent.py`:**

    ```python
    import json
    from google.adk.agents import LlmAgent, ToolCallbackContext

    # --- 1. Define the Callback Function ---
    # A callback function receives a special context object.
    # For tool callbacks, it's a ToolCallbackContext.
    def log_tool_call(context: ToolCallbackContext):
        """
        This function will be called before any tool is executed.
        """
        tool_name = context.tool_name
        tool_args = context.tool_args

        # We'll print a structured log message to the console.
        print("\n--- [CALLBACK LOG] ---")
        print(f"Agent is about to call tool: {tool_name}")
        print(f"With arguments: {json.dumps(tool_args, indent=2)}")
        print("----------------------\n")
        
        # By returning None, we tell the ADK to proceed with the normal execution.
        return None

    # --- 2. Define the Agent in Python ---
    # We are programmatically defining the same agent that was in root_agent.yaml
    root_agent = LlmAgent(
        name="calculator_agent",
        model="gemini-1.5-flash",
        description="An agent that can perform basic arithmetic calculations.",
        instruction="""You are a helpful calculator assistant.
    When the user asks you to perform a calculation (add, subtract, multiply, or divide), you MUST use the appropriate tool.
    Clearly state the result of the calculation to the user.
    If the user asks a question that is not a calculation, politely state that you can only perform math.""",
        
        # --- 3. Register the Tools and the Callback ---
        # The tool names are strings that point to the functions.
        tools=[
            "tools.calculator.add",
            "tools.calculator.subtract",
            "tools.calculator.multiply",
            "tools.calculator.divide"
        ],
        # We register our function for the 'before_tool_callback' event.
        before_tool_callback=log_tool_call
    )
    ```

3.  **Delete the old YAML file:**
    Since the agent is now defined in `agent.py`, we no longer need `root_agent.yaml`.

    ```shell
    rm root_agent.yaml
    ```

### Step 3: Test the Callback

1.  **Ensure your environment is set up:**
    *   Make sure your virtual environment is active.
    *   Make sure your `.env` file is correctly configured.

2.  **Start the web server:**
    The `adk web` command will automatically find the `root_agent` object in your `agent.py` file.

    ```shell
    adk web
    ```

3.  **Interact with the agent:**
    *   Open the Dev UI in your browser.
    *   Ask the agent a question that will trigger a tool call: "What is 25 * 8?"

4.  **Check the Console Logs:**
    *   Go back to the terminal where you are running `adk web`.
    *   You will see the normal server logs, but in addition, you will see the output from our callback function printed directly to the console!

    ```
    --- [CALLBACK LOG] ---
    Agent is about to call tool: tools.calculator.multiply
    With arguments: {
      "a": 25,
      "b": 8
    }
    ----------------------
    ```
    This confirms that your callback was successfully registered and executed by the ADK framework before the `multiply` tool was run.

### Lab Summary

You have successfully implemented a callback to add custom logging to your agent. This is a fundamental pattern for observing and debugging agent behavior.

You have learned to:
*   Define a callback function that accepts a context object (e.g., `ToolCallbackContext`).
*   Access information about the agent's execution from the context object (like `tool_name` and `tool_args`).
*   Register a callback function with an agent when defining it programmatically.
*   Use a callback for observation (logging) by having it return `None`.

This opens up a world of possibilities for adding custom logic, validation, and integrations at any point in your agent's lifecycle.
