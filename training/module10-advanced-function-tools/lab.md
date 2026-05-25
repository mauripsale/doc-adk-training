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
    uv add google-adk python-dotenv
    ```

2.  **Create the tools module:**
    ```bash
    mkdir tools
    touch tools/__init__.py
    touch tools/finance.py
    ```

3.  **Setup Authentication:** Ensure your `.env` file is ready.

### Step 2: Implement Advanced Tools

**Exercise:** Open `tools/finance.py` and implement the two functions below.

```python
# In tools/finance.py
from google.adk.tools import ToolContext

def get_savings_projection(years: int, tool_context: ToolContext) -> dict:
    """
    Calculates projected savings over a period of years.
    
    Use this tool when the user asks how much they will have saved in the future.
    
    Args:
        years: The number of years to project.
    """
    # TODO: Read the 'monthly_budget' from the tool_context.state.
    # If it's not set, return an error asking the user to set it first.
    budget = ... 
    
    # TODO: Calculate: total = budget * 12 * years
    # Return a success dictionary with the result.
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
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from tools.finance import get_savings_projection, execute_investment_plan

# TODO: Create a FunctionTool for the investment plan with confirmation enabled.
# Hint: Pass the function as the first argument, and use require_confirmation=True.
investment_tool = FunctionTool(
    ...,
    require_confirmation=...
)

root_agent = LlmAgent(
    name="wealth_planner",
    model="gemini-3.5-flash",
    instruction="""
You are a professional Wealth Planner.
Your goal is to help users project their savings and execute investment plans.

Rules:
1. To project savings, you MUST use `get_savings_projection`.
2. If the tool says the budget is missing, ask the user: "What is your monthly budget?"
3. To invest money, use the `execute_investment_plan` tool.
4. If a user tells you their budget (e.g., "My budget is $500"), simply acknowledge it. 
""",
    tools=[
        get_savings_projection, # Direct passing is fine for simple tools
        investment_tool          # Use the wrapped tool for HITL
    ]
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
    
    In the terminal (or Dev UI `adk web`), you will see a prompt asking for permission. Only if you say **"yes"** will the tool actually execute.

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
