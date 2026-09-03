---
sidebar_position: 10
title: "Module 10: Stateful Tools & ToolContext"
---

# Module 10: Stateful Tools & ToolContext

## Theory

### Beyond Stateless Functions

In the previous module, you built stateless tools: they take an input and return an immediate result. However, many real-world agents need **memory**. They need tools that can "remember" a user's preference or use data gathered in a previous turn.

In ADK 2.0, you achieve this using the **`ToolContext`**.

### 1. The `ToolContext` Object

By adding a parameter typed as `ToolContext` to your function, the ADK automatically injects the current execution context. The LLM does **not** see this parameter in the tool schema.

```python
from google.adk.tools import ToolContext

def remember_info(data: str, tool_context: ToolContext):
    # This parameter is invisible to the model!
    ...
```

### 2. State Management (`tool_context.state`)

This is the most powerful feature of the context. It gives your tool direct read/write access to the current conversation's state.

*   **Writing to State:** Save information to be used later.
    ```python
    tool_context.state["user_name"] = "Alice"
    ```
*   **Reading from State:** Make decisions based on historical data.
    ```python
    name = tool_context.state.get("user_name", "Stranger")
    ```

### The "Memory" Pattern

The most common use case for stateful tools is a **Store and Recall** pair:
1.  **Store Tool:** Takes user input and saves it to a specific key in `tool_context.state`.
2.  **Recall Tool:** Reads that key from the state and returns it to the agent.

This allows the agent to maintain a "structured memory" that is more reliable than just relying on the raw chat history.

### Key Takeaways
- Use **`ToolContext`** to securely access the ADK runtime.
- **`tool_context.state`** allows tools to persist data across turns.
- Stateful tools enable agents to have a structured, programmable memory.
- **Rule:** Never describe `tool_context` in your docstring; it's for the framework, not the LLM.