---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 18: Dynamic Orchestration (@node) — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 18: Building a Smart Support Router with Dynamic Workflows

## Goal

In this lab, you will build a sophisticated orchestration system using a **Dynamic Workflow**. You will create a `support_router_workflow` node that intercepts user requests, uses a fast LLM node to classify the sentiment (angry, neutral, happy), and then programmatically routes the request to the appropriate specialist agent node.

This exercise demonstrates the power of ADK 2.0: using standard Python logic to orchestrate multiple AI components with deterministic control.

### Step 1: Create the Project Structure

<Setup/>

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
    # Step 2a: Run the classifier node asynchronously using ctx.run_node().
    # Note: Even though the classifier's output_schema is the SentimentClassification
    # Pydantic model, run_node() returns it as a plain dict at runtime --
    # access fields with result["sentiment"], not result.sentiment.
    classification = None 
    
    # Step 2b: Routing Logic.
    # Use a standard Python 'if' statement to choose the target agent.
    # If sentiment is "angry", choose human_escalation.
    # Otherwise, choose ai_support.
    chosen_agent = None 
    
    # Step 2c: Execute the chosen target node via ctx.run_node() and return its result.
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

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="18">

# Lab 18 Solution: Building a Smart Support Router with Dynamic Workflows

## Goal

This file contains the complete code for the `agent.py` script in the Smart Support Router lab using the ADK 2.0 Dynamic Workflow pattern.

### `support_router_v2/agent.py`

```python
from __future__ import annotations
from pydantic import BaseModel
from google.adk import Agent, Workflow, Context, Event
from google.adk.workflow import node
from typing import AsyncGenerator, Literal

# ===== 1. Specialist Agent Nodes =====

ai_support = Agent(
    name="ai_support_bot",
    model="gemini-3.5-flash",
    instruction="You are a helpful customer support AI. Answer technical questions clearly."
)

human_escalation = Agent(
    name="human_escalation_team",
    model="gemini-3.5-flash",
    instruction="You are a human rep. Frustrated customer. apologize and promise a call."
)

# ===== 2. Classifier Agent Node =====

class SentimentClassification(BaseModel):
    sentiment: Literal["angry", "neutral", "happy"]

classifier = Agent(
    name="classifier",
    model="gemini-3.5-flash",
    instruction="Classify the sentiment of the user's latest message.",
    output_schema=SentimentClassification
)

# ===== 3. Build the Dynamic Workflow (The Orchestrator) =====

@node(rerun_on_resume=True)
async def support_router_workflow(ctx: Context, node_input: str):
    # Step 3a: Run the classifier node.
    # In ADK 2.0, run_node returns the node's output directly! No more manual
    # digging into session state -- but note it comes back as a plain dict,
    # even though the node's output_schema is a Pydantic model.
    classification: dict = await ctx.run_node(classifier, node_input)
    
    # Step 3b: Routing Logic.
    # Use standard Python logic to choose the next node in the graph.
    if classification["sentiment"] == "angry":
        chosen_agent = human_escalation
    else:
        chosen_agent = ai_support
    
    # Step 3c: Execute the chosen specialist agent and return its result.
    # By returning the result of run_node, the workflow engine automatically
    # handles the event emission to the user.
    return await ctx.run_node(chosen_agent, node_input)

# ===== 4. Register the Workflow as the Root =====

root_agent = Workflow(
    name="SupportSystem",
    edges=[("START", support_router_workflow)]
)
```

### Self-Reflection Answers

1.  **How is `ctx.run_node()` in ADK 2.0 different from the way we passed data between agents in ADK 1.x?**
    *   **Answer:** In ADK 1.x, you had to set an `output_key` on an agent and then manually retrieve that data from the `ctx.session.state` dictionary in the parent agent. In ADK 2.0, `ctx.run_node()` returns the result of the node execution directly (as a string, or as a plain `dict` when the node has an `output_schema` -- never a Pydantic instance), making the data flow much more intuitive and "Pythonic".

2.  **Why is it important to set `rerun_on_resume=True` for the orchestrator node?**
    *   **Answer:** Dynamic workflows are **resumable**. If a workflow is paused (e.g., waiting for human input inside a sub-node), the orchestrator itself might be stopped. By setting `rerun_on_resume=True`, you ensure that when the workflow starts again, the orchestrator logic re-evaluates which branch to take based on the saved state of its sub-nodes.

3.  **Can a dynamic workflow call another dynamic workflow?**
    *   **Answer:** Yes! In ADK 2.0, every `Workflow` and every `@node` function is just a **Node**. This allows for deep nesting and modularity: you can build complex systems by composing many small, testable dynamic workflows together.

</SolutionVault>
