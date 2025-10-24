# Module 11: Building a Coordinator/Dispatcher Agent

## Theory

### The Coordinator Pattern

The most common and intuitive multi-agent design pattern is the **Coordinator/Dispatcher** (also known as a Router). In this pattern, one central `LlmAgent` acts as a manager or a switchboard. Its primary responsibility is not to perform tasks itself, but to understand an incoming request and delegate it to the correct specialist sub-agent.

This pattern is incredibly effective for building modular and maintainable systems. The coordinator provides a single point of entry, while the specialists handle the complex, domain-specific logic.

### Implementing the Coordinator Pattern in ADK

The ADK is designed with this pattern in mind and makes it straightforward to implement using a combination of YAML configuration and carefully crafted instructions.

#### 1. Establishing the Hierarchy (`sub_agents`)

The first step is to define the parent-child relationship. The coordinator agent is the parent, and the specialist agents are its children. In a config-based setup, this is done in the parent's YAML file using the `sub_agents` key.

```yaml
# In the coordinator's root_agent.yaml
name: coordinator_agent
model: gemini-2.5-flash
instruction: You are a router...
# ...
sub_agents:
  - config_path: billing_agent.yaml
  - config_path: tech_support_agent.yaml
```
The `config_path` tells the ADK to load the agent definitions from those other YAML files and register them as children of the `coordinator_agent`.

#### 2. The Key to Delegation: `description`

How does the coordinator's LLM know which specialist to choose? It relies on the `description` field of each sub-agent.

When the coordinator agent runs, the ADK framework provides the LLM with not only the user's query and the coordinator's own instruction, but also a list of the available sub-agents and their descriptions.

**`billing_agent.yaml`:**
```yaml
name: billing_agent
description: "Handles all questions related to billing, invoices, payments, and subscriptions."
instruction: "You are a billing expert..."
```

**`tech_support_agent.yaml`:**
```yaml
name: tech_support_agent
description: "Assists users with technical problems, error messages, and troubleshooting."
instruction: "You are a technical support specialist..."
```
The LLM uses these descriptions like a function's docstring to decide which "tool" (in this case, which sub-agent) is the best fit for the user's request. A clear, concise, and accurate description is therefore critical for reliable routing.

#### 3. The Coordinator's `instruction`

The final piece of the puzzle is the coordinator's own `instruction`. This instruction must explicitly tell the agent that its job is to delegate.

```yaml
# In the coordinator's root_agent.yaml
instruction: |
  You are the primary customer support assistant.
  Your main job is to understand the user's problem and delegate it to the correct specialist.
  - If the user has a question about a payment or an invoice, delegate to the `billing_agent`.
  - If the user is reporting an error or can't log in, delegate to the `tech_support_agent`.
  Do not attempt to answer billing or technical questions yourself. Always delegate.
```
This instruction, combined with the sub-agents' descriptions, gives the LLM all the information it needs to make an intelligent routing decision.

#### 4. The Magic of Agent Transfer

When the coordinator's LLM decides to delegate, it invokes a special built-in function called `transfer_to_agent`, specifying the `name` of the target agent. The ADK framework intercepts this and automatically transfers control of the conversation to the chosen sub-agent. The sub-agent then takes over and responds to the user directly.

In the following lab, you will implement the "Greeting Router" you designed in the previous module, putting all these concepts into practice.
