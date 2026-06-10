---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 13.5: Extending ADK with Custom Firestore Persistence

## Goal

In this lab, you will learn how to extend the ADK's core functionality by implementing a **Custom Session Service**. You will take a specialized `FirestoreSessionService` implementation and "plug it in" to an agent's runtime.

By the end of this lab, you will have an agent that persists its memory to Google Cloud Firestore, surviving restarts of the Python process.

### Step 1: Pre-requisites

1.  **Enable Firestore:** In the GCP Console, ensure you have a Firestore database in **Native mode**.
2.  **Auth:** `gcloud auth application-default login`
3.  **Dependencies:**
    ```bash
    uv add google-cloud-firestore
    ```

### Step 2: The Custom Provider

Create a file named `firestore_provider.py`. This contains the implementation that inherits from `BaseSessionService`. **Study the code** to see how it uses `firestore.AsyncClient` to map ADK concepts (Apps, Users, Sessions) to document paths.

```python
# firestore_provider.py
from typing import Any, Optional
import uuid
from google.cloud import firestore
from google.adk.sessions.base_session_service import BaseSessionService, GetSessionConfig, ListSessionsResponse
from google.adk.sessions.session import Session
from google.adk.events.event import Event

class FirestoreSessionService(BaseSessionService):
    def __init__(self, project_id: str):
        self._client = firestore.AsyncClient(project=project_id)

    async def create_session(self, *, app_name: str, user_id: str, state: Optional[dict] = None, session_id: Optional[str] = None) -> Session:
        sid = session_id or str(uuid.uuid4())
        # Simplified for the lab: logic to save to apps/{app}/users/{user}/sessions/{sid}
        # In a real app, you would perform an initial write here.
        return Session(id=sid, app_name=app_name, user_id=user_id, state=state or {})

    async def get_session(self, config: GetSessionConfig) -> Optional[Session]:
        # Logic to retrieve session and its events from Firestore
        pass # Implementation details hidden for brevity

    async def append_event(self, event: Event, session: Session) -> None:
        # Logic to write a new event to the Firestore sub-collection
        print(f"🔥 [Firestore] Appending event: {event.author}")

    async def update_session_state(self, session: Session) -> None:
        # Logic to update the session document with current state
        print(f"🔥 [Firestore] Syncing state for session: {session.id}")

    # Mandatory stubs for BaseSessionService
    async def list_sessions(self, app_name: str, user_id: str) -> ListSessionsResponse:
        return ListSessionsResponse(sessions=[])

    async def delete_session(self, app_name: str, user_id: str, session_id: str) -> None:
        pass
```

### Step 3: Integrate the Provider

**Exercise:** Open `agent.py`. Your task is to modify the `main()` function to use your new `FirestoreSessionService` instead of the default in-memory runner.

```python
# agent.py
import asyncio
import os
from google.adk import Agent, Runner
from google.adk.apps import App
from firestore_provider import FirestoreSessionService # Import your custom class
from dotenv import load_dotenv

load_dotenv()

# --- 1. Define a simple agent ---
agent = Agent(
    model="gemini-3.5-flash",
    name="PersistentAgent",
    instruction="You are a helpful assistant that remembers the user's favorite color."
)

async def main():
    # TODO: 1. Setup metadata
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    app = App(name="extensibility_demo", root_agent=agent)
    
    # TODO: 2. Instantiate your custom service
    # custom_fs = ...
    
    # TODO: 3. Create a base Runner (NOT InMemoryRunner)
    # Inject your custom_fs into the session_service parameter
    # runner = Runner(app=app, session_service=...)
    
    # 4. Test it
    print("Agent is now powered by Firestore persistence!")
    await runner.run_debug("My favorite color is blue.", user_id="student_1")

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 4: Verify Persistence

1.  Run the script once to set the favorite color.
2.  Stop the script.
3.  Modify the last line of `main()` to ask: `"What is my favorite color?"`.
4.  Run it again. If the agent answers "Blue", your custom provider is working!

### Self-Reflection Questions

*   How does the use of an Abstract Base Class (`BaseSessionService`) make the ADK more flexible for large companies?
*   If you wanted to use **Redis** instead of Firestore, what parts of the `firestore_provider.py` would you need to rewrite?
*   Why is it better to inject the session service into the `Runner` rather than hardcoding it inside the `Agent`?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMTNfNS1maXJlc3RvcmUtcGVyc2lzdGVuY2UvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module13.5-firestore-persistence/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
