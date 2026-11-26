---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 18: Dynamic Workflows (@node) — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 18: Building a Smart Support Router with Dynamic Workflows

## Goal

In this lab, you will build a conditional multi-step orchestration system using a **Dynamic Workflow** — doing something Module 17's fixed static `edges` cannot do:

1. Run `classifier` to detect the customer's sentiment (`"angry"`, `"neutral"`, or `"happy"`).
2. If the customer is **not** angry, simply call `ai_support` and return its technical answer.
3. If the customer **is** `"angry"`, execute a **dynamic 2-step chain**:
   * **First**, call `ai_support` to draft a quick technical troubleshooting note.
   * **Second**, pass *both* the customer's original message and that technical draft into `human_escalation`, so the escalation team responds with empathy **and** an immediate technical fix!

This shows the real superpower of `@node` + `ctx.run_node()`: chaining and combining multiple agent outputs in plain Python variables.

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

### Step 2: Implement the Dynamic Router

**Exercise:** Open `agent.py`. Complete the `TODO` placeholders to define the two specialist agents (`ai_support` and `human_escalation`), the `classifier` agent, and the `support_router_workflow` function using `@node` and `ctx.run_node()`.

```python
# In agent.py (Starter Code)

from __future__ import annotations
from pydantic import BaseModel
from google.adk import Agent, Workflow, Context
from google.adk.workflow import node
from typing import Literal

# ===== Specialist Agent Nodes =====

# TODO: Define ai_support (name="ai_support_bot") and human_escalation (name="human_escalation_team") agents.
# Hint: Set model="gemini-3.8-flash" and rerun_on_resume=True on EVERY child Agent called via ctx.run_node()!
# One answers technical questions clearly; the other apologizes to frustrated customers and includes any provided technical steps.
ai_support = ...
human_escalation = ...

# ===== 1. Define Sentiment Schema =====

# Define a Pydantic model for structured classification
class SentimentClassification(BaseModel):
    sentiment: Literal["angry", "neutral", "happy"]

# TODO: Create the classifier agent node using the schema above (remember rerun_on_resume=True!).
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
    
    # Step 2b: Dynamic Multi-Step Orchestration.
    # - If classification["sentiment"] == "angry":
    #     1. Call `ai_support` via ctx.run_node() to draft a preliminary technical fix.
    #     2. Combine `node_input` and that technical draft into a prompt, then
    #        call `human_escalation` via ctx.run_node() and return its response.
    # - Otherwise:
    #     Call `ai_support` directly via ctx.run_node() and return its response.
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

1.  **Return to the parent directory and start the Dev UI:**
    ```shell
    cd ..
    uv run adk web
    ```
    *(Select `support_router_v2` from the agent dropdown in the UI).*
2.  **Test the dynamic orchestration:**
    *   **Input:** "My internet is down, help!" -> Runs `classifier` -> calls `ai_support_bot` directly.
    *   **Input:** "THIS IS DISGUSTING! MY ROUTER IS STILL BROKEN!" -> Runs `classifier` -> calls `ai_support_bot` for a preliminary technical fix -> passes both the complaint and the fix to `human_escalation_team`!
3.  **Inspect the Workflow Graph:**
    In the Dev UI, open the **Graph View**. You will see the visual representation of your dynamic execution: the flow from the router node to the specific specialist agent.

### Lab Summary

By completing this lab, you have mastered the fundamental orchestration pattern of ADK 2.0:
*   Using **`@node`** to turn standard Python functions into workflow components.
*   Leveraging **`ctx.run_node()`** to execute agents and retrieve structured results directly.
*   Implementing **Programmable Routing** that combines AI classification with deterministic business rules.

### Self-Reflection Questions
- How does passing data with `ctx.run_node()` in a Dynamic Workflow differ from passing data with `output_key` in Static Edges (Module 17)?
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
from google.adk import Agent, Workflow, Context
from google.adk.workflow import node
from typing import Literal

# ===== 1. Specialist Agent Nodes =====
# Every child Agent invoked via ctx.run_node() inside @node(rerun_on_resume=True)
# must also set rerun_on_resume=True so multi-turn sessions re-run cleanly.

ai_support = Agent(
    name="ai_support_bot",
    model="gemini-3.8-flash",
    rerun_on_resume=True,
    instruction="You are a helpful customer support AI. Answer technical questions clearly.",
)

human_escalation = Agent(
    name="human_escalation_team",
    model="gemini-3.8-flash",
    rerun_on_resume=True,
    instruction=(
        "You are a senior human escalation rep handling a frustrated customer. "
        "Apologize sincerely, promise a follow-up call, and include any preliminary "
        "technical troubleshooting steps provided to you."
    ),
)

# ===== 2. Classifier Agent Node =====

class SentimentClassification(BaseModel):
    sentiment: Literal["angry", "neutral", "happy"]

classifier = Agent(
    name="classifier",
    model="gemini-3.8-flash",
    rerun_on_resume=True,
    instruction="Classify the sentiment of the user's latest message.",
    output_schema=SentimentClassification,
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

2.  **Why is it important to set `rerun_on_resume=True` for the orchestrator node (and its dynamically invoked child agents)?**
    *   **Answer:** Dynamic workflows are **resumable** across conversational turns. In ADK 2.0, setting `rerun_on_resume=True` on both the `@node` orchestrator and every child `Agent` called via `await ctx.run_node(...)` ensures that on subsequent user turns in the same session, both the orchestrator and its specialist sub-nodes re-execute cleanly instead of raising `ValueError: A node must have rerun_on_resume=True`.

3.  **Can a dynamic workflow call another dynamic workflow?**
    *   **Answer:** Yes! In ADK 2.0, every `Workflow` and every `@node` function is just a **Node**. This allows for deep nesting and modularity: you can build complex systems by composing many small, testable dynamic workflows together.

</SolutionVault>
