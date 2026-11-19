---
sidebar_position: 20
title: "Module 20: Cyclic Workflows - Iteration and Self-Correction"
pagination_label: "Module 20: Cyclic Workflows (Iteration & Self-Correction) — 📖 Theory & Overview"
---

# Module 20: Cyclic Workflows - Iteration and Self-Correction

![Cyclic Workflows Hero (Light)](img/cyclic-workflows-hero-light.webp#gh-light-mode-only)
![Cyclic Workflows Hero (Dark)](img/cyclic-workflows-hero-dark.webp#gh-dark-mode-only)
*Figure: Iterative critique, evaluation, and self-correction loops with strict iteration guardrails.*


## Theory

### Iterative Refinement in ADK 2.0

Many real-world AI tasks — writing code, drafting legal summaries, or crafting essays — rarely produce a perfect result on the first try. Instead of accepting the first draft, you can let one agent **critique** the work and another agent **improve** it in a loop until it meets your quality bar.

In ADK 2.0, you build cyclic workflows using a **`@node` Dynamic Workflow** (from Module 18) with a standard Python **`for`** or **`while`** loop. Because the loop is plain Python, you have total control over termination conditions and safety guardrails like `max_iterations`.

### The Critic → Refiner Loop Pattern

![Evaluator-Optimizer Iteration Loop (Light)](img/cyclic-workflows-loop-light.webp#gh-light-mode-only)
![Evaluator-Optimizer Iteration Loop (Dark)](img/cyclic-workflows-loop-dark.webp#gh-dark-mode-only)
*Figure: Generator-Evaluator feedback architecture showing draft critique, rubric scoring thresholding, and iteration limits.*

The most common iterative architecture is the **Critic → Refiner** loop:

```python
from google.adk import Agent, Context, Workflow
from google.adk.workflow import node

# 1. Define the specialist agents
critic = Agent(
    name="critic",
    model="gemini-3.8-flash",
    instruction="Review the draft. Reply 'APPROVED' if great, otherwise give brief feedback.",
)
refiner = Agent(
    name="refiner",
    model="gemini-3.8-flash",
    instruction="Rewrite the draft using the provided feedback. Return only the improved text.",
)

# 2. Define the Orchestrator Node with a bounded Python loop
@node(rerun_on_resume=True)
async def refinement_workflow(ctx: Context, node_input: str):
    current_work = node_input

    # Bounded loop (max 5 iterations) prevents infinite loops and runaway API costs
    for i in range(5):
        print(f"--- Iteration {i + 1} ---")

        # Ask the Critic to review the current draft
        feedback = await ctx.run_node(critic, current_work)

        # Early exit condition
        if "APPROVED" in feedback:
            break

        # Ask the Refiner to improve the draft using the Critic's feedback
        current_work = await ctx.run_node(
            refiner, f"WORK:\n{current_work}\n\nFEEDBACK:\n{feedback}"
        )

    return current_work

# 3. Register the orchestrator in a Workflow
root_agent = Workflow(
    name="RefinementSystem",
    edges=[("START", refinement_workflow)],
)
```

### Why Use Python Loops in `@node` Workflows?

1.  **Zero Boilerplate:** Just write a normal Python `for` or `while` loop — no special loop DSL required.
2.  **Flexible Exit Conditions:** Stop on `"APPROVED"`, on a structured numeric score (`score >= 0.8`), or when the draft stops changing.
3.  **Built-in Cost Guardrails:** `for i in range(max_iterations)` guarantees the loop always terminates, even if the Critic is never satisfied.
4.  **Full Trace Visibility:** In the Dev UI, every `ctx.run_node()` call inside the loop shows up as its own trace step, letting you watch the draft improve iteration by iteration.

### Key Takeaways
- **Iterative tasks** require multiple passes of review and refinement.
- **Dynamic Workflows (`@node`)** are the modern way to implement loops in ADK 2.0.
- **Safety First:** Always use a `max_iterations` limit to prevent infinite loops and excessive API costs.
- **Node-to-Node passing:** The output of one iteration is manually passed as the input to the next via `ctx.run_node()`.

