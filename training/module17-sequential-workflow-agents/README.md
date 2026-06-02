---
sidebar_position: 17
title: "Module 17: Sequential Workflows - Building Agent Pipelines"
---

# Module 17: Sequential Workflows - Building Agent Pipelines

## Theory

### Beyond a Single Agent

Complex problems often require multiple steps or areas of expertise. Instead of creating one massive, monolithic agent, the ADK allows you to build **multi-agent systems** where several specialized agents collaborate.

For processes that follow a fixed, predictable sequence, the ADK provides the `SequentialAgent`.

### Sequential Workflows in ADK 2.0

In ADK 2.0, there is no separate `SequentialAgent` class. Instead, you build a sequential pipeline by defining a **linear set of edges** within a **`Workflow`**.

A `Workflow` is a deterministic controller that executes nodes according to the graph structure you define. When edges are linear (A -> B -> C), the ADK executes them one after another, in the exact order specified.

**Key Concepts:**
*   **Linear Edges:** Define a sequence like `[("START", node1), (node1, node2), (node2, node3)]`.
*   **Automatic Data Flow:** By default, the output of `node1` is passed as the `node_input` to `node2`.
*   **Shared State and `output_key`:** While data is passed directly between nodes, you can still use `output_key` to save a node's result into the global `ctx.session.state`. This allows later nodes to access data from much earlier steps using the `{key}` syntax in their prompts.

**When to Use a Sequential Workflow:**
*   When tasks MUST happen in a specific order.
*   When each step depends on the previous step's output.
*   When you need predictable, deterministic execution.
*   For building professional content creation or data processing pipelines.

### Key Takeaways
- **Sequential is a structure, not a class:** Use `Workflow` with linear edges.
- **Predictable execution:** Guaranteed order of operations.
- **Direct and Indirect Data Flow:** Pass data directly via node inputs or indirectly via `output_key` and session state.
- **Structured Pass-through:** Use Pydantic models in `output_schema` to pass robust JSON objects between nodes.

