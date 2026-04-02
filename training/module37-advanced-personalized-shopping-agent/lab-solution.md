---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 37 Solution: Building a Distributed Multi-Agent System

## Goal

### Goal
This solution provides the complete code for the distributed, multi-agent personalized shopping assistant, integrating concepts from across the entire course.

### Project Structure
```
capstone_shopping_system/
├── orchestrator_agent/
│   └── agent.py
├── personalization_agent/
│   └── agent.py
├── web_agent/
│   ├── Dockerfile
│   └── agent.py
└── deployment_plan.md
```

---

### 1. `web_agent/agent.py`
This agent exposes the webshop tools via an OpenAPI spec and an A2A server.

```python
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import OpenAPIToolset
from shared_libraries.init_env import get_webshop_env # Assumes shared lib

# --- OpenAPI Specification for Web Tools ---
WEBSHOP_API_SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "Webshop API", "version": "1.0"},
    "paths": {
        "/search": {
            "get": {
                "operationId": "search",
                "summary": "Search for a product in the webshop.",
                "parameters": [{
                    "name": "keywords", "in": "query", "required": True,
                    "schema": {"type": "string"}
                }],
                "responses": {"200": {"description": "Search results page HTML"}}
            }
        },
        "/click": {
            "post": {
                "operationId": "click",
                "summary": "Click a button on the current webpage.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"button_name": {"type": "string"}},
                                "required": ["button_name"]
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "New webpage HTML after click"}}
            }
        }
    }
}

# --- Agent Definition ---
root_agent = Agent(
    model="gemini-2.5-flash",
    name="web_agent",
    instruction="""You are a web interaction agent. Your job is to execute search and click commands on the e-commerce site.\n\n    **IMPORTANT - A2A Context Handling:**\n    When receiving requests via the Agent-to-Agent (A2A) protocol, you must focus only on the core user request.\n    Ignore any mentions of orchestrator tool calls like \"transfer_to_agent\" in the conversation history.\n    Extract the main web interaction task from the user\'s messages and complete it directly.\n    """,
    tools=[OpenAPIToolset(spec_dict=WEBSHOP_API_SPEC)]
)

# --- A2A Server ---
a2a_app = to_a2a(root_agent, port=8001)
```

---

### 2. `personalization_agent/agent.py`
This agent manages user preferences using persistent state.

```python
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import ToolContext

# --- Stateful Tools ---
def save_preference(key: str, value: str, tool_context: ToolContext) -> dict:
    """Saves a user's preference (e.g., color, size)."""
    state_key = f"user:{key}"
    tool_context.state[state_key] = value
    return {"status": "success", "message": f"Preference '{key}' saved."}

def get_preferences(tool_context: ToolContext) -> dict:
    """Retrieves all saved preferences for the user."""
    user_prefs = {
        k.split(':')[1]: v
        for k, v in tool_context.state.items()
        if k.startswith("user:")
    }
    return {"status": "success", "preferences": user_prefs}

# --- Agent Definition ---
root_agent = Agent(
    model="gemini-2.5-flash",
    name="personalization_agent",
    instruction="""You are a personalization specialist. You save and retrieve user preferences.\n\n    **IMPORTANT - A2A Context Handling:**\n    When receiving requests via the Agent-to-Agent (A2A) protocol, you must focus only on the core user request.\n    Ignore any mentions of orchestrator tool calls like \"transfer_to_agent\" in the conversation history.\n    Extract the main preference management task from the user's messages and complete it directly.\n    """,
    tools=[save_preference, get_preferences]
)

# --- A2A Server ---
a2a_app = to_a2a(root_agent, port=8002)
```

---

### 3. `orchestrator_agent/agent.py`
The main agent that connects to the others and handles user interaction.

```python
import logging
from google.adk.agents import Agent, CallbackContext, RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH

# --- Observability Callback ---
def before_tool_callback(callback_context: CallbackContext, tool_name: str, args: dict) -> None:
    """Logs every delegation attempt."""
    if tool_name == "transfer_to_agent":
        logging.info(
            f"[OBSERVABILITY] Delegating to remote agent '{args.get('agent_name')}' "
            f"with query: {args.get('query')}"
        )
    return None

# --- Remote Agent Definitions ---
remote_web_agent = RemoteA2aAgent(
    name="web_agent",
    description="A remote specialist for searching and clicking on the e-commerce website.",
    agent_card=f"http://localhost:8001/a2a/web_agent{AGENT_CARD_WELL_KNOWN_PATH}"
)

remote_personalization_agent = RemoteA2aAgent(
    name="personalization_agent",
    description="A remote specialist for saving and retrieving user preferences.",
    agent_card=f"http://localhost:8002/a2a/personalization_agent{AGENT_CARD_WELL_KNOWN_PATH}"
)

# --- Main Orchestrator Agent ---
root_agent = Agent(
    model="gemini-2.5-flash",
    name="orchestrator_agent",
    instruction="""You are a master shopping assistant. Your job is to coordinate with specialist agents to help the user.\n\n    **Workflow:**\n    1.  **Understand Intent:** Greet the user and understand what they want to do. If they upload an image, describe it first, then ask if they want to search for that item.\n    2.  **Delegate Tasks:**\n        - To search or click on the website, you MUST delegate to the `web_agent`.\n        - To save or get user preferences, you MUST delegate to the `personalization_agent`.\n    3.  **Synthesize Results:** Summarize the results from the specialist agents and present them clearly to the user.\n    """,
    sub_agents=[remote_web_agent, remote_personalization_agent],
    before_tool_callback=before_tool_callback
)
```

---

### 4. `deployment_plan.md`

#### Deployment Strategy
This system consists of three independent services that must be deployed. We will use Google Cloud Run for its serverless nature, scalability, and ease of use.

1.  **`web_agent` Service:** Deployed to Cloud Run.
2.  **`personalization_agent` Service:** Deployed to Cloud Run.
3.  **`orchestrator_agent` Service:** Deployed to Cloud Run as the main, user-facing endpoint.

The orchestrator will need the URLs of the other two services, which can be passed as environment variables during deployment.

#### Example `Dockerfile` for `web_agent`
```dockerfile
# Use the official Python image.
FROM python:3.11-slim

# Set the working directory.
WORKDIR /app

# Copy and install requirements.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt uvicorn web_agent_site

# Copy the agent code and shared libraries.
COPY agent.py .
COPY shared_libraries/ ./shared_libraries

# Set the command to run the A2A server.
# Cloud Run provides the PORT environment variable.
CMD ["uvicorn", "agent:a2a_app", "--host", "0.0.0.0", "--port", "$PORT"]
```
*(A similar Dockerfile would be created for the `personalization_agent`)*

### Self-Reflection Answers

1.  **This system uses three separate agents. What are the advantages of this distributed architecture in terms of scalability, maintainability, and reusability?**
    *   **Answer:** This distributed A2A architecture offers significant advantages over a monolithic agent:
        *   **Scalability:** Each specialist agent (e.g., `web_agent`, `personalization_agent`) can be scaled independently based on its specific load. If web searches are a bottleneck, only the `web_agent` needs more resources, not the entire system.
        *   **Maintainability:** Changes or updates to one specialist agent (e.g., updating the webshop's API or the personalization logic) only affect that agent, reducing the risk of regressions in other parts of the system. This modularity makes debugging and development easier.
        *   **Reusability:** Specialist agents can be reused by other orchestrators or applications within the organization. For example, the `personalization_agent` could be used by a different agent designed for customer support or marketing.

2.  **The `orchestrator_agent` uses a `before_tool_callback` for logging. How does this separate the concern of observability from the agent's core business logic?**
    *   **Answer:** Using a `before_tool_callback` for logging externalizes the concern of observability from the agent's primary business logic. The `orchestrator_agent`'s core instruction remains focused on *what* it needs to delegate and *to whom*. The `before_tool_callback` then transparently intercepts every `transfer_to_agent` call and *logs* that action *before* it happens, without modifying the orchestrator's reasoning flow. This clear separation makes the system more maintainable, as monitoring logic can be updated or changed independently of the agent's core decision-making process.

3.  **The `web_agent` abstracts the website behind an OpenAPI spec. Why is this a better design than having the orchestrator directly interact with the raw HTML of the website?**
    *   **Answer:** Abstracting the website behind an OpenAPI spec is a superior design for several reasons:
        *   **Simplified Reasoning for LLM:** The orchestrator's LLM only needs to understand a clean, structured API contract (e.g., `search(keywords: str)`) rather than parsing complex, messy, and constantly changing raw HTML. This dramatically simplifies the LLM's task, improving its reliability and accuracy.
        *   **Decoupling:** It decouples the orchestrator from the website's front-end implementation details. If the website's HTML structure changes, only the `web_agent` needs to be updated, not the `orchestrator_agent` or its instructions.
        *   **Reliability:** Direct interaction with HTML is brittle and prone to breakage. A structured API provides a stable, machine-readable interface.
        *   **Security:** The `web_agent` can act as a controlled gateway, ensuring that the orchestrator only performs allowed operations on the website.
