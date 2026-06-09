---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 10 Solution: Building an Advanced Financial Assistant

## Goal

In this lab, we upgraded our Financial Assistant to be more secure and context-aware. We used `ToolContext` to access the session state and the `FunctionTool` wrapper to implement a human-in-the-loop confirmation step for budget changes.

### `wealth_planner/agent.py`

```python
import os
from pydantic import BaseModel
from google.adk import Agent
from google.adk.tools import ToolContext, FunctionTool
from dotenv import load_dotenv

load_dotenv()

# --- 1. Define Structured Tool Output ---
class SavingsResult(BaseModel):
    status: str
    total: float = 0
    message: str | None = None

# --- 2. Define Custom Tools ---

def set_budget(amount: float, tool_context: ToolContext) -> str:
    """Saves the user's monthly budget to their session profile."""
    # ADK 2.0: Use tool_context.session.state
    tool_context.session.state["monthly_budget"] = amount
    return f"Success: Your budget is now set to ${amount:.2f}/mo."

def get_savings_projection(years: int, tool_context: ToolContext) -> SavingsResult:
    """Calculates savings based on the stored budget."""
    budget = tool_context.session.state.get("monthly_budget", 0)
    
    if budget <= 0:
        return SavingsResult(status="error", message="No budget found. Please use set_budget first.")
        
    total = budget * 12 * years
    return SavingsResult(status="success", total=total)

def execute_investment_plan(amount: float) -> dict:
    """Simulates executing a long-term investment plan."""
    return {"status": "success", "message": f"Investment of ${amount} initiated!"}

# --- 3. Wrap with Advanced Features ---
# We wrap execute_investment_plan because it's a sensitive action
investment_tool = FunctionTool(execute_investment_plan, require_confirmation=True)

# --- 4. Define the Agent ---
root_agent = Agent(
    name="wealth_planner",
    model="gemini-3.5-flash",
    instruction="""
      You are a professional Wealth Planner. 
      - Help users manage their budget using 'set_budget'.
      - Help users project their savings using 'get_savings_projection'.
      - Execute plans using 'execute_investment_plan'.
      
      If you don't know their budget, ask them to set it first.
    """,
    tools=[set_budget, get_savings_projection, investment_tool]
)
```

### Key Technical Takeaways

1.  **Context Injection:** By adding `tool_context: ToolContext` to our functions, we enabled the tools to interact with the ADK's session management without the LLM being aware of this complexity.
2.  **Human-in-the-Loop (HITL):** Using `require_confirmation=True` ensures that sensitive operations (like updating a user's financial profile) are not performed without explicit user consent, adding a vital layer of safety.
3.  **Stateful Reasoning:** The agent can now "remember" information from one turn (the budget) and use it to perform calculations in a subsequent turn, creating a much more cohesive user experience.

### Self-Reflection Answers

1.  **Why is it more secure to read the budget from `ToolContext` rather than asking the LLM to provide it as a tool argument?**
    *   **Answer:** It ensures **data integrity**. By reading the budget directly from the `tool_context.session.state`, we rely on a value that was previously validated and stored by our own code (`set_budget`). If we let the LLM provide it, a user could potentially "jailbreak" the prompt to make the agent use a fake budget, bypassing our business rules.

2.  **What happens if the user denies the confirmation for the investment tool? How does the LLM react?**
    *   **Answer:** If the user clicks "Deny," the ADK cancels the execution of the Python function. The agent then receives a notification that the tool call was rejected by the user. Most modern LLMs will gracefully acknowledge this, responding with something like, "I understand, I have cancelled the investment as requested."

3.  **How does parallel execution help with "latency-sensitive" tools?**
    *   **Answer:** It dramatically improves performance. If an agent needs to fetch data from three different external APIs, executing them **sequentially** would force the user to wait for the sum of all response times. By executing them **in parallel**, the total wait time is reduced to only the slowest single API call.
