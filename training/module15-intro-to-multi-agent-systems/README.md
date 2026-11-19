---
sidebar_position: 15
title: "Module 15: Introduction to Multi-Agent Systems"
pagination_label: "Module 15: Introduction to MAS — 📖 Theory & Overview"
---

# Module 15: Introduction to Multi-Agent Systems

![Multi-Agent Systems Hero (Light)](img/multi-agent-systems-hero-light.webp#gh-light-mode-only)
![Multi-Agent Systems Hero (Dark)](img/multi-agent-systems-hero-dark.webp#gh-dark-mode-only)
*Figure: Architectural transition from monolithic agent bottlenecks to distributed, specialized Multi-Agent Systems.*


## Theory

### Beyond a Single Agent

So far, you've built single, specialized agents. This is a great start, but the true power of the ADK is unlocked when you begin to compose multiple agents into a **Multi-Agent System (MAS)**.

As applications grow, trying to pack all the logic, tools, and instructions into a single monolithic agent becomes difficult to manage, debug, and scale. Imagine a customer support bot that needs to handle billing, technical support, and sales. A single agent trying to do all of this would have an incredibly complex instruction prompt and a confusing mix of tools.

A much better approach is to break down the problem.

### The Power of Specialization and Collaboration

![Monolithic vs Multi-Agent Architecture (Light)](img/monolithic-vs-multi-agent-light.webp#gh-light-mode-only)
![Monolithic vs Multi-Agent Architecture (Dark)](img/monolithic-vs-multi-agent-dark.webp#gh-dark-mode-only)
*Figure: Structural breakdown of a single monolithic agent versus a decomposed multi-agent team with clean cognitive boundaries.*


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

### How Multi-Agent Systems Work in ADK 2.0

Up to this point, you have built single `Agent` applications where `root_agent` handles everything on its own. In ADK 2.0, multi-agent systems are built natively around a **Graph Execution Model** managed by the **Workflow Runtime**.

Rather than cramming dozens of tools and instructions into one prompt, you compose independent **Nodes** inside a **`Workflow`** graph and connect them with **Edges** — all sharing the same session state.

#### 1. The Three Core Building Blocks

1. **Nodes (The Workers):**
   A node is any executable unit in your system. In ADK 2.0, a node is typically an **`Agent`** (LLM-powered reasoning with its own `instruction`, `model`, and `tools`) or a custom Python **`@node`** function (covered in Module 18).
2. **`Workflow` (The Graph Container):**
   `Workflow` is the top-level orchestrator that replaces a standalone `Agent` as your `root_agent`. It holds the graph topology and drives execution from node to node.
3. **Edges (The Execution Paths):**
   Edges are directed pairs `(source, target)` that tell the `Workflow` where execution starts and how control flows. Every workflow begins at the reserved **`"START"`** entry point — for example, `("START", router)` means the `router` node executes first when a user sends a message.

#### 2. Two Ways Agents Collaborate

Depending on how much control you want over routing, ADK 2.0 supports two complementary collaboration mechanisms:

*   **Dynamic LLM Transfer (`sub_agents`):**
    When you pass `sub_agents=[billing_expert, tech_support]` to an `Agent`, ADK automatically registers those specialists and exposes their **`name`** and **`description`** to the parent agent's LLM via a built-in transfer mechanism (`transfer_to_agent`). At runtime, Gemini reads the user request, inspects each specialist's `description`, and dynamically decides whether to handle the request itself or transfer control to a specialist.
*   **Explicit Graph Routing (`edges` & `@node`):**
    When you want deterministic, predictable pipelines (A → B → C), parallel fan-out, or code-driven branching, you wire nodes directly using `Workflow` `edges` or call `ctx.run_node(specialist_agent)` inside a `@node` function. You will master these patterns in Modules 16–18.

#### 3. Shared Session State Across Nodes

Because all nodes in a `Workflow` run within the same session, they share `ctx.session.state`. An upstream specialist can save structured results using `output_key` (introduced in Module 04), and downstream agents or router nodes can immediately read that data without re-parsing the conversation.

#### 4. The "Specialist + Orchestrator" Pattern in Practice

Below is the canonical ADK 2.0 Multi-Agent blueprint combining a `Workflow` entry point with an LLM-driven orchestrator and two domain specialists:

```python
from google.adk import Agent, Workflow

# 1. Define Specialist Nodes (each with a clear `description` for discovery)
billing_expert = Agent(
    name="billing_expert",
    model="gemini-3.8-flash",
    description="Handles invoices, refunds, and payment questions.",
    instruction="You are a billing specialist. Help the user with payment issues.",
)

tech_support = Agent(
    name="tech_support",
    model="gemini-3.8-flash",
    description="Handles bugs, login errors, and technical troubleshooting.",
    instruction="You are a technical support engineer. Diagnose and resolve technical issues.",
)

# 2. Define the Orchestrator (Router) and register specialists via `sub_agents`
router = Agent(
    name="router",
    model="gemini-3.8-flash",
    instruction=(
        "Triage the user's request and transfer it to the appropriate specialist: "
        "'billing_expert' for payment issues or 'tech_support' for technical problems."
    ),
    sub_agents=[billing_expert, tech_support],
)

# 3. Wrap the entry node in a Workflow graph
root_agent = Workflow(
    name="SupportSystem",
    edges=[("START", router)],
)
```

> **Why `description` matters so much:** Notice that `router` does not guess blindly — Gemini relies directly on each sub-agent's `description` to decide *which* specialist matches the user's intent. Writing crisp, non-overlapping descriptions is one of the most important skills in MAS design.

<KnowledgeCheck
  id="m15-mas-orchestration-specialists"
  question="In an ADK 2.0 multi-agent architecture using the Specialist/Orchestrator pattern, what is the primary purpose of passing specialist agents to the router's sub_agents list?"
  options={[
    "To register the nodes for discovery, routing schema generation, and telemetry within the Workflow graph",
    "To force all specialist agents to execute in parallel synchronously on every turn",
    "To merge all specialist tools into a single shared prompt template",
    "To disable session state isolation between specialist nodes"
  ]}
  correctIndex={0}
  hint="Think about how the router agent discovers available specialist targets and how the ADK runtime instruments them."
  explanation="In ADK 2.0, passing specialist agents to sub_agents registers them with the orchestrator, enabling automatic tool/transfer schema generation for Gemini and graph telemetry in the Workflow runtime."
/>

### Key Takeaways
- **Think in Graphs:** Multi-agent systems are collections of nodes orchestrated by a Workflow.
- **Specialization is Key:** Each node should have a narrow, well-defined purpose.
- **Workflow Runtime:** ADK 2.0 manages the transitions and state sharing between nodes automatically.
- **Modularity:** Breaking a large problem into multiple nodes makes your AI application easier to test, debug, and scale.