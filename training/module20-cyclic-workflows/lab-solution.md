---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 20 Solution: Building an Essay Refinement System

## Goal

This file contains the complete code for the `agent.py` script using the ADK 2.0 **Dynamic Workflow** pattern for iterative refinement.

### `essay_refiner/agent.py`

```python
from __future__ import annotations
from google.adk import Agent, Context, Workflow
from google.adk.workflow import node

# 1. Specialist Agents (Nodes)
# Note: these instructions describe the input in plain language rather than
# using {template} placeholders -- ctx.run_node()'s second argument becomes
# the node's input content directly, it does NOT populate {key} placeholders
# in the instruction (those are only filled from session state).
writer = Agent(
    name="writer",
    model="gemini-3.5-flash",
    instruction="Write a 2-sentence story based on the topic you're given."
)

critic = Agent(
    name="critic",
    model="gemini-3.5-flash",
    instruction="""
    You are a strict literary critic. Review the story you are given.
    If it is good, respond with exactly the word 'APPROVED' and nothing else.
    Otherwise, provide brief, actionable feedback on how to improve it.
    """
)

refiner = Agent(
    name="refiner",
    model="gemini-3.5-flash",
    instruction="""
    You are a writer revising a story based on feedback. You will be given
    the current story and the feedback on it. Rewrite the story addressing
    the feedback. Return ONLY the revised story, with no extra commentary.
    """
)

# 2. Dynamic Workflow Orchestrator
# rerun_on_resume=True is required on every @node used with ctx.run_node().
@node(rerun_on_resume=True)
async def refinement_orchestrator(ctx: Context, node_input: str):
    # Phase 1: Initial Creation
    # ctx.run_node()'s second argument is positional -- there's no `input=`
    # keyword.
    current_story = await ctx.run_node(writer, f"Topic: {node_input}")

    # Phase 2: Iterative Refinement Loop
    for i in range(3):
        # A. Call the critic node
        feedback = await ctx.run_node(critic, current_story)
        
        # B. Termination Condition
        if "APPROVED" in feedback:
            break
            
        # C. Refinement
        current_story = await ctx.run_node(
            refiner, f"STORY:\n{current_story}\n\nFEEDBACK:\n{feedback}"
        )
        
    return current_story

# 3. Root Workflow Definition
root_agent = Workflow(
    name="EssayRefiner",
    edges=[("START", refinement_orchestrator)]
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
