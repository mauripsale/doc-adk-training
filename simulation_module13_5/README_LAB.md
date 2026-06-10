---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 13.5 Solution: Extending ADK with Firestore

## Goal

This file contains the complete solution for both the `firestore_provider.py` and the `agent.py` script.

### `firestore_provider.py`

This is a functional implementation of the ADK 2.0 `BaseSessionService` using Firestore. Note how it implements the mandatory `append_event` and `update_session_state` methods.

```python
from typing import Any, Optional
import uuid
import time
from google.cloud import firestore
from google.adk.sessions.base_session_service import BaseSessionService, GetSessionConfig
from google.adk.sessions.session import Session
from google.adk.events.event import Event

class FirestoreSessionService(BaseSessionService):
    def __init__(self, project_id: str):
        self._client = firestore.AsyncClient(project=project_id)

    async def create_session(self, *, app_name: str, user_id: str, state: Optional[dict] = None, session_id: Optional[str] = None) -> Session:
        sid = session_id or str(uuid.uuid4())
        # Reference: apps/{app}/users/{user}/sessions/{sid}
        session_ref = self._client.collection("apps").document(app_name)\
            .collection("users").document(user_id)\
            .collection("sessions").document(sid)
        
        # Check if exists, else create
        doc = await session_ref.get()
        if not doc.exists:
            await session_ref.set({
                "created_at": time.time(),
                "state": state or {}
            })
        
        return Session(id=sid, app_name=app_name, user_id=user_id, state=doc.to_dict().get("state", {}) if doc.exists else (state or {}))

    async def append_event(self, event: Event, session: Session) -> None:
        # Save event to sub-collection
        event_ref = self._client.collection("apps").document(session.app_name)\
            .collection("users").document(session.user_id)\
            .collection("sessions").document(session.id)\
            .collection("events").document(event.invocation_id)
        
        await event_ref.set(event.model_dump())
        print(f"🔥 [Firestore] Persisted event from {event.author}")

    async def update_session_state(self, session: Session) -> None:
        # Update the main session document's state
        session_ref = self._client.collection("apps").document(session.app_name)\
            .collection("users").document(session.user_id)\
            .collection("sessions").document(session.id)
            
        await session_ref.update({"state": session.state})
        print(f"🔥 [Firestore] Updated session state in cloud.")

    # Other methods (get_session, list_sessions) would be implemented similarly
    async def get_session(self, config: GetSessionConfig) -> Optional[Session]:
        return await self.create_session(app_name=config.app_name, user_id=config.user_id, session_id=config.session_id)
```

### `agent.py`

```python
import asyncio
import os
from google.adk import Agent, Runner
from google.adk.apps import App
from firestore_provider import FirestoreSessionService
from dotenv import load_dotenv

load_dotenv()

agent = Agent(
    model="gemini-3.5-flash",
    name="PersistentAgent",
    instruction="You are a helpful assistant that remembers the user's favorite color."
)

async def main():
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    app = App(name="extensibility_demo", root_agent=agent)
    
    # --- SOLUTION: INJECTING THE CUSTOM PROVIDER ---
    custom_fs = FirestoreSessionService(project_id=project_id)
    
    runner = Runner(
        app=app, 
        session_service=custom_fs # <--- Injected here
    )
    
    # On first run, tell it your color.
    # On second run, comment the line below and ask: "What is my color?"
    await runner.run_debug("My favorite color is emerald green.", user_id="student_123")

if __name__ == "__main__":
    asyncio.run(main())
```

### Self-Reflection Answers

1.  **How does the use of an Abstract Base Class make the ADK more flexible?**
    *   **Answer:** It creates a "Contract." The framework (Runner) doesn't care *how* you save the data, as long as you provide methods like `append_event`. This allows ADK to work with any database on the planet without changing the core engine.

2.  **If you wanted to use Redis instead of Firestore?**
    *   **Answer:** You would create a `RedisSessionService(BaseSessionService)` and replace the `AsyncClient` logic with `redis-py` logic. The `agent.py` would remain 100% identical.

3.  **Why inject into the Runner?**
    *   **Answer:** Separation of Concerns. The Agent should only focus on AI reasoning. The Runner handles the "dirty work" of I/O and infrastructure.
