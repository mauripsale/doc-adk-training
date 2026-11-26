---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 20: Cyclic Workflows (Iteration & Self-Correction) — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 20: Building an Essay Refinement System

## Goal

In this lab, you will build a self-improving agent system that uses a **Dynamic Workflow** to iteratively refine an essay. You will implement the powerful **"Critic -> Refiner"** pattern using a standard Python loop.

### The Architecture

1.  **Initial Writer Node:** An agent that creates the first draft.
2.  **Refinement Loop Node (`@node`):** A function that orchestrates the iteration:
    *   **Critic Node (`output_schema=CritiqueResult`):** Evaluates the draft using a structured Pydantic schema (`approved: bool`, `feedback: str`) so termination is 100% deterministic rather than relying on brittle string matching.
    *   **Refiner Node:** Applies `review.get("feedback", "")` to improve the draft.
    *   **Termination:** The loop breaks immediately when `review.get("approved")` is `True`, or after at most 3 iterations.

### Step 1: Create the Project Structure

<Setup/>

1.  **Create the project:**
    ```shell
    uv run adk create essay_refiner
    ```

### Step 2: Define the Structured Schema, Nodes, and Orchestrator

**Exercise:** Open `essay_refiner/agent.py`. Your task is to define the `CritiqueResult` Pydantic schema, the three specialist agents (each with `rerun_on_resume=True`), and the `@node(rerun_on_resume=True)` function that runs the bounded loop.

```python
# In agent.py (Starter Code)

from pydantic import BaseModel, Field
from google.adk import Agent, Context, Workflow
from google.adk.workflow import node

# 1. Define Structured Critique Schema
class CritiqueResult(BaseModel):
    approved: bool = Field(
        description="True ONLY when the draft satisfies all criteria and needs no further edits."
    )
    feedback: str = Field(
        description="Specific actionable revision notes if not approved, or brief praise if approved."
    )

# 2. Define the Specialist Agents
# IMPORTANT:
# - Every child Agent invoked via ctx.run_node() inside @node(rerun_on_resume=True)
#   MUST also set rerun_on_resume=True!
# - Write instructions in plain language describing the input, not with {template}
#   placeholders -- ctx.run_node()'s second argument becomes the node's input
#   content directly (not session state).

# TODO: Define the initial writer agent (model="gemini-3.8-flash", rerun_on_resume=True).
writer = ...

# TODO: Define the critic agent (model="gemini-3.8-flash", rerun_on_resume=True, output_schema=CritiqueResult).
critic = ...

# TODO: Define the refiner agent (model="gemini-3.8-flash", rerun_on_resume=True).
# It must rewrite the story based on the critique feedback.
refiner = ...

# 3. Define the Iterative Orchestrator
# rerun_on_resume=True is required on both @node and every child Agent called via ctx.run_node().
@node(rerun_on_resume=True)
async def refinement_orchestrator(ctx: Context, node_input: str):
    # Step A: Get the initial draft from 'writer' via await ctx.run_node().
    # Note: ctx.run_node()'s second argument is positional (there is no `input=` keyword).
    current_story = ...  # TODO: Call writer with f"Topic: {node_input}"

    # Step B: Run the loop (max 3 times)
    # 1. Call 'critic' with review = await ctx.run_node(critic, current_story).
    #    Remember: when output_schema=CritiqueResult is set, ctx.run_node() returns a
    #    validated Python dict (review["approved"], review["feedback"]), NOT a JSON
    #    string and NOT a BaseModel instance!
    # 2. Check `if review.get("approved"): break`
    # 3. Pass `review.get("feedback", "")` along with `current_story` into 'refiner'

    # TODO: Implement the bounded for-loop here

    return current_story

root_agent = Workflow(
    name="EssayRefiner",
    edges=[("START", refinement_orchestrator)]
)
```

### Step 3: Run and Test

1.  **Start the Dev UI from your parent `adk-training` directory:**
    ```shell
    uv run adk web
    ```
    *(Select `essay_refiner` from the agent dropdown in the UI).*
2.  **Observe the Trace:**
    Notice how each call to `ctx.run_node()` appears in the trace. You can see the story evolving iteration by iteration.

### Lab Summary

You have successfully built an iterative system!
- You used a **Dynamic Workflow** (`@node`) to manage execution logic.
- You used a **standard Python loop** to implement `max_iterations`.
- You learned how to pass data between nodes manually by passing the node's input as the **positional** second argument to `ctx.run_node()` (there is no `input` keyword).

### Self-Reflection Questions
- Why is the `max_iterations` limit a crucial safety feature for an iterative workflow? What could go wrong without it?
- In our pattern, the `refiner` returns a new version of the story. How would you modify the loop to keep track of *all* versions in the session state?
- Can you think of another problem, besides writing an essay, that could be solved effectively using a Dynamic Workflow loop?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="20">

# Lab 20 Solution: Building an Essay Refinement System

## Goal

This file contains the complete code for the `agent.py` script using the ADK 2.0 **Dynamic Workflow** pattern for iterative refinement.

### `essay_refiner/agent.py`

```python
from __future__ import annotations
from pydantic import BaseModel, Field
from google.adk import Agent, Context, Workflow
from google.adk.workflow import node

# 1. Structured Critique Schema
class CritiqueResult(BaseModel):
    approved: bool = Field(
        description="True ONLY when the draft satisfies all criteria and needs no further edits."
    )
    feedback: str = Field(
        description="Specific actionable revision notes if not approved, or brief praise if approved."
    )

# 2. Specialist Agents (Nodes)
# - Every child Agent invoked via ctx.run_node() inside @node(rerun_on_resume=True)
#   must also set rerun_on_resume=True!
# - Instructions describe the input in plain language rather than {template}
#   placeholders because ctx.run_node()'s second argument is passed directly
#   as node input content (not session state).
writer = Agent(
    name="writer",
    model="gemini-3.8-flash",
    rerun_on_resume=True,
    instruction="Write a 2-sentence story based on the topic you're given.",
)

critic = Agent(
    name="critic",
    model="gemini-3.8-flash",
    rerun_on_resume=True,
    output_schema=CritiqueResult,
    instruction="""
    You are a strict literary critic. Review the story you are given for vivid
    imagery, narrative arc, and conciseness (2-3 sentences).
    Set approved=True ONLY when the story satisfies every criterion and needs no edits;
    otherwise set approved=False and provide specific, actionable feedback.
    """,
)

refiner = Agent(
    name="refiner",
    model="gemini-3.8-flash",
    rerun_on_resume=True,
    instruction="""
    You are a writer revising a story based on feedback. You will be given
    the current story and the feedback on it. Rewrite the story addressing
    the feedback. Return ONLY the revised story, with no extra commentary.
    """,
)

# 3. Dynamic Workflow Orchestrator
# rerun_on_resume=True is required on both @node and every child Agent called via ctx.run_node().
@node(rerun_on_resume=True)
async def refinement_orchestrator(ctx: Context, node_input: str):
    # Phase 1: Initial Creation (second argument to ctx.run_node is positional)
    current_story = await ctx.run_node(writer, f"Topic: {node_input}")

    # Phase 2: Iterative Refinement Loop (bounded to at most 3 passes)
    for i in range(3):
        # A. Call the critic node -- output_schema returns a validated Python dict!
        review = await ctx.run_node(critic, current_story)

        # B. Structured boolean termination condition
        if review.get("approved"):
            break

        # C. Refinement using structured feedback
        feedback_notes = review.get("feedback", "")
        current_story = await ctx.run_node(
            refiner, f"STORY:\n{current_story}\n\nFEEDBACK:\n{feedback_notes}"
        )

    return current_story

# 4. Root Workflow Definition
root_agent = Workflow(
    name="EssayRefiner",
    edges=[("START", refinement_orchestrator)],
)
```

### Self-Reflection Answers

1.  **Why is the `max_iterations` limit a crucial safety feature for an iterative workflow? What could go wrong without it?**
    *   **Answer:** LLMs are non-deterministic. It is possible for the `critic` and `refiner` to get stuck in an endless cycle where the critic is never satisfied ("infinite loop"). Without a limit, the agent would run forever, consuming time and API credits. A Python `for` loop provides a guaranteed hard stop.

2.  **In our pattern, the `refiner` returns a new version of the story. How would you modify the loop to keep track of *all* versions in the session state?**
    *   **Answer:** You could use `ctx.session.state` to store an array of versions. Instead of just overwriting a local variable, you could do: `ctx.session.state.setdefault("versions", []).append(current_story)`.

3.  **Can you think of another problem, besides writing an essay, that could be solved effectively using a Dynamic Workflow loop?**
    *   **Answer:**
        *   **Code Debugging:** Write code -> Run tests -> If fail, provide error to refiner -> Loop until pass.
        *   **Fact Checking:** Generate claim -> Search for evidence -> If inconsistent, revise claim -> Loop.
        *   **Optimization:** Propose a solution -> Calculate cost/efficiency -> Refine solution -> Loop until target reached.

</SolutionVault>
