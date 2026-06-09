---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 10: Building a "Wealth Planner" Agent Challenge

## Goal

In this lab, you will evolve your basic Calculator into a **Wealth Planner**. You will learn how to make tools context-aware (reading from session state) and how to implement **Human-in-the-Loop** confirmation for sensitive actions.

### Step 1: Prepare the Project

We will continue using the `uv` workflow.

1.  **Initialize the project:**
    ```bash
    uv init wealth_planner --python 3.10
    cd wealth_planner
    uv add "google-adk>=2.1.0" python-dotenv
    ```

2.  **Create the tools module:**
    ```bash
    mkdir tools
    touch tools/__init__.py
    touch tools/finance.py
    ```

3.  **Setup Authentication:** Ensure your `.env` file is ready.

### Step 2: Implement Advanced Tools
**Exercise:** Open `tools/finance.py` and implement the three functions below.

```python
# In tools/finance.py
from google.adk.tools import ToolContext

def set_budget(amount: float, tool_context: ToolContext) -> str:
    """
    Saves the user's monthly budget to their session profile.

    Use this tool when the user tells you how much they can save or spend per month.
    """
    # TODO: Save the 'amount' to the session state under the key "monthly_budget"
    # Hint: Use tool_context.session.state
    pass

def get_savings_projection(years: int, tool_context: ToolContext) -> dict:
    """
    Calculates projected savings over a period of years.
    
    Use this tool when the user asks how much they will have saved in the future.
    """
    # TODO: Access session state via tool_context.session.state to get "monthly_budget"
    # TODO: If budget is 0 or missing, return an error dictionary.
    # TODO: Calculate: total = budget * 12 * years
    # TODO: Return a success dictionary with the result.
    pass

def execute_investment_plan(amount: float) -> dict:
    """
    Simulates executing a long-term investment plan.
    
    Use this tool ONLY when the user explicitly asks to "execute", "start", 
    or "invest" a specific amount of money.
    
    Args:
        amount: The total amount of money to invest.
    """
    # This tool is "sensitive" and will require confirmation.
    return {
        "status": "success", 
        "message": f"Investment of ${amount} has been successfully initiated!"
    }
```

### Step 3: Configure the Agent with HITL

**Exercise:** Create `agent.py`. You will need to wrap the sensitive tool in a `FunctionTool` to enable the `require_confirmation` feature.

```python
# In agent.py
from google.adk import Agent
from google.adk.tools import FunctionTool
from tools.finance import set_budget, get_savings_projection, execute_investment_plan

# TODO: Create a FunctionTool for the investment plan with confirmation enabled.
# Hint: Use require_confirmation=True
investment_tool = ...

# TODO: Define the root Agent node and register all three tools.
root_agent = Agent(
    name="wealth_planner",
    model="gemini-3.5-flash",
    instruction="""
# TODO: Write instructions for a professional Wealth Planner.
# Ensure it knows to use 'set_budget' first if the budget is unknown.
""",
    tools=[...]
)
```

### Step 4: Test and Observe Parallel Execution

1.  **Run the agent:**
    ```bash
    uv run adk run agent.py
    ```

2.  **Advanced CLI Testing (Parallelism):**
    Try asking two independent things at once:
    > "Project my savings for 5 years and also calculate 452 * 12." 
    *(Assuming you added the multiply tool from Mod 09)*. 
    
    Observe in the logs how both tools are triggered.

3.  **Test Confirmation (HITL):**
    Try: > "I want to invest $5000 now."
    
    In the terminal (or Dev UI `uv run adk web`), you will see a prompt asking for permission. Only if you say **"yes"** will the tool actually execute.

### Lab Summary

You have successfully built an enterprise-ready financial agent! You have learned:
*   How to use **`ToolContext`** to bridge the gap between your tools and the session state.
*   How to implement **Human-in-the-Loop** confirmation for sensitive actions using `FunctionTool`.
*   How the ADK handles **Parallel Execution** for complex user queries.

### Self-Reflection Questions
- Why is it more secure to read the `user_id` or `budget` from `ToolContext` rather than asking the LLM to provide it as a tool argument?
- What happens if the user denies the confirmation for the investment tool? How does the LLM react?
- How does parallel execution help with "latency-sensitive" tools (like calling a slow external API)?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMTAtYWR2YW5jZWQtZnVuY3Rpb24tdG9vbHMvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module10-advanced-function-tools/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
