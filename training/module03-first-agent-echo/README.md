---
sidebar_position: 3
title: "Module 3: Your First Agent: The \"Echo\" Agent"
---

# Module 3: Your First Agent: The "Echo" Agent

## Theory

### The Core of an ADK Agent

At its heart, an ADK Agent is a blueprint that tells a Large Language Model (LLM) how to behave. This blueprint consists of a few key pieces of information:

*   **`name`:** A unique identifier for your agent.
*   **`model`:** The specific LLM that will act as the agent's "brain" (e.g., `gemini-3.5-flash`).
*   **`instruction`:** The most critical part. This is the detailed prompt that defines the agent's persona, goals, and constraints. Crafting a clear and effective instruction is the key to building a successful agent.
*   **`description`:** A short, human-readable summary of the agent's purpose.

### Two Ways to Define an Agent

The ADK provides two primary methods for creating this blueprint, catering to different needs and complexity levels.

#### 1. Configuration-Based (YAML)

The simplest way to define an agent is with a **YAML** configuration file (e.g., `root_agent.yaml`). This "configuration-over-code" approach is excellent for rapid prototyping and for agents that don't require complex logic.

**Advantages:**
*   **Simple & Fast:** Define an agent in just a few lines.
*   **Clear:** The agent's purpose and instructions are easy to read and understand.
*   **Accessible:** Non-programmers can easily create and modify agents.

A typical YAML configuration looks like this:
```yaml
name: echo_agent
model: gemini-3.5-flash
description: An agent that repeats the user's input.
instruction: You are an echo agent. Your only job is to repeat the user's input back to them exactly as they wrote it.
```

#### 2. Programmatic (Python)

For more advanced scenarios, you can define your agent directly in a Python script (e.g., `agent.py`) using the `LlmAgent` class. This is the more powerful and flexible method.

**Advantages:**
*   **Flexibility:** Allows for dynamic configuration and logic.
*   **Advanced Features:** Required for implementing features like tools and callbacks, which you will learn about in later modules.
*   **Integration:** Easily integrates with other Python code and systems.

The same agent defined in Python would look like this:
```python
from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    name="echo_agent",
    model="gemini-3.5-flash",
    description="An agent that repeats the user's input.",
    instruction="You are an echo agent. Your only job is to repeat the user's input back to them exactly as they wrote it."
)
```
**Important:** When defining an agent in Python, the ADK requires that the main agent variable be named exactly `root_agent`.

### Scaffolding Your Project with `adk create`

The ADK command-line tool helps you quickly set up the necessary file structure for a new agent.

Running `adk create <agent_name>` initiates a wizard that lets you choose your preferred method (Config-based or Programmatic). It then creates a directory containing:

*   **`root_agent.yaml`** (for config-based) or **`agent.py`** (for programmatic).
*   **`.env`:** A file for storing environment variables, such as your API keys. This keeps your secrets separate from your agent's code and configuration.

In the upcoming lab, you will use these concepts to create, configure, and run your first agent using both methods.

### Key Takeaways
- An ADK agent is defined by its `name`, `model`, `instruction`, and `description`.
- The `instruction` is the most critical part, defining the agent's persona, goals, and rules.
- Agents can be defined simply with YAML (`root_agent.yaml`) or programmatically with Python (`agent.py`).
- The `adk create` command scaffolds the necessary project structure for a new agent.
