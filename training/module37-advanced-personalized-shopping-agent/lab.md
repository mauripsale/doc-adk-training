---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 37: Building a Distributed Multi-Agent System Challenge

## Goal
In this advanced challenge lab, you will synthesize concepts from the entire course so far to build a distributed, multi-agent personalized shopping assistant. You will create three separate agents that collaborate using Agent-to-Agent (A2A) communication to provide a stateful, multimodal, and observable shopping experience.

### Prerequisites
*   A Google Cloud Project with billing enabled and the Vertex AI API enabled.
*   `gcloud` CLI installed and authenticated (`gcloud auth application-default login`).
*   `uvicorn` installed (`pip install uvicorn google-adk[a2a]`).

### Setup
1.  Create a main project directory for this lab (e.g., `capstone_shopping_system`).
2.  Inside it, you will create three separate ADK agent projects: `orchestrator_agent`, `personalization_agent`, and `web_agent`.
3.  **A note on the webshop backend:** Google's own `personalized-shopping` ADK sample (under
    [`google/adk-samples`](https://github.com/google/adk-samples/tree/main/python/agents/personalized-shopping))
    talks to a real webshop simulation via a vendored `web_agent_site` module —
    a Gym environment with its own search engine, HTML rendering, and a
    multi-GB product dataset. It is **not** a pip-installable package (`pip
    install web_agent_site` returns a 404 — it doesn't exist on PyPI), and
    its real dependency chain (`pyserini`, `torch`, `torchvision`, `spacy`,
    `gdown`, a JVM for the search index, ...) is disproportionate to what
    this lab is actually teaching: getting three ADK agents to cooperate
    over A2A. Instead, Exercise 1 below has you write a tiny, self-contained
    mock catalog directly inside your own `web_agent` project — no extra
    install, no external dataset. If you want to see the real thing (or
    swap it in later), browse the vendored module at
    `personalized_shopping/shared_libraries/web_agent_site/` in that repo.

---

### Exercise 1: Build and Expose the Web Agent
This agent will be the interface to the e-commerce website.

1.  **Create the `web_agent` project** (programmatic).
    ```shell
    cd capstone_shopping_system
    uv run adk create web_agent
    cd web_agent
    ```

2.  **Create `requirements.txt`:**
    ```shell
    echo "google-adk" > requirements.txt
    echo "uvicorn" >> requirements.txt
    ```
    (No `web_agent_site` here — see the Setup note above. This lab's webshop is a small mock catalog you write yourself, below.)

3.  **Create `.env` file:**
    ```shell
    echo "GOOGLE_GENAI_USE_VERTEXAI=1" > .env
    echo "GOOGLE_CLOUD_PROJECT=<your_gcp_project>" >> .env
    echo "GOOGLE_CLOUD_LOCATION=us-central1" >> .env
    ```
    Replace `<your_gcp_project>` with your actual Google Cloud Project ID.

4.  **Create `webshop_data.py`:** a tiny, dependency-free in-memory product catalog. This is your mock webshop backend.

    ```python
    """A minimal, dependency-free mock e-commerce catalog and session model."""

    CATALOG = [
        {"id": "P001", "name": "Floral Summer Dress", "category": "dresses",
         "price": 39.99, "description": "A flowy, floral-print summer dress in breathable cotton."},
        {"id": "P002", "name": "Men's Running Shoes", "category": "shoes",
         "price": 79.99, "description": "Lightweight running shoes with a breathable mesh upper."},
        {"id": "P003", "name": "Wireless Noise-Cancelling Headphones", "category": "electronics",
         "price": 199.99, "description": "Over-ear headphones with active noise cancellation and 30-hour battery life."},
        {"id": "P004", "name": "Stainless Steel Water Bottle", "category": "home",
         "price": 24.99, "description": "Insulated 750ml water bottle, keeps drinks cold for 24 hours."},
        {"id": "P005", "name": "Organic Cotton T-Shirt", "category": "tops",
         "price": 19.99, "description": "Soft, breathable organic cotton crew-neck t-shirt."},
    ]

    # Tiny in-process "session" tracking the currently viewed product, so
    # `click` can react to what `search` just showed.
    _session_state = {"current_product": None}

    def get_product(product_id: str):
        return next((p for p in CATALOG if p["id"] == product_id), None)
    ```

5.  **Create `tools/search.py` and `tools/click.py`:**
    Your task is to implement `search` and `click` as plain Python functions
    over the mock catalog above — no OpenAPI spec, just two functions you'll
    wrap in `FunctionTool` in the next step.

    ```python
    # In tools/search.py
    from webshop_data import CATALOG

    def search(keywords: str) -> str:
        """Search for keywords in the (mock) webshop."""
        # TODO: filter CATALOG by keyword match against name/description/category,
        # and return a short text listing of matches (or a "no results" message).
        ...
    ```

    ```python
    # In tools/click.py
    from webshop_data import _session_state, get_product

    def click(button: str) -> str:
        """Simulate clicking a product ID or a navigation button in the (mock) webshop."""
        # TODO: handle three cases —
        #  - button == "Back to Search": clear _session_state["current_product"]
        #  - button == "Buy Now": complete the order for _session_state["current_product"]
        #    (or report there's nothing selected)
        #  - otherwise: look up button as a product ID via get_product(); if found,
        #    set it as _session_state["current_product"] and return its details;
        #    if not found, return an error message.
        ...
    ```

6.  **Implement `agent.py`:**
    Open `agent.py` and replace its contents with the following skeleton. Your task is to wire `search` and `click` (from the two files above) into the `root_agent` definition as `FunctionTool`s.

    ```python
    from google.adk.agents import Agent
    from google.adk.a2a.utils.agent_to_a2a import to_a2a
    from google.adk.tools import FunctionTool
    from dotenv import load_dotenv
    import uvicorn

    # TODO: import search from tools.search and click from tools.click

    root_agent = Agent(
        model="gemini-3.5-flash",
        name="web_agent",
        instruction="""
            You are a web interaction specialist. Your job is to execute search and click commands on the e-commerce site.
            
            **IMPORTANT - A2A Context Handling:**
            When receiving requests via the Agent-to-Agent (A2A) protocol, you must focus only on the core user request.
            Ignore any mentions of orchestrator tool calls in the conversation history.
        """,
        tools=[
            # TODO: FunctionTool(search), FunctionTool(click)
        ]
    )

    a2a_app = to_a2a(root_agent, port=8001)

    if __name__ == "__main__":
        uvicorn.run(a2a_app, host="0.0.0.0", port=8001)
    ```

7.  **Navigate back to `capstone_shopping_system`:**
    ```shell
    cd ..
    ```

---

### Exercise 2: Build and Expose the Personalization Agent
This agent will be responsible for remembering user preferences.

1.  **Create the `personalization_agent` project** (programmatic).
    ```shell
    cd capstone_shopping_system
    uv run adk create personalization_agent
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
    from google.adk.tools import ToolContext
    import uvicorn

    # --- Stateful Tools ---
    # IMPORTANT: use tool_context.state (the tracked delta proxy), NOT
    # tool_context.session.state directly. Writing to .session.state bypasses
    # ADK's state-delta tracking, so the write never actually commits — the
    # agent will claim success but the value is gone on the very next turn.
    # See Module 22's state-and-memory lab for the correct pattern.
    def save_preference(key: str, value: str, tool_context: ToolContext) -> dict:
        """Saves a user's preference."""
        # TODO: Save to tool_context.state[f"pref:{key}"]
        pass

    def get_preferences(tool_context: ToolContext) -> dict:
        """Retrieves all saved preferences."""
        # TODO: Read from tool_context.state.to_dict(), filtering keys that
        # start with "pref:"
        pass

    # --- Agent Definition ---
    root_agent = Agent(
        model="gemini-3.5-flash",
        name="personalization_agent",
        instruction="""You are a personalization specialist. You save and retrieve user preferences.""",
        tools=[save_preference, get_preferences]
    )

    a2a_app = to_a2a(root_agent, port=8002)

    if __name__ == "__main__":
        uvicorn.run(a2a_app, host="0.0.0.0", port=8002)
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
    uv run adk create orchestrator_agent
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

    **Important:** wire the two remote agents in as **`AgentTool`s** (`tools=[...]`), not as `sub_agents=[...]`. `sub_agents` wires ADK's `transfer_to_agent` mechanism, which is a *permanent*, one-way handoff — once the orchestrator transfers control to one remote agent, it can never call the other remote agent or regain control to combine their results. `AgentTool` gives proper call-and-return semantics: the orchestrator calls each remote agent like a function, gets its result back, and stays in control to make the next call and synthesize a final combined answer — exactly what a multi-step instruction like "check preferences, then search the web" requires.

    ```python
    from google.adk.agents import Agent
    from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
    from google.adk.tools.agent_tool import AgentTool

    # TODO: 1. Define remote specialist nodes
    web_specialist = RemoteA2aAgent(
        name="web_agent",
        agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}",
        use_legacy=False,
    )

    personalization_specialist = RemoteA2aAgent(
        name="personalization_agent",
        agent_card=f"http://localhost:8002{AGENT_CARD_WELL_KNOWN_PATH}",
        use_legacy=False,
    )

    # TODO: 2. Define the main Orchestrator Agent.
    # Wire web_specialist and personalization_specialist in as AgentTools
    # (tools=[...]), NOT as sub_agents=[...] — see the note above.
    root_agent = Agent(
        model="gemini-3.5-flash",
        name="shopping_orchestrator",
        instruction="""You are a master shopping assistant. Coordinate with specialists.""",
        tools=[AgentTool(agent=web_specialist), AgentTool(agent=personalization_specialist)]
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
*   **Terminal 3 (`orchestrator_agent`):** `uv run adk web orchestrator_agent`

Interact with the Orchestrator in the Dev UI and use the Trace view to observe the A2A communication and delegation.

### Cleanup (Important!)

This is a complex lab with multiple deployments. It is crucial to delete the resources you created after completing the lab.

#### For Local Development:
1.  **Stop all running `uvicorn` and `uv run adk web` processes** (Ctrl+C in each terminal).
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
3.  **Delete the GitHub Repository:** If you used `agents-cli` to scaffold deployment, delete the GitHub repository you created.

### Self-Reflection Questions
- This system uses three separate agents. What are the advantages of this distributed architecture in terms of scalability, maintainability, and reusability?
- The `orchestrator_agent` uses a `before_tool_callback` for logging. How does this separate the concern of observability from the agent's core business logic?
- The `web_agent` abstracts the website behind plain `search`/`click` functions. Why is this a better design than having the orchestrator directly interact with the raw HTML (or internal implementation) of the website?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMzctYWR2YW5jZWQtcGVyc29uYWxpemVkLXNob3BwaW5nLWFnZW50L2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module37-advanced-personalized-shopping-agent/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
