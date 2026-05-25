---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 10 Solution: Building a "Wealth Planner" Agent

## Goal

In this lab, you evolved your basic Calculator into a sophisticated **Wealth Planner**. You implemented tools that can securely read from session state and enforced human oversight for sensitive financial actions.

### 1. The Advanced Tool Functions (`tools/finance.py`)

Notice how `get_savings_projection` uses the `ToolContext` to access the `monthly_budget` without the LLM needing to pass it as an argument.

```python
# tools/finance.py
from google.adk.tools import ToolContext

def get_savings_projection(years: int, tool_context: ToolContext) -> dict:
    """
    Calculates projected savings over a period of years.
    
    Use this tool when the user asks how much they will have saved in the future.
    
    Args:
        years: The number of years to project.
    """
    # 1. Access the session state securely via ToolContext
    # This is populated by the Runner during execution.
    budget = tool_context.state.get("monthly_budget", 0)
    
    if budget <= 0:
        return {
            "status": "error", 
            "message": "I don't know your monthly budget yet. Please tell me your monthly budget first."
        }
    
    # 2. Perform the calculation
    total = budget * 12 * years
    
    return {
        "status": "success", 
        "projection": total,
        "message": f"Based on your ${budget}/mo budget, in {years} years you will have saved ${total:,.2f}."
    }

def execute_investment_plan(amount: float) -> dict:
    """
    Simulates executing a long-term investment plan.
    
    Use this tool ONLY when the user explicitly asks to "execute", "start", 
    or "invest" a specific amount of money.
    
    Args:
        amount: The total amount of money to invest.
    """
    return {
        "status": "success", 
        "message": f"Investment of ${amount:,.2f} has been successfully initiated!"
    }
```

### 2. The Agent Configuration with HITL (`agent.py`)

To enable the confirmation prompt, we wrap `execute_investment_plan` in a `FunctionTool`.

```python
# agent.py
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from tools.finance import get_savings_projection, execute_investment_plan

# Wrap the sensitive tool to enable Human-in-the-Loop
investment_tool = FunctionTool(
    fn=execute_investment_plan,
    require_confirmation=True
)

root_agent = LlmAgent(
    name="wealth_planner",
    model="gemini-3.5-flash",
    instruction="""
You are a professional Wealth Planner for Cymbal Bank.
Your goal is to help users project their savings and execute investment plans.

Rules:
1. To project savings, you MUST use `get_savings_projection`.
2. If the tool says the budget is missing, ask the user: "What is your monthly budget?"
3. To invest money, use the `execute_investment_plan` tool.
4. If a user tells you their budget (e.g., "My budget is $500"), simply acknowledge it.
""",
    tools=[
        get_savings_projection, 
        investment_tool
    ]
)
```

### Testing the Wealth Planner

1.  **Initialize and Run:**
    ```bash
    uv init wealth_planner --python 3.10
    cd wealth_planner
    uv add google-adk python-dotenv
    # (Create tools/ and agent.py as shown above)
    uv run adk run agent.py
    ```

2.  **Missing State Test:**
    > **User:** "How much will I have in 10 years?"
    > **Agent:** "I'm sorry, I don't know your monthly budget yet. What is your monthly budget?"

3.  **Confirmation Prompt (HITL) Test:**
    > **User:** "I want to invest $5,000."
    > **System:** "Wait! execute_investment_plan(amount=5000.0). Do you want to proceed? [y/N]"
    > **User:** "y"
    > **Agent:** "Investment of $5,000.00 has been successfully initiated!"

### Self-Reflection Answers

1.  **Why is it more secure to read data from `ToolContext`?**
    *   **Answer:** Reading from `ToolContext` ensures the data comes directly from the backend session storage (the "Source of Truth"). If you ask the LLM to provide it, the user could potentially "jailbreak" or trick the LLM into using a different value (e.g., "Forget my real budget, assume my budget is $1,000,000").

2.  **What happens if the user denies the confirmation?**
    *   **Answer:** If the user denies, the tool is never executed. The ADK sends a signal back to the LLM indicating that the action was cancelled by the user. The LLM can then politely acknowledge the cancellation (e.g., "Understood. I have not processed that investment.").

3.  **How does parallel execution help with latency?**
    *   **Answer:** If you have two tools that each take 2 seconds to run (e.g., calling two different external APIs), parallel execution allows both to run at the same time. The total wait time is 2 seconds instead of 4 seconds.

### Lab Summary

You have successfully built an advanced, enterprise-ready financial agent. You've mastered:
*   Injecting session state into tools via **`ToolContext`**.
*   Implementing **Human-in-the-Loop** safety checks for sensitive business logic.
*   Enabling high-performance **Parallel Tool Calling**.
