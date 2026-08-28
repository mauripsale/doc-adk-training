---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 18: Building a Smart Support Router with Dynamic Workflows

## Goal

In this lab, you will build a sophisticated orchestration system using a **Dynamic Workflow**. You will create a `support_router_workflow` node that intercepts user requests, uses a fast LLM node to classify the sentiment (angry, neutral, happy), and then programmatically routes the request to the appropriate specialist agent node.

This exercise demonstrates the power of ADK 2.0: using standard Python logic to orchestrate multiple AI components with deterministic control.

### Step 1: Create the Project Structure

1.  **Create a new project:**
    ```shell
    uv run adk create support_router_v2
    ```

2.  **Navigate into the new directory:**
    ```shell
    cd support_router_v2
    ```

3.  **Upgrade your environment:**
    Ensure you are using ADK 2.0 or higher:
    ```shell
    uv pip install -U "google-adk>=2.1.0"
    ```

### Step 2: Implement the Dynamic Router

**Exercise:** Open `agent.py`. The two specialist agents (`ai_support` and `human_escalation`) have been provided for you as starter nodes.

Your task is to implement the `support_router_workflow` function using the `@node` decorator and the `ctx.run_node()` method.

```python
# In agent.py (Starter Code)

from __future__ import annotations
from pydantic import BaseModel
from google.adk import Agent, Workflow, Context, Event
from google.adk.workflow import node
from typing import AsyncGenerator, Literal

# ===== Specialist Agent Nodes =====

# TODO: Define ai_support and human_escalation agents.
# Hint: One is for technical help, the other for frustrated customers.
ai_support = ...
human_escalation = ...

# ===== 1. Define Sentiment Schema =====

# Define a Pydantic model for structured classification
class SentimentClassification(BaseModel):
    sentiment: Literal["angry", "neutral", "happy"]

# TODO: Create the classifier agent node using the schema above.
classifier = ...

# ===== 2. Build the Dynamic Workflow =====

# TODO: Implement the orchestrator node
# 1. Use the @node(rerun_on_resume=True) decorator.
# 2. Accept 'ctx: Context' and 'node_input: str' as arguments.
@node(rerun_on_resume=True)
async def support_router_workflow(ctx: Context, node_input: str):
    # Step 2a: Run the classifier node.
    # Hint: result = await ctx.run_node(classifier, node_input)
    # Even though the classifier's output_schema is the SentimentClassification
    # Pydantic model, run_node() returns it as a plain dict at runtime --
    # access fields with result["sentiment"], not result.sentiment.
    classification = None 
    
    # Step 2b: Routing Logic.
    # Use a standard Python 'if' statement to choose the target agent.
    # If sentiment is "angry", choose human_escalation.
    # Otherwise, choose ai_support.
    chosen_agent = None 
    
    # Step 2c: Execute the chosen agent and return the result.
    # Hint: return await ctx.run_node(chosen_agent, node_input)
    return None

# ===== 3. Register the System =====

# TODO: Create a Workflow named "SupportSystem" 
# and link the "START" edge to your support_router_workflow.
root_agent = Workflow(
    name="SupportSystem",
    edges=[("START", ...)]
)
```

### Step 3: Run and Test the Router

1.  **Start the Dev UI:**
    ```shell
    uv run adk web .
    ```
2.  **Test the routing:**
    *   **Input:** "My internet is down, help!" -> Should route to `ai_support_bot`.
    *   **Input:** "THIS IS DISGUSTING! I WANT TO CANCEL EVERYTHING!" -> Should route to `human_escalation_team`.
3.  **Inspect the Workflow Graph:**
    In the Dev UI, open the **Graph View**. You will see the visual representation of your dynamic execution: the flow from the router node to the specific specialist agent.

### Lab Summary

By completing this lab, you have mastered the fundamental orchestration pattern of ADK 2.0:
*   Using **`@node`** to turn standard Python functions into workflow components.
*   Leveraging **`ctx.run_node()`** to execute agents and retrieve structured results directly.
*   Implementing **Programmable Routing** that combines AI classification with deterministic business rules.

### Self-Reflection Questions
- How is `ctx.run_node()` in ADK 2.0 different from the way we passed data between agents in ADK 1.x?
- Why is it important to set `rerun_on_resume=True` for the orchestrator node?
- Can a dynamic workflow call another dynamic workflow? (Hint: Yes, every workflow is just a node!)

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMTgtZHluYW1pYy1vcmNoZXN0cmF0aW9uL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module18-dynamic-orchestration/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
