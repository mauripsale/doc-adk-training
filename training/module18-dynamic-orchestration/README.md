---
sidebar_position: 18
title: "Module 18: Dynamic Orchestration - Programmable Graphs with @node"
pagination_label: "Module 18: Dynamic Orchestration (@node) — 📖 Theory & Overview"
---

# Module 18: Dynamic Orchestration - Programmable Graphs with @node

![Dynamic Orchestration Hero (Light)](img/dynamic-orchestration-hero-light.webp#gh-light-mode-only)
![Dynamic Orchestration Hero (Dark)](img/dynamic-orchestration-hero-dark.webp#gh-dark-mode-only)
*Figure: Fully programmable multi-agent workflows executing dynamic routing and state evaluation with the `@node` decorator.*


## Theory

In Modules 16 and 17, you wired workflows using static `edges` and dictionary lookups (`ctx.route`). That works great when your routing rules fit in a fixed table.

**Dynamic Workflows** go one step further: instead of expressing routing rules through `edges` and `ctx.route`, **your Python function *is* the orchestrator**. You get the full power of standard Python (`if/else`, `for` loops, `try/except`) to decide which agents to run and in what order.

### Dynamic Workflows with `@node` and `ctx.run_node()`

![Dynamic Node Execution Engine (Light)](img/dynamic-orchestration-engine-light.webp#gh-light-mode-only)
![Dynamic Node Execution Engine (Dark)](img/dynamic-orchestration-engine-dark.webp#gh-dark-mode-only)
*Figure: Programmatic node invocation lifecycle with context state inspection, adaptive node dispatch, and result aggregation.*

In Module 17, you already saw `@node` and `await ctx.run_node(...)` used as a small bridge for `ctx.route`. In Module 18, **you drop `ctx.route` and dictionary edges completely** and orchestrate everything directly inside your `@node` function:

1.  **Define your specialist `Agent` nodes** as usual (`researcher`, `writer`, etc.).
2.  **Write an `async def` orchestrator function** decorated with `@node(rerun_on_resume=True)`.
3.  **Call any node directly with `await ctx.run_node(agent, input)`** — just like calling a normal Python function! It runs that agent and returns its response directly into a Python variable.
4.  **Wire `"START"` to your orchestrator** inside `Workflow(edges=[("START", my_orchestrator)])`.

```python
from google.adk import Agent, Workflow, Context
from google.adk.workflow import node

# 1. Define specialist agents
researcher = Agent(
    name="researcher",
    model="gemini-3.8-flash",
    instruction="Research key facts about the user's topic.",
)
writer = Agent(
    name="writer",
    model="gemini-3.8-flash",
    instruction="Turn the provided research notes into a short, engaging article.",
)

# 2. Build the Dynamic Orchestrator (pure Python control flow!)
@node(rerun_on_resume=True)
async def newsletter_workflow(ctx: Context, node_input: str):
    # Step A: Call researcher just like a Python function
    research_notes = await ctx.run_node(researcher, node_input)

    # Step B: Pass its output directly to writer
    final_article = await ctx.run_node(writer, research_notes)

    # Step C: Return the final answer to the user
    return final_article

# 3. Register the orchestrator as the entry point
root_agent = Workflow(
    name="NewsletterSystem",
    edges=[("START", newsletter_workflow)],
)
```

Notice how clean that is:
*   **No `ctx.route`:** You don't need dictionary keys; you just write Python `if`/`else` statements.
*   **No `output_key` boilerplate:** `await ctx.run_node(...)` returns the agent's output directly into your Python variable (`research_notes`), ready to pass to the next step.

### When to Choose Dynamic Workflows (`@node`)

1.  **Complex Control Flow:** Use standard `if/else` branching, `for` loops (e.g., retry or refine until quality passes), and `try/except` error handling.
2.  **Direct Variable Passing:** Pass outputs between agents using normal Python variables without needing `output_key` state templates.
3.  **Automatic Checkpointing & Tracing:** ADK's Workflow Runtime still tracks every `ctx.run_node()` call, giving you full trace visibility and graph inspection in the Dev UI.

### Bonus: Using a `@node` as an Agent Tool

Because every `@node` function is a first-class ADK component, you can also pass a `@node` directly into an `Agent`'s `tools=[...]` list without any extra wrapper — ADK wraps it automatically so Gemini can invoke it as a tool whenever needed:

```python
from google.adk import Agent, Context
from google.adk.workflow import node

@node
async def calculate_vip_discount(ctx: Context, tier: str) -> str:
    """Calculates the discount rate for a given customer tier."""
    return "20% VIP discount" if "VIP" in tier.upper() else "5% standard discount"

root_agent = Agent(
    model="gemini-3.8-flash",
    name="pricing_agent",
    instruction="Help customers with discounts using the calculate_vip_discount tool.",
    tools=[calculate_vip_discount],
)
```

### Key Takeaways
- **Dynamic Workflows** let you write orchestration logic in plain Python (`if/else`, loops) inside a `@node` function.
- **`await ctx.run_node(node, input)`** executes an agent or sub-workflow and returns its result directly into a Python variable.
- Use Module 16 for fixed pipelines, Module 17 for simple dictionary switches, and **Module 18** when routing depends on complex Python logic, loops, or multi-step decisions.
