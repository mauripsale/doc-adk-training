---
sidebar_position: 21.5
title: "Module 21.5: MAS Knowledge Milestone - Architecture Choice"
pagination_label: "Module 21.5: MAS Architecture Milestone — 📖 Theory & Overview"
---

# Module 21.5: MAS Knowledge Milestone - Architecture Choice

> **🧭 Where We Are in Part 3:** You have now mastered all three chapters of **Part 3: Multi-Agent Systems** — LLM-Driven Agent Teams (15–16), Graph & Code Workflows (17–20), and Distributed A2A Graphs (21). This capstone milestone brings them together into a single **Architecture Decision Framework**!

![MAS Milestone Taxonomy Hero (Light)](img/mas-milestone-hero-light.webp#gh-light-mode-only)
![MAS Milestone Taxonomy Hero (Dark)](img/mas-milestone-hero-dark.webp#gh-dark-mode-only)
*Figure: Comprehensive Multi-Agent System architecture taxonomy and master design framework.*


## Theory

Congratulations! You have completed the core Multi-Agent Systems (MAS) section of the course. You have moved from thinking about single agents to designing complex networks of specialized nodes.

Before we move on to operational concerns like State, Evaluation, and Observability, let's recap the different architectural patterns you've mastered. Choosing the **right geometry** for your graph is the most important decision an AI Architect makes.

### MAS Architecture Recap

![MAS Architecture Selection Matrix (Light)](img/mas-milestone-matrix-light.webp#gh-light-mode-only)
![MAS Architecture Selection Matrix (Dark)](img/mas-milestone-matrix-dark.webp#gh-dark-mode-only)
*Figure: Architectural decision grid comparing conversational, linear/parallel, dynamic, routed, cyclic, and distributed MAS topologies.*


| Pattern | Module | Key ADK Primitives | Best For... |
| :--- | :--- | :--- | :--- |
| **Sub-Agent Delegation** | 15 | `Agent(sub_agents=[...])`, `description` | Simple conversational triage and one-way specialist hand-offs. |
| **Collaborative Teams** | 16 | `sub_agents`, `mode="single_turn"` / `"task"`, `rerun_on_resume=True` | Interactive multi-specialist teams with guaranteed return to the coordinator. |
| **Static Workflows** | 17 | `Workflow`, Linear/Parallel `edges`, `JoinNode`, `output_key` | Predictable, fixed business pipelines and concurrent fan-out/fan-in steps. |
| **Dynamic Workflows** | 18 | `@node(rerun_on_resume=True)`, `await ctx.run_node()` | Conditional multi-step chains and Python-driven orchestration logic. |
| **Structured Routing** | 19 | `Workflow`, Dictionary `edges`, `ctx.route` inside `@node` | Auditable 1-to-N branching where every route stays visible in the Graph View. |
| **Cyclic Workflows** | 20 | `@node` with bounded Python `for` loop + `ctx.run_node()` | Iterative Evaluator → Optimizer refinement and self-correction with cost caps. |
| **Distributed Graphs** | 21 | `to_a2a()`, `RemoteA2aAgent`, `AgentTool` | Cross-team microservices, independent scaling, and remote agent composition. |

### How to choose?

When designing a new system, ask yourself these four questions in order:

1.  **Is it open-ended conversational triage or an interactive sub-task?** If yes, start with **LLM-Driven Teams** (`sub_agents` + `mode` in Modules 15–16).
2.  **Is the execution path fixed or cleanly switchable on a graph?** If yes, use **Static Workflows** (Module 17) or **Dictionary Router Edges** (Module 19) for maximum speed and Graph View clarity.
3.  **Does orchestration require multi-step Python logic or iterative refinement loops?** If yes, use **Dynamic (`@node`)** or **Cyclic** workflows (Modules 18 & 20).
4.  **Do the agents live in separate codebases, teams, or clouds?** If yes, connect them over **Distributed A2A** (`RemoteA2aAgent` / `AgentTool` in Module 21).

<KnowledgeCheck
  id="m21_5-mas-architecture-choice"
  question="A regulated legal team needs to run Privacy and Liability checks concurrently on every contract, wait for both to finish, and then deterministically route high-risk contracts to a Senior Partner node. Which hybrid combination of ADK 2.0 primitives fits best?"
  options={[
    "A single monolithic Agent with temperature=2.0",
    "Parallel `Workflow` edges converging on a `JoinNode` (Module 17), followed by a `@node` setting `ctx.route` into a Dictionary Edge (Module 19)",
    "Bare `sub_agents` in default `chat` mode with no `Workflow`",
    "An unbounded `while True` loop with no exit condition"
  ]}
  correctIndex={1}
  hint="Combine concurrent fan-out/fan-in with auditable conditional branching."
  explanation="Parallel `Workflow` edges + `JoinNode` guarantee concurrent execution and barrier synchronization, while a `@node` router setting `ctx.route` into a Dictionary Edge keeps high-risk vs. low-risk branching 100% deterministic and auditable."
/>

### Key Takeaways
- There is no "one size fits all" architecture. Most production systems use a **Hybrid** approach.
- Always prefer the **simplest** geometry that solves the problem. Don't use a Dynamic workflow if a Static one suffices.
- Use the **Dev UI Graph View** to validate that your code matches your mental model.
