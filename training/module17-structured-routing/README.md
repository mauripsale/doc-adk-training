---
sidebar_position: 17
title: "Module 17: Structured Routing - Edges and Dictionaries"
---

# Module 17: Structured Routing - Edges and Dictionaries

## Theory

In Module 16, you learned how to define static paths. But what if you want your graph to branch based on a specific decision? 

While you can use **Dynamic Workflows** (Module 18) for total control, ADK 2.0 provides a more efficient middle ground: **Dictionary-based Routing**.

### Why use Deterministic Workflows?

1.  **Transparency:** The structure of your application is visible at a glance in the code (and in the Dev UI Graph View).
2.  **Efficiency:** Routing via a dictionary or a fixed list of edges is faster and cheaper than asking an LLM to decide the next step.
3.  **Reliability:** You eliminate the "hallucination" risk of an LLM choosing a non-existent path.

### Anatomy of a Workflow Graph

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

#### Router Edges (Conditional)
You can use a **dictionary as the target of an edge** to route to different nodes without writing a full `if`/`else` orchestrator. The key that gets matched isn't the node's raw output, though — it's `ctx.route`, a value the source node must set explicitly.

A plain `Agent` never sets `ctx.route` on its own, even with a Pydantic `output_schema` — so the source of a Router Edge needs to be a small `@node` function that runs the classifier and then sets the route from its result:

```python
from google.adk import Workflow, Context
from google.adk.workflow import node

# The classifier itself is a plain Agent with a Pydantic output_schema
classifier_node = Agent(..., output_schema=RequestType)

# A tiny @node wrapper is what actually makes the dictionary routing work
@node(rerun_on_resume=True)
async def classify_and_route(ctx: Context, node_input: str):
    result = await ctx.run_node(classifier_node, node_input)  # a dict, not the Pydantic instance
    ctx.route = result["category"]
    return node_input

# A system that routes based on ctx.route
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

The specialist branches (`tech_agent`, `billing_agent`, `general_agent`) stay fully declarative — only the classifier needs this small amount of glue code, which is what keeps this pattern meaningfully simpler than a full Dynamic Workflow (Module 18), where *every* routing decision is hand-written Python.

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
