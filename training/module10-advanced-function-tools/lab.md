---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 10: Building a Personal Finance Assistant Challenge

## Goal

### Goal

In this lab, you will build a **Personal Finance Assistant** with multiple, complex function tools. This will teach you how to implement robust tools and see the ADK's parallel execution feature in action.

### Step 1: Create the Agent Project

1.  **Create the agent project:**
    Choose the **Programmatic (Python script)** option when prompted.
    ```shell
    adk create finance_assistant
    cd finance_assistant
    ```

2.  **Set up your API key** in the `.env` file.

### Step 2: Implement the Financial Tools

**Exercise:** Open `agent.py`. A skeleton with three financial tool functions is provided. Your task is to implement the logic for each function based on the `# TODO` comments. You will need to perform calculations, validate inputs, and return a structured dictionary.

```python
# In agent.py (Starter Code)

from __future__ import annotations
from google.adk.agents import Agent

def calculate_compound_interest(
    principal: float,
    annual_rate: float,
    years: int,
    compounds_per_year: int = 1
) -> dict:
    """
    Calculate compound interest for savings or investments.
    Formula: A = P(1 + r/n)^(nt)
    ...
    """
    # TODO: 1. Validate that principal, annual_rate, and years are positive.
    # If not, return an error dictionary: {'status': 'error', 'report': '...'}
    
    # TODO: 2. Calculate the final amount and interest earned.
    
    # TODO: 3. Create a human-readable report string.
    
    # TODO: 4. Return a success dictionary with the report.
    return {'status': 'pending', 'report': 'Implementation needed.'}


def calculate_loan_payment(
    loan_amount: float,
    annual_rate: float,
    years: int
) -> dict:
    """
    Calculate monthly loan payments using the standard amortization formula.
    ...
    """
    # TODO: 1. Validate inputs.
    # TODO: 2. Calculate the monthly payment.
    # TODO: 3. Create a human-readable report.
    # TODO: 4. Return a success dictionary.
    return {'status': 'pending', 'report': 'Implementation needed.'}


def calculate_monthly_savings(
    target_amount: float,
    years: int,
    annual_return: float = 0.05
) -> dict:
    """
    Calculate monthly savings needed to reach a financial goal.
    ...
    """
    # TODO: 1. Validate inputs.
    # TODO: 2. Calculate the required monthly savings.
    # TODO: 3. Create a human-readable report.
    # TODO: 4. Return a success dictionary.
    return {'status': 'pending', 'report': 'Implementation needed.'}


# TODO: Define the root_agent. Give it an appropriate instruction and
# register the three tool functions you just implemented.
root_agent = None
```

### Step 3: Run and Test Your Assistant

1.  **Navigate to the parent directory** (`cd ..`) and start the Dev UI:
    ```shell
    adk web
    ```
2.  **Interact with the agent:**
    *   Select `finance_assistant` from the dropdown menu.
    *   Test each of your tools with prompts like:
        *   "If I invest $10,000 at 6% for 5 years, how much will I have?"
        *   "What's the monthly payment on a $300,000 house over 30 years at 4.5%?"
        *   "How much do I need to save each month to get $50,000 in 3 years?"
    *   Check the **Events** tab to see the `FunctionCall` and `FunctionResponse`.

### Step 4: Test Parallel Tool Execution

Now, see the agent's advanced capabilities in action. Send a single prompt that requires two separate calculations.

**Try this prompt:**
> "I want to know the monthly payment for a $25,000 car loan over 5 years at 7% interest. Also, tell me how much my $5,000 investment will be worth in 10 years at 8% annual return."

**Observe the Events Tab:** Expand the events for the last turn. You should see that the agent made two `FunctionCall`s—one for `calculate_loan_payment` and one for `calculate_compound_interest`—**in the same turn**. This is parallel execution!

### Having Trouble?

If you get stuck, you can find the complete, working code in the `lab-solution.md` file.

### Lab Summary

You have successfully built an advanced agent with multiple, complex function tools. You have learned:
*   How to implement robust tools with input validation and structured error handling.
*   How to write tools that produce user-friendly reports.
*   How to trigger and verify parallel tool execution for more efficient agent responses.

### Self-Reflection Questions
- Why is it a good practice for a tool to perform its own input validation, even though the LLM is usually good at providing the correct arguments?
- In the parallel execution test, the two tool calls are independent. Can you think of a scenario where a user's query might seem like it could be parallelized, but actually requires the tools to be run sequentially?
- How does providing a pre-formatted, human-readable `report` in the tool's return dictionary simplify the agent's `instruction` prompt?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMTAtYWR2YW5jZWQtZnVuY3Rpb24tdG9vbHMvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module10-advanced-function-tools/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
