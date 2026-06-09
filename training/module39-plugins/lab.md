---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 39: Fixing a "Hallucinating" Agent with Plugins

## Goal

In this lab, you will work with an agent that has been given misleading instructions. It will try to call a tool by the wrong name. Your task is to use the `ReflectAndRetryToolPlugin` to allow the agent to self-correct and succeed *without* changing the misleading instruction.

### Step 1: Create the Project

1.  **Create a new agent project:**
    ```shell
    uv run adk create retry_agent
    ```
    Choose the **Programmatic (Python script)** option.

2.  **Navigate to the directory:**
    ```shell
    cd retry_agent
    ```

### Step 2: The "Broken" Agent

**Exercise:** Open `agent.py` and replace its content with the code below.

This code defines a tool named `secret_calculator`. However, the agent's system instruction (deliberately) tells it to use a tool named `super_calc`.

```python
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import InMemoryRunner
from google.adk.apps.app import App
from google.genai import types
import asyncio

# The actual tool
def secret_calculator(a: int, b: int) -> int:
    """Adds two numbers."""
    return a + b

# The agent with MISLEADING instructions
root_agent = Agent(
    name="confused_agent",
    model="gemini-3.5-flash",
    # We lie to the agent about the tool name!
    instruction="You are a helper. To add numbers, you MUST use the tool named 'super_calc'. Do not use any other tool name.",
    tools=[FunctionTool(secret_calculator)]
)

async def main():
    # TODO: 1. Import ReflectAndRetryToolPlugin from google.adk.plugins
    
    # TODO: 2. Initialize the plugin here with max_retries=3
    
    # TODO: 3. Create an App instance, passing the root_agent and the plugins list
    app = App(
        name="retry_app",
        root_agent=root_agent,
        # Add your plugin here
    )

    runner = InMemoryRunner(app=app)
    
    print("User: What is 5 + 5?")
    # Running programmatically
    async for event in runner.run_async(
        user_id="test", 
        session_id="1", 
        new_message=types.Content(role="user", parts=[types.Part.from_text(text="What is 5 + 5?")])
    ):
        if event.is_final_response():
            print(f"Agent: {event.content.parts[0].text}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 3: Observe the Failure

1.  **Run the agent:**
    ```shell
    python agent.py
    ```
2.  **Analyze the Output:**
    You should see an error (likely a `ValueError` or `ToolNotFoundError` stack trace, or the agent apologizing that it can't find the tool). This is because the agent tried to call `super_calc`, but only `secret_calculator` is registered.

### Step 4: Add the Safety Net

Now, let's fix this using the Plugin *instead* of fixing the prompt.

1.  **Import the Plugin:**
    Add `from google.adk.plugins import ReflectAndRetryToolPlugin` to your imports.

2.  **Initialize the Plugin:**
    Create an instance of `ReflectAndRetryToolPlugin` with `max_retries=3`.

3.  **Register the Plugin:**
    Update the `App` initialization to include your plugin instance in the `plugins` list.

### Step 5: Verify Success

1.  **Run the agent again:**
    ```shell
    python agent.py
    ```
2.  **Analyze the Output:**
    *   It might take a few seconds longer than usual.
    *   You should now see the correct answer: "Agent: The result is 10" (or similar).
    *   **What happened?** 
        1. Agent called `super_calc`.
        2. System threw "Tool not found".
        3. Plugin caught it and told the Agent: "Error: Tool 'super_calc' not found. Available tools: 'secret_calculator'".
        4. Agent reasoned: "Oops, I should use 'secret_calculator'."
        5. Agent called `secret_calculator`.
        6. Success!

### Self-Reflection Questions
- Why is it better to handle this with a Plugin rather than just fixing the prompt in this specific scenario? (Think about dynamic/unknown errors).
- What would happen if we set `max_retries=0`?
- How does this plugin help with "transient" errors, like a temporary network glitch in a tool?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMzktcGx1Z2lucy9sYWItc29sdXRpb24=`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module39-plugins/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
