---
sidebar_position: 18
title: "Module 18: Parallel Processing with ParallelAgent"
---

# Module 18: Parallel Processing with ParallelAgent

## Theory

### Parallel Workflows in ADK 2.0: Fan-Out and Join

In ADK 2.0, you don't need a special "Parallel" class to run tasks concurrently. Parallelism is a native feature of the **`Workflow`** graph. When you define multiple edges originating from the same node (or from `"START"`), the ADK executes those branches in parallel.

To synchronize these parallel branches and combine their results, you use a **`JoinNode`**.

**Key Concepts:**
*   **Fan-Out:** Define multiple paths from a single source. For example, `("START", node_a)` and `("START", node_b)` will cause both nodes to start simultaneously.
*   **JoinNode:** A special node that waits for all its incoming branches to finish. It collects the outputs from every parallel branch into a list.
*   **Fan-In:** Connecting the parallel nodes to a `JoinNode`, which then connects to a final synthesis node.

```python
from google.adk import Workflow
from google.adk.workflow import JoinNode

# 1. Define the Join point
syncer = JoinNode(name="result_gatherer")

# 2. Define the Graph
root_agent = Workflow(
    name="ParallelSystem",
    edges=[
        # Fan-out: Start three nodes in parallel
        ("START", research_node, syncer),
        ("START", analysis_node, syncer),
        ("START", audit_node, syncer),
        
        # Fan-in: Wait for all three, then run the merger
        (syncer, merger_node)
    ]
)
```

**When to Use Parallel Workflows:**
*   When tasks are independent and can run in any order.
*   When you need to gather data from multiple slow sources (LLMs or APIs) concurrently to minimize total latency.
*   When you need to perform diverse checks (e.g., security, style, logic) on the same input simultaneously.

### Key Takeaways
- **Parallelism is a Graph property:** Multiple outgoing edges = parallel execution.
- **Synchronization via `JoinNode`:** Use it to wait for multiple branches to complete.
- **Performance:** The total execution time is limited by the **slowest** branch, not the sum of all branches.
- **Error Handling:** If one of the parallel branches fails, the `JoinNode` may never receive all its expected inputs, potentially causing the workflow to hang or fail. It is a best practice to ensure parallel nodes have robust error handling or "failsafe" outputs to ensure the graph can always converge.
- **Structured State:** Each parallel node should still use a unique `output_key` if you want to store results individually in the session state for long-term reference.

