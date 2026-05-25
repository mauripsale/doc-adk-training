---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 13.5: Implementing Firestore Persistence Challenge

## Goal

In this lab, you will take a simple agent that currently uses in-memory storage and upgrade it to use Google Cloud Firestore. You will verify that the agent remembers a user's name even after the Python script is completely stopped and restarted.

### Step 1: Pre-requisites Setup (Instructor Led / Self-Paced)

*Ensure you have a Google Cloud Project with billing enabled.*

1.  **Enable Firestore:** Open the Google Cloud Console, navigate to **Firestore**, and click **Create Database**. Choose **Native mode** and select a region close to you.
2.  **Authenticate locally:** Ensure your terminal is authenticated with your Google Cloud credentials:
    ```shell
    gcloud auth application-default login
    gcloud config set project YOUR_PROJECT_ID
    ```
3.  **Install the dependency:** Ensure the Firestore package is installed in your virtual environment:
    ```shell
    uv pip install google-cloud-firestore
    ```

### Step 2: Review the Starter Code

Create a file named `agent.py` and paste the following starter code. Notice that it uses `InMemoryRunner`. It includes a simple tool to save the user's name to the session state.

```python
# agent.py (Starter Code)
import asyncio
import os
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.adk.tools import ToolContext, FunctionTool
from google.genai import types

load_dotenv()

def remember_name(name: str, tool_context: ToolContext) -> str:
    """Saves the user's name to memory."""
    tool_context.session.state["user_name"] = name
    return f"I have successfully remembered that your name is {name}."

agent = LlmAgent(
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
    
    # 2. Start a simple loop
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        content = types.Content(role="user", parts=[types.Part.from_text(text=user_input)])
        
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=content
        ):
            if event.content and event.content.parts and event.content.parts[0].text:
                print(f"Agent: {event.content.parts[0].text}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 3: Test the Transient Nature of Memory

1.  Run the script: `python agent.py`
2.  Tell the agent your name: `My name is Alice.`
3.  Ask the agent: `What is my name?` (It should remember).
4.  Type `quit` to exit the script completely.
5.  Run the script *again*: `python agent.py`
6.  Ask the agent immediately: `What is my name?` 
    *   **Observation:** The agent has forgotten. The session ID is likely the same, but the in-memory storage was wiped when the script terminated.

### Step 4: Upgrade to FirestoreSessionService

**Exercise:** Modify the `agent.py` script to use `FirestoreSessionService`.

**Hints:**
1.  You will need to import `FirestoreSessionService` and `Runner`.
    ```python
    from google.adk.sessions import FirestoreSessionService
    from google.adk.runners import Runner
    ```
2.  Retrieve your Google Cloud Project ID (e.g., using `os.getenv("GOOGLE_CLOUD_PROJECT")`).
3.  Instantiate the `FirestoreSessionService` passing the `project_id`.
4.  Replace the `InMemoryRunner` initialization with the base `Runner` initialization, passing both the `agent` and your new `session_service`.

### Step 5: Verify Persistence

1.  Run your updated script.
2.  Tell the agent a *new* name: `My name is Bob.`
3.  Type `quit` to exit.
4.  Run the script again.
5.  Ask immediately: `What is my name?`
6.  **Success Criteria:** The agent should reply "Bob", proving that both the conversation history and the session state were successfully retrieved from Firestore!

### Self-Reflection Questions

1.  Why is it important to use the same `user_id` and `app_name` when testing persistence across script restarts?
2.  If you open the Google Cloud Console and look at your Firestore database, what kind of structure (Collections/Documents) do you see the ADK has created?

