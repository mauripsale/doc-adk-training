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

In Module 16, every edge was unconditional: when Node A finished, Node B always ran. But in real applications, you often want a **fork in the road** — running *only one* specialist based on a decision.

ADK 2.0 lets you express a fork in the road by passing a **Python dictionary** as the edge target:

```python
(router_node, {
    "fast_track": priority_agent,
    "standard": normal_agent,
})
```

##### How does the `Workflow` know which dictionary key to pick? (`ctx.route`)

Every node running inside a `Workflow` receives a `Context` object (**`ctx`**), which carries shared state and execution controls. One of its built-in properties is **`ctx.route`**: think of it as a **railroad switch lever**.

* When a node finishes, ADK checks `ctx.route`.
* If `ctx.route` is `"fast_track"`, ADK activates **only** the `"fast_track"` branch in the dictionary and ignores the others.

To set `ctx.route`, you write a small Python function decorated with **`@node`** (from `google.adk.workflow`), which turns a regular `async def` function into a graph node:

```python
from google.adk import Workflow, Context
from google.adk.workflow import node

@node(rerun_on_resume=True)
async def check_urgency(ctx: Context, node_input: str):
    # 1. Decide which branch to take by setting ctx.route
    if "urgent" in node_input.lower():
        ctx.route = "fast_track"
    else:
        ctx.route = "standard"

    # 2. Return the data to pass to the next node
    return node_input

my_workflow = Workflow(
    name="UrgencyRouter",
    edges=[
        ("START", check_urgency),
        (check_urgency, {
            "fast_track": priority_agent,
            "standard": normal_agent,
        }),
    ],
)
```

Notice two crucial details in those 6 lines:
1. **Why `return node_input`?** In a `Workflow`, whatever a node *returns* becomes the input to the next node. By returning `node_input` unchanged, the chosen specialist (`priority_agent` or `normal_agent`) still receives the user's original message — while `ctx.route` separately tells the `Workflow` *which* branch to activate.
2. **Why `rerun_on_resume=True`?** In a multi-turn conversation, each new user message resumes the workflow; `rerun_on_resume=True` ensures the router re-evaluates every new message instead of reusing the previous turn's decision.

##### Combining a Classifier `Agent` with a `@node` Router

Simple `if` statements work for keywords, but what if you need an LLM to understand user intent (e.g., *"My invoice is wrong"* → `"billing"`)?

A plain `Agent` only generates text or JSON — **it never sets `ctx.route` on its own**, even with `output_schema`. So you simply call your classifier `Agent` *inside* the `@node` function using `await ctx.run_node(...)`:

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

# 2. Small @node wrapper: calls the classifier, flips the ctx.route switch, forwards the prompt
@node(rerun_on_resume=True)
async def classify_and_route(ctx: Context, node_input: str):
    result = await ctx.run_node(classifier_node, node_input)  # Returns a plain dict, e.g. {"category": "billing"}
    ctx.route = result["category"]                            # Sets the dictionary key to follow
    return node_input                                         # Forwards original user message to specialist

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

> **Why `result["category"]` instead of `result.category`?** When `ctx.run_node()` executes an `Agent` with `output_schema`, ADK deserializes the JSON output into a plain Python `dict` (e.g., `{"category": "billing"}`), not a Pydantic model object.

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
