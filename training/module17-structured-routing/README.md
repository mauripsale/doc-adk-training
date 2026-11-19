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

In Module 16, every step in the graph ran automatically. Here, you want a **fork in the road** — like an office **switchboard** that routes incoming requests to the right department using a simple lookup table (a Python dictionary):

```python
edges=[
    ("START", classify_and_route),
    (classify_and_route, {
        "technical": tech_agent,
        "billing": billing_agent,
        "other": general_agent,
    }),
]
```

##### The Switchboard Analogy: Why we need a tiny `@node` function

Suppose a customer writes: *"I was charged twice on my invoice!"*

Gemini (`classifier_node`) is great at reading that message and replying `{"category": "billing"}`. **However, an `Agent` only generates text or JSON — it doesn't have hands to turn the switchboard dial.**

So we put a tiny 4-line Python function (`classify_and_route`) in front of the dictionary to act as the **switchboard operator**:
1. It asks Gemini which department should handle the message.
2. It dials that department's extension (**`ctx.route`**).
3. It transfers the customer on the line (**`return node_input`**) so the specialist hears the real question, not just the word `"billing"`.

> **Think of it in one sentence:** `ctx.route` is the **extension number** you dial; `return node_input` is the **customer on the line** you connect to that extension.

```python
from pydantic import BaseModel
from typing import Literal
from google.adk import Agent, Workflow, Context
from google.adk.workflow import node

class RequestType(BaseModel):
    category: Literal["technical", "billing", "other"]

# 1. The Classifier Agent
classifier_node = Agent(
    name="classifier",
    model="gemini-3.8-flash",
    instruction="Classify the request as 'technical', 'billing', or 'other'.",
    output_schema=RequestType,
)

# 2. The Switchboard Operator (@node)
@node(rerun_on_resume=True)
async def classify_and_route(ctx: Context, node_input: str):
    result = await ctx.run_node(classifier_node, node_input)  # a dict, not the Pydantic instance
    ctx.route = result["category"]
    return node_input

# 3. The Workflow Graph
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

##### Line-by-Line Breakdown

*   **`classifier_node = Agent(..., output_schema=RequestType)`**
    Creates a normal Gemini agent whose only job is to read the message and return guaranteed JSON matching `RequestType` (for example, `{"category": "billing"}`).
*   **`@node(rerun_on_resume=True)`**
    `@node` tells ADK to treat this Python function as a step in the graph. `rerun_on_resume=True` ensures that in a multi-turn chat, this router runs again for every new message the user sends instead of being skipped.
*   **`async def classify_and_route(ctx: Context, node_input: str):`**
    `async def` lets the function wait for Gemini without blocking. `ctx` is ADK's workflow control panel (where `ctx.route` lives), and `node_input` is the user's message arriving at this step (e.g., `"I was charged twice..."`).
*   **`result = await ctx.run_node(classifier_node, node_input)`**
    Calls `classifier_node` and waits for its answer. Because `classifier_node` uses `output_schema`, ADK gives you `result` as a plain Python dictionary (`{"category": "billing"}`), not a Pydantic class instance.
*   **`ctx.route = result["category"]`**
    Dials the extension on the switchboard. ADK reads `ctx.route` (`"billing"`), looks it up in the dictionary edge, and activates `billing_agent`.
*   **`return node_input`**
    Passes the customer's original message (`"I was charged twice..."`) untouched to `billing_agent`. Without this line (if you returned `result` instead), `billing_agent` would only see `{"category": "billing"}` and wouldn't know what the customer actually asked!

The specialist branches (`tech_agent`, `billing_agent`, `general_agent`) stay completely declarative — only those 4 lines of glue code are Python.

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
