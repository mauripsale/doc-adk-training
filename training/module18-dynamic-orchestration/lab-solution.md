---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 21.5 Solution: Building a Smart Support Router with Dynamic Workflows

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
    *   **Answer:** In ADK 1.x, you had to set an `output_key` on an agent and then manually retrieve that data from the `ctx.session.state` dictionary in the parent agent. In ADK 2.0, `ctx.run_node()` returns the result of the node execution directly (as a string or a Pydantic object), making the data flow much more intuitive and "Pythonic".

2.  **Why is it important to set `rerun_on_resume=True` for the orchestrator node?**
    *   **Answer:** Dynamic workflows are **resumable**. If a workflow is paused (e.g., waiting for human input inside a sub-node), the orchestrator itself might be stopped. By setting `rerun_on_resume=True`, you ensure that when the workflow starts again, the orchestrator logic re-evaluates which branch to take based on the saved state of its sub-nodes.

3.  **Can a dynamic workflow call another dynamic workflow?**
    *   **Answer:** Yes! In ADK 2.0, every `Workflow` and every `@node` function is just a **Node**. This allows for deep nesting and modularity: you can build complex systems by composing many small, testable dynamic workflows together.
