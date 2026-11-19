---
sidebar_position: 17
title: "Module 17: Structured Routing - Edges and Dictionaries"
pagination_label: "Module 17: Structured Routing (Edges & Dicts) — 📖 Theory & Overview"
---

# Module 17: Structured Routing - Edges and Dictionaries

![Structured Routing Hero (Light)](img/structured-routing-hero-light.webp#gh-light-mode-only)
![Structured Routing Hero (Dark)](img/structured-routing-hero-dark.webp#gh-dark-mode-only)
*Figure: High-speed intent routing through structured decision dictionaries and deterministic edge resolvers.*


## Theory

In Module 16, you learned how to define static paths. But what if you want your graph to branch based on a specific decision? 

While you can use **Dynamic Workflows** (Module 18) for total control, ADK 2.0 provides a more efficient middle ground: **Dictionary-based Routing**.

### Why use Deterministic Workflows?

1.  **Transparency:** The structure of your application is visible at a glance in the code (and in the Dev UI Graph View).
2.  **Efficiency:** Routing via a dictionary or a fixed list of edges is faster and cheaper than asking an LLM to decide the next step.
3.  **Reliability:** You eliminate the "hallucination" risk of an LLM choosing a non-existent path.

### Anatomy of a Workflow Graph

![Dictionary-Based Intent Routing Architecture (Light)](img/structured-routing-architecture-light.webp#gh-light-mode-only)
![Dictionary-Based Intent Routing Architecture (Dark)](img/structured-routing-architecture-dark.webp#gh-dark-mode-only)
*Figure: 4-stage pipeline showing query classification, route key emission, edge dictionary mapping, and specialist execution.*


A Workflow in ADK 2.0 is defined by two things:
1.  **Nodes:** The individual components (Agents, FunctionTools, or `@node` functions).
2.  **Edges:** The connections between nodes, defining the execution path.

#### Static Edges (Sequential)
The simplest edge is a tuple `("NodeA", "NodeB")`, which means "after NodeA finishes, run NodeB".

```python
from google.adk import Workflow

# A simple sequential pipeline: START -> Researcher -> Writer
my_workflow = Workflow(
    name="SequentialSystem",
    edges=[
        ("START", researcher_node),
        (researcher_node, writer_node)
    ]
)
```

#### Router Edges (Conditional Dictionary Routing)

You can use a **Python dictionary as the target of an edge** to branch dynamically to different specialist agents based on a classification decision — without having to write manual `if`/`else` logic for every branch.

However, a dictionary edge does **not** inspect a plain `Agent`'s raw text or Pydantic JSON automatically. Instead, ADK matches the dictionary keys against **`ctx.route`**, a special routing attribute on the workflow execution `Context` (`ctx`).

Because a plain `Agent` never sets `ctx.route` on its own, we use a lightweight **`@node` wrapper function** (a Python function decorated with `@node` from `google.adk.workflow`) to bridge the classifier agent and the router dictionary:

1. **`@node(rerun_on_resume=True)`**: Turns an `async def` Python function into a graph node. `rerun_on_resume=True` ensures the router runs again on subsequent turns in a multi-turn conversation.
2. **`await ctx.run_node(classifier_node, node_input)`**: Executes the classifier `Agent` programmatically and returns its structured `output_schema` result as a plain Python **`dict`** (e.g., `{"category": "technical"}`).
3. **`ctx.route = result["category"]`**: Tells the `Workflow` which key in the dictionary edge to follow.
4. **`return node_input`**: Separates *routing* from *data flow*. Returning `node_input` passes the user's original prompt unchanged to the chosen specialist agent, rather than overwriting it with the classification dict.

```python
from pydantic import BaseModel
from typing import Literal
from google.adk import Agent, Workflow, Context
from google.adk.workflow import node

class RequestType(BaseModel):
    category: Literal["technical", "billing", "other"]

# 1. Plain classifier Agent enforcing a strict output schema
classifier_node = Agent(
    name="classifier",
    model="gemini-3.8-flash",
    instruction="Classify the user request into 'technical', 'billing', or 'other'.",
    output_schema=RequestType,
)

# 2. Lightweight @node wrapper that sets ctx.route and forwards the original prompt
@node(rerun_on_resume=True)
async def classify_and_route(ctx: Context, node_input: str):
    result = await ctx.run_node(classifier_node, node_input)  # Returns a plain dict
    ctx.route = result["category"]                            # Sets the routing key
    return node_input                                         # Forwards original input

# 3. Workflow graph wiring the dictionary edge
my_workflow = Workflow(
    name="SmartRouter",
    edges=[
        ("START", classify_and_route),
        (classify_and_route, {
            "technical": tech_agent,
            "billing": billing_agent,
            "other": general_agent
        })
    ]
)
```

The specialist branches (`tech_agent`, `billing_agent`, `general_agent`) stay completely declarative — only the classifier needs this small glue function, keeping this pattern much simpler than a full Dynamic Workflow (Module 18), where *every* routing step is custom Python logic.

### The "START" and "END" Reserved Keywords
- **`START`**: The entry point of your workflow. Every workflow must have at least one edge originating from `"START"`.
- **`END`**: (Optional) Explicitly signals that the workflow has finished. If a node has no outgoing edges, the workflow ends automatically.

### Data Flow in Deterministic Workflows

In a deterministic `Workflow`, the output of one node is automatically passed as the input to the next node. 
- If `NodeA` returns a string, `NodeB` receives that string as its input.
- If you use a **Router Dictionary**, routing is decided separately from data flow: it's `ctx.route` (set explicitly, as shown above) that must match one of the dictionary's keys — not necessarily the value passed along as input to the next node.

### Key Takeaways
- **Deterministic Workflows** define fixed paths using the `edges` parameter.
- **Edges** can be simple tuples or use dictionaries for conditional routing — but the dictionary matches against `ctx.route`, which only a `@node` function can set. A plain `Agent`, even with a Pydantic `output_schema`, never sets it on its own.
- This approach is **preferred for well-defined business processes** where you want maximum predictability and lowest latency.
- You can mix and match: a node in a deterministic `Workflow` can itself be a dynamic `@node` workflow!
