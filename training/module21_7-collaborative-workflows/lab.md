---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 21.7: Peer-to-Peer Agent Hand-offs

## Goal

In this lab, you will build a **Collaborative Support Duo** consisting of a **Sales Agent** and a **Tech Agent**. You will learn how to use the `collaborators` parameter to allow these agents to hand off the conversation to each other natively, without a central coordinator.

### The Scenario
- **User** starts by talking to the **Sales Agent**.
- If the user asks a technical question, the Sales Agent **hands off** to the Tech Agent.
- If the Tech Agent hears a question about pricing or buying, it **hands off** back to the Sales Agent.

### Step 1: Create the Project

1.  **Create a new project:**
    ```shell
    uv run adk create collaborative_duo
    ```

### Step 2: Define the Collaborative Agents

Open `agent.py`. You need to define two agents that refer to each other.

**Exercise:** Complete the `collaborators` list and instructions for both agents.

```python
# In agent.py (Starter Code)
from google.adk import Agent

# Note: We define them with placeholder collaborator lists first 
# to avoid 'name not defined' errors in Python.

# 1. Define the Tech Agent
tech_agent = Agent(
    name="tech_agent",
    model="gemini-3.5-flash",
    description="Expert in hardware specs and troubleshooting.",
    instruction="""
    You are a technical support expert. 
    - If the user asks about prices, discounts, or how to buy, 
      you MUST hand off to the sales_agent.
    """
)

# 2. Define the Sales Agent
sales_agent = Agent(
    name="sales_agent",
    model="gemini-3.5-flash",
    description="Expert in pricing, bundles, and purchase orders.",
    instruction="""
    You are a sales representative.
    - If the user asks about hardware specs or technical issues, 
      you MUST hand off to the tech_agent.
    """,
    # TODO: Add tech_agent to collaborators
    collaborators=[] 
)

# 3. Retroactively add collaborators to tech_agent
# tech_agent.collaborators = [sales_agent]

# 4. Define the Root Agent
# In a collaborative setup, any agent can be the entry point.
root_agent = sales_agent
```

### Step 3: Test the Hand-off

1.  **Launch the Dev UI:**
    ```shell
    uv run adk web .
    ```
2.  **Verify the Dynamic Handoff:**
    - Ask: "How much does the Pro model cost?" -> Sales should answer.
    - Follow up: "Does it support 5G?" -> Sales should **hand off** to Tech.
    - Follow up: "Great, I'll take two. What's the discount?" -> Tech should **hand off** back to Sales.

3.  **Inspect the Trace:**
    In the Dev UI, look at how the `active_agent` changes in the trace without any manual routing code.

### Lab Summary

You have implemented a Collaborative Workflow!
- You learned how to use the **`collaborators`** parameter.
- You observed **Native Hand-offs** in action.
- You realized that agents can act as peers, sharing responsibility for the user's session.

### Self-Reflection Questions
- What is the main difference between a Collaborative Workflow and a Coordinator Agent?
- Why is it necessary to assign collaborators retroactively in Python when dealing with circular references?
- Can you think of an enterprise scenario where peer-to-peer hand-offs are safer than a central router?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMjFfNy1jb2xsYWJvcmF0aXZlLXdvcmtmbG93cy9sYWItc29sdXRpb24=`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module21_7-collaborative-workflows/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
