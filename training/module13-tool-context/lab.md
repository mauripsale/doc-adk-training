---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 13: Creating a "Memory" Agent with Tool Context Challenge

## Goal

In this lab, you will build an agent that can remember and recall a piece of information using a custom tool. You will learn how to use the `ToolContext` object to read from and write to the session's state, giving your tool "memory."

### Step 1: Create the Memory Agent Project

1.  **Create the agent project:**
    ```shell
    adk create memory_agent
    cd memory_agent
    ```

2.  **Create the tools module:**
    ```shell
    mkdir tools
    touch tools/__init__.py
    touch tools/memory.py
    ```

### Step 2: Write the State-Aware Tool Functions

**Exercise:** Open `tools/memory.py`. A skeleton with two functions is provided. Your task is to implement the logic for each function using the `tool_context` to manage the agent's memory.

```python
# In tools/memory.py (Starter Code)

from google.adk.tools import ToolContext

def remember_name(name: str, tool_context: ToolContext) -> dict:
    """
    Remembers the user's name by saving it to the session state.
    Use this tool when the user tells you their name.
    Args:
        name: The user's name to remember.
    """
    # Note: Do not describe the 'tool_context' parameter in the docstring.
    # The LLM does not need to know about it.
    
    # TODO: Use the tool_context to save the user's `name` to the
    # session state under the key 'user_name'.
    
    return {"status": "success", "message": f"I will remember that your name is {name}."}

def recall_name(tool_context: ToolContext) -> dict:
    """
    Recalls the user's name from the session state.
    Use this tool when the user asks you what their name is.
    """
    # TODO: Use the tool_context to get the 'user_name' from the state.
    # If the name exists, return it in a success dictionary:
    # {"status": "success", "name": user_name}
    # If it doesn't exist, return a "not_found" status:
    # {"status": "not_found", "message": "I don't believe you've told me your name yet."}
    pass
```

### Step 3: Configure the Agent in `agent.py`

**Exercise:** Open `agent.py` and configure the agent to use your new tools.

```python
# In agent.py
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

# TODO: Import the `remember_name` and `recall_name` functions from your tools.memory module.

# TODO: Create a FunctionTool for each of your imported functions.

root_agent = LlmAgent(
    name="memory_agent",
    model="gemini-2.5-flash",
    description="An agent that can remember and recall the user's name.",
    instruction="""
# TODO: Write an instruction that tells the agent:
# - To use the `remember_name` tool when the user provides their name.
# - To use the `recall_name` tool when the user asks what their name is.
""",
    # TODO: Add the two FunctionTool objects you created to this list.
    tools=[]
)
```

### Step 4: Test the Memory Agent

1.  **Set up your `.env` file.**
2.  **Navigate to the parent directory** (`cd ..`) and start the Dev UI:
    ```shell
    adk web
    ```
3.  **Interact with the agent:**
    *   **Turn 1:** "Hi, my name is Alex."
    *   **Turn 2:** "What is my name?"
4.  **Examine the Trace and State:**
    *   After the first turn, check the **State** tab to see if `user_name` was saved correctly.
    *   Check the **Trace** view for both turns to see the `remember_name` and `recall_name` tools being called.

### Having Trouble?

If you get stuck, you can find the complete, working code in the `lab-solution.md` file.

### Lab Summary

You have now created a tool with "memory"! You have learned to:
*   Access the `ToolContext` by adding it to a tool function's signature.
*   Write data to the session `state` using `tool_context.state['key'] = value`.
*   Read data from the session `state` using `tool_context.state.get('key')`.
*   Build an agent that can carry information across multiple turns of a conversation.

### Self-Reflection Questions
- Why is it important that the `tool_context` parameter is *not* included in the function's docstring?
- The `recall_name` function uses `tool_context.state.get('user_name')` instead of `tool_context.state['user_name']`. What is the difference, and why is `.get()` a safer choice here?
- How could you extend this agent to forget a user's name? What would the new tool function look like?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMTMtdG9vbC1jb250ZXh0L2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module13-tool-context/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
