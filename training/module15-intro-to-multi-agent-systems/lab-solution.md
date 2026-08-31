---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 15 Solution: Designing a Multi-Agent System

## Goal

This lab was a conceptual design exercise. There is no single "correct" solution, but this file provides a more detailed example of the design planned in the lab, prioritizing the Python-first approach.

### Python Design (Primary Approach)

Here is a more fleshed-out version of the agent designs as they would be implemented in Python files using ADK 2.0 patterns.

#### `greeting_system/agent.py` (The Router and Workflow)

```python
from google.adk import Agent, Workflow
from . import spanish_greeter_agent

# The Router Node
router = Agent(
    name="router_agent",
    model="gemini-3.5-flash",
    instruction="""
You are a language routing specialist. Your primary function is to identify the language requested by the user and delegate the task to the correct sub-node.

Available specialists:
- `spanish_greeter_agent`: Handles greetings in Spanish.

Your rules:
1.  If the user requests a greeting in Spanish, you MUST transfer control to the `spanish_greeter_agent`.
2.  If the language is not supported, politely inform the user.
""",
    sub_agents=[spanish_greeter_agent.agent] # Crucial for discovery
)

# The System Graph
# In ADK 2.0, the Workflow orchestrates the nodes.
root_agent = Workflow(
    name="GreetingSystem",
    edges=[("START", router)]
)
```

#### `greeting_system/spanish_greeter_agent.py` (The Specialist Node)

```python
from google.adk import Agent

agent = Agent(
    name="spanish_greeter_agent",
    model="gemini-3.5-flash",
    description="This agent is an expert at providing warm greetings in Spanish.",
    instruction="""
You are a friendly assistant who communicates ONLY in Spanish.
Provide a single, warm greeting and then stop.
"""
)
```

### Self-Reflection Answers

1.  **What is the most important piece of information that allows the `router_agent` to decide which specialist to delegate to?**
    *   **Answer:** The **`description`** field of the sub-node. In the ADK 2.0 graph, when an agent performs a transfer, it looks at the descriptions of all registered `sub_agents` to decide where to route the request.

2.  **How would you extend this system to support a new language, like French? What new files or modifications would you need to make?**
    *   **Answer:** 
        1. Create `french_greeter_agent.py`.
        2. Register it in the `router_agent`'s `sub_agents` list.
        3. Since we are using LLM-driven delegation, the `Workflow` graph stays the same, but the "pool" of available nodes grows.

3.  **This lab uses LLM-driven delegation (agent transfer). What might be the advantages or disadvantages of this approach compared to the `router_agent` using an `AgentTool` to explicitly call the `spanish_greeter_agent`?**
    *   **Answer:** Agent Transfer (via `sub_agents`) is a permanent, one-way handoff -- once `router_agent` transfers to `spanish_greeter_agent`, the specialist is the active agent for the rest of the run and `router_agent` never regains control. That's fine here, since a greeting is genuinely a one-shot exchange. But if `router_agent` needed to, say, greet the user AND then look something else up via a *different* specialist in the same turn, Agent Transfer would leave it stuck on `spanish_greeter_agent` with no way back. An `AgentTool(agent=spanish_greeter_agent)` would instead let `router_agent` call the greeter like a function, get its greeting back, and stay in control to make further calls or compose a combined response -- at the cost of an extra LLM reasoning step to decide when to call the tool, versus the framework handling the transfer automatically. This distinction -- and the same bug you'd hit by registering multiple specialists as `sub_agents` and expecting call-and-return -- is covered in depth in Module 19.
    *   For a related question -- Agent Transfer vs. a fully **Deterministic Workflow** (extracting a routing key with no LLM reasoning at all) -- see the pattern-comparison table in Module 21.5: Agent Transfer suits natural language where the "key" isn't obvious and the LLM needs to understand intent, while a Deterministic Workflow (Module 16) is faster and more reliable when you can extract a clear key (like a language code) without an LLM reasoning step.
