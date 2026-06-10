---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 35 Solution: Deploying an Agent to Agent Runtime

## Goal

This lab is a procedural tutorial. The solution for both parts is a successfully deployed Agent Runtime instance.

---

### Part 1: Accelerated Deployment Solution

After running `make backend`, a successful run of the command is the primary indicator of success.

**Expected Outcome:**
*   The `make backend` command completes without errors in your terminal.
*   A new agent with the name you configured appears in the **Agent Platform -> Agent Runtime** section of the Google Cloud Console.
*   You can copy the **Agent Runtime ID** from the console to use with a client application.

---

### Part 2: Standard Deployment Solution

This section contains the complete code for the `deploy.py` and `interact.py` scripts used in the manual deployment part of the lab.

#### `multi_tool_agent/agent.py`

This file defines the agent using the modern ADK 2.0 `Agent` class.

```python
from google.adk import Agent
import random

def roll_die(sides: int, count: int = 1) -> dict:
    """Rolls a die with a specified number of sides, multiple times."""
    rolls = [random.randint(1, sides) for _ in range(count)]
    return {"rolls": rolls}

def check_prime(number: int) -> dict:
    """Checks if a number is prime."""
    if number < 2:
        is_prime = False
    else:
        is_prime = all(number % i != 0 for i in range(2, int(number**0.5) + 1))
    return {"is_prime": is_prime}

root_agent = Agent(
    model="gemini-3.5-flash",
    name="multi_tool_agent",
    instruction="You roll dice and answer questions about prime numbers.",
    tools=[roll_die, check_prime],
)
```

#### `deploy.py`

This script uses the Vertex AI SDK to package and deploy the agent.

```python
import vertexai
from vertexai import agent_engines
from google.adk.apps import App
from multi_tool_agent.agent import root_agent

# --- CONFIGURATION ---
PROJECT_ID = "your-gcp-project-id"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://your-unique-bucket-name"
AGENT_DISPLAY_NAME = "my-multi_tool_agent"

def main():
    # Initialize Vertex AI SDK
    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

    # 1. Wrap your agent in an App (Required for ADK 2.0 deployment)
    print("Wrapping agent in App...")
    app = App(
        name="multi_tool_app",
        root_agent=root_agent
    )

    # 2. Deploy to Agent Runtime
    # The 'agent_engines.create' function accepts an App object.
    print(f"Deploying '{AGENT_DISPLAY_NAME}' to Agent Runtime...")
    remote_app = agent_engines.create(
        agent_engine=app,
        display_name=AGENT_DISPLAY_NAME,
        # Ensure the remote environment uses the modern SDK
        requirements=["google-cloud-aiplatform[adk,agent_engines]>=1.111"],
    )

    print(f"Deployment complete. Resource Name: {remote_app.resource_name}")
    print(f"Agent Runtime ID: {remote_app.resource_name.split('/')[-1]}")

if __name__ == "__main__":
    main()
```

#### `interact.py`

```python
import asyncio
import vertexai
from vertexai import agent_engines

# --- CONFIGURATION ---
# Note: Replace these with your actual Google Cloud project details.
PROJECT_ID = "your-gcp-project-id"
LOCATION = "us-central1"
# Note: Replace this with the ID output by the deploy.py script.
AGENT_ENGINE_ID = "YOUR_AGENT_ENGINE_ID" 

async def main():
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    # Get a reference to the deployed agent
    remote_app = agent_engines.get(AGENT_ENGINE_ID)

    # Create a new session
    print("Creating new session...")
    remote_session = await remote_app.async_create_session(user_id="test-user-123")

    # Send a query and stream the response
    query = "Roll a 20-sided die 3 times."
    print(f"\nUser: {query}")
    print("Agent: ", end="")
    
    final_response = ""
    async for event in remote_app.async_stream_query(
        session_id=remote_session["id"],
        message=query,
    ):
        # Look for the final text part in the model's response
        if (
            event.get("content", {}).get("parts", [{}])[0].get("text")
            and not event.get("content", {}).get("parts", [{}])[0].get("function_call")
        ):
            final_response = event["content"]["parts"][0]["text"]

    print(final_response)

if __name__ == "__main__":
    asyncio.run(main())
```

#### `local_test.py` (Optional)

This script shows the code for the optional local testing step.

```python
import asyncio
import vertexai
from vertexai import agent_engines
from multi_tool_agent.agent import root_agent

async def main():
    # Wrap the agent in an AdkApp object
    app = agent_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )

    # Create a local session to maintain conversation history
    session = await app.async_create_session(user_id="u_123")
    print(f"Local session created: {session.id}")

    # Send a query to the agent
    events = []
    async for event in app.async_stream_query(
        user_id="u_123",
        session_id=session.id,
        message="Roll a 6-sided die.",
    ):
        events.append(event)

    # The full event stream shows the agent's thought process
    print("\n--- Full Event Stream ---")
    for event in events:
        print(event)

    # For quick tests, you can extract just the final text response
    final_text_responses = [
        e for e in events
        if e.get("content", {}).get("parts", [{}])[0].get("text")
        and not e.get("content", {}).get("parts", [{}])[0].get("function_call")
    ]
    if final_text_responses:
        print("\n--- Final Response ---")
        print(final_text_responses[0]["content"]["parts"][0]["text"])

if __name__ == "__main__":
    asyncio.run(main())
```

### Self-Reflection Answers

1.  **What are the primary advantages of using the Accelerated Deployment method with the Agent Starter Pack compared to the Standard Deployment method for production use?**
    *   **Answer:** The Accelerated Deployment method with the Agent Starter Pack (ASP) is significantly more robust and recommended for production due to several advantages:
        *   **Infrastructure as Code (IaC):** ASP generates Terraform configurations, ensuring that your cloud infrastructure is provisioned in a reproducible, auditable, and version-controlled manner. The Standard method requires manual `gcloud` commands or custom scripting for infrastructure.
        *   **Built-in CI/CD:** ASP includes pre-configured Cloud Build pipelines (`Makefile`) for automated testing, building, and deploying. This streamlines development workflows and enforces best practices for continuous integration and delivery.
        *   **Best Practices:** It incorporates Google Cloud and ADK best practices for security (e.g., IAM roles, service accounts), reliability, and scalability from the start.
        *   **Reduced Manual Effort & Errors:** It minimizes manual configuration, reducing human error and accelerating time to market compared to the more involved Standard Deployment.

2.  **Agent Runtime is a managed backend. How does this simplify the development of complex clients (e.g., web or mobile applications) that interact with your agent?**
    *   **Answer:** As a managed backend, Agent Runtime significantly simplifies client development by abstracting away the complexities of server-side operations. This includes:
        *   **Automatic Scaling & Concurrency:** Clients don't need to worry about the agent's backend scaling to handle thousands of concurrent users. Agent Runtime handles this automatically.
        *   **Stable API:** It provides a stable and consistent API endpoint that clients (whether web, mobile, or other services) can easily connect to without needing to understand the underlying agent's implementation details.
        *   **Separation of Concerns:** The client can focus solely on UI/UX, session management, and presenting information, while Agent Runtime handles the heavy lifting of agent orchestration, LLM interaction, tool execution, and state management.
        *   **Security:** Agent Runtime handles much of the backend security, allowing clients to focus on secure authentication with the managed service rather than managing complex server-side security.

3.  **For what scenarios might the Standard Deployment method (using `deploy.py` and the Vertex AI SDK) still be advantageous, even if Accelerated Deployment is generally recommended?**
    *   **Answer:** While Accelerated Deployment is the best practice for new production projects, the Standard Deployment method still has advantages for specific scenarios:
        *   **Learning & Understanding:** It provides a deeper understanding of the underlying Vertex AI SDK and Agent Runtime APIs, which is invaluable for debugging or custom integrations.
        *   **Customization:** For highly specialized deployment workflows that deviate significantly from the ASP templates (e.g., integrating with existing, complex CI/CD systems or custom infrastructure), a manual script offers greater flexibility.
        *   **Modifying Existing Deployments:** If you need to programmatically update specific aspects of an already deployed Agent Runtime instance that aren't covered by the ASP `Makefile` commands, a custom script is often necessary.
        *   **Simplified Projects:** For very simple, one-off deployments or internal tools that don't require a full IaC/CI/CD setup, a direct script might be quicker to set up initially.