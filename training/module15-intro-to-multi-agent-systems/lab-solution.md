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

3.  **This lab uses LLM-driven delegation (agent transfer). What might be the advantages or disadvantages of this approach compared to a Deterministic Workflow?**
    *   **Answer:**
        *   **Agent Transfer (Dynamic):** Great for natural language where the "key" isn't always obvious. The LLM understands intent.
        *   **Deterministic (Module 16):** Faster and more reliable if you can extract a clear key (like a "language" code). It avoids unnecessary LLM reasoning for the routing step.
