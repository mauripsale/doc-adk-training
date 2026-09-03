---
sidebar_position: 2
title: "Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

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

## Lab Tasks

<Setup/>

1.  Use the `uv run adk create` command to scaffold a new agent named `echo_agent`. By default, this will create a Python-based project structure:
    ```shell
    uv run adk create echo_agent
    ```
    > **Note:** This is an interactive wizard — it will prompt you for choices like the model, backend, GCP project, and region. Answer the prompts as they appear.
2.  Follow the **Python Approach** below to define the agent's behavior.
3.  **Instruction Strategy:** Craft an instruction that forces the agent to only echo and explicitly forbids it from answering questions or being helpful.
4.  Configure the `.env` file with your Google API key or Google Cloud project details.
5.  Run the agent using the `uv run adk web` command (remember to run this from the parent directory of your agent).
6.  Interact with the agent in the Dev UI to verify it passes the "Expected Behavior" tests.


### Python Approach (Primary)
Modify your `agent.py` file to look like the following, filling in the `TODO` sections.

```python
from google.adk import Agent

# TODO: Define the root_agent for your application.
# You will need to provide a name, a model, and the instruction for the agent.
root_agent = Agent(
    name=...,  # TODO: Give your agent a name (e.g., "echo_agent")
    model=..., # TODO: Specify the model to use (e.g., "gemini-3.5-flash")
    description=...,  # TODO: Provide a short description of what the agent does.
    instruction=...,  # TODO: Provide the instruction for the echo agent.
)
```

### Alternative Approach: Using YAML Configuration (Informational Only)
*Note: For the remainder of this course, we will focus exclusively on the Python approach. While the ADK supports YAML configuration, it lacks the flexibility required for the advanced modules you will encounter later. You do not need to perform this step.*

If you prefer a simpler, config-based agent, you can define your agent in a YAML file instead of Python. To do this, you would create a `root_agent.yaml` file instead of `agent.py`.

```yaml
# The first line is an optional schema definition that provides
# auto-completion and validation in compatible code editors.
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json

name: ... # Give your agent a name (e.g., "echo_agent")
model: ... # Specify the model to use (e.g., "gemini-3.5-flash")
instruction: ... # Provide the instruction for the echo agent.
```
> **Note:** If both `agent.py` and `root_agent.yaml` exist in the same directory, the ADK will use `agent.py` -- the generated `__init__.py` hard-imports it, regardless of a sibling YAML file. Avoid keeping both in the same directory.

### Self-Reflection Questions
- What are the advantages of defining an agent in a Python script versus a YAML file?
- Why is it important to keep API keys and other secrets in a `.env` file instead of directly in your agent's code?
- Explore the **"Trace"** tab in the Dev UI after running your agent. What information does it provide, and how could this be useful for debugging a more complex agent?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMDMtZmlyc3QtYWdlbnQtZWNoby9sYWItc29sdXRpb24=`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module03-first-agent-echo/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
