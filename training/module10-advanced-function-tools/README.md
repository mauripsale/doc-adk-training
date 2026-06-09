---
sidebar_position: 10
title: "Module 10: Advanced Function Tools"
---

# Module 10: Advanced Function Tools

## Theory

### Beyond the Basics

In the previous module, you learned the fundamentals of creating custom function tools by building a basic Calculator. Now, we will explore advanced techniques to make your tools more robust, context-aware, and secure. We will cover **ToolContext**, **Human-in-the-Loop (HITL)**, and **Parallel Tool Execution**.

### 1. Context-Aware Tools (`ToolContext`)

In a real application, your tools shouldn't exist in a vacuum. A tool often needs to know *who* it is acting for or what data was previously saved in the session. 

By adding a parameter typed as `ToolContext` to your function, the ADK will automatically populate it at runtime. The LLM does **not** see this parameter in the tool schema.

```python
from google.adk.tools import ToolContext
from pydantic import BaseModel

class GrowthReport(BaseModel):
    status: str
    total: float
    message: str | None = None

def calculate_wealth_growth(years: int, tool_context: ToolContext) -> GrowthReport:
    """Calculates projected savings based on the user's saved monthly budget."""
    # ADK 2.0: Access session state via tool_context.session.state
    monthly_budget = tool_context.session.state.get("monthly_budget", 0)
    
    if monthly_budget <= 0:
        return GrowthReport(status="error", total=0, message="Set budget first.")
        
    total = monthly_budget * 12 * years
    return GrowthReport(status="success", total=total)
```

**Rule:** Never mention `tool_context` in your function's docstring. The LLM doesn't need to know about it.

### 2. Human-in-the-Loop (`require_confirmation`)

When an agent performs "destructive" or "financial" actions (like actually transferring money or executing a stock trade), you want a human to review the action before it happens.

In Module 9, you passed raw functions to the `tools` list. To enable advanced features like confirmation, you must wrap your function in the ADK's `FunctionTool` class.

Setting `require_confirmation=True` pauses the agent's execution and asks the user for explicit permission in the Dev UI (or via code) before running the Python function.

```python
from google.adk.tools import FunctionTool

# Wrap the sensitive function
transfer_tool = FunctionTool(
    execute_transfer, 
    require_confirmation=True
)

# Usage in Agent:
# tools=[transfer_tool]
```

### 3. Automatic Parallel Tool Execution

One of the most powerful features of the ADK is its ability to execute multiple tools simultaneously. If a user asks a complex question like: *"How much will I have in 5 years if I save $500/mo, and what is the current interest rate for a mortgage?"*, the LLM is smart enough to request both tool calls in a single turn.

The ADK receives this list and executes them **in parallel** using `asyncio.gather()`. This significantly improves performance, as the response time is limited only by the slowest tool, not the sum of all tools.

### Best Practices for Complex Tools

*   **Input Validation:** Your tool is the last line of defense. Always validate arguments (e.g., ensure `years` is a positive number).
*   **Structured Errors:** Always return a dictionary with a `status` key. If something goes wrong, use `{"status": "error", "message": "..."}` so the LLM can explain the failure to the user.

### Key Takeaways
- Use **`ToolContext`** to securely access session state without confusing the LLM.
- Use the **`FunctionTool`** wrapper with `require_confirmation=True` for sensitive actions.
- The ADK automatically handles **Parallel Execution** when multiple tools are requested.