---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 13.5: Implementing Firestore Persistence (ADK 2.0)

## Goal

In this lab, you will take a simple agent that currently uses in-memory storage and upgrade it to use Google Cloud Firestore. You will verify that the agent remembers a user's name even after the Python script is completely stopped and restarted.

### Step 1: Pre-requisites Setup

*Ensure you have a Google Cloud Project with billing enabled.*

1.  **Enable Firestore:** Open the Google Cloud Console, navigate to **Firestore**, and click **Create Database**. Choose **Native mode**.
2.  **Authenticate locally:**
    ```shell
    gcloud auth application-default login
    gcloud config set project YOUR_PROJECT_ID
    ```
3.  **Install dependencies:**
    ```shell
    uv pip install google-adk google-cloud-firestore
    ```

### Step 2: Review the Starter Code

Create a file named `agent.py` and paste the following starter code. Notice that it uses `InMemoryRunner`. 

```python
# agent.py (Starter Code)
import asyncio
import os
from google.adk import Agent, Context, Event
from google.adk.runners import InMemoryRunner
from google.adk.tools import ToolContext
from google.genai import types

def remember_name(name: str, tool_context: ToolContext) -> str:
    """Saves the user's name to memory."""
    tool_context.session.state["user_name"] = name
    return f"I have successfully remembered that your name is {name}."

agent = Agent(
    model="gemini-3.5-flash",
    name="MemoryAgent",
    instruction="You are a helpful assistant. Use the remember_name tool if the user tells you their name.",
    tools=[remember_name]
)

async def main():
    app_name = "persistence_demo"
    user_id = "test_user_001"
    
    # --- STARTER CODE USES IN-MEMORY RUNNER ---
    runner = InMemoryRunner(agent=agent, app_name=app_name)
    
    # 1. Create or get the session
    session = await runner.session_service.create_session(app_name=app_name, user_id=user_id)
    print(f"--- Session ID: {session.id} ---")
    
    # 2. Basic interactive loop
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]: break
            
        content = types.Content(role="user", parts=[types.Part.from_text(text=user_input)])
        async for event in runner.run_async(user_id=user_id, session_id=session.id, new_message=content):
            if event.content and event.content.parts and event.content.parts[0].text:
                print(f"Agent: {event.content.parts[0].text}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 3: Test the Transient Nature of Memory

1.  Run the script: `python agent.py`
2.  Tell the agent your name: `My name is Alice.`
3.  Type `quit` to exit.
4.  Run the script *again*: `python agent.py`
5.  Ask immediately: `What is my name?` 
    *   **Observation:** The agent has forgotten. The in-memory storage was wiped.

### Step 4: Upgrade to FirestoreSessionService

**Exercise:** Modify the `agent.py` script to use `FirestoreSessionService`.

**Hints:**
1.  Import `FirestoreSessionService` and the base `Runner`.
    ```python
    from google.adk.sessions import FirestoreSessionService
    from google.adk import Runner
    ```
2.  Retrieve your Project ID: `project_id = os.getenv("GOOGLE_CLOUD_PROJECT")`.
3.  Instantiate the service: `fs = FirestoreSessionService(project_id=project_id)`.
4.  Replace `InMemoryRunner` with `Runner(agent=agent, session_service=fs)`.

### Step 5: Verify Persistence

1.  Run your updated script.
2.  Tell the agent a *new* name: `My name is Bob.`
3.  Type `quit` to exit.
4.  Run the script again.
5.  Ask immediately: `What is my name?`
6.  **Success Criteria:** The agent should reply "Bob", proving that state was successfully retrieved from Firestore!

### Self-Reflection Questions
1.  Why does ADK 2.0 store `node_info` in Firestore events? How does this help with resuming complex workflows?
2.  What happens if two different runners try to append an event to the same session simultaneously? (Hint: Check the `FirestoreSessionService` lock mechanism).
