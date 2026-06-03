---
sidebar_position: 21.7
title: "Module 21.7: Collaborative Workflows - Native Agent Hand-offs"
---

# Module 21.7: Collaborative Workflows - Native Agent Hand-offs

## Theory

In previous modules, you learned how to orchestrate agents using **Coordinators** (Module 16) or **Deterministic Edges** (Module 21.6). ADK 2.0 introduces a third, highly dynamic way for agents to work together: **Collaborative Workflows**.

### What is a Collaborative Workflow?

In a Collaborative Workflow, agents are not just "tools" called by an orchestrator. They are peers that can **pass the conversation to each other** directly using a native `hand_off` mechanism.

Unlike the Coordinator pattern where one agent *always* stays in control, Collaborative Workflows allow for a "Relay Race" style of interaction.

### The `collaborators` Parameter

To enable this, you use the `collaborators` parameter in the `Agent` definition. This tells the ADK that these agents are allowed to hand off control to one another.

```python
from google.adk import Agent

# Agent A knows about Agent B
agent_a = Agent(
    name="sales_expert",
    collaborators=[agent_b],
    instruction="Handle sales queries. Hand off to tech_expert for technical details."
)

# Agent B knows about Agent A
agent_b = Agent(
    name="tech_expert",
    collaborators=[agent_a],
    instruction="Handle technical queries. Hand off to sales_expert for pricing."
)
```

### How it works: Native Hand-offs

When an agent is part of a collaborative group, the ADK automatically injects a `hand_off_to_<agent_name>` tool into its toolkit. 
1.  **Detection:** The LLM realizes it cannot fulfill a request (e.g., a Sales agent gets a deep technical question).
2.  **Invocation:** The agent calls the auto-generated `hand_off` tool.
3.  **Transition:** The Workflow Runtime immediately pauses the current agent and activates the collaborator.

### Why use Collaborative Workflows?

1.  **Dynamic Peer-to-Peer:** Perfect for scenarios where there is no clear "boss" agent.
2.  **Reduced Overhead:** You don't need a middle-man "Router" agent that consumes tokens just to decide where to go.
3.  **Natural Conversation:** The transition is seamless for the user, as the context is preserved across hand-offs.

### Key Takeaways
- **Collaborative Workflows** enable peer-to-peer agent transitions.
- The **`collaborators`** list defines the "circle of trust" for an agent.
- **Native Hand-offs** are powered by auto-generated tools managed by the Workflow Runtime.
- Use this pattern for **fluid, expert-led interactions** where agents need to bounce the user back and forth based on evolving needs.
