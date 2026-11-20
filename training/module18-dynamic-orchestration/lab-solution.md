---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 18 Solution: Building a Smart Support Router with Dynamic Workflows

## Goal

This file contains the complete code for the `agent.py` script in the Smart Support Router lab using the ADK 2.0 Dynamic Workflow pattern.

### `support_router_v2/agent.py`

```python
from __future__ import annotations
from pydantic import BaseModel
from google.adk import Agent, Workflow, Context
from google.adk.workflow import node
from typing import Literal

# ===== 1. Specialist Agent Nodes =====

ai_support = Agent(
    name="ai_support_bot",
    model="gemini-3.8-flash",
    instruction="You are a helpful customer support AI. Answer technical questions clearly."
)

human_escalation = Agent(
    name="human_escalation_team",
    model="gemini-3.8-flash",
    instruction=(
        "You are a senior human escalation rep handling a frustrated customer. "
        "Apologize sincerely, promise a follow-up call, and include any preliminary "
        "technical troubleshooting steps provided to you."
    )
)

# ===== 2. Classifier Agent Node =====

class SentimentClassification(BaseModel):
    sentiment: Literal["angry", "neutral", "happy"]

classifier = Agent(
    name="classifier",
    model="gemini-3.8-flash",
    instruction="Classify the sentiment of the user's latest message.",
    output_schema=SentimentClassification
)

# ===== 3. Build the Dynamic Workflow (The Orchestrator) =====

@node(rerun_on_resume=True)
async def support_router_workflow(ctx: Context, node_input: str):
    # Step 3a: Run the classifier node.
    # run_node() returns the structured output directly as a plain Python dict.
    classification: dict = await ctx.run_node(classifier, node_input)
    
    # Step 3b: Dynamic multi-step orchestration using plain Python control flow.
    if classification["sentiment"] == "angry":
        # Chain 2 agents dynamically: first draft a technical fix, then escalate with context!
        tech_draft = await ctx.run_node(ai_support, node_input)
        escalation_prompt = (
            f"Customer message: {node_input}\n\n"
            f"Preliminary technical analysis: {tech_draft}"
        )
        return await ctx.run_node(human_escalation, escalation_prompt)
    
    # Standard path: single call to AI support
    return await ctx.run_node(ai_support, node_input)

# ===== 4. Register the Workflow as the Root =====

root_agent = Workflow(
    name="SupportSystem",
    edges=[("START", support_router_workflow)]
)
```

### Self-Reflection Answers

1.  **How does passing data with `ctx.run_node()` in a Dynamic Workflow differ from passing data with `output_key` in Static Edges (Module 17)?**
    *   **Answer:** With Static Edges (Module 17), you save results into `session.state` via `output_key` and reference them via `{placeholders}` inside static instruction strings. In a Dynamic Workflow, `ctx.run_node()` returns the agent's output directly into a normal Python variable (a string, or a plain `dict` when using `output_schema`), so you can inspect, combine, or transform outputs in pure Python before passing them to the next node.

2.  **Why is it important to set `rerun_on_resume=True` for the orchestrator node?**
    *   **Answer:** Dynamic workflows are **resumable**. If a workflow is paused (e.g., waiting for human input inside a sub-node), the orchestrator itself might be stopped. By setting `rerun_on_resume=True`, you ensure that when the workflow starts again, the orchestrator logic re-evaluates which branch to take based on the saved state of its sub-nodes.

3.  **Can a dynamic workflow call another dynamic workflow?**
    *   **Answer:** Yes! In ADK 2.0, every `Workflow` and every `@node` function is just a **Node**. This allows for deep nesting and modularity: you can build complex systems by composing many small, testable dynamic workflows together.
