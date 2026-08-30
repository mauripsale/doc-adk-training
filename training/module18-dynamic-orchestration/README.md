---
sidebar_position: 18
title: "Module 18: Dynamic Orchestration - Programmable Graphs with @node"
---

# Module 18: Dynamic Orchestration - Programmable Graphs with @node

## Theory

In Modules 16 and 17, you learned how to orchestrate nodes using static edges and dictionary-based routing. While these methods are excellent for predictability, real-world complexity often requires more flexibility.

**ADK 2.0** provides **Dynamic Workflows**, which give you the full power of Python to define your own routing logic on the fly.

### Dynamic Workflows with `@node`

A Dynamic Workflow is a special type of node that can execute other nodes programmatically. You define it using the **`@node`** decorator and the **`Context`** object.

To build a programmable orchestrator in ADK 2.0, you follow these principles:
1.  **Define your components as Nodes:** Use `Agent`, `FunctionTool`, or standard functions decorated with `@node`.
2.  **Create an orchestrator function:** Decorate it with `@node(rerun_on_resume=True)`.
3.  **Use `ctx.run_node()`:** This method is the "heartbeat" of ADK 2.0. It executes a node and returns its output directly to your code.

```python
from google.adk import Agent, Workflow, Context
from google.adk.workflow import node

# 1. Define specialist agents (Nodes)
researcher = Agent(name="researcher", ...)
writer = Agent(name="writer", ...)

# 2. Build the Dynamic Orchestrator
@node(rerun_on_resume=True)
async def newsletter_workflow(ctx: Context, node_input: str):
    # Step A: Run the researcher node
    # ADK 2.0 returns the result directly!
    research_notes = await ctx.run_node(researcher, node_input)
    
    # Step B: Run the writer node
    final_article = await ctx.run_node(writer, research_notes)
    
    return final_article

# 3. Register the workflow
root_agent = Workflow(
    name="NewsletterSystem",
    edges=[("START", newsletter_workflow)]
)
```

### Why `@node` is superior to legacy methods

1.  **Pythonic Control Flow:** You can use standard `if/else` statements, `for` loops, and `try/except` blocks to manage your agents.
2.  **Simplified Data Passing:** `ctx.run_node()` returns data directly. You don't need to manually manage `output_key` for internal routing.
3.  **Automatic Checkpointing:** The ADK automatically saves the progress of each node. If execution is interrupted, it resumes exactly where it left off.
4.  **Observability:** The Workflow Runtime tracks every node execution, providing detailed traces in the Dev UI.

### Going Further: Using a Node as a Tool

You've built `@node`-based workflows that a parent graph orchestrates. ADK also lets a plain `Agent` call a `@node` directly as a tool — just list it in `tools=[...]`, no wrapper needed (ADK wraps it in an internal `NodeTool` automatically). Combined with `RequestInput`, a node-as-tool can even pause mid-call for human approval and resume on the next turn:

```python
from typing import Generator
from google.adk import Agent, Context
from google.adk.workflow import node
from google.adk.events import RequestInput
from google.adk.apps import App, ResumabilityConfig

@node(rerun_on_resume=True)
def apply_discount(ctx: Context, tier: str) -> Generator[str, None, str]:
    """Applies a discount for the given customer tier. Args: tier: the customer's tier."""
    resume_input = ctx.resume_inputs.get("confirm_vip")
    if "VIP" in tier and not resume_input:
        yield RequestInput(interrupt_id="confirm_vip", message=f"Apply VIP discount for '{tier}'?")
        return "pending"
    return "20% off applied" if resume_input else "5% off applied"

root_agent = Agent(
    model="gemini-3.5-flash",
    name="pricing_agent",
    instruction="Help customers with discounts using the apply_discount tool.",
    tools=[apply_discount],
)

app = App(
    name="pricing_app",
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)
```

`ResumabilityConfig` is still marked `@experimental`, so expect this API to keep evolving — treat it as a preview rather than a pattern to build on yet.

### Key Takeaways
- **Dynamic Workflows** allow defining complex orchestration logic using standard Python code decorated with `@node`.
- **`ctx.run_node()`** is the primary way to execute other agents or functions within a workflow.
- Use this pattern when routing depends on complex logic, loops, or external state that cannot be represented by a simple dictionary.
