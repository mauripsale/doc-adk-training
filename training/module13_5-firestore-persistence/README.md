---
sidebar_position: 13.5
title: "Module 13.5: Enterprise Persistence with Firestore (ADK 2.0)"
---

# Module 13.5: Enterprise Persistence with Firestore

## Theory

### The Need for Persistent Memory

Up until now, our agents have been running using the `InMemorySessionService` (implicitly provided by `InMemoryRunner`). This is fantastic for development because it requires zero setup.

However, `InMemorySessionService` stores the entire conversation history and the **Session State** directly in the RAM of the Python process. This introduces a critical limitation: **if your server restarts, crashes, or scales down, all memory is completely lost.**

In production, users expect an agent to remember past interactions and preferences even if they return days later.

### Introduction to `FirestoreSessionService`

To achieve durable persistence, the ADK provides the **`FirestoreSessionService`**. This service replaces the in-memory store with [Google Cloud Firestore](https://cloud.google.com/firestore), a highly scalable, serverless NoSQL document database.

By using `FirestoreSessionService`, the ADK automatically:
1.  Saves every event (user messages, agent responses, tool calls) to Firestore.
2.  Persists the key-value pairs stored in the `SessionState`.
3.  Loads the history back into the agent's context when a user returns, allowing the **Workflow Runtime** to resume exactly where it left off.

### Implementation Pattern

Switching from in-memory to Firestore requires almost zero changes to your actual agent logic. You only change the `Runner` configuration.

Instead of `InMemoryRunner`, you use the base `Runner` class and explicitly pass an instance of `FirestoreSessionService`.

**Installation:**
```bash
uv add "google-adk[gcp]>=2.1.0"
```

**Code Pattern:**
```python
from google.adk.apps import App
from google.adk.sessions import FirestoreSessionService
from google.adk import Runner

# 1. Wrap your agent/workflow in an App
app = App(name="persistence_demo", root_agent=my_agent)

# 2. Initialize the Firestore Session Service
firestore_service = FirestoreSessionService(
    project_id="your-gcp-project-id"
)

# 3. Create a Runner and inject the service
runner = Runner(
    app=app,
    session_service=firestore_service
)
```

### Pre-requisites

To use `FirestoreSessionService`, you need:
1.  A Google Cloud Project with the Firestore API enabled.
2.  A Firestore Database created in "Native mode".
3.  The `google-cloud-firestore` Python package installed.

---

## Key Takeaways

*   **Durable by Design:** `FirestoreSessionService` ensures state survives process restarts and horizontal scaling.
*   **Decoupled Architecture:** Business logic (agents/nodes) remains identical whether using in-memory or cloud storage.
*   **Workflow Integration:** ADK 2.0's Workflow engine uses the session service to store node-level checkpoints, making complex graphs fully resumable across failures.
