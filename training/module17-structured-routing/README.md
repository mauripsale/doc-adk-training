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
To build a router without writing a full `@node` function, you can use a **dictionary as the target of an edge**. The key in the dictionary corresponds to the **output** of the previous node.

```python
from google.adk import Workflow

# A system that routes based on a classifier's output
my_workflow = Workflow(
    name="SmartRouter",
    edges=[
        ("START", classifier_node),
        (classifier_node, {
            "technical": tech_agent,
            "billing": billing_agent,
            "other": general_agent
        })
    ]
)
```

### The "START" and "END" Reserved Keywords
- **`START`**: The entry point of your workflow. Every workflow must have at least one edge originating from `"START"`.
- **`END`**: (Optional) Explicitly signals that the workflow has finished. If a node has no outgoing edges, the workflow ends automatically.

### Data Flow in Deterministic Workflows

In a deterministic `Workflow`, the output of one node is automatically passed as the input to the next node. 
- If `NodeA` returns a string, `NodeB` receives that string as its input.
- If you use a **Router Dictionary**, the output of the previous node must match one of the keys in the dictionary.

### Key Takeaways
- **Deterministic Workflows** define fixed paths using the `edges` parameter.
- **Edges** can be simple tuples or use dictionaries for conditional routing.
- This approach is **preferred for well-defined business processes** where you want maximum predictability and lowest latency.
- You can mix and match: a node in a deterministic `Workflow` can itself be a dynamic `@node` workflow!
