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
    uv run adk create web_agent
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
    from google.adk.tools import FunctionTool
    from dotenv import load_dotenv
    import uvicorn
    
    # Assume tools search and click are imported
    
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
            FunctionTool(func=search),
            FunctionTool(func=click),
        ]
    )

    a2a_app = to_a2a(root_agent, port=8001)

    if __name__ == "__main__":
        uvicorn.run(a2a_app, host="0.0.0.0", port=8001)
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
    def save_preference(key: str, value: str, tool_context: ToolContext) -> dict:
        """Saves a user's preference."""
        # TODO: Save to tool_context.session.state
        pass

    def get_preferences(tool_context: ToolContext) -> dict:
        """Retrieves all saved preferences."""
        # TODO: Read from tool_context.session.state
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

    ```python
    from google.adk.agents import Agent
    from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH

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

    # TODO: 2. Define the main Orchestrator Agent
    root_agent = Agent(
        model="gemini-3.5-flash",
        name="shopping_orchestrator",
        instruction="""You are a master shopping assistant. Coordinate with specialists.""",
        sub_agents=[web_specialist, personalization_specialist]
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
- The `web_agent` abstracts the website behind an OpenAPI spec. Why is this a better design than having the orchestrator directly interact with the raw HTML of the website?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMzctYWR2YW5jZWQtcGVyc29uYWxpemVkLXNob3BwaW5nLWFnZW50L2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module37-advanced-personalized-shopping-agent/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
