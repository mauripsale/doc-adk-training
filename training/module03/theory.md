# Module 3: Your First Agent: The "Echo" Agent

## Theory

### Configuration over Code

One of the powerful features of the Google ADK is the ability to define agents without writing any Python or Java code. This is achieved through a simple, human-readable configuration file format called **YAML** (YAML Ain't Markup Language).

This "configuration-over-code" approach offers several advantages:

*   **Simplicity:** It's much faster to define an agent's core properties in a few lines of YAML than to write a full script.
*   **Clarity:** The agent's purpose, model, and instructions are laid out in a clear, structured format, making it easy for anyone to understand what the agent does.
*   **Rapid Prototyping:** You can quickly create and test new agent ideas by simply creating a new YAML file and modifying a few lines.
*   **Accessibility:** It allows people who are not programmers, such as prompt engineers or product managers, to build and experiment with agents.

### Anatomy of an Agent Configuration File

The primary configuration file for an agent is typically named `root_agent.yaml`. This file acts as the main entry point for your agent. Let's break down the essential components you'll find in a basic configuration:

```yaml
# A unique identifier for your agent.
name: my_first_agent

# The specific LLM the agent will use for its reasoning.
model: gemini-1.5-flash

# A brief, human-readable summary of what the agent does.
description: A simple agent that introduces itself.

# The core prompt that defines the agent's persona, goals, and constraints.
instruction: You are a friendly assistant. Your job is to say hello to the user.
```

*   **`name`:** A unique identifier for the agent. This is important for logging and for distinguishing between agents in a multi-agent system.
*   **`model`:** Specifies which Large Language Model will power the agent's "brain." The choice of model can affect the agent's performance, cost, and capabilities.
*   **`description`:** A short summary of the agent's purpose. While optional for a single agent, this becomes very important in multi-agent systems, as it's how other agents know what this agent is capable of.
*   **`instruction`:** This is the most critical part. The instruction is the detailed prompt given to the LLM that tells the agent who it is, what its goal is, how it should behave, and what it should do. Crafting a clear and effective instruction is the key to building a successful agent.

### The `adk create` Command

To streamline the process of creating a new agent, the ADK provides a command-line tool: `adk create`.

When you run `adk create --type=config <agent_name>`, it scaffolds a new project directory for you. This directory includes:

*   **`root_agent.yaml`:** A pre-populated agent configuration file, ready for you to edit.
*   **`.env`:** A file for storing environment variables, such as your API keys. This keeps your secret keys separate from your main configuration.

In the upcoming lab, you will use these concepts to create, configure, and run your first agent.
