---
sidebar_position: 16
title: "Module 16: Static Orchestration - Linear and Parallel Edges"
---

# Module 16: Static Orchestration - Linear and Parallel Edges

## Theory

In ADK 2.0, orchestration is no longer about choosing between a "Sequential" or a "Parallel" agent. Instead, you design the **geometry of your graph** using **Edges**.

A `Workflow` is a deterministic engine that executes nodes based on these connections. By arranging your edges, you can create linear pipelines, concurrent branches, or a mix of both.

### 1. Sequential Flow (Linear Edges)

When you define edges in a chain, the ADK executes them one after another. Each node waits for the previous one to finish and receives its output as input.

```python
from google.adk import Workflow

# A -> B -> C
my_pipeline = Workflow(
    name="SequentialSystem",
    edges=[
        ("START", researcher),
        (researcher, writer),
        (writer, editor)
    ]
)
```

### 2. Parallel Flow (Fan-Out)

When multiple edges originate from the same source (like `"START"` or a specific node), the ADK triggers all target nodes **simultaneously**.

```python
# A and B start at the same time
parallel_run = Workflow(
    name="ParallelSystem",
    edges=[
        ("START", task_a),
        ("START", task_b)
    ]
)
```

### 3. Synchronization (The `JoinNode`)

When you have parallel branches, you often need to "wait" for all of them to finish before moving to a final step. This is called **Fan-In**, and it is handled by the **`JoinNode`**.

The `JoinNode` acts as a barrier: it will not fire its outgoing edge until **every incoming edge** has completed.

```python
from google.adk.workflow import JoinNode

syncer = JoinNode(name="sync_point")

# Fan-out to A and B, then converge at 'syncer' to run C
complex_graph = Workflow(
    name="HybridSystem",
    edges=[
        ("START", task_a, syncer),
        ("START", task_b, syncer),
        (syncer, final_task)
    ]
)
```

### Why use Static Orchestration?

1.  **Performance:** Parallel execution reduces total latency to the duration of the slowest branch.
2.  **Predictability:** The path is fixed and code-defined; there is no "hallucination" risk in the routing.
3.  **Transparency:** The Dev UI Graph View gives you a 1:1 visual map of your business process.

### Key Takeaways
- **Edges define the flow:** Chain them for sequential, branch them for parallel.
- **`JoinNode`** is the mandatory synchronization point for parallel branches.
- **Data Flow:** ADK 2.0 handles passing results between nodes automatically, ensuring a seamless pipeline.
