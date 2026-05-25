---
sidebar_position: 16
title: "Module 16: Building a Coordinator/Dispatcher Agent"
---

# Module 16: Building a Coordinator/Dispatcher Agent

## Theory

### The Coordinator Pattern

The most common and intuitive multi-agent design pattern is the **Coordinator/Dispatcher** (also known as a Router). In this pattern, one central `LlmAgent` acts as a manager or a switchboard. Its primary responsibility is not to perform tasks itself, but to understand an incoming request and delegate it to the correct specialist sub-agent.

This pattern is incredibly effective for building modular and maintainable systems. The coordinator provides a single point of entry, while the specialists handle the complex, domain-specific logic.

### Implementing the Coordinator Pattern in ADK

The ADK is designed with this pattern in mind and makes it straightforward to implement using a combination of Python code and carefully crafted instructions.

#### 1. Establishing the Hierarchy (`sub_agents`)

The first step is to define the parent-child relationship. The coordinator agent is the parent, and the specialist agents are its children.

**Python (Primary Approach):**
In the coordinator's `agent.py`, you import the sub-agent's module and add its agent object to the `sub_agents` list.

```python
# In the coordinator's agent.py
from google.adk.agents import LlmAgent
from . import billing_agent_module, tech_support_module

root_agent = LlmAgent(
    name="coordinator_agent",
    model="gemini-3.5-flash",
    instruction="You are a router...",
    # ...
    sub_agents=[
        billing_agent_module.agent,
        tech_support_module.agent
    ]
)
```

**YAML (Alternative Approach):**
In the parent's `root_agent.yaml` file, you use the `sub_agents` key and `config_path` to link to the specialist agents' YAML files.

```yaml
# In the coordinator's root_agent.yaml
name: coordinator_agent
model: gemini-3.5-flash
instruction: You are a router...
# ...
sub_agents:
  - config_path: billing_agent.yaml
  - config_path: tech_support_agent.yaml
```

#### 2. The Key to Delegation: `description`

How does the coordinator's LLM know which specialist to choose? It relies on the `description` field of each sub-agent.

When the coordinator agent runs, the ADK framework provides the LLM with not only the user's query and the coordinator's own instruction, but also a list of the available sub-agents and their descriptions.

**`billing_agent_module.py`:**
```python
# ...
agent = LlmAgent(
    name="billing_agent",
    description="Handles all questions related to billing, invoices, payments, and subscriptions.",
    instruction="You are a billing expert..."
)
```

**`tech_support_module.py`:**
```python
# ...
agent = LlmAgent(
    name="tech_support_agent",
    description="Assists users with technical problems, error messages, and troubleshooting.",
    instruction="You are a technical support specialist..."
)
```
The LLM uses these descriptions like a function's docstring to decide which "tool" (in this case, which sub-agent) is the best fit for the user's request. A clear, concise, and accurate description is therefore critical for reliable routing.

#### 3. The Coordinator's `instruction`

The final piece of the puzzle is the coordinator's own `instruction`. This instruction must explicitly tell the agent that its job is to delegate.

```python
# In the coordinator's agent.py
# ...
root_agent = LlmAgent(
    # ...
    instruction="""
You are the primary customer support assistant.
Your main job is to understand the user's problem and delegate it to the correct specialist.
- If the user has a question about a payment or an invoice, delegate to the `billing_agent`.
- If the user is reporting an error or can't log in, delegate to the `tech_support_agent`.
Do not attempt to answer billing or technical questions yourself. Always delegate.
"""
)
```
This instruction, combined with the sub-agents' descriptions, gives the LLM all the information it needs to make an intelligent routing decision.

#### 4. The Magic of Agent Transfer

When the coordinator's LLM decides to delegate, it invokes a special built-in function called `transfer_to_agent`, specifying the `name` of the target agent. The ADK framework intercepts this and automatically transfers control of the conversation to the chosen sub-agent. The sub-agent then takes over and responds to the user directly.

> **Note on `transfer_to_agent`:** While it acts as a delegation mechanism, `transfer_to_agent` is internally treated as a special kind of built-in tool. The LLM implicitly "calls" this tool when its reasoning, based on the coordinator's instruction and sub-agent descriptions, leads it to delegate. This connects the multi-agent delegation pattern directly to the Function Calling mechanism you learned in earlier modules.

In the following lab, you will implement the "Greeting Router" you designed in the previous module, putting all these concepts into practice.

### Key Takeaways
- The Coordinator/Dispatcher is a common multi-agent pattern where a central agent routes tasks to specialists.
- In the ADK, this is implemented by defining a parent agent with a list of `sub_agents`.
- The coordinator's LLM uses the `description` of each sub-agent to make intelligent routing decisions.
- A clear `instruction` is needed to tell the coordinator that its primary job is to delegate, not to perform tasks itself.
- The `transfer_to_agent` function is the mechanism by which the coordinator hands off control to a sub-agent.
