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
from google.adk import Agent, node, Context, Workflow

# 1. Specialist Agents (Nodes)
writer = Agent(
    name="writer",
    model="gemini-3.5-flash",
    instruction="Write a 2-sentence story about: {topic}"
)

# ... [critic and refiner stay the same] ...

# 2. Dynamic Workflow Orchestrator
@node
async def refinement_orchestrator(ctx: Context, initial_topic: str):
    # Phase 1: Initial Creation
    # We pass the 'initial_topic' as input to the writer node.
    current_story = await ctx.run_node(writer, input={"topic": initial_topic})
    
    # Phase 2: Iterative Refinement Loop
    for i in range(3):
        # A. Call the critic node
        feedback = await ctx.run_node(critic, input=current_story)
        
        # B. Termination Condition
        if "APPROVED" in feedback:
            break
            
        # C. Refinement
        current_story = await ctx.run_node(refiner, input={
            "story": current_story,
            "feedback": feedback
        })
        
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
