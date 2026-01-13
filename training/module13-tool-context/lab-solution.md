---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 13 Solution: Creating a "Memory" Agent with Tool Context

## Goal

This file contains the complete code for the `memory.py` and `agent.py` files in the Memory Agent lab.

### `memory_agent/tools/memory.py`

```python
from google.adk.tools import ToolContext

def remember_name(name: str, tool_context: ToolContext) -> dict:
    """
    Remembers the user's name by saving it to the session state.

    Use this tool when the user tells you their name.

    Args:
        name: The user's name to remember.
    
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

### `memory_agent/agent.py` (Primary Solution)

```python
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

# Import the functions from your tools module
from .tools.memory import remember_name, recall_name

# Create a FunctionTool for each function
remember_tool = FunctionTool(fn=remember_name)
recall_tool = FunctionTool(fn=recall_name)

root_agent = LlmAgent(
    name="memory_agent",
    model="gemini-2.5-flash",
    description="An agent that can remember and recall the user's name.",
    instruction="""
You are a friendly assistant with a memory.
- If the user tells you their name, you MUST use the `remember_name` tool to save it.
- If the user asks you what their name is, you MUST use the `recall_name` tool to find it.
- After recalling a name, address the user by their name.
""",
    tools=[
        remember_tool,
        recall_tool,
    ],
)
```

### `memory_agent/root_agent.yaml` (Alternative)

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

### Self-Reflection Answers

1.  **Why is it important that the `tool_context` parameter is *not* included in the function's docstring?**
    *   **Answer:** The docstring is the "user manual" for the LLM. The LLM only needs to know about the parameters *it* is responsible for providing (like `name`). The `tool_context` is an internal infrastructure object provided by the ADK runtime, not the LLM. Including it in the docstring would confuse the model, leading it to mistakenly try to generate a value for it, which would cause the tool call to fail.

2.  **The `recall_name` function uses `tool_context.state.get('user_name')` instead of `tool_context.state['user_name']`. What is the difference, and why is `.get()` a safer choice here?**
    *   **Answer:** The `state` object behaves like a Python dictionary. If you try to access a key directly (`state['key']`) and that key doesn't exist, Python raises a `KeyError`, crashing your tool. The `.get('key')` method is safer because if the key is missing, it simply returns `None` (or a default value you provide) instead of crashing. Since we can't guarantee the user has already told us their name, `.get()` allows us to handle the "unknown" case gracefully.

3.  **How could you extend this agent to forget a user's name? What would the new tool function look like?**
    *   **Answer:** You would create a `forget_name` function that takes `tool_context` as an argument. Inside, you would use the `pop` method to remove the key from the state.
        ```python
        def forget_name(tool_context: ToolContext) -> dict:
            """Forgets the user's name."""
            if 'user_name' in tool_context.state:
                tool_context.state.pop('user_name')
                return {"status": "success", "message": "I have forgotten your name."}
            return {"status": "error", "message": "I didn't know your name to begin with."}
        ```
