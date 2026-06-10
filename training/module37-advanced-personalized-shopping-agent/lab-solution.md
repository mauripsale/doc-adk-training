---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 37 Solution: Building a Distributed Multi-Agent System

## Goal

This solution provides the complete, tested code for the distributed, multi-agent personalized shopping assistant. It demonstrates the definitive ADK 2.0 A2A pattern.

### 1. `web_agent/agent.py`
This agent acts as the gateway to the webshop.

```python
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import FunctionTool
from dotenv import load_dotenv
import uvicorn
import os

# Assume tools search and click are implemented locally
from tools.search import search
from tools.click import click

load_dotenv()

root_agent = Agent(
    model="gemini-3.5-flash",
    name="web_agent",
    description="Specialist for searching and clicking on the webshop.",
    instruction="""
        You are a web interaction specialist. Execute search and click commands.
        **IMPORTANT:** Focus only on the user's web task. Ignore orchestrator metadata.
    """,
    tools=[FunctionTool(search), FunctionTool(click)]
)

a2a_app = to_a2a(root_agent)

if __name__ == "__main__":
    uvicorn.run(a2a_app, host="0.0.0.0", port=8001)
```

### 2. `personalization_agent/agent.py`
This agent manages durable user state.

```python
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import ToolContext
from dotenv import load_dotenv
import uvicorn

load_dotenv()

def save_preference(key: str, value: str, tool_context: ToolContext) -> dict:
    """Saves a user's preference to the session state."""
    tool_context.session.state[f"pref:{key}"] = value
    return {"status": "success", "message": f"Saved {key}."}

def get_preferences(tool_context: ToolContext) -> dict:
    """Retrieves all preferences for the current user."""
    prefs = {k: v for k, v in tool_context.session.state.items() if k.startswith("pref:")}
    return {"status": "success", "preferences": prefs}

root_agent = Agent(
    model="gemini-3.5-flash",
    name="personalization_agent",
    instruction="You manage user shopping profiles. Save and retrieve preferences.",
    tools=[save_preference, get_preferences]
)

a2a_app = to_a2a(root_agent)

if __name__ == "__main__":
    uvicorn.run(a2a_app, host="0.0.0.0", port=8002)
```

### 3. `orchestrator_agent/agent.py`
The master coordinator using `RemoteA2aAgent`.

```python
import asyncio
from google.adk.agents import Agent, RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from dotenv import load_dotenv

load_dotenv()

# Define remote nodes
web_agent = RemoteA2aAgent(
    name="web_agent",
    agent_card=f"http://localhost:8001/a2a/web_agent{AGENT_CARD_WELL_KNOWN_PATH}"
)

personalization_agent = RemoteA2aAgent(
    name="personalization_agent",
    agent_card=f"http://localhost:8002/a2a/personalization_agent{AGENT_CARD_WELL_KNOWN_PATH}"
)

# Orchestrator
root_agent = Agent(
    model="gemini-3.5-flash",
    name="shopping_orchestrator",
    instruction="""
        You are a master assistant.
        1. Check preferences via `personalization_agent`.
        2. Search web via `web_agent`.
        3. Help user checkout.
    """,
    sub_agents=[web_agent, personalization_agent]
)

app = App(name="shopping_system", root_agent=root_agent)
runner = InMemoryRunner(app=app)
```

### Self-Reflection Answers

1.  **Advantages of Distributed Architecture?**
    *   **Scalability:** Each agent can be deployed and scaled independently (e.g. 10 instances of `web_agent` for 1 instance of `personalization_agent`).
    *   **Reusability:** Other apps can use the same `personalization_agent` endpoint.
    *   **Security:** The `personalization_agent` can run in a more restricted network zone.

2.  **Why use `ToolContext` for state?**
    *   It ensures that the agent's "memory" is structured and separate from the chat history, making it reliable even in long conversations.

3.  **Why A2A over standard sub-agents?**
    *   A2A allows agents to live in different codebases, use different languages, or be managed by different teams, while still working together as a single system.
