---
sidebar_position: 13.5
title: "Module 13.5: Enterprise Persistence with Firestore"
---

# Module 13.5: Enterprise Persistence with Firestore

## Theory

### The Need for Persistent Memory

Up until now, our agents have been running using the `InMemorySessionService` (often implicitly provided by `InMemoryRunner`). This is fantastic for development, rapid prototyping, and learning because it requires zero setup.

However, `InMemorySessionService` stores the entire conversation history (the `Session` object) and the `SessionState` directly in the RAM of the Python process running the agent. This introduces a critical limitation for production: **if your server restarts, crashes, or scales down, all memory is completely lost.**

In an enterprise environment, users expect an agent to remember their past interactions, preferences, and the current state of a long-running process, even if they return days later or if their request is routed to a different server instance.

### Introduction to FirestoreSessionService

To achieve this persistence, the ADK provides the **`FirestoreSessionService`**. This service seamlessly replaces the in-memory store with [Google Cloud Firestore](https://cloud.google.com/firestore), a highly scalable, serverless NoSQL document database.

By using `FirestoreSessionService`, the ADK automatically:
1.  Saves every user message and agent response (Events) to a Firestore collection.
2.  Persists the key-value pairs stored in the `SessionState` (which we used via `ToolContext` in Module 13).
3.  Loads the entire conversation history back into the agent's context when a user returns, allowing the conversation to resume exactly where it left off.

### How to use it

The beauty of the ADK's design is that switching from in-memory to Firestore requires almost zero changes to your actual agent logic or tools. You only need to change how you initialize the `Runner`.

Instead of `InMemoryRunner`, you use the base `Runner` class and explicitly pass an instance of `FirestoreSessionService`.

```python
from google.adk.runners import Runner
from google.adk.sessions import FirestoreSessionService
# ... other imports ...

# 1. Initialize the Firestore Session Service
# It will use Application Default Credentials (ADC) by default
firestore_service = FirestoreSessionService(
    project_id="your-gcp-project-id",
    collection_name="adk_sessions" # Optional: specify a custom collection
)

# 2. Use the base Runner instead of InMemoryRunner
runner = Runner(
    agent=my_agent,
    session_service=firestore_service
)
```

### Pre-requisites

To use `FirestoreSessionService`, you need:
1.  A Google Cloud Project.
2.  The Firestore API enabled in that project.
3.  A Firestore Database created (usually in "Native mode").
4.  Proper authentication configured locally (e.g., via `gcloud auth application-default login`).

---

## Key Takeaways

*   **In-Memory is for Dev:** `InMemoryRunner` loses all data when the application stops.
*   **Firestore is for Prod:** `FirestoreSessionService` provides durable, scalable persistence for both conversation history and session state.
*   **Seamless Integration:** You do not need to change your agent's core logic or tools to enable persistence; you only change the `Runner` configuration.
