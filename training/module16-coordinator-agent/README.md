---
sidebar_position: 16
title: "Module 16: Building a Coordinator/Dispatcher Agent"
---

# Module 16: Building a Coordinator/Dispatcher Agent

## Theory

### The Coordinator Pattern

The most common and intuitive multi-agent design pattern is the **Coordinator/Dispatcher** (also known as a Router). In this pattern, one central `LlmAgent` acts as a manager or a switchboard. Its primary responsibility is not to perform tasks itself, but to understand an incoming request and delegate it to the correct specialist sub-agent.

This pattern is incredibly effective for building modular and maintainable systems. The coordinator provides a single point of entry, while the specialists handle the complex, domain-specific logic.

### Implementing the Coordinator Pattern in ADK 2.0

In ADK 2.0, the Coordinator is a **Node** within a **Workflow Graph**. 

#### 1. Establishing the Graph (`Workflow`)

The coordinator agent is usually the first node in the graph, connected to the `"START"` edge.

**Python (Primary Approach):**
In your `agent.py`, you define the specialist agents and the coordinator, then register them in a `Workflow`.

```python
from google.adk import Agent, Workflow
from . import billing_agent_module, tech_support_module

# The Coordinator Node
coordinator = Agent(
    name="coordinator_agent",
    model="gemini-3.5-flash",
    instruction="You are a router...",
    # Registering specialists for discovery
    sub_agents=[
        billing_agent_module.agent,
        tech_support_module.agent
    ]
)

# The Workflow Graph
root_agent = Workflow(
    name="SupportSystem",
    edges=[("START", coordinator)]
)
```

#### 2. The Key to Routing: `description`

The coordinator node uses the **`description`** field of its registered `sub_agents` to make routing decisions. The Workflow Runtime provides this metadata to the coordinator's LLM automatically.

**`billing_agent_module.py`:**
```python
agent = Agent(
    name="billing_agent",
    description="Handles all questions related to billing, invoices, and payments.",
    instruction="You are a billing expert..."
)
```

#### 3. The Magic of Agent Transfer

When the coordinator node decides to delegate, it triggers an **Agent Transfer**. The ADK 2.0 Workflow Runtime intercepts this request, pauses the coordinator node, and activates the chosen specialist node in the graph. 

Because both nodes are part of the same **Workflow**, the specialist automatically has access to the conversation context and responds directly to the user.

### Key Takeaways
- The **Coordinator** is a node that manages the entry point of a Workflow.
- **Agent Transfer** is the mechanism for handing off control between nodes in the graph.
- Clear **descriptions** are the "API" that allow the coordinator to discover and use other nodes.
- **Workflow Orchestration:** The `Workflow` class ties everything together, defining the "START" point and the pool of available nodes.

