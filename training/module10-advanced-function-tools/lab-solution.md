---
sidebar_position: 3
title: "Lab Solution"
---

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
    model="gemini-3.8-flash",
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
    *   **Answer:** Chat history is "noisy" and has a limited context window. As a conversation gets longer, older messages (like an introduction) might be pushed out. Session state is **structured and persistent**; it acts as a reliable "database" for key facts that the agent can access deterministically.

2.  **What would happen if you used the same key (e.g., "user_name") for two different users?**
    *   **Answer:** Nothing bad! The ADK's `Runner` automatically isolates sessions based on the `user_id`. Each user has their own independent `state` dictionary, so Alice's "user_name" will never overwrite Bob's "user_name."

3.  **When should you use `require_confirmation=True` vs a conditional predicate function?**
    *   **Answer:** Use `require_confirmation=True` for unconditionally destructive operations (e.g. `clear_memory`, `delete_database`). Use a conditional predicate when operations are safe below a certain threshold (e.g., refunds < \$50 are automatic, while refunds > \$50 require manager approval).
