---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 15 Solution: Building Your First Multi-Agent Greeting Router

## Goal

In this lab, you built and ran a live Multi-Agent System using LLM-driven `sub_agents` delegation: a `router_agent` (`root_agent`) that inspects specialist `description` strings and transfers control dynamically to `spanish_greeter_agent` or `japanese_greeter_agent`.

#### `greeting_system/specialists.py`

```python
from google.adk import Agent

spanish_greeter = Agent(
    name="spanish_greeter_agent",
    model="gemini-3.8-flash",
    description="Handles user requests for greetings in Spanish.",
    instruction=(
        "You are a warm, friendly assistant who communicates ONLY in Spanish. "
        "Provide a welcoming Spanish greeting and nothing else."
    ),
)

japanese_greeter = Agent(
    name="japanese_greeter_agent",
    model="gemini-3.8-flash",
    description="Handles user requests for greetings in Japanese.",
    instruction=(
        "You are a polite assistant who communicates ONLY in Japanese (with romaji in parentheses). "
        "Provide a welcoming Japanese greeting and nothing else."
    ),
)
```

#### `greeting_system/agent.py`

```python
from google.adk import Agent
from .specialists import spanish_greeter, japanese_greeter

root_agent = Agent(
    name="router_agent",
    model="gemini-3.8-flash",
    instruction=(
        "You are a language greeting coordinator. "
        "Understand which language the user wants to be greeted in and delegate to the matching specialist in your sub_agents. "
        "Never perform Spanish or Japanese greetings yourself — always transfer to the specialist. "
        "If the user asks for a language you do not have a specialist for (such as French), politely explain that no specialist is available for that language yet."
    ),
    sub_agents=[spanish_greeter, japanese_greeter],
)
```

### Self-Reflection Answers

1.  **What is the single most important field that lets `router_agent` know which specialist to transfer to?**
    *   **Answer:** Each specialist's **`description`** field. ADK exposes the `name` and `description` of every entry in `sub_agents` to the coordinator's LLM via its built-in `transfer_to_agent` mechanism, allowing Gemini to pick the matching expert.

2.  **How would you extend this team to support Italian greetings without rewriting the existing specialists?**
    *   **Answer:** Define `italian_greeter = Agent(name="italian_greeter_agent", description="Handles user requests for greetings in Italian.", ...)` in `specialists.py` and append `italian_greeter` to `sub_agents=[...]` in `agent.py`. Because `router_agent`'s instruction delegates based on matching specialist descriptions rather than hardcoding every language name, it scales cleanly!

3.  **After `router_agent` transfers a conversation to `spanish_greeter_agent`, who handles the user's *next* message by default?**
    *   **Answer:** By default (`mode="chat"`), `spanish_greeter_agent` stays active as the current conversational agent unless it decides to transfer back. In **Module 16**, you will learn how `mode="single_turn"` and `mode="task"` guarantee an automatic return to the coordinator!
