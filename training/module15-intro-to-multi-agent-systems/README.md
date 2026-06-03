---
sidebar_position: 15
title: "Module 15: Introduction to Multi-Agent Systems"
---

# Module 15: Introduction to Multi-Agent Systems

## Theory

### Beyond a Single Agent

So far, you've built single, specialized agents. This is a great start, but the true power of the ADK is unlocked when you begin to compose multiple agents into a **Multi-Agent System (MAS)**.

As applications grow, trying to pack all the logic, tools, and instructions into a single monolithic agent becomes difficult to manage, debug, and scale. Imagine a customer support bot that needs to handle billing, technical support, and sales. A single agent trying to do all of this would have an incredibly complex instruction prompt and a confusing mix of tools.

A much better approach is to break down the problem.

### The Power of Specialization and Collaboration

A multi-agent system is an application where different, specialized agents collaborate to achieve a larger goal. Instead of one agent that does everything, you create a team of experts:

*   One agent is an expert in billing.
*   Another is an expert in technical support.
*   A third is an expert in sales.
*   And a "manager" or "coordinator" agent whose only job is to understand the user's initial request and route it to the correct specialist.

This design pattern offers significant advantages:

*   **Modularity:** Each agent is a self-contained unit with a clear purpose. Its instructions and tools are focused on a single domain.
*   **Maintainability:** If you need to update the billing logic, you only need to modify the billing agent, without any risk of breaking the technical support functionality.
*   **Reusability:** A well-defined "Billing Agent" can be reused in other applications across your organization.
*   **Scalability:** It's easier to reason about and scale a system of smaller, collaborating components than one giant, complex agent.

### How Agents Collaborate in ADK 2.0: The Workflow Runtime

In ADK 2.0, multi-agent collaboration is managed by the **Workflow Runtime**. Instead of a simple hierarchy, your application is a **Graph** where each agent is a **Node**.

#### 1. **The Graph Structure (`Workflow`)**
The `Workflow` class is the container for your multi-agent system. You define the relationships between nodes using **Edges**. 

#### 2. **Registration vs. Execution**
*   **Registration:** You still use the `sub_agents` list when defining an `Agent` or `Workflow`. This tells the framework which nodes are part of the system for discovery and telemetry.
*   **Execution:** The actual collaboration happens via **Routing**. 
    *   **Agent Transfer:** An agent can decide to transfer control to another node in the graph.
    *   **Programmatic Routing:** A `@node` or a deterministic `Workflow` can call `ctx.run_node(specialist_agent)` to delegate a task and receive the result.

#### 3. **The "Specialist" Pattern**
This is the most common MAS architecture. You have:
*   **Specialist Nodes:** Agents or tools focused on a single domain (e.g., `billing_expert`, `tech_support`).
*   **Orchestrator Node:** A node (often an `Agent` or a `@node` function) that analyzes the user input and routes the request to the appropriate specialist.

```python
from google.adk import Agent, Workflow

# Specialists
billing_expert = Agent(name="billing_expert", ...)
tech_support = Agent(name="tech_support", ...)

# The Orchestrator (Router)
# It uses sub_agents for registration/discovery
router = Agent(
    name="router",
    instruction="Route requests to 'billing' or 'technical' experts.",
    sub_agents=[billing_expert, tech_support]
)

# The Workflow Graph
root_agent = Workflow(
    name="SupportSystem",
    edges=[("START", router)]
)
```

### Key Takeaways
- **Think in Graphs:** Multi-agent systems are collections of nodes orchestrated by a Workflow.
- **Specialization is Key:** Each node should have a narrow, well-defined purpose.
- **Workflow Runtime:** ADK 2.0 manages the transitions and state sharing between nodes automatically.
- **Modularity:** Breaking a large problem into multiple nodes makes your AI application easier to test, debug, and scale.