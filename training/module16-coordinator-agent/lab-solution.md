---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 16 Solution: Implementing the "Greeting Router"

## Goal

This file contains the complete Python and YAML configurations for the "Greeting Router" multi-agent system.

### Python Approach (Primary)

#### `greeting_agent/spanish_greeter_agent.py`

```python
from google.adk.agents import LlmAgent

agent = LlmAgent(
    name="spanish_greeter_agent",
    model="gemini-2.5-flash",
    description="An expert at providing friendly greetings in Spanish.",
    instruction="""
You are a friendly assistant who only speaks Spanish.
Your job is to greet the user warmly in Spanish.
Do not say anything else or try to answer questions. Just provide a simple, warm greeting.
"""
)
```

#### `greeting_agent/agent.py` (The Coordinator)

```python
from google.adk.agents import LlmAgent
from . import spanish_greeter_agent

root_agent = LlmAgent(
    name="router_agent",
    model="gemini-2.5-flash",
    description="The main greeter agent that routes to language specialists.",
    instruction="""
You are a language router. Your job is to understand which language the user wants to be greeted in and delegate to the appropriate specialist agent.
If the user asks for a greeting in Spanish, you MUST delegate to the `spanish_greeter_agent`.
Do not greet the user yourself.
""",
        sub_agents=[spanish_greeter_agent.agent]
    )
    ```
    
    ---
    
    ### YAML Approach (Alternative)
    
    #### `greeting_agent/spanish_greeter.yaml`
    
    ```yaml
    # yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
    name: spanish_greeter_agent
    model: gemini-2.5-flash
    description: "An expert at providing friendly greetings in Spanish."
    instruction: |
      You are a friendly assistant who only speaks Spanish.
      Your job is to greet the user warmly in Spanish.
      Do not say anything else or try to answer questions. Just provide a simple, warm greeting.
    ```
    
    #### `greeting_agent/root_agent.yaml` (The Coordinator)
    
    ```yaml
    # yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
    name: router_agent
    model: gemini-2.5-flash
    description: The main greeter agent that routes to language specialists.
    instruction: |
      You are a language router. Your job is to understand which language the user wants to be greeted in and delegate to the appropriate specialist agent.
      If the user asks for a greeting in Spanish, you MUST delegate to the `spanish_greeter_agent`.
      Do not greet the user yourself.
    sub_agents:
      - config_path: spanish_greeter.yaml
    ```
    
    ### Self-Reflection Answers
    
    1.  **What do you think would happen if you forgot to add the `description` to the `spanish_greeter_agent`? How would the `router_agent` behave?**
        *   **Answer:** Without a description, the `router_agent`'s LLM would have no idea what the sub-agent does. It would just see a name (`spanish_greeter_agent`), which might give a hint, but it's not reliable. The router would likely fail to delegate, possibly apologizing to the user ("I don't know how to do that") or, worse, trying to hallucinate a Spanish greeting itself. The description is the essential "interface" that makes delegation possible.
    
    2.  **In the `router_agent`'s instruction, why is it important to explicitly tell it *not* to greet the user itself?**
        *   **Answer:** LLMs are trained to be helpful. If a user says "Say hello in Spanish," the router's natural inclination as an LLM is to simply reply "Hola." By explicitly instructing it *not* to greet, we force it to look for another way to solve the problem—specifically, by delegating to the specialist. This enforces the "router" role and prevents the main agent from doing work it isn't supposed to do.
    
    3.  **How does breaking the logic into a router and a specialist make the system easier to extend in the future (e.g., to add a `french_greeter_agent`)?**
        *   **Answer:** It creates a modular architecture. To add French support, you don't need to touch the `spanish_greeter_agent` at all. You simply add a new `french_greeter_agent` file and register it with the router. This isolation means bugs in the French logic won't break the Spanish logic. It also keeps the router's code clean; it just manages a list of agents rather than containing a giant `if/else` block of greeting strings in every language.
    