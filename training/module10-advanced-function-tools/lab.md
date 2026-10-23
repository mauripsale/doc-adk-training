---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 10: Stateful Tools & ToolContext — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 10: Building a "Memory" Agent with Stateful Tools

## Goal

In this lab, you will build an agent that can remember a user's name across multiple turns. You will learn how to use the **`ToolContext`** to read from and write to the session state.

### Step 1: Prepare the Project

<Setup/>

1.  **Create the agent project:**
    ```bash
    uv run adk create memory_agent
    cd memory_agent
    ```

2.  **Create the tools package:**
    ```bash
    mkdir tools
    touch tools/__init__.py
    touch tools/memory.py
    ```

### Step 2: Implement Stateful & Sensitive Tools

**Exercise:** Open `tools/memory.py` and implement these three functions:

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

def clear_memory(tool_context: ToolContext) -> str:
    """
    Permanently erases the user's stored name and session memory.
    Use this tool when the user asks to forget them or reset memory.
    """
    # TODO: Remove "user_name" from tool_context.state if present.
    # Return a confirmation string.
    pass
```

### Step 3: Configure the Agent with Tool Confirmation

**Exercise:** Configure `agent.py`. Because `clear_memory` is a destructive action, wrap it inside `FunctionTool` with Human-in-the-Loop confirmation as covered in the Theory section.

```python
# In agent.py
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from .tools.memory import store_name, recall_name, clear_memory

# TODO: Wrap clear_memory using FunctionTool to enforce human confirmation
guarded_clear_tool = ... # Configure FunctionTool with confirmation parameter

root_agent = Agent(
    name="memory_agent",
    model="gemini-3.5-flash",
    description="An agent node that remembers users with guarded memory controls.",
    instruction="""
    You are a friendly assistant. 
    Use 'store_name' if the user introduces themselves.
    Use 'recall_name' if they ask for their name.
    Use 'clear_memory' if they ask you to forget them or erase their data.
    """,
    tools=[store_name, recall_name, guarded_clear_tool]
)
```

### Step 4: Test Memory and Tool Confirmation

1.  **Run:** `uv run adk run .` (run this from inside the `memory_agent` agent directory created in Step 1)
2.  **Test Memory:**
    - "Hi, I'm Mario." -> Should call `store_name`.
    - "What is my name?" -> Should call `recall_name` and respond "Mario".
3.  **Test Human-in-the-Loop Confirmation:**
    - "Please forget my name." -> Should trigger `clear_memory` and request explicit confirmation before executing.
4.  **Inspect:** Open the Dev UI (`uv run adk web`) and check the **State** tab to observe state mutations.

### Lab Summary

You have successfully built an agent with programmable memory and safety governance! You have learned:
*   How to use **`ToolContext`** to access the ADK's session management.
*   How to read and write to **`tool_context.state`**.
*   How to create a **Store and Recall** pattern to maintain context across multiple turns.
*   How to enforce **`require_confirmation`** on sensitive actions with `FunctionTool`.

### Self-Reflection Questions
- Why is it more reliable to store data in the session state rather than just relying on the LLM's chat history?
- What would happen if you used the same key (e.g., "user_name") for two different users? (Hint: The ADK isolates sessions automatically).
- When should you use `require_confirmation=True` vs a conditional predicate function?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="10">

# Lab 10 Solution: Building a "Memory" Agent with Stateful Tools

## Goal

This file contains the complete code for the `agent.py` and `tools/memory.py` files using ADK 2.0 standards for stateful tools and Human-in-the-Loop confirmation.

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

def clear_memory(tool_context: ToolContext) -> str:
    """
    Permanently erases the user's stored name and session memory.
    Use this tool when the user asks to forget them or reset memory.
    """
    tool_context.state.pop("user_name", None)
    return "Your name and session memory have been completely erased."
```

### `memory_agent/agent.py`

```python
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from .tools.memory import store_name, recall_name, clear_memory

# Wrap destructive tool with Human-in-the-Loop confirmation
guarded_clear_tool = FunctionTool(
    func=clear_memory,
    require_confirmation=True
)

root_agent = Agent(
    name="memory_agent",
    model="gemini-3.5-flash",
    description="An agent node that remembers users with guarded memory controls.",
    instruction="""
    You are a friendly assistant. 
    Use 'store_name' if the user introduces themselves.
    Use 'recall_name' if they ask for their name.
    Use 'clear_memory' if they ask you to forget them or erase their data.
    """,
    tools=[
        store_name,
        recall_name,
        guarded_clear_tool
    ]
)
```

### Self-Reflection Answers

1.  **Why is it more reliable to store data in the session state rather than just relying on the LLM's chat history?**
    *   **Answer:** Chat history is "noisy" and has a limited context window. As a conversation gets longer, older messages might be pushed out. Session state is **structured and persistent**; it acts as a reliable "database" for key facts that the agent can access deterministically.

2.  **What would happen if you used the same key (e.g., "user_name") for two different users?**
    *   **Answer:** Nothing bad! The ADK's `Runner` automatically isolates sessions based on the `user_id`. Each user has their own independent `state` dictionary, so Alice's "user_name" will never overwrite Bob's "user_name."

3.  **When should you use `require_confirmation=True` vs a conditional predicate function?**
    *   **Answer:** Use `require_confirmation=True` for unconditionally destructive operations (e.g. `clear_memory`, `delete_database`). Use a conditional predicate when operations are safe below a certain threshold (e.g., refunds < \$50 are automatic, while refunds > \$50 require manager approval).

</SolutionVault>
