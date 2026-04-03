---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 37: Building a Distributed Multi-Agent System Challenge

## Goal
In this capstone lab, you will synthesize concepts from the entire course to build a distributed, multi-agent personalized shopping assistant. You will create three separate agents that collaborate using Agent-to-Agent (A2A) communication to provide a stateful, multimodal, and observable shopping experience.

### Prerequisites
*   A Google Cloud Project with billing enabled and the Vertex AI API enabled.
*   `gcloud` CLI installed and authenticated (`gcloud auth application-default login`).
*   `uvicorn` installed (`pip install uvicorn google-adk[a2a]`).
*   `web_agent_site` installed (`pip install web_agent_site`).

### Setup
1.  Create a main project directory for this lab (e.g., `capstone_shopping_system`).
2.  Inside it, you will create three separate ADK agent projects: `orchestrator_agent`, `personalization_agent`, and `web_agent`.
3.  Copy the `shared_libraries` and data from the original `personalized-shopping` sample into a shared location accessible by all three agents.

---

### Exercise 1: Build and Expose the Web Agent
This agent will be the interface to the e-commerce website.

1.  **Create the `web_agent` project** (programmatic).
    ```shell
    cd capstone_shopping_system
    adk create web_agent
    cd web_agent
    ```

2.  **Create `requirements.txt`:**
    ```shell
    echo "google-adk" > requirements.txt
    echo "uvicorn" >> requirements.txt
    echo "web_agent_site" >> requirements.txt
    ```

3.  **Create `.env` file:**
    ```shell
    echo "GOOGLE_GENAI_USE_VERTEXAI=1" > .env
    echo "GOOGLE_CLOUD_PROJECT=<your_gcp_project>" >> .env
    echo "GOOGLE_CLOUD_LOCATION=us-central1" >> .env
    ```
    Replace `<your_gcp_project>` with your actual Google Cloud Project ID.

4.  **Implement `agent.py`:**
    Open `agent.py` and replace its contents with the following skeleton. Your task is to complete the `WEBSHOP_API_SPEC` and the `root_agent` definition.

    ```python
    from google.adk.agents import Agent
    from google.adk.a2a.utils.agent_to_a2a import to_a2a
    from dotenv import load_dotenv
    load_dotenv()

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
    # TODO: Define the `root_agent`. It should be an `Agent` that:
    # - Uses the `gemini-2.5-flash` model.
    # - Is named "web_agent".
    # - Has an instruction to act as a web interaction agent, executing search and click commands.
    # - Includes the A2A Context Handling instruction to ignore orchestrator tool calls.
    # - Uses the `OpenAPIToolset` with `WEBSHOP_API_SPEC` as its tools.
    root_agent = Agent(
        model="gemini-2.5-flash",
        name="web_agent",
        instruction="""You are a web interaction agent. Your job is to execute search and click commands on the e-commerce site.\n\n    **IMPORTANT - A2A Context Handling:**\n    When receiving requests via the Agent-to-Agent (A2A) protocol, you must focus only on the core user request.\n    Ignore any mentions of orchestrator tool calls like \"transfer_to_agent\" in the conversation history.\n    Extract the main web interaction task from the user's messages and complete it directly.\n    """,
        tools=[OpenAPIToolset(spec_dict=WEBSHOP_API_SPEC)]
    )

    # --- A2A Server ---
    a2a_app = to_a2a(root_agent, port=8001)
    ```

5.  **Navigate back to `capstone_shopping_system`:**
    ```shell
    cd ..
    ```

---

### Exercise 2: Build and Expose the Personalization Agent
This agent will be responsible for remembering user preferences.

1.  **Create the `personalization_agent` project** (programmatic).
    ```shell
    cd capstone_shopping_system
    adk create personalization_agent
    cd personalization_agent
    ```

2.  **Create `requirements.txt`:**
    ```shell
    echo "google-adk" > requirements.txt
    echo "uvicorn" >> requirements.txt
    ```

3.  **Create `.env` file:**
    ```shell
    echo "GOOGLE_GENAI_USE_VERTEXAI=1" > .env
    echo "GOOGLE_CLOUD_PROJECT=<your_gcp_project>" >> .env
    echo "GOOGLE_CLOUD_LOCATION=us-central1" >> .env
    ```
    Replace `<your_gcp_project>` with your actual Google Cloud Project ID.

4.  **Implement `agent.py`:**
    Open `agent.py` and replace its contents with the following skeleton. Your task is to implement the `save_preference` and `get_preferences` tools.

    ```python
    from google.adk.agents import Agent
    from google.adk.a2a.utils.agent_to_a2a import to_a2a
    from dotenv import load_dotenv
    load_dotenv()

    from google.adk.tools import ToolContext

    # --- Stateful Tools ---
    def save_preference(key: str, value: str, tool_context: ToolContext) -> dict:
        """Saves a user's preference (e.g., color, size)."""
        # TODO: Implement state management to save the preference.
        state_key = f"user:{key}"
        tool_context.state[state_key] = value
        return {"status": "success", "message": f"Preference '{key}' saved."}

    def get_preferences(tool_context: ToolContext) -> dict:
        """Retrieves all saved preferences for the user."""
        # TODO: Implement state management to retrieve all preferences.
        user_prefs = {
            k.split(':')[1]: v
            for k, v in tool_context.state.items()
            if k.startswith("user:")
        }
        return {"status": "success", "preferences": user_prefs}

    # --- Agent Definition ---
    # TODO: Define the `root_agent`. It should be an `Agent` that:
    # - Uses the `gemini-2.5-flash` model.
    # - Is named "personalization_agent".
    # - Has an instruction to act as a personalization specialist, saving and retrieving user preferences.
    # - Includes the A2A Context Handling instruction to ignore orchestrator tool calls.
    # - Uses the `save_preference` and `get_preferences` tools.
    root_agent = Agent(
        model="gemini-2.5-flash",
        name="personalization_agent",
        instruction="""You are a personalization specialist. You save and retrieve user preferences.\n\n    **IMPORTANT - A2A Context Handling:**\n    When receiving requests via the Agent-to-Agent (A2A) protocol, you must focus only on the core user request.\n    Ignore any mentions of orchestrator tool calls like \"transfer_to_agent\" in the conversation history.\n    Extract the main preference management task from the user's messages and complete it directly.\n    """,
        tools=[save_preference, get_preferences]
    )

    # --- A2A Server ---
    a2a_app = to_a2a(root_agent, port=8002)
    ```

5.  **Navigate back to `capstone_shopping_system`:**
    ```shell
    cd ..
    ```

---

### Exercise 3: Build the Orchestrator Agent
This is the main, user-facing agent that will coordinate the others.

1.  **Create the `orchestrator_agent` project** (programmatic).
    ```shell
    cd capstone_shopping_system
    adk create orchestrator_agent
    cd orchestrator_agent
    ```

2.  **Create `requirements.txt`:**
    ```shell
    echo "google-adk" > requirements.txt
    echo "uvicorn" >> requirements.txt
    ```

3.  **Create `.env` file:**
    ```shell
    echo "GOOGLE_GENAI_USE_VERTEXAI=1" > .env
    echo "GOOGLE_CLOUD_PROJECT=<your_gcp_project>" >> .env
    echo "GOOGLE_CLOUD_LOCATION=us-central1" >> .env
    ```
    Replace `<your_gcp_project>` with your actual Google Cloud Project ID.

4.  **Implement `agent.py`:**
    Open `agent.py` and replace its contents with the following skeleton. Your task is to define the `RemoteA2aAgent` instances and complete the `root_agent` definition.

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
    # TODO: 1. Define `remote_web_agent` as a `RemoteA2aAgent`.
    # - Name: "web_agent"
    # - Description: "A remote specialist for searching and clicking on the e-commerce website."
    # - agent_card: Point to the web_agent server at `http://localhost:8001/a2a/web_agent/.well-known/agent-card.json`.
    remote_web_agent = RemoteA2aAgent(
        name="web_agent",
        description="A remote specialist for searching and clicking on the e-commerce website.",
        agent_card=f"http://localhost:8001/a2a/web_agent{AGENT_CARD_WELL_KNOWN_PATH}"
    )

    # TODO: 2. Define `remote_personalization_agent` as a `RemoteA2aAgent`.
    # - Name: "personalization_agent"
    # - Description: "A remote specialist for saving and retrieving user preferences."
    # - agent_card: Point to the personalization_agent server at `http://localhost:8002/a2a/personalization_agent/.well-known/agent-card.json`.
    remote_personalization_agent = RemoteA2aAgent(
        name="personalization_agent",
        description="A remote specialist for saving and retrieving user preferences.",
        agent_card=f"http://localhost:8002/a2a/personalization_agent{AGENT_CARD_WELL_KNOWN_PATH}"
    )

    # --- Main Orchestrator Agent ---
    # TODO: 3. Define the `root_agent`. It should be an `Agent` that:
    # - Uses the `gemini-2.5-flash` model.
    # - Is named "orchestrator_agent".
    # - Has an instruction to act as a master shopping assistant, coordinating with specialists.
    # - Its `sub_agents` list should contain `remote_web_agent` and `remote_personalization_agent`.
    # - Registers the `before_tool_callback` for observability.
    root_agent = Agent(
        model="gemini-2.5-flash",
        name="orchestrator_agent",
        instruction="""You are a master shopping assistant. Your job is to coordinate with specialist agents to help the user.\n\n    **Workflow:**\n    1.  **Understand Intent:** Greet the user and understand what they want to do. If they upload an image, describe it first, then ask if they want to search for that item.\n    2.  **Delegate Tasks:**\n        - To search or click on the website, you MUST delegate to the `web_agent`.\n        - To save or get user preferences, you MUST delegate to the `personalization_agent`.\n    3.  **Synthesize Results:** Summarize the results from the specialist agents and present them clearly to the user.\n    """,
        sub_agents=[remote_web_agent, remote_personalization_agent],
        before_tool_callback=before_tool_callback
    )
    ```

5.  **Navigate back to `capstone_shopping_system`:**
    ```shell
    cd ..
    ```

---

### Exercise 4: Add Multimodal Vision
Enhance the Orchestrator to handle image-based searches.

1.  **Challenge: Update the Orchestrator's `instruction` prompt.** Add logic to handle image uploads. If a user provides an image, instruct the agent to:
    a.  First, describe the item in the image.
    b.  Then, use that text description to perform a search by delegating to the `web_agent`.

---

### Exercise 5: Create a Deployment Plan
Plan how you would deploy this distributed system.

1.  **Challenge: Create a `Dockerfile`** for the `web_agent`. This file should define the steps to build a container image for your remote agent.
2.  **Create a `deployment_plan.md` file.** In this file, briefly explain the steps you would take to deploy the `orchestrator_agent`, `web_agent`, and `personalization_agent` as separate services on Google Cloud Run.

### Running the System
To test your full system, you will need to run all three agents in separate terminals:
*   **Terminal 1 (`web_agent`):** `uvicorn agent:a2a_app --host localhost --port 8001`
*   **Terminal 2 (`personalization_agent`):** `uvicorn agent:a2a_app --host localhost --port 8002`
*   **Terminal 3 (`orchestrator_agent`):** `adk web orchestrator_agent`

Interact with the Orchestrator in the Dev UI and use the Trace view to observe the A2A communication and delegation.

### Cleanup (Important!)

This is a complex lab with multiple deployments. It is crucial to delete the resources you created after completing the lab.

#### For Local Development:
1.  **Stop all running `uvicorn` and `adk web` processes** (Ctrl+C in each terminal).
2.  **Delete the `capstone_shopping_system` directory:**
    ```shell
    cd ..
    rm -rf capstone_shopping_system
    ```

#### For Cloud Deployments (if you completed Exercise 5):
1.  **Delete Cloud Run Services:**
    ```shell
    gcloud run services delete web-agent-service --region=$GOOGLE_CLOUD_LOCATION --async
    gcloud run services delete personalization-agent-service --region=$GOOGLE_CLOUD_LOCATION --async
    gcloud run services delete orchestrator-agent-service --region=$GOOGLE_CLOUD_LOCATION --async
    ```
2.  **Delete Artifact Registry Repository:**
    ```shell
    gcloud artifacts repositories delete adk-images --location=$GOOGLE_CLOUD_LOCATION --async
    ```
3.  **Delete the GitHub Repository:** If you used the Agent Starter Pack, delete the GitHub repository you created.

### Self-Reflection Questions
- This system uses three separate agents. What are the advantages of this distributed architecture in terms of scalability, maintainability, and reusability?
- The `orchestrator_agent` uses a `before_tool_callback` for logging. How does this separate the concern of observability from the agent's core business logic?
- The `web_agent` abstracts the website behind an OpenAPI spec. Why is this a better design than having the orchestrator directly interact with the raw HTML of the website?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMzctYWR2YW5jZWQtcGVyc29uYWxpemVkLXNob3BwaW5nLWFnZW50L2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module37-advanced-personalized-shopping-agent/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
