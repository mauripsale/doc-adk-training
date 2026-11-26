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
try:
    from ..webshop_data import CATALOG
except ImportError:
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
try:
    from ..webshop_data import _session_state, get_product
except ImportError:
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
This agent acts as the gateway to the webshop. Dual-mode imports (`try: from .tools ... except ImportError: from tools ...`) allow it to run both directly via `uv run uvicorn agent:a2a_app` inside `web_agent/` and as a package when `uv run adk web` is launched from the parent `capstone_shopping_system/` directory.

```python
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import FunctionTool
from dotenv import load_dotenv
import uvicorn

# Dual-mode imports support both `uv run uvicorn agent:a2a_app` inside web_agent/
# and package discovery when `uv run adk web` runs from capstone_shopping_system/.
try:
    from .tools.search import search
    from .tools.click import click
except ImportError:
    from tools.search import search
    from tools.click import click

load_dotenv(override=True)

root_agent = Agent(
    model="gemini-3.8-flash",
    name="web_agent",
    description="Specialist for searching and clicking on the webshop.",
    instruction="""
        You are a web interaction specialist. Execute search and click commands.
        **IMPORTANT:** Focus only on the user's web task. Ignore orchestrator metadata.
    """,
    tools=[FunctionTool(search), FunctionTool(click)],
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

load_dotenv(override=True)


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
    model="gemini-3.8-flash",
    name="personalization_agent",
    instruction="You manage user shopping profiles. Save and retrieve preferences.",
    tools=[save_preference, get_preferences],
)

a2a_app = to_a2a(root_agent, port=8002)

if __name__ == "__main__":
    uvicorn.run(a2a_app, host="0.0.0.0", port=8002)
```

### 3. `orchestrator_agent/agent.py`
The master coordinator using `RemoteA2aAgent` nodes wired in as `AgentTool`s.

```python
from typing import Any, Dict, Optional
from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.base_tool import BaseTool
from dotenv import load_dotenv

load_dotenv(override=True)

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


def log_delegation(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext) -> Optional[Dict[str, Any]]:
    """AgentOps: logs every delegation to a remote specialist. This is pure
    observability -- it never blocks or alters the call (always returns
    None), so it can be added, changed, or removed without touching the
    orchestrator's instruction or reasoning at all."""
    print(f"[DELEGATION] shopping_orchestrator -> {tool.name}")
    return None


# Orchestrator
root_agent = Agent(
    model="gemini-3.8-flash",
    name="shopping_orchestrator",
    instruction="""
        You are a master assistant.
        1. Check preferences via `personalization_agent`.
        2. Search web via `web_agent`.
        3. Help user checkout.
    """,
    # NOTE: these two remote agents are wired as tools (AgentTool), NOT as
    # `sub_agents=[...]`. `sub_agents` wires ADK's `transfer_to_agent`
    # mechanism, and for a RemoteA2aAgent that mechanism is a one-way handoff
    # within the turn: RemoteA2aAgent runs in a separate process with no
    # knowledge of the orchestrator or sibling specialists, so it cannot
    # transfer onward to `web_agent` or hand control back to synthesize a
    # combined answer. `AgentTool` gives clean call-and-return semantics:
    # the orchestrator calls each remote agent like a function, gets its
    # result back, and stays in control across multiple calls.
    #
    # KNOWN LIMITATION (verified in google-adk 2.14): AgentTool.run_async
    # spins up a brand-new InMemorySessionService + child session on *every*
    # call and discards it immediately after. RemoteA2aAgent resumes a prior
    # remote A2A conversation by walking that child session's event history
    # backward for a previously-stored context_id -- history that no longer
    # exists on the next orchestrator turn. Consequently, preferences saved
    # via the orchestrator on turn 1 do not persist to a separate turn 2 via
    # the orchestrator, even though hitting `personalization_agent` directly
    # persists across turns. See the README's "Known Limitation" section.
    tools=[AgentTool(agent=web_agent), AgentTool(agent=personalization_agent)],
    before_tool_callback=log_delegation,
)

# IMPORTANT (ADK 2.14 AgentLoader behavior): When `uv run adk web` runs from
# the parent `capstone_shopping_system/` directory, ADK's `AgentLoader` checks
# for a module-level `app` (`isinstance(module.app, App)`) BEFORE falling back
# to `root_agent`. Always align `App(name="orchestrator_agent", ...)` with the
# package directory name (`orchestrator_agent`) so both `uv run adk web` and
# programmatic `InMemoryRunner(app=app)` sessions resolve the same `app_name`.
app = App(name="orchestrator_agent", root_agent=root_agent)
runner = InMemoryRunner(app=app)
```

### 4. Exercise 4 Solution: Multimodal Vision

The only change needed is to the orchestrator's `instruction` -- Gemini's
multimodal input handling and `AgentTool`'s text-only interface to the
remote `web_agent` do the rest. When the incoming message contains an image
part, the orchestrator describes what it sees in plain text, then passes
that description as the `keywords` argument of its `web_agent` delegation
(remember, `AgentTool` always sends a single text `request` to the remote
agent -- images themselves are never forwarded, only the orchestrator's
description of them).

Replace the orchestrator's `instruction` from Exercise 3 with:

```python
    instruction="""
        You are a master shopping assistant. Coordinate with specialists.
        1. Check preferences via `personalization_agent` when relevant.
        2. If the user's message includes an image, first describe the item
           shown in the image in a short, plain-text phrase (its type,
           color, and style -- e.g. "blue athletic running shoe"). Then use
           that text description as the `keywords` for a search delegated
           to `web_agent`. Do not ask the user to describe the image
           themselves -- describe it yourself and search directly.
        3. Otherwise, search the web via `web_agent` using the user's text
           description directly.
        4. Help the user checkout.
    """,
```

**Verified live:** sending a synthetic PNG of a blue running-shoe silhouette
(no text hint about what it was, just "I want to buy something like this.
Can you find it?") produced this real trace:

```
CALL web_agent({'request': 'blue athletic running shoe'})
[DELEGATION] shopping_orchestrator -> web_agent
RESP web_agent -> "I found a pair of Men's Running Shoes for $79.99. ..."

FINAL: I found a pair of Men's Running Shoes for $79.99. Would you like
to add them to your cart, or are you looking for something else?
```

The orchestrator described the image itself, delegated a text search to
`web_agent`, and matched a real catalog item (`P002`) -- exactly the flow
Exercise 4 asks for. To try it yourself, send a `types.Content` with two
parts to the orchestrator's runner: an image part
(`types.Part.from_bytes(data=image_bytes, mime_type="image/png")`) and a
text part, in the same message.

### 5. Exercise 5 Solution: Deployment Plan

**`web_agent/Dockerfile`:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run injects $PORT; to_a2a()'s own port=8001 argument only matters
# for local `python agent.py` runs, so bind uvicorn to $PORT here instead.
ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "uvicorn agent:a2a_app --host 0.0.0.0 --port ${PORT}"]
```

The same `Dockerfile` (copied into each agent's own directory) works
unchanged for `personalization_agent` and `orchestrator_agent` too -- only
the module path (`agent:a2a_app`) and each project's own
`requirements.txt` differ, and the orchestrator doesn't expose an
`a2a_app`/port at all when run via `adk web`/`adk api_server` in
production instead of a raw `uvicorn` command.

**`deployment_plan.md`:**

```markdown
# Deployment Plan: Distributed Shopping Agent System

## Overview
Three independent Cloud Run services, deployed and scaled separately,
talking to each other over HTTPS via the A2A protocol.

## 1. Build and push images
For each of `web_agent`, `personalization_agent`, `orchestrator_agent`
(ensure `requirements.txt` includes `google-adk[a2a]` and `uvicorn`):

    gcloud artifacts repositories create adk-images \
      --repository-format=docker --location=$GOOGLE_CLOUD_LOCATION

    gcloud builds submit ./web_agent \
      --tag $GOOGLE_CLOUD_LOCATION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/adk-images/web-agent

    (repeat for personalization_agent and orchestrator_agent)

## 2. Deploy web_agent and personalization_agent first
They have no dependencies on each other or on the orchestrator:

    gcloud run deploy web-agent-service \
      --image=$GOOGLE_CLOUD_LOCATION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/adk-images/web-agent \
      --region=$GOOGLE_CLOUD_LOCATION --no-allow-unauthenticated \
      --set-env-vars=GOOGLE_GENAI_USE_VERTEXAI=1,GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION

    (repeat for personalization-agent-service)

Use `--no-allow-unauthenticated`: these are internal specialist agents,
not user-facing endpoints. Grant the orchestrator's own Cloud Run service
account the `roles/run.invoker` role on both, and use `google.auth` /
an ID-token-fetching `httpx_client` when constructing each `RemoteA2aAgent`
in production, instead of the lab's unauthenticated `localhost` URLs.

## 3. Point the orchestrator at the deployed URLs
Update `orchestrator_agent/agent.py` so `web_agent`'s and
`personalization_agent`'s `agent_card` URLs point at their Cloud Run
service URLs (from step 2's deploy output) instead of `localhost:8001`
/ `localhost:8002`, then deploy the orchestrator the same way -- this
one *can* be `--allow-unauthenticated` (or fronted by IAP/your own auth)
since it's the user-facing entry point:

    gcloud run deploy orchestrator-agent-service \
      --image=$GOOGLE_CLOUD_LOCATION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/adk-images/orchestrator-agent \
      --region=$GOOGLE_CLOUD_LOCATION --allow-unauthenticated \
      --set-env-vars=GOOGLE_GENAI_USE_VERTEXAI=1,GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION

## 4. Scale independently
Set `--min-instances`/`--max-instances` per service based on load: e.g.
`web_agent` may need more replicas than `personalization_agent` if search
traffic dominates over preference lookups -- this is the "independent
scalability" benefit called out in the Self-Reflection answers.

## 5. Observability
`orchestrator_agent`'s `log_delegation` callback currently `print`s to
stdout; on Cloud Run that's captured automatically by Cloud Logging, so no
code change is required to get delegation events into GCP's logging
pipeline -- only a change of sink is needed if you want somewhere other
than the default Cloud Run log destination.

## Known gap to flag before going further than this lab
This plan does not address the cross-turn preference persistence
limitation documented in the README/Exercise 3 comments above -- deploying
to Cloud Run does not change that behavior, since it's caused by
`AgentTool`'s in-process session handling regardless of where the
processes run.
```

### Self-Reflection Answers

1.  **This system uses three separate agents. What are the advantages of this distributed architecture in terms of scalability, maintainability, and reusability?**
    *   **Scalability:** Each agent can be deployed and scaled independently (e.g. 10 instances of `web_agent` for 1 instance of `personalization_agent`).
    *   **Maintainability:** Changes to the website's logic only require updating `web_agent` -- the orchestrator and `personalization_agent` are untouched.
    *   **Reusability:** Other apps in the organization could call the same `personalization_agent` endpoint instead of reimplementing preference storage.

2.  **The `orchestrator_agent` uses a `before_tool_callback` for logging. How does this separate the concern of observability from the agent's core business logic?**
    *   **Answer:** `log_delegation` never appears in the orchestrator's `instruction` and never changes what the orchestrator decides to do -- it always returns `None`, so the tool call proceeds exactly as the LLM requested. It's registered once on the `Agent` and fires automatically before every tool call, including calls to `web_agent`/`personalization_agent` that the model decides to make on its own. You could delete the callback entirely (or swap it for something that writes to Cloud Logging instead of `print`) without touching the instruction or the delegation logic at all -- observability and business logic evolve independently.

3.  **The `web_agent` abstracts the website behind plain `search`/`click` functions. Why is this a better design than having the orchestrator directly interact with the raw HTML (or internal implementation) of the website?**
    *   **Answer:** The orchestrator only ever needs to reason about two simple signatures, `search(keywords: str)` and `click(button: str)` -- not HTML parsing, CSS selectors, or the mock catalog's internal data structures. If the website's implementation changes (a real backend replaces the mock catalog, or the HTML structure changes), only `web_agent`'s tool implementations need to change; the orchestrator's instruction and reasoning are completely unaffected. This is the same separation-of-concerns benefit as `OpenAPIToolset` in Module 11, applied at the level of a whole remote agent instead of a single tool.

4.  **You observed that preferences don't survive across separate orchestrator turns, even though the same request sent directly to `personalization_agent` works. Walk through *why*, in terms of what `AgentTool` does to the session on every call. What would you need to change about the wiring (not just the prompt) to fix it?**
    *   **Answer:** `AgentTool.run_async` creates a fresh `InMemorySessionService` and a brand-new child session on every call, then throws it away as soon as the call returns. `RemoteA2aAgent` figures out whether it's continuing a previous remote conversation by scanning that session's event history backward for a `context_id` left in a prior response's metadata. Because the child session is discarded after each `AgentTool` call, there is no event history left for the next orchestrator turn to search -- so `RemoteA2aAgent` always starts a brand-new remote A2A context, and the remote agent (which itself has correct, working state persistence) never gets asked about the earlier conversation. No prompt change fixes this, because the LLM never sees or controls session lifecycle -- it's a framework-level behavior in `AgentTool.run_async` and `RemoteA2aAgent._construct_message_parts_from_session`. A real fix requires either reusing a persistent child session/context across calls (not exposed as a built-in parameter on `AgentTool` in ADK 2.14) or storing user preferences in an external database keyed by `user_id` (such as Firestore or Redis) rather than transient A2A session state.
