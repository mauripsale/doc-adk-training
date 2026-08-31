---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 37 Solution: Building a Distributed Multi-Agent System

## Goal

This solution provides the complete, tested code for the distributed, multi-agent personalized shopping assistant. It demonstrates the definitive ADK 2.0 A2A pattern.

### 0. `web_agent/webshop_data.py`
A minimal, dependency-free mock e-commerce catalog standing in for a real
webshop, so `web_agent`'s `search`/`click` tools have something to operate
on without any extra install step.

```python
"""A minimal, dependency-free mock e-commerce catalog and session model."""

CATALOG = [
    {
        "id": "P001",
        "name": "Floral Summer Dress",
        "category": "dresses",
        "price": 39.99,
        "description": "A flowy, floral-print summer dress in breathable cotton.",
    },
    {
        "id": "P002",
        "name": "Men's Running Shoes",
        "category": "shoes",
        "price": 79.99,
        "description": "Lightweight running shoes with a breathable mesh upper.",
    },
    {
        "id": "P003",
        "name": "Wireless Noise-Cancelling Headphones",
        "category": "electronics",
        "price": 199.99,
        "description": "Over-ear headphones with active noise cancellation and 30-hour battery life.",
    },
    {
        "id": "P004",
        "name": "Stainless Steel Water Bottle",
        "category": "home",
        "price": 24.99,
        "description": "Insulated 750ml water bottle, keeps drinks cold for 24 hours.",
    },
    {
        "id": "P005",
        "name": "Organic Cotton T-Shirt",
        "category": "tops",
        "price": 19.99,
        "description": "Soft, breathable organic cotton crew-neck t-shirt.",
    },
]

# Tiny in-process "session" tracking the currently viewed product, so
# `click` can react to what `search` just showed.
_session_state = {"current_product": None}

def get_product(product_id: str):
    return next((p for p in CATALOG if p["id"] == product_id), None)
```

### `web_agent/tools/search.py`

```python
from webshop_data import CATALOG

def search(keywords: str) -> str:
    """Search for keywords in the (mock) webshop."""
    terms = keywords.lower().split()
    matches = [
        p for p in CATALOG
        if any(
            t in p["name"].lower() or t in p["description"].lower() or t in p["category"].lower()
            for t in terms
        )
    ]
    if not matches:
        return "No products found matching your search. Try different keywords."
    lines = [f"Found {len(matches)} product(s):"]
    for p in matches:
        lines.append(f"- [{p['id']}] {p['name']} — ${p['price']:.2f}")
    return "\n".join(lines)
```

### `web_agent/tools/click.py`

```python
from webshop_data import _session_state, get_product

def click(button: str) -> str:
    """Simulate clicking a product ID or a navigation button in the (mock) webshop."""
    normalized = button.strip().lower()

    if normalized == "back to search":
        _session_state["current_product"] = None
        return "Returned to the search page. Use `search` to look for products again."

    if normalized == "buy now":
        product = _session_state["current_product"]
        if not product:
            return "No product selected. Click a product ID from the search results first."
        return f"Order placed for '{product['name']}' (${product['price']:.2f}). Thank you for shopping!"

    product = get_product(button.strip())
    if not product:
        return (
            f"'{button}' is not a valid product ID or button. Try a product ID "
            "from the search results, 'Buy Now', or 'Back to Search'."
        )
    _session_state["current_product"] = product
    return (
        f"{product['name']} — ${product['price']:.2f}\n"
        f"{product['description']}\n"
        "Options: [Buy Now] [Back to Search]"
    )
```

### 1. `web_agent/agent.py`
This agent acts as the gateway to the webshop.

```python
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import FunctionTool
from dotenv import load_dotenv
import uvicorn
import os

# search/click are plain functions defined in tools/search.py and
# tools/click.py, operating on the mock catalog in webshop_data.py above —
# no OpenAPI spec, no external `web_agent_site` package.
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

a2a_app = to_a2a(root_agent, port=8001)

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
    # Use tool_context.state (the tracked delta proxy), NOT
    # tool_context.session.state directly — writing to .session.state
    # bypasses ADK's state-delta tracking, so the write never actually
    # commits and is gone on the very next turn. See Module 22.
    tool_context.state[f"pref:{key}"] = value
    return {"status": "success", "message": f"Saved {key}."}

def get_preferences(tool_context: ToolContext) -> dict:
    """Retrieves all preferences for the current user."""
    prefs = {k: v for k, v in tool_context.state.to_dict().items() if k.startswith("pref:")}
    return {"status": "success", "preferences": prefs}

root_agent = Agent(
    model="gemini-3.5-flash",
    name="personalization_agent",
    instruction="You manage user shopping profiles. Save and retrieve preferences.",
    tools=[save_preference, get_preferences]
)

a2a_app = to_a2a(root_agent, port=8002)

if __name__ == "__main__":
    uvicorn.run(a2a_app, host="0.0.0.0", port=8002)
```

### 3. `orchestrator_agent/agent.py`
The master coordinator using `RemoteA2aAgent` nodes wired in as `AgentTool`s.

```python
import asyncio
from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.adk.tools.agent_tool import AgentTool
from dotenv import load_dotenv

load_dotenv()

# Define remote nodes
web_agent = RemoteA2aAgent(
    name="web_agent",
    agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}",
    use_legacy=False,
)

personalization_agent = RemoteA2aAgent(
    name="personalization_agent",
    agent_card=f"http://localhost:8002{AGENT_CARD_WELL_KNOWN_PATH}",
    use_legacy=False,
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
    # NOTE: these two remote agents are wired as tools (AgentTool), NOT as
    # `sub_agents=[...]`. `sub_agents` wires ADK's `transfer_to_agent`
    # mechanism, which is a *permanent*, one-way handoff — once the
    # orchestrator transfers control to personalization_agent,
    # personalization_agent becomes the active agent for the rest of the run,
    # and it has no way to transfer onward to web_agent or back to the
    # orchestrator (it's a separate process with no knowledge of that agent
    # tree). AgentTool gives proper call-and-return semantics instead: the
    # orchestrator calls each remote agent like a function, gets its result
    # back, and stays in control to make the next call and synthesize the
    # final combined answer.
    tools=[AgentTool(agent=web_agent), AgentTool(agent=personalization_agent)],
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
