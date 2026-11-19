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

In Module 16, every edge ran unconditionally. Here, you want a **fork in the road** — like a `switch` statement in your graph:

```python
edges=[
    ("START", router),
    (router, {
        "fast_track": priority_agent,
        "standard": normal_agent,
    }),
]
```

**How does `Workflow` know which branch to pick?**
Look at the two separate things a `router` node does:
- **`ctx.route = ...`** → decides **WHERE** to go (matches a key in the dictionary).
- **`return ...`** → decides **WHAT** text to send to that next agent.

```text
User: "URGENT: server down!"
       │
       ▼
  ┌──────────┐
  │  router  │── ctx.route = "fast_track"  ──► picks `priority_agent` from dict
  │  (@node) │── returns "URGENT: server.."──► passes this prompt to `priority_agent`
  └──────────┘
```

In Python, you write the `router` as a small `@node` function (a decorator from `google.adk.workflow` that lets a Python function act as a graph node):

```python
from google.adk import Workflow, Context
from google.adk.workflow import node

@node(rerun_on_resume=True)  # Re-run on every new turn in a chat
async def check_urgency(ctx: Context, node_input: str):
    # 1. WHERE to go
    ctx.route = "fast_track" if "urgent" in node_input.lower() else "standard"
    # 2. WHAT to pass along (keep the user's original message)
    return node_input
```

##### Using an LLM Classifier Instead of an `if` Statement

What if you need Gemini to classify the intent instead of checking keywords? A regular `Agent` only generates text or JSON — it never sets `ctx.route` on its own. So the `@node` function simply calls the classifier `Agent` (`await ctx.run_node(...)`) and copies its result into `ctx.route`:

```python
from pydantic import BaseModel
from typing import Literal
from google.adk import Agent, Workflow, Context
from google.adk.workflow import node

class RequestType(BaseModel):
    category: Literal["technical", "billing", "other"]

# 1. Classifier Agent (returns JSON like {"category": "billing"})
classifier_node = Agent(
    name="classifier",
    model="gemini-3.8-flash",
    instruction="Classify the request as 'technical', 'billing', or 'other'.",
    output_schema=RequestType,
)

# 2. 3-line bridge: run classifier -> set ctx.route -> forward original prompt
@node(rerun_on_resume=True)
async def classify_and_route(ctx: Context, node_input: str):
    result = await ctx.run_node(classifier_node, node_input)  # Plain dict from output_schema
    ctx.route = result["category"]                            # WHERE to go
    return node_input                                         # WHAT to send

# 3. Wire the dictionary edge
my_workflow = Workflow(
    name="SmartRouter",
    edges=[
        ("START", classify_and_route),
        (classify_and_route, {
            "technical": tech_agent,
            "billing": billing_agent,
            "other": general_agent,
        }),
    ],
)
```

That's it: only those 3 lines of glue code are Python, while all your specialist agents stay purely declarative.

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
