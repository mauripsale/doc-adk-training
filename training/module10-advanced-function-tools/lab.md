---
sidebar_position: 2
title: "Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 10: Building a "Memory" Agent with Stateful Tools

## Goal

In this lab, you will build an agent that can remember a user's name across multiple turns. You will learn how to use the **`ToolContext`** to read from and write to the session state.

### Step 1: Prepare the Project

<Setup/>

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
from .tools.memory import store_name, recall_name

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

1.  **Run:** `uv run adk run .` (run this from inside the `memory_agent` agent directory created in Step 1; `adk run` expects an agent directory, not a file)
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

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="10">

# Lab 10 Solution: Building a "Memory" Agent with Stateful Tools

## Goal

This file contains the complete code for the `agent.py` and `tools/memory.py` files using ADK 2.0 standards for stateful tools.

### `memory_agent/tools/memory.py`

```python
from google.adk.tools import ToolContext

def store_name(name: str, tool_context: ToolContext) -> str:
    """
    Saves the user's name to the session memory.
    Use this tool when the user tells you their name.
    """
    # Write to session state
    tool_context.state["user_name"] = name
    return f"Got it, {name}! I've saved your name."

def recall_name(tool_context: ToolContext) -> str:
    """
    Retrieves the user's name from the session memory.
    Use this tool if the user asks who they are or what their name is.
    """
    # Read from session state
    name = tool_context.state.get("user_name", "Stranger")
    return f"Your name is {name}."
```

### `memory_agent/agent.py`

```python
from google.adk import Agent
from .tools.memory import store_name, recall_name

root_agent = Agent(
    name="memory_agent",
    model="gemini-3.5-flash",
    description="An agent node that remembers users.",
    instruction="""
    You are a friendly assistant. 
    Use 'store_name' if the user introduces themselves.
    Use 'recall_name' if they ask for their name.
    """,
    tools=[store_name, recall_name]
)
```

### Self-Reflection Answers

1.  **Why is it more reliable to store data in the session state rather than just relying on the LLM's chat history?**
    *   **Answer:** Chat history is "noisy" and has a limited context window. As a conversation gets longer, older messages (like an introduction) might be pushed out. Session state is **structured and persistent**; it acts as a reliable "database" for key facts that the agent can access deterministically.

2.  **What would happen if you used the same key (e.g., "user_name") for two different users?**
    *   **Answer:** Nothing bad! The ADK's `Runner` automatically isolates sessions based on the `user_id`. Each user has their own independent `state` dictionary, so Alice's "user_name" will never overwrite Bob's "user_name."

3.  **How could you extend this agent to remember other things?**
    *   **Answer:** You can create more tools that follow the same pattern (e.g., `store_preference(key, value)`, `recall_preference(key)`). Because `tool_context.state` is just a Python dictionary, you can store any JSON-serializable data there.

</SolutionVault>
