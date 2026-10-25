---
sidebar_position: 10
title: "Module 10: Stateful Tools & ToolContext"
pagination_label: "Module 10: Stateful Tools & ToolContext — 📖 Theory & Overview"
---

# Module 10: Stateful Tools & ToolContext

![Advanced Function Tools & Robust Execution (Light)](img/hero-advanced-tools-light.webp#gh-light-mode-only)
![Advanced Function Tools & Robust Execution (Dark)](img/hero-advanced-tools-dark.webp#gh-dark-mode-only)

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

![Tool Validation and Error Recovery Pipeline (Light)](img/arch-error-recovery-pipeline-light.webp#gh-light-mode-only)
![Tool Validation and Error Recovery Pipeline (Dark)](img/arch-error-recovery-pipeline-dark.webp#gh-dark-mode-only)
*Figure: The tool validation, exception interceptor, and adaptive recovery pipeline for robust function execution.*

### 3. Human-in-the-Loop: Tool Confirmation

In production systems, some tool actions are **irreversible or sensitive** (e.g., deleting a database table, transferring money, rebooting a server). ADK 2.0 provides native **Human-in-the-Loop (HITL)** support via the `require_confirmation` parameter in `FunctionTool`.

#### Static vs. Conditional Confirmation

You can enforce confirmation either statically (always require approval) or dynamically using a predicate function:

```python
from google.adk.tools import FunctionTool

def delete_user_record(user_id: str) -> dict:
    """Permanently deletes a user record."""
    # DB deletion logic...
    return {"status": "deleted", "user_id": user_id}

# 1. Static Confirmation (Always prompt the user for approval)
delete_tool = FunctionTool(
    func=delete_user_record,
    require_confirmation=True,
)

def transfer_funds(account_id: str, amount: float) -> dict:
    """Transfers funds to a target account."""
    # Transfer logic...
    return {"status": "transferred", "amount": amount}

# 2. Dynamic / Conditional Confirmation (Prompt only when amount > $1,000)
def needs_transfer_approval(amount: float, **kwargs) -> bool:
    return amount > 1000.0

transfer_tool = FunctionTool(
    func=transfer_funds,
    require_confirmation=needs_transfer_approval,
)
```

When a tool requires confirmation:
1. The ADK execution engine halts before invoking the Python function and emits an event requesting user confirmation.
2. The UI or client application prompts the human operator with the tool name and proposed arguments.
3. Upon receiving approval, execution resumes seamlessly; if rejected, the agent receives an explanation to pivot its plan.

<KnowledgeCheck
  id="m10-hitl-dynamic-confirmation"
  question="When configuring Human-in-the-Loop (HITL) safety in ADK 2.0 with FunctionTool, what type of value can be passed to require_confirmation to evaluate risk dynamically based on input arguments?"
  options={[
    "A callable predicate function that receives argument kwargs and returns a boolean",
    "A JSON Schema string with regex security constraints",
    "An async gRPC interceptor channel",
    "A static integer representing the risk level (1-5)"
  ]}
  correctIndex={0}
  hint="Look at how require_confirmation supports conditional checks for high amounts or dangerous operations."
  explanation="In ADK 2.0, require_confirmation accepts either a static boolean (True/False) or a callable predicate function (e.g., lambda amount, **kwargs: amount > 1000) to conditionally gate high-risk actions based on runtime arguments."
/>

### Key Takeaways
- Use **`ToolContext`** to securely access the ADK runtime.
- **`tool_context.state`** allows tools to persist data across turns.
- Stateful tools enable agents to have a structured, programmable memory.
- **`require_confirmation`** in `FunctionTool` provides native Human-in-the-Loop governance for high-risk actions.
- **Rule:** Never describe `tool_context` in your docstring; it's for the framework, not the LLM.