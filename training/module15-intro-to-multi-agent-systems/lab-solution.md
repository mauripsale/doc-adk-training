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
        3. **Update the router's `instruction` text too, not just the `sub_agents` list.** As written, the instruction hardcodes the Spanish case ("If the user requests a greeting in Spanish, you MUST transfer control to the `spanish_greeter_agent`.") and never mentions French at all. Adding `french_greeter_agent` to `sub_agents` without touching the instruction means the router's LLM has no textual rule telling it when to use the new specialist -- it may never get routed to, even though it's technically registered. You either need to add an equivalent French rule to the instruction, or generalize the wording (e.g. "delegate to whichever specialist's description matches the requested language") so it scales without an instruction edit every time you add a language.
        4. Since we are using LLM-driven delegation, the `Workflow` graph structure itself stays the same, but the "pool" of available nodes -- and the instruction that references them -- grows.

3.  **This lab uses LLM-driven delegation (agent transfer). What might be the advantages or disadvantages of this approach compared to the `router_agent` using an `AgentTool` to explicitly call the `spanish_greeter_agent`?**
    *   **Answer:** Agent Transfer (via `sub_agents`) hands control to `spanish_greeter_agent` with no *automatic* way back -- once transferred, `router_agent` doesn't regain control the way it would with `mode="task"`. In this lab that's fine: `spanish_greeter_agent`'s instruction is to give one greeting and stop, so it's never asked to hand anything back. It's not a mechanical dead end, though -- since neither agent sets `disallow_transfer_to_parent`, `spanish_greeter_agent` could call `transfer_to_agent` back to `router_agent` if its instructions told it to; nothing in the framework blocks that path for a *local* agent. The real failure mode shows up when `router_agent` needs to consult more than one specialist to answer a single request: unless every specialist is explicitly instructed to transfer back (and does), Agent Transfer can leave `router_agent` waiting on a specialist that never hands control back within that turn -- and that risk becomes a hard guarantee, not just a prompting risk, once a specialist is a *remote* agent (a `RemoteA2aAgent` has no framework-injected way to transfer back at all). An `AgentTool(agent=spanish_greeter_agent)` sidesteps this entirely: `router_agent` calls the greeter like a function, gets its greeting back, and stays in control to make further calls or compose a combined response -- at the cost of an extra LLM reasoning step to decide when to call the tool, versus the framework handling the transfer automatically. This distinction -- and exactly how it breaks for remote specialists -- is covered in depth in Module 19.
    *   For a related question -- Agent Transfer vs. a fully **Deterministic Workflow** (extracting a routing key with no LLM reasoning at all) -- see the pattern-comparison table in Module 21.5: Agent Transfer suits natural language where the "key" isn't obvious and the LLM needs to understand intent, while a Deterministic Workflow (Module 16) is faster and more reliable when you can extract a clear key (like a language code) without an LLM reasoning step.
