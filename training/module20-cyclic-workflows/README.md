---
sidebar_position: 20
title: "Module 20: Cyclic Workflows - Iteration and Self-Correction"
---

# Module 20: Cyclic Workflows - Iteration and Self-Correction

## Theory

### Iterative Refinement in ADK 2.0

In ADK 2.0, the legacy `LoopAgent` is superseded by **Dynamic Workflows** using the **`@node`** decorator. This allows you to use standard Python `for` or `while` loops to orchestrate iterative tasks.

This approach is more flexible because you have full control over the termination logic, and you can easily implement safety features like `max_iterations`.

### The Dynamic Loop Pattern

The most common pattern for iteration is the **Critic -> Refiner** loop. Instead of a dedicated class, you define it as a function:

```python
from google.adk import Context, Agent
from google.adk.workflow import node

# 1. Define the specialist nodes
critic = Agent(name="critic", ...)
refiner = Agent(name="refiner", ...)

# 2. Define the Orchestrator Node with a Python loop
# rerun_on_resume=True is required on every @node used with ctx.run_node().
@node(rerun_on_resume=True)
async def refinement_workflow(ctx: Context, node_input: str):
    current_work = node_input
    
    # Standard Python loop for max_iterations
    for i in range(5):
        print(f"--- Iteration {i+1} ---")
        
        # Call the Critic node. ctx.run_node()'s second argument is
        # positional -- there's no `input=` keyword.
        feedback = await ctx.run_node(critic, current_work)
        
        # Termination Condition
        if "APPROVED" in feedback:
            break
            
        # Call the Refiner node to improve the work
        current_work = await ctx.run_node(
            refiner, f"WORK:\n{current_work}\n\nFEEDBACK:\n{feedback}"
        )
        
    return current_work
```

### Why Dynamic Loops are Superior

1.  **Python Native:** No need to learn custom "Loop" classes; just use `for` or `while`.
2.  **Explicit Logic:** You can easily add complex exit conditions (e.g., "stop if the quality score is > 0.8" or "stop if the changes are minimal").
3.  **Resilience:** You can use standard try/except blocks inside the loop to handle errors in specific iterations.
4.  **Transparency:** In the Dev UI, each call to `ctx.run_node()` creates a new entry in the trace, allowing you to see exactly how the work improved over time.

### Key Takeaways
- **Iterative tasks** require multiple passes of review and refinement.
- **Dynamic Workflows (`@node`)** are the modern way to implement loops in ADK 2.0.
- **Safety First:** Always use a `max_iterations` limit to prevent infinite loops and excessive API costs.
- **Node-to-Node passing:** The output of one iteration is manually passed as the input to the next via `ctx.run_node()`.

