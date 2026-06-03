---
sidebar_position: 19
title: "Module 19: Advanced Multi-Agent Architectures"
---

# Module 19: Advanced Multi-Agent Architectures

## Theory

### Combining Workflows: Nested Graphs

You have learned the fundamental multi-agent patterns: dynamic routing with a **Coordinator**, linear pipelines with **Sequential Edges**, and concurrent execution with **Parallel Edges** and **JoinNodes**. 

The true power of ADK 2.0 comes from **nesting workflows**. In the Graph Runtime, a **`Workflow`** object is itself a **Node**. This means you can build complex, modular systems by using one workflow as a single step inside another workflow's graph.

### The "Parallel Workflows" Pattern

A common advanced pattern is to run multiple, multi-step sub-workflows at the same time.

*   **Structure:** A parent `Workflow` defines multiple edges from `"START"` that each point to a different sub-`Workflow`.
*   **Use Case:** A content publishing system. 
    *   **Research Phase:** Three separate sub-workflows (e.g., News Research, Social Analysis, Expert Opinion) run concurrently. Each sub-workflow might have several internal nodes (Fetch -> Summarize -> Extract).
    *   **Generation Phase:** Once all research sub-workflows are complete (using a `JoinNode`), a final sequence of nodes handles writing, editing, and formatting.

```python
from google.adk import Workflow

# 1. Define Sub-Workflows
news_subgraph = Workflow(name="NewsResearch", edges=[...])
social_subgraph = Workflow(name="SocialResearch", edges=[...])

# 2. Use Workflows as Nodes in a Parent Graph
root_agent = Workflow(
    name="PublishingSystem",
    edges=[
        ("START", news_subgraph, research_joiner),
        ("START", social_subgraph, research_joiner),
        (research_joiner, article_writer_node)
    ]
)
```

This architecture is highly efficient and **modular**. Each sub-workflow can be developed, tested, and maintained independently.

### Key Takeaways
- **Workflows are Nodes:** Nest graphs to manage complexity.
- **High Modularity:** Each sub-workflow is a self-contained unit of logic.
- **Transparent Traceability:** The Dev UI allows you to drill down into nested workflows to see exactly what happened at every level of the system.
- **Scalability:** It's easier to reason about a system made of 3 workflows than a single graph with 50 nodes.