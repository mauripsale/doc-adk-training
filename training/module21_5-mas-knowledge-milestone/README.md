---
sidebar_position: 21.5
title: "Module 21.5: MAS Knowledge Milestone - Architecture Choice"
---

# Module 21.5: MAS Knowledge Milestone - Architecture Choice

## Theory

Congratulations! You have completed the core Multi-Agent Systems (MAS) section of the course. You have moved from thinking about single agents to designing complex networks of specialized nodes.

Before we move on to operational concerns like State, Evaluation, and Observability, let's recap the different architectural patterns you've mastered. Choosing the **right geometry** for your graph is the most important decision an AI Architect makes.

### MAS Architecture Recap

| Pattern | Module | Key ADK Primitives | Best For... |
| :--- | :--- | :--- | :--- |
| **Static Orchestration** | 16 | `Workflow`, Linear Edges, `JoinNode` | Predictable, fixed business processes with parallel steps. |
| **Structured Routing** | 17 | `Workflow`, Conditional Edges (Dict) | Workflows that branch based on deterministic model outputs. |
| **Dynamic Orchestration** | 18 | `@node`, `ctx.run_node()` | Complex logic, nested loops, and code-driven decision making. |
| **Collaborative Teams** | 19 | `sub_agents`, `mode="task"` | Fluid hand-offs where specialists manage their own task lifecycle. |
| **Cyclic Workflows** | 20 | Edges returning to previous nodes | Iterative refinement, self-correction, and "human-in-the-loop" review loops. |
| **Distributed Graphs** | 21 | `RemoteA2aAgent`, `to_a2a()` | Independent scaling, team-separated codebases, and cross-org collaboration. |

### How to choose?

When designing a new system, ask yourself these three questions:

1.  **Is the path predictable?** If yes, use **Static/Structured** edges for performance and clarity.
2.  **Does the logic require Python control flow (loops, try/except)?** If yes, use **Dynamic (@node)** workflows.
3.  **Do the agents need to live in different environments?** If yes, use **Distributed (A2A)**.

### Key Takeaways
- There is no "one size fits all" architecture. Most production systems use a **Hybrid** approach.
- Always prefer the **simplest** geometry that solves the problem. Don't use a Dynamic workflow if a Static one suffices.
- Use the **Dev UI Graph View** to validate that your code matches your mental model.
