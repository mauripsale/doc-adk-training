---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 10: Building a "Memory" Agent with Stateful Tools

## Goal

In this lab, you will build an agent that can remember a user's name across multiple turns. You will learn how to use the **`ToolContext`** to read from and write to the session state.

### Step 1: Prepare the Project

```bash
uv run adk create memory_agent
cd memory_agent
```

### Step 2: Implement Stateful Tools

**Exercise:** Create `tools/memory.py` and implement these two functions.

```python
# In tools/memory.py
from google.adk.tools import ToolContext

def store_name(name: str, tool_context: ToolContext) -> str:
    """
    Saves the user's name to the session memory.
    Use this tool when the user tells you their name.
    """
    # TODO: Save 'name' to tool_context.state under key "user_name"
    pass

def recall_name(tool_context: ToolContext) -> str:
    """
    Retrieves the user's name from the session memory.
    Use this tool if the user asks who they are or what their name is.
    """
    # TODO: Get "user_name" from tool_context.state.
    # Return the name, or "Stranger" if not found.
    pass
```

### Step 3: Configure the Agent

**Exercise:** Configure `agent.py` to use these tools.

```python
# In agent.py
from google.adk import Agent
from tools.memory import store_name, recall_name

root_agent = Agent(
    name="memory_agent",
    model="gemini-3.5-flash",
    instruction="""
    You are a friendly assistant. 
    Use 'store_name' if the user introduces themselves.
    Use 'recall_name' if they ask for their name.
    """,
    tools=[store_name, recall_name]
)
```

### Step 4: Test the Memory

1.  **Run:** `uv run adk run agent.py`
2.  **Test:**
    - "Hi, I'm Mario." -> Should call `store_name`.
    - "What is my name?" -> Should call `recall_name` and respond "Mario".
3.  **Inspect:** Open the Dev UI (`uv run adk web`) and check the **State** tab to see the JSON data.

### Lab Summary

You have successfully built an agent with programmable memory! You have learned:
*   How to use **`ToolContext`** to access the ADK's session management.
*   How to read and write to **`tool_context.state`**.
*   How to create a **Store and Recall** pattern to maintain context across multiple turns.

### Self-Reflection Questions
- Why is it more reliable to store data in the session state rather than just relying on the LLM's chat history?
- What would happen if you used the same key (e.g., "user_name") for two different users? (Hint: The ADK isolates sessions automatically).
- How could you extend this agent to remember other things, like a user's birthday or their favorite color?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMTAtYWR2YW5jZWQtZnVuY3Rpb24tdG9vbHMvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module10-advanced-function-tools/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
