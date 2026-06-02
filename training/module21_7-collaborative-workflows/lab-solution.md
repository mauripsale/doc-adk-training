---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 21.7 Solution: Peer-to-Peer Agent Hand-offs

## Goal

This file contains the complete code for the `agent.py` script using ADK 2.0 Collaborative Workflows.

### `collaborative_duo/agent.py`

```python
from google.adk import Agent

# 1. Define the Tech Agent
# We define it without collaborators initially to avoid reference errors.
tech_agent = Agent(
    name="tech_agent",
    model="gemini-3.5-flash",
    description="Expert in hardware specs and troubleshooting.",
    instruction="""
    You are a technical support expert. Your job is to answer deep technical questions.
    
    **HAND-OFF RULES:**
    - If the user asks about prices, discounts, or expressed intent to BUY, 
      you MUST hand off to the sales_agent.
    """
)

# 2. Define the Sales Agent
# This agent already knows about the tech_agent.
sales_agent = Agent(
    name="sales_agent",
    model="gemini-3.5-flash",
    description="Expert in pricing, bundles, and purchase orders.",
    instruction="""
    You are a sales representative. Your job is to help users with pricing and buying.
    
    **HAND-OFF RULES:**
    - If the user asks about hardware specs, compatibility, or technical issues, 
      you MUST hand off to the tech_agent.
    """,
    collaborators=[tech_agent] 
)

# 3. Retroactively link the tech_agent back to sales_agent
# This enables bi-directional hand-offs.
tech_agent.collaborators = [sales_agent]

# 4. Set the Root Agent
# Any agent in the collaborative group can be the entry point.
root_agent = sales_agent
```

### Self-Reflection Answers

1.  **What is the main difference between this and the Coordinator pattern?**
    *   **Answer:** In the Coordinator pattern, there is a "boss" agent that manages sub-agents. Control always returns to the coordinator after a sub-agent finishes. In a Collaborative Workflow, control stays with the new agent after a hand-off. It is peer-to-peer rather than hierarchical.

2.  **How does the LLM know how to perform the hand-off?**
    *   **Answer:** The ADK automatically creates a tool (e.g., `hand_off_to_tech_agent`) for every agent listed in the `collaborators` parameter. The LLM sees these tools in its toolkit and calls them when its instructions tell it to delegate.

3.  **Why did we have to set `tech_agent.collaborators` retroactively?**
    *   **Answer:** In Python, you cannot refer to a variable (`sales_agent`) before it has been defined. By setting the collaborators list on the second agent and then updating the first one, we create the circular reference required for bi-directional hand-offs.
