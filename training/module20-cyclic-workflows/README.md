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

### The Evaluator → Optimizer Loop Pattern

![Evaluator-Optimizer Iteration Loop (Light)](img/cyclic-workflows-loop-light.webp#gh-light-mode-only)
![Evaluator-Optimizer Iteration Loop (Dark)](img/cyclic-workflows-loop-dark.webp#gh-dark-mode-only)
*Figure: Generator-Evaluator feedback architecture showing draft critique, rubric scoring thresholding, and iteration limits.*

The most common iterative architecture is the **Evaluator → Optimizer** loop (for example, a **Code Auditor → Code Fixer** pipeline):

```python
from pydantic import BaseModel
from google.adk import Agent, Context, Workflow
from google.adk.workflow import node

class AuditResult(BaseModel):
    passed: bool
    issues: str

# 1. Define the specialist agents
code_auditor = Agent(
    name="code_auditor",
    model="gemini-3.8-flash",
    instruction="Check the Python snippet for bugs or security issues. Set passed=True only if clean.",
    output_schema=AuditResult,
)
code_fixer = Agent(
    name="code_fixer",
    model="gemini-3.8-flash",
    instruction="Fix the provided Python snippet based on the listed issues. Return only the corrected code.",
)

# 2. Define the Orchestrator Node with a bounded Python loop
@node(rerun_on_resume=True)
async def code_review_loop(ctx: Context, node_input: str):
    current_code = node_input

    # Bounded loop (max 5 iterations) prevents infinite loops and runaway API costs
    for i in range(5):
        print(f"--- Review Iteration {i + 1} ---")

        # Ask the Auditor to review the current code (returns a plain dict)
        audit = await ctx.run_node(code_auditor, current_code)

        # Structured, reliable early exit condition
        if audit["passed"]:
            break

        # Ask the Fixer to improve the code using the Auditor's feedback
        current_code = await ctx.run_node(
            code_fixer, f"CODE:\n{current_code}\n\nISSUES:\n{audit['issues']}"
        )

    return current_code

# 3. Register the orchestrator in a Workflow
root_agent = Workflow(
    name="CodeReviewSystem",
    edges=[("START", code_review_loop)],
)
```

> **Pro Tip — Avoid Fragile Substring Checks:** If you use a plain-text evaluator instead of a Pydantic `output_schema`, avoid loose substring checks like `if "APPROVED" in feedback:` — if the model replies `"NOT APPROVED: needs more detail"`, `"APPROVED" in feedback` evaluates to `True` and exits early on a failed draft! Prefer either a boolean `output_schema` field (as above) or an exact check like `feedback.strip().upper() == "APPROVED"`.

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

