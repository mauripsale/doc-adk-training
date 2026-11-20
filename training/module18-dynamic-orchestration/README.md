---
sidebar_position: 18
title: "Module 18: Dynamic Workflows - Programmable Graphs with @node"
pagination_label: "Module 18: Dynamic Workflows (@node) — 📖 Theory & Overview"
---

# Module 18: Dynamic Workflows - Programmable Graphs with `@node`

> **🧭 Where We Are in Part 3:** In **Module 17**, you built fixed pipelines (`A → B`, parallel fan-out + `JoinNode`) where every branch always ran. What if your workflow needs **runtime decisions** — like *"inspect an article draft first; if it passes length and quality checks, send it to the publisher; otherwise stop early"*? Welcome to **Dynamic Workflows (`@node`)**, where **standard Python code** (`if/else`, variables, functions) becomes your orchestrator!

![Dynamic Orchestration Hero (Light)](img/dynamic-orchestration-hero-light.webp#gh-light-mode-only)
![Dynamic Orchestration Hero (Dark)](img/dynamic-orchestration-hero-dark.webp#gh-dark-mode-only)
*Figure: Fully programmable multi-agent workflows executing dynamic routing and state evaluation with the `@node` decorator.*

## Theory

Static `edges` (Module 17) are unbeatable when every step in your pipeline is fixed ahead of time. When execution depends on runtime conditions, **Dynamic Workflows** let you write an ordinary Python `async def` function that calls agents just like regular Python functions!

### Building Your First `@node` Orchestrator

![Dynamic Node Execution Engine (Light)](img/dynamic-orchestration-engine-light.webp#gh-light-mode-only)
![Dynamic Node Execution Engine (Dark)](img/dynamic-orchestration-engine-dark.webp#gh-dark-mode-only)
*Figure: Programmatic node invocation lifecycle with context state inspection, adaptive node dispatch, and result aggregation.*

ADK 2.0 introduces two simple primitives for programmable orchestration:
*   **`@node`** (from `google.adk.workflow`): A decorator that turns any Python function into a graph node that a `Workflow` can run.
*   **`await ctx.run_node(target_node, input_data)`**: Executes an `Agent` (or another node) and returns its output directly into a Python variable!

```python
from google.adk import Agent, Workflow, Context
from google.adk.workflow import node

# 1. Define specialist agents as usual
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

# 2. Write a Python orchestrator decorated with @node
@node(rerun_on_resume=True)
async def newsletter_workflow(ctx: Context, node_input: str):
    # Step A: Run researcher and store its answer in a normal Python variable
    research_notes = await ctx.run_node(researcher, node_input)

    # Step B: Use standard Python if/else or string formatting freely!
    if len(research_notes) < 50:
        return "Not enough public information found on this topic."

    # Step C: Pass research_notes directly into writer and return its final article
    final_article = await ctx.run_node(writer, research_notes)
    return final_article

# 3. Register the orchestrator as the Workflow's entry point
root_agent = Workflow(
    name="NewsletterSystem",
    edges=[("START", newsletter_workflow)],
)
```

#### Line-by-Line Breakdown of the New Primitives

*   **`@node(rerun_on_resume=True)`**: Registers `newsletter_workflow` as a workflow node. Setting `rerun_on_resume=True` ensures that in a multi-turn conversation, this orchestrator runs fresh on every new message the user sends rather than being skipped.
*   **`async def newsletter_workflow(ctx: Context, node_input: str):`**:
    *   `ctx: Context` is ADK's runtime control object (giving you `ctx.run_node(...)` and `ctx.session.state`).
    *   `node_input: str` is the incoming user message (because `"START"` connects to this function).
*   **`await ctx.run_node(researcher, node_input)`**: Runs `researcher` with `node_input` as its prompt and returns the result directly:
    *   If the agent returns plain text, you get a `str`.
    *   If the agent has a Pydantic `output_schema`, ADK automatically parses the JSON and returns a plain Python **`dict`** (e.g., `result["approved"]`).
*   **`return final_article`**: Whatever your `@node` function returns is emitted as the workflow's final response to the user!

### When to Choose Dynamic `@node` Workflows

1.  **Multi-Step Conditional Chains:** Run Agent A, inspect or combine its result in Python, and conditionally pass enriched context to Agent B.
2.  **Direct Variable Passing:** No need for `output_key` or `{placeholder}` templates — outputs live in normal Python variables.
3.  **Full Trace Visibility:** Even though routing happens in Python, ADK's Workflow Runtime still records every `ctx.run_node()` call in the Dev UI **Trace** tab!

### Bonus: Using a `@node` as an Agent Tool

Because every `@node` function is a first-class ADK component, you can also pass a `@node` directly into an `Agent`'s `tools=[...]` list without any extra wrapper:

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

<KnowledgeCheck
  id="m18-dynamic-run-node"
  question="When `await ctx.run_node(topic_checker, node_input)` executes an `Agent` configured with a Pydantic `output_schema`, what Python type does `run_node()` return at runtime?"
  options={[
    "A raw unparsed XML string",
    "A plain Python `dict` matching the schema fields (accessed via `result['field']`)",
    "An unawaited coroutine object",
    "None — results can only be read from disk"
  ]}
  correctIndex={1}
  hint="Remember how structured outputs are deserialized by `ctx.run_node()`."
  explanation="When an `Agent` uses `output_schema`, `await ctx.run_node()` validates the JSON output and returns it directly as a plain Python `dict` (so you access fields with `result['key']` rather than dot notation)."
/>

### Key Takeaways
- **`@node(rerun_on_resume=True)`** turns a standard `async def` Python function into a programmable workflow orchestrator.
- **`await ctx.run_node(node, input)`** executes any agent and returns its output directly (`str`, or `dict` when `output_schema` is set).
- Use Module 17 for fixed pipelines, and **Module 18** when orchestration requires conditional multi-step Python logic!
