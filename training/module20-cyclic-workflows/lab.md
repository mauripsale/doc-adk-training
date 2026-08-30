---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 20: Building an Essay Refinement System

## Goal

In this lab, you will build a self-improving agent system that uses a **Dynamic Workflow** to iteratively refine an essay. You will implement the powerful **"Critic -> Refiner"** pattern using a standard Python loop.

### The Architecture

1.  **Initial Writer Node:** An agent that creates the first draft.
2.  **Refinement Loop Node (`@node`):** A function that orchestrates the iteration:
    *   **Critic Node:** Evaluates the draft and provides feedback.
    *   **Refiner Node:** Applies feedback to improve the draft.
    *   **Termination:** The loop breaks if the Critic returns "APPROVED" or after 3 iterations.

### Step 1: Create the Project Structure

1.  **Create the project:**
    ```shell
    uv run adk create essay_refiner
    ```

### Step 2: Define the Nodes and Orchestrator

**Exercise:** Open `agent.py`. Your task is to define the specialist agents and the `@node` function that runs the loop.

```python
# In agent.py (Starter Code)

from google.adk import Agent, Context, Workflow
from google.adk.workflow import node

# 1. Define the Specialist Agents
# Note: write these instructions in plain language describing the input,
# not with {template} placeholders -- ctx.run_node()'s second argument
# becomes the node's input content directly, it does NOT populate {key}
# placeholders in the instruction (those only come from session state).

# TODO: Define the initial writer agent.
writer = ...

# TODO: Define the critic agent. 
# It must return 'APPROVED' if the work is good, or feedback otherwise.
critic = ...

# TODO: Define the refiner agent.
# It must rewrite the story based on feedback.
refiner = ...

# 2. Define the Iterative Orchestrator
# rerun_on_resume=True is required on every @node used with ctx.run_node().
@node(rerun_on_resume=True)
async def refinement_orchestrator(ctx: Context, node_input: str):
    # Step A: Get the initial draft from the 'writer'.
    # Note: ctx.run_node()'s second argument is positional, not a keyword
    # (there's no `input=` parameter).
    current_story = await ctx.run_node(writer, f"Topic: {node_input}")

    # Step B: Run the loop (max 3 times)
    # 1. Call the 'critic' with ctx.run_node(critic, current_story)
    # 2. Check if 'APPROVED' is in the feedback (break if so)
    # 3. Call the 'refiner' to improve 'current_story' based on feedback

    # [STUDENT TODO: Implement the loop here]

    return current_story

root_agent = Workflow(
    name="EssayRefiner",
    edges=[("START", refinement_orchestrator)]
)
```

### Step 3: Run and Test

1.  **Start the Dev UI:**
    ```shell
    uv run adk web .
    ```
2.  **Observe the Trace:**
    Notice how each call to `ctx.run_node()` appears in the trace. You can see the story evolving iteration by iteration.

### Lab Summary

You have successfully built an iterative system!
- You used a **Dynamic Workflow** (`@node`) to manage execution logic.
- You used a **standard Python loop** to implement `max_iterations`.
- You learned how to pass data between nodes manually using the `input` parameter of `ctx.run_node()`.

### Self-Reflection Questions
- Why is the `max_iterations` limit a crucial safety feature for an iterative workflow? What could go wrong without it?
- In our pattern, the `refiner` returns a new version of the story. How would you modify the loop to keep track of *all* versions in the session state?
- Can you think of another problem, besides writing an essay, that could be solved effectively using a Dynamic Workflow loop?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMjAtY3ljbGljLXdvcmtmbG93cy9sYWItc29sdXRpb24=`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module20-cyclic-workflows/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
