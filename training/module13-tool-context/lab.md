---
sidebar_position: 2
title: "Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 13: Building a Secure Agent with HITL and Actions

## Goal

In this lab, you will build a **Secure Finance Agent**. You will learn how to implement **Human-in-the-Loop (HITL)** for sensitive transactions and how to use **`tool_context.actions`** to dynamically escalate a conversation to a supervisor node.

### Step 1: Prepare the Project

<Setup/>

```bash
uv run adk create secure_finance
cd secure_finance
```

### Step 2: Implement the Secure Tools

**Exercise:** Create `tools/finance.py`. You will implement a tool that handles investments.

```python
# In tools/finance.py
from google.adk.tools import ToolContext

def execute_investment(amount: float, tool_context: ToolContext) -> str:
    """
    Executes a long-term investment.
    Use this tool only when the user explicitly asks to 'invest' or 'buy'.
    """
    # 1. Check for escalation: Any amount > 10,000 needs a human supervisor
    if amount > 10000:
        # TODO: Set tool_context.actions.transfer_to_agent to "supervisor"
        # Hint: This will dynamically route the user to a different node.
        pass
        return f"Amount ${amount} requires supervisor approval. Escalating..."

    # 2. Regular investment logic
    return f"Success! ${amount} has been invested in your portfolio."
```

### Step 3: Configure the Agent with HITL

**Exercise:** Open `agent.py`. You need to wrap your tool in a `FunctionTool` to enable the confirmation pop-up.

```python
# In agent.py
from google.adk import Agent, Workflow
from google.adk.tools import FunctionTool
from .tools.finance import execute_investment

# --- 1. Define the Supervisor Node ---
supervisor = Agent(
    name="supervisor",
    model="gemini-3.5-flash",
    instruction="You are a senior supervisor. Review the large investment request and provide a final verdict."
)

# --- 2. Wrap the Tool for Safety ---
# TODO: Create a FunctionTool named 'secure_investment_tool'
# Enable require_confirmation=True
secure_investment_tool = ...

# --- 3. Define the Main Agent ---
finance_agent = Agent(
    name="finance_agent",
    model="gemini-3.5-flash",
    instruction="Help users with their investments. Use 'execute_investment' for trades.",
    tools=[secure_investment_tool],
    sub_agents=[supervisor] # Required for discovery during transfer
)

# --- 4. Build the Workflow Graph ---
root_agent = Workflow(
    name="SecureSystem",
    edges=[("START", finance_agent)]
)
```

### Step 4: Test the Secure Workflow

1.  **Start the Dev UI:** `uv run adk web .`
2.  **Test HITL:** 
    - Ask: "Invest $500 for me."
    - **Observe:** A confirmation box should appear. The code only runs if you click "Approve."
3.  **Test Dynamic Transfer:**
    - Ask: "Invest $50,000 for me."
    - **Observe:** Since `require_confirmation=True` wraps the tool unconditionally, you will see the *same* confirmation pop-up as above first — click "Approve" to let the tool actually run. Only then does the escalation logic inside `execute_investment` fire. In the Trace, you will see the `active_agent` change from `finance_agent` to `supervisor`.

### Lab Summary

You have built a production-ready secure agent! You learned:
*   How to **pause execution** for human approval using `require_confirmation`.
*   How to **reroute the conversation** dynamically using `tool_context.actions.transfer_to_agent`.
*   How to combine manual safety (HITL) with automated business rules (Escalation).

### Self-Reflection Questions
- Why is it important to use `require_confirmation` for sensitive actions rather than just relying on the LLM's instructions?
- In the dynamic transfer example, why did we need to add the `supervisor` agent to the `sub_agents` list of the `finance_agent`?
- How does `tool_context.actions` allow you to implement business rules that the LLM cannot override?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="13">

# Lab 13 Solution: Building a Secure Agent with HITL and Actions

## Goal

This file contains the complete code for the `finance.py` and `agent.py` files using ADK 2.0 standards for advanced tool interactions.

### `secure_finance/tools/finance.py`

```python
from google.adk.tools import ToolContext

def execute_investment(amount: float, tool_context: ToolContext) -> str:
    """
    Executes a long-term investment.
    Use this tool only when the user explicitly asks to 'invest' or 'buy'.
    """
    # Business Rule: Large amounts require senior supervisor review
    if amount > 10000:
        # 🏃 Dynamic Workflow Action: Hand-off to the supervisor node
        tool_context.actions.transfer_to_agent = "supervisor"
        return f"Investment of ${amount} exceeds local limit. Handing off to supervisor..."

    # Logic for standard investments
    return f"Success! ${amount} has been invested in your portfolio."
```

### `secure_finance/agent.py`

```python
from google.adk import Agent, Workflow
from google.adk.tools import FunctionTool
from .tools.finance import execute_investment

# 1. Define the Specialist Node (Supervisor)
supervisor = Agent(
    name="supervisor",
    model="gemini-3.5-flash",
    instruction="""
    You are a senior investment supervisor. 
    You have been called because a user wants to make a large investment (> $10,000).
    Review the request and the user's history, then provide a professional recommendation.
    """
)

# 2. Wrap the Tool for Safety (HITL)
# We use FunctionTool to add the requirement for human confirmation.
secure_investment_tool = FunctionTool(
    execute_investment, 
    require_confirmation=True
)

# 3. Define the Main Agent Node
finance_agent = Agent(
    name="finance_agent",
    model="gemini-3.5-flash",
    description="A secure finance assistant.",
    instruction="""
    You are a helpful investment assistant. 
    Use 'execute_investment' to help users trade.
    If the user wants to invest more than $10k, explain that you are escalating to a supervisor.
    """,
    tools=[secure_investment_tool],
    sub_agents=[supervisor] # Discovery for dynamic hand-off
)

# 4. Build the Workflow Graph
root_agent = Workflow(
    name="SecureSystem",
    edges=[("START", finance_agent)]
)
```

### Self-Reflection Answers

1.  **Why is it more secure to use `require_confirmation` for sensitive actions rather than just relying on the LLM's instructions?**
    *   **Answer:** Instructions are just "advice" to the LLM. Through prompt injection or adversarial inputs, a user could trick the model into skipping a step or ignoring a rule. `require_confirmation` is a **hard-coded framework feature**. The ADK literally will not call your Python function unless the user explicitly approves the action in the UI, providing a solid security guarantee.

2.  **In the dynamic transfer example, why did we need to add the `supervisor` agent to the `sub_agents` list of the `finance_agent`?**
    *   **Answer:** In ADK 2.0, an agent can only transfer to nodes it "knows" about. Adding an agent to the `sub_agents` list registers it as a valid destination in the local graph. Without this registration, the `transfer_to_agent` action would fail because the framework wouldn't be able to find the target node.

3.  **How does `tool_context.actions` allow you to implement business rules that the LLM cannot override?**
    *   **Answer:** Because the `actions` are processed by the **Python runtime**, not the LLM. When our code sets `transfer_to_agent`, the ADK intercepts this and forces the transition. The LLM doesn't even get to see the result of the tool before the hand-off happens, ensuring the business logic (like the $10,000 limit) is strictly enforced.

</SolutionVault>
