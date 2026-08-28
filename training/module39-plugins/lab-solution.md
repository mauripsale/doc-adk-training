---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 39 Solution: Fixing a "Hallucinating" Agent with Plugins

## Goal

This solution demonstrates how to use the `ReflectAndRetryToolPlugin` to automatically recover from tool usage errors (like incorrect tool names) without modifying the agent's prompt code.

### `retry_agent/agent.py`

```python
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import InMemoryRunner
from google.adk.apps.app import App
from google.adk.plugins import ReflectAndRetryToolPlugin  # 1. Import
from google.genai import types
from dotenv import load_dotenv
import asyncio

load_dotenv()

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
    # 2. Configure the Plugin
    # We give the agent 3 chances to realize its mistake and try the correct tool name.
    retry_plugin = ReflectAndRetryToolPlugin(max_retries=3)
    
    # 3. Register the Plugin on the App
    app = App(
        name="retry_app",
        root_agent=root_agent,
        plugins=[retry_plugin]
    )

    runner = InMemoryRunner(app=app)

    # /run_async requires a session that already exists.
    await runner.session_service.create_session(app_name=app.name, user_id="test", session_id="1")

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

### Self-Reflection Answers

1.  **Why is it better to handle this with a Plugin rather than just fixing the prompt in this specific scenario?**
    *   **Answer:** While fixing the prompt is ideal for *known* errors, the Plugin protects against *unknown* or *dynamic* errors. For example, if you have hundreds of tools, the model might occasionally hallucinate a name even with a perfect prompt. Or, the tool arguments might be slightly wrong (e.g., passing a string instead of an int). The Plugin provides a universal safety net for *all* tools and *all* types of execution errors, making the system robust against the inherent unpredictability of LLMs.

2.  **What would happen if we set `max_retries=0`?**
    *   **Answer:** The plugin would be effectively disabled. When the agent calls `super_calc`, the exception would propagate immediately, crashing the application (or returning an error to the user) without giving the agent a chance to correct itself.

3.  **How does this plugin help with "transient" errors, like a temporary network glitch in a tool?**
    *   **Answer:** If a tool fails due to a network glitch (e.g., raising a `ConnectionError`), the plugin catches it. It feeds the error ("Connection failed") back to the agent. The agent, seeing this, will likely decide to "try again" (retry the same tool call). If the glitch was temporary, the second attempt might succeed. This adds automatic resilience to your tools.
