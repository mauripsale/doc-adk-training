---
sidebar_position: 13.5
title: "Module 13.5: Extending ADK - Custom Persistence with Firestore"
---

# Module 13.5: Extending ADK - Custom Persistence with Firestore

## Theory

### The Power of Extensibility

One of the key strengths of ADK 2.0 is its **pluggable architecture**. While the core library provides built-in services for common tasks (like `InMemorySessionService` or `DatabaseSessionService` for SQL), enterprise requirements often demand integration with specific technologies.

Instead of being locked into a fixed set of database providers, you can **extend the ADK** by implementing your own services.

### The `BaseSessionService` Interface

In the ADK, all session persistence is governed by a single abstract class: **`BaseSessionService`**. 

Any class that inherits from `BaseSessionService` and implements its core methods can be used by the `Runner`. This allows you to store agent conversations and state in **any database**—from Redis and MongoDB to Google Cloud Firestore.

### Why Implement a Custom Session Service?

1.  **Organizational Standards:** Your company may already use Firestore as its primary serverless database.
2.  **Performance & Latency:** You might need **sub-second latency** for a high-traffic customer bot. In this case, you could implement a custom service using **Redis** to cache session state in-memory, ensuring near-instant response times that a standard persistent database might not provide.
3.  **Specific Features:** You might want to leverage Firestore's real-time listeners or its native integration with Firebase.
4.  **Cost & Scaling:** Firestore offers a specialized pricing model and automatic scaling that might be better suited for your agent's traffic patterns than a traditional SQL database.

### How it works: Dependency Injection

The ADK uses **Dependency Injection** at the `Runner` level. When you instantiate a `Runner`, you don't have to use the default `InMemoryRunner`. Instead, you can provide your own custom session service instance.

```python
# Custom implementation (which we will build in this lab)
custom_service = FirestoreSessionService(project_id="my-project")

# Inject it into the base Runner
runner = Runner(
    app=my_app,
    session_service=custom_service
)
```

From this point on, every call to `runner.run()` or `runner.run_async()` will automatically use your Firestore logic to save and load data, without you having to change a single line of agent instruction or tool code.

---

## Key Takeaways

*   **ADK is extensible:** You can plug in custom implementations for sessions, artifacts, and more.
*   **Decoupled Logic:** Your agent's "brain" (intelligence) is completely separated from its "memory" (storage technology).
*   **Enterprise Ready:** Building custom providers is the standard way to integrate ADK into existing enterprise data ecosystems.
