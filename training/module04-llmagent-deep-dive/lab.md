---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 4 Challenge: Transforming an Agent

## Goal
Your task is to create a new "Haiku Poet" agent by duplicating and modifying the "Echo" agent from the previous lab. This will demonstrate how to build upon existing agents.

## Requirements
1.  In your `adk-training` directory, duplicate the `echo_agent` directory and rename the copy to `haiku_poet_agent`.
2.  Navigate into the new `haiku_poet_agent` sub-directory.
3.  Follow the **Python Approach** below to modify the agent's behavior.
    *   Change the `name` to `haiku_poet_agent`.
    *   Update the `description`.
    *   Craft a new `instruction` that gives the agent the persona of a wise poet who transforms the user's topic into a haiku.
    *   Include at least two examples (few-shot prompts) in your instruction to guide the agent.
4.  Return to the parent `adk-training` directory.
5.  Run the new agent using the `adk web haiku_poet_agent` command.
6.  Interact with the agent in the Dev UI to verify that it correctly responds with a haiku.

### Python Approach (Primary)
Modify the `agent.py` file inside your new `haiku_poet_agent` directory. You will need to update the `name`, `description`, and `instruction` arguments in the `LlmAgent` constructor.

### Alternative Approach: Using YAML Configuration
If you are using a `root_agent.yaml` file:
1.  Modify the `name`, `description`, and `instruction` fields in your `root_agent.yaml` file.
2.  Ensure you do not have an `agent.py` file in the same directory, as the YAML file will take precedence.

### Self-Reflection Questions
- How does providing examples (few-shot prompting) in the instruction help the LLM understand the task better than just describing it?
- What would happen if you removed the constraint "Do not answer questions or have a conversation"? How would the agent's behavior change?
- Experiment with creating a new persona for the agent (e.g., a Shakespearean poet, a futuristic robot). What are the key elements you need to include in the instruction to make the new persona convincing?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMDQtbGxtYWdlbnQtZGVlcC1kaXZlL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module04-llmagent-deep-dive/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
