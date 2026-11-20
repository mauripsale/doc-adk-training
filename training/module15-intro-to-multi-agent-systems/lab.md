---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 15: Introduction to MAS — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 15: Building Your First Multi-Agent Greeting Router

## Goal

In this lab, you will build and run your first live **Multi-Agent System (MAS)** using ADK 2.0's **`sub_agents`** delegation pattern:

* A **`router_agent`** (`root_agent`) whose sole job is to understand which language the user wants and transfer the conversation to the matching specialist.
* Two domain specialists — **`spanish_greeter_agent`** and **`japanese_greeter_agent`** — isolated in their own module (`specialists.py`) with crisp, non-overlapping `description` strings.

### Expected Behavior

| User Prompt | Expected Flow |
| :--- | :--- |
| `"Can you greet me in Spanish?"` | `router_agent` transfers to `spanish_greeter_agent` → replies warmly in Spanish (`"¡Hola!..."`). |
| `"Please greet me in Japanese."` | `router_agent` transfers to `japanese_greeter_agent` → replies politely in Japanese. |
| `"Greet me in French!"` | `router_agent` sees no matching specialist in `sub_agents` → politely explains French isn't supported yet. |

---

### Step 1: Scaffold the Project

<Setup/>

From your main `adk-training` directory, scaffold a new agent project:

```shell
uv run adk create greeting_system
```

Your folder structure will look like this once you add `specialists.py`:

```text
adk-training/
└── greeting_system/
    ├── .env
    ├── __init__.py
    ├── specialists.py   <-- Step 2: Specialist sub-agents
    └── agent.py         <-- Step 3: Coordinator (root_agent)
```

---

### Step 2: Implement the Specialist Sub-Agents (`greeting_system/specialists.py`)

Create `greeting_system/specialists.py` and complete the `TODO` placeholders. Remember: the coordinator's LLM reads each specialist's **`description`** to decide whom to transfer to!

```python
# greeting_system/specialists.py
from google.adk import Agent

# TODO: Define spanish_greeter (name="spanish_greeter_agent", model="gemini-3.8-flash")
# - Write a clear `description` so the router knows it handles Spanish greetings.
# - Write an `instruction` telling it to greet warmly ONLY in Spanish.
spanish_greeter = Agent(
    name="spanish_greeter_agent",
    model="gemini-3.8-flash",
    description=...,  # TODO: Action-oriented description for discovery
    instruction=...,  # TODO: Greet warmly in Spanish only
)

# TODO: Define japanese_greeter (name="japanese_greeter_agent", model="gemini-3.8-flash")
# - Write a clear `description` so the router knows it handles Japanese greetings.
# - Write an `instruction` telling it to greet politely ONLY in Japanese (with romaji).
japanese_greeter = Agent(
    name="japanese_greeter_agent",
    model="gemini-3.8-flash",
    description=...,  # TODO: Action-oriented description for discovery
    instruction=...,  # TODO: Greet politely in Japanese only
)
```

---

### Step 3: Wire the Coordinator (`greeting_system/agent.py`)

Open `greeting_system/agent.py` and configure `root_agent` to delegate via `sub_agents`:

```python
# greeting_system/agent.py
from google.adk import Agent
from .specialists import spanish_greeter, japanese_greeter

# TODO: Define root_agent (name="router_agent", model="gemini-3.8-flash")
# - Instruct it to delegate to the matching specialist in sub_agents (never greet in Spanish/Japanese itself),
#   and politely decline unsupported languages like French.
# - Register both specialists in `sub_agents=[...]`.
root_agent = Agent(
    name="router_agent",
    model="gemini-3.8-flash",
    instruction=...,  # TODO: Triage instructions
    sub_agents=[...], # TODO: Register spanish_greeter and japanese_greeter
)
```

---

### Step 4: Run and Inspect the Hand-off in Dev UI

1.  **Launch the Dev UI from your parent `adk-training` directory:**
    ```shell
    uv run adk web
    ```
    *(Select `greeting_system` from the agent dropdown).*
2.  **Test all three scenarios** (Spanish, Japanese, and unsupported French).
3.  **Check the Trace Tab:** Expand the turn where you asked for Spanish — you will see `router_agent` automatically invoke `transfer_to_agent(agent_name="spanish_greeter_agent")`, followed immediately by `spanish_greeter_agent` generating the final reply!

### Self-Reflection Questions
- What is the single most important field that lets `router_agent` know which specialist to transfer to?
- How would you extend this team to support Italian greetings without rewriting the existing specialists?
- After `router_agent` transfers a conversation to `spanish_greeter_agent`, who handles the user's *next* message by default? *(Hint: Try sending a second message in the same chat session!)*

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="15">

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

</SolutionVault>
