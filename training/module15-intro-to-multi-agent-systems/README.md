---
sidebar_position: 15
title: "Module 15: Introduction to Multi-Agent Systems"
pagination_label: "Module 15: Introduction to MAS — 📖 Theory & Overview"
---

# Module 15: Introduction to Multi-Agent Systems

> **🧭 Where We Are in Part 3:** Welcome to **Part 3: Multi-Agent Systems**! Here in **Chapter A (Modules 15–16)**, we start with **LLM-Driven Agent Teams**, where a coordinator `Agent` dynamically delegates work to specialist `sub_agents`. Later in **Chapter B (Modules 17–20)**, you will build deterministic and programmable workflows where your graph and Python code control the exact execution order.

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

### The Master Map of Multi-Agent Systems in ADK 2.0

In ADK 2.0, every multi-agent architecture falls into one of **three clear families**, which you will master step by step across Part 3:

| Chapter | Modules | Who Controls Routing? | Core Pattern | When to Choose It |
| :--- | :--- | :--- | :--- | :--- |
| **A. LLM-Driven Agent Teams** | **15 – 16** | **Gemini decides dynamically** based on specialist descriptions | Coordinator `Agent` + `sub_agents` & collaboration modes | Conversational triage, open-ended requests, interactive sub-tasks. |
| **B. Graph & Code Workflows** | **17 – 20** | **Your graph / Python code decides** deterministically | Sequential/parallel pipelines, Python orchestrators, dictionary switches, loops | Fixed business steps, parallel fan-out/fan-in, multi-step Python logic, iterative refinement. |
| **C. Distributed MAS** | **21** | **Cross-service network calls** over HTTP | Remote network proxy agents & tool wrappers | Agents owned by separate teams or running as independent microservices. |

### Your First Multi-Agent Pattern: `sub_agents` Delegation

Let's start with the simplest, most intuitive pattern — **LLM-Driven Delegation** using `sub_agents`:

1. **Define Specialist Agents:** Create focused `Agent` instances, giving each one a crisp, action-oriented **`description`**.
2. **Define a Coordinator (`root_agent`):** Pass your specialists into the coordinator's **`sub_agents=[...]`** list.
3. **Automatic Hand-off Under the Hood:** ADK inspects every specialist's `name` and `description` and automatically injects a built-in `transfer_to_agent` capability into the coordinator. At runtime, Gemini reads the user's message, matches it against the specialists' descriptions, and hands off the conversation to the right expert!

```python
from google.adk import Agent

# 1. Define Specialist Agents (each with a clear `description` for discovery)
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

# 2. Define the Coordinator as root_agent and register specialists via `sub_agents`
root_agent = Agent(
    name="support_router",
    model="gemini-3.8-flash",
    instruction=(
        "Triage the user's request and transfer it to the appropriate specialist: "
        "'billing_expert' for payment issues or 'tech_support' for technical problems. "
        "If neither applies, answer politely yourself."
    ),
    sub_agents=[billing_expert, tech_support],
)
```

> **Why `description` matters so much:** Notice that `support_router` does not guess blindly — Gemini relies directly on each sub-agent's `description` to decide *which* specialist matches the user's intent. Writing clear, non-overlapping descriptions is one of the most important skills in MAS design.

All agents in the same session also share `ctx.session.state`, so any structured data saved via `output_key` (from Module 04) remains accessible across the team.

<KnowledgeCheck
  id="m15-mas-orchestration-specialists"
  question="In an ADK 2.0 multi-agent team using `sub_agents=[...]`, what is the primary role of each specialist agent's `description` parameter?"
  options={[
    "Gemini reads each sub-agent's description (via ADK's built-in transfer mechanism) to decide which specialist matches the user's request",
    "It forces all specialist agents to execute in parallel synchronously on every turn",
    "It merges all specialist tools into a single shared prompt template",
    "It disables session state sharing between specialist agents"
  ]}
  correctIndex={0}
  hint="Think about how the coordinator's LLM knows what each specialist actually does."
  explanation="When you register specialists in `sub_agents`, ADK exposes their `name` and `description` to the coordinator's LLM so Gemini can accurately transfer control to the matching expert."
/>

### Key Takeaways
- **Three MAS Families:** Part 3 progresses from LLM-driven `sub_agents` teams (15–16) to deterministic/programmable `Workflow` graphs (17–20) to distributed A2A services (21).
- **Specialization is Key:** Each agent should have a narrow, well-defined domain and toolset.
- **`sub_agents` + `description`:** Registering specialists in `sub_agents` enables automatic LLM-driven hand-offs guided by each specialist's `description`.