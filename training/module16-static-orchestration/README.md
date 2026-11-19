---
sidebar_position: 16
title: "Module 16: Static Orchestration - Linear and Parallel Edges"
pagination_label: "Module 16: Static Orchestration (Linear & Parallel) — 📖 Theory & Overview"
---

# Module 16: Static Orchestration - Linear and Parallel Edges

![Static Workflow Orchestration Hero (Light)](img/static-orchestration-hero-light.webp#gh-light-mode-only)
![Static Workflow Orchestration Hero (Dark)](img/static-orchestration-hero-dark.webp#gh-dark-mode-only)
*Figure: Deterministic graph orchestration utilizing linear execution, concurrent fan-out, and join synchronization.*


## Theory

In ADK 2.0, static orchestration is modeled directly through the **geometry of your `Workflow` graph** using **Edges**.

A `Workflow` is a deterministic execution engine that runs nodes in the exact order defined by their connections. By arranging `edges`, you can build linear pipelines, concurrent fan-out branches, or hybrid topologies combining both.

### 1. Sequential Flow (Linear Edges)

When you connect nodes in a chain, ADK executes them one after another:

```python
from google.adk import Workflow

# START -> researcher -> writer -> editor
my_pipeline = Workflow(
    name="SequentialSystem",
    edges=[
        ("START", researcher),
        (researcher, writer),
        (writer, editor)
    ]
)
```

> **Edge Shorthand:** You can also write a multi-hop chain as a single tuple `(A, B, C)`, which is shorthand for `(A, B)` followed by `(B, C)`. For example, `("START", researcher, writer, editor)` defines the exact same pipeline.

### 2. Parallel Flow (Fan-Out)

When multiple edges originate from the same source (such as `"START"` or an upstream node), ADK executes all target branches **concurrently**:

```python
# task_a and task_b run simultaneously
parallel_run = Workflow(
    name="ParallelSystem",
    edges=[
        ("START", task_a),
        ("START", task_b)
    ]
)
```

### 3. Synchronization (Fan-In with `JoinNode`)

![Linear and Parallel Graph Edges Pipeline (Light)](img/static-orchestration-pipeline-light.webp#gh-light-mode-only)
![Linear and Parallel Graph Edges Pipeline (Dark)](img/static-orchestration-pipeline-dark.webp#gh-dark-mode-only)
*Figure: Multi-stage workflow topology demonstrating concurrent branch execution converging into a barrier join node.*

When parallel branches finish, you often need to **wait for all of them** before running a final aggregation step. This pattern is called **Fan-In**, and it is handled by **`JoinNode`**.

A `JoinNode` acts as a synchronization barrier: it pauses execution until **every incoming edge** has completed, and only then fires its outgoing edge.

```python
from google.adk import Workflow
from google.adk.workflow import JoinNode

syncer = JoinNode(name="sync_point")

# Fan-out from START to task_a and task_b, converge at syncer, then run final_task
complex_graph = Workflow(
    name="HybridSystem",
    edges=[
        ("START", task_a, syncer),  # Shorthand for ("START", task_a) + (task_a, syncer)
        ("START", task_b, syncer),  # Shorthand for ("START", task_b) + (task_b, syncer)
        (syncer, final_task)
    ]
)
```

### 4. Passing Data Between Parallel Branches (`output_key` & `{placeholders}`)

When multiple parallel branches converge into a `JoinNode`, a single downstream agent needs a clean way to read **both** upstream results separately. ADK solves this using **Session State Interpolation**:

1. Each upstream branch saves its output under a unique key using **`output_key`** (introduced in Module 04).
2. The downstream agent references those saved keys directly inside its `instruction` string using curly braces **`{key_name}`**.

```python
weather_scout = Agent(
    name="weather_scout",
    model="gemini-3.8-flash",
    instruction="Summarize the weekend weather forecast for the requested city.",
    output_key="weather_info",   # Stored in session.state["weather_info"]
)

events_scout = Agent(
    name="events_scout",
    model="gemini-3.8-flash",
    instruction="List 3 popular cultural events happening this weekend in the city.",
    output_key="local_events",   # Stored in session.state["local_events"]
)

city_briefing = Agent(
    name="city_briefing",
    model="gemini-3.8-flash",
    instruction="Create a short weekend guide combining WEATHER: {weather_info} and EVENTS: {local_events}.",
)
```

Before sending the prompt to Gemini, ADK automatically replaces `{weather_info}` and `{local_events}` with the values stored in `session.state`.

### Why use Static Orchestration?

1.  **Performance:** Parallel execution reduces total latency to the duration of the slowest branch.
2.  **Predictability:** The path is fixed and code-defined; there is no risk of routing hallucinations.
3.  **Transparency:** The Dev UI Graph View gives you a 1:1 visual map of your business process.

### Key Takeaways
- **Edges define the flow:** Chain nodes sequentially or fan them out from a shared source for parallel execution.
- **`JoinNode`** acts as the barrier synchronization point for parallel branches (Fan-In).
- **`output_key` + `{placeholder}`**: Upstream branches save named outputs to session state, and downstream agents inject them cleanly into their `instruction` templates.
