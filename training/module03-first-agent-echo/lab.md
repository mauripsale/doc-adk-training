---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 3 Challenge: Build and Run the "Echo" Agent

## Goal
Your task is to create, configure, and run a simple "Echo" agent using the ADK. 

**The Challenge:** Unlike a standard chatbot, this agent must act like a **parrot**. It should never answer questions or provide information; it must only repeat the user's input exactly as it was received.

### Expected Behavior
| User Input | Agent Response (Correct) | Agent Response (Wrong) |
| :--- | :--- | :--- |
| "Hello!" | "Hello!" | "Hi there, how can I help you?" |
| "What is the capital of France?" | "What is the capital of France?" | "The capital of France is Paris." |
| "12345" | "12345" | "You entered the numbers 1 through 5." |
e
## Requirements
1.  Use the `adk create` command to scaffold a new agent named `echo_agent`.
2.  Follow the **Python Approach** below to define the agent's behavior.
3.  **Instruction Strategy:** Craft an instruction that forces the agent to only echo and explicitly forbids it from answering questions or being helpful.
4.  Configure the `.env` file with your Google API key or Google Cloud project details.
5.  Run the agent using the `adk web` command.
6.  Interact with the agent in the Dev UI to verify it passes the "Expected Behavior" tests.

### Python Approach (Primary)
Modify your `agent.py` file to look like the following, filling in the `TODO` sections.

```python
from google.adk.agents import LlmAgent

# TODO: Define the root_agent for your application.
# You will need to provide a name, a model, and the instruction for the agent.
root_agent = LlmAgent(
    name=...,  # TODO: Give your agent a name (e.g., "echo_agent")
    model=..., # TODO: Specify the model to use (e.g., "gemini-2.5-flash")
    instruction=...,  # TODO: Provide the instruction for the echo agent.
)
```

### Alternative Approach: Using YAML Configuration
If you prefer a simpler, config-based agent, you can use a YAML file instead of Python.

1.  Create your agent using `adk create --type=config echo_agent`. This will create a `root_agent.yaml` file instead of `agent.py`.
2.  Fill in the `TODO` sections in your `root_agent.yaml` file.

```yaml
# The first line is an optional schema definition that provides
# auto-completion and validation in compatible code editors.
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json

# TODO: Define the root_agent for your application.
name: ... # TODO: Give your agent a name (e.g., "echo_agent")
model: ... # TODO: Specify the model to use (e.g., "gemini-2.5-flash")
instruction: ... # TODO: Provide the instruction for the echo agent.
```
> **Note:** If both `agent.py` and `root_agent.yaml` exist, the ADK will use the `root_agent.yaml` file.

### Self-Reflection Questions
- What are the advantages of defining an agent in a Python script versus a YAML file?
- Why is it important to keep API keys and other secrets in a `.env` file instead of directly in your agent's code?
- Explore the "Events" tab in the Dev UI after running your agent. What information does it provide, and how could this be useful for debugging a more complex agent?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMDMtZmlyc3QtYWdlbnQtZWNoby9sYWItc29sdXRpb24=`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module03-first-agent-echo/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
