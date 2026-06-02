---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 16 Solution: Implementing the "Greeting Router"

## Goal

This file contains the complete Python and YAML configurations for the "Greeting Router" multi-agent system.

### Python Approach (Primary)

#### `greeting_system/spanish_greeter_agent.py`

```python
from google.adk import Agent

agent = Agent(
    name="spanish_greeter_agent",
    model="gemini-3.5-flash",
    description="An expert at providing friendly greetings in Spanish.",
    instruction="""
You are a friendly assistant who only speaks Spanish.
Your job is to greet the user warmly in Spanish.
Do not say anything else. Just provide a simple, warm greeting.
"""
)
```

#### `greeting_system/agent.py` (The Coordinator and Workflow)

```python
from google.adk import Agent, Workflow
from . import spanish_greeter_agent

coordinator = Agent(
    name="router_agent",
    model="gemini-3.5-flash",
    description="The main greeter agent that routes to language specialists.",
    instruction="""
You are a language router. Your job is to understand which language the user wants to be greeted in and delegate to the appropriate specialist agent.
If the user asks for a greeting in Spanish, you MUST delegate to the `spanish_greeter_agent`.
Do not greet the user yourself.
""",
    sub_agents=[spanish_greeter_agent.agent]
)

root_agent = Workflow(
    name="GreetingSystem",
    edges=[("START", coordinator)]
)
```

### Self-Reflection Answers

1.  **What do you think would happen if you forgot to add the `description` to the `spanish_greeter_agent`? How would the `router_agent` behave?**
    *   **Answer:** Without a description, the coordinator node sees a potential target but doesn't know its capabilities. It would likely fail to perform the **Agent Transfer**, possibly apologizing to the user or trying to fulfill the request itself (violating its instructions). The description is the "metadata" that makes the graph discoverable.

2.  **In the `router_agent`'s instruction, why is it important to explicitly tell it *not* to greet the user itself?**
    *   **Answer:** LLMs are naturally "helpful" and might try to answer directly. By explicitly forbidding it, we force the LLM to use the **Agent Transfer** mechanism, ensuring the specialist (which might have more complex logic or tools in the future) is the one responding.

3.  **How does the ADK 2.0 Workflow Runtime handle the interaction between nodes?**
    *   **Answer:** When the coordinator node initiates a transfer, the Workflow engine pauses the current node and activates the target specialist. Because they are part of the same **Workflow**, the conversation history and context are shared automatically, allowing for a seamless hand-off from the user's perspective.