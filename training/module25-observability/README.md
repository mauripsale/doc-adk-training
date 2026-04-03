---
sidebar_position: 1
title: "Module 25: Advanced Observability with Plugins"
---

# Module 25: Advanced Observability with Plugins

## Theory

### Why Advanced Observability Matters

Production agents require deep visibility into their behavior, performance, and failures for debugging and optimization. While manual event logging is a good start, a more scalable and modular approach is needed for enterprise-grade monitoring.

The ADK provides a powerful **Plugin System** for this purpose.

### The Observability Pillars

A comprehensive observability strategy is built on four pillars, all of which can be implemented via plugins:

*   **Traces**: Follow a request's entire journey through a distributed system.
*   **Metrics**: Collect quantitative data (e.g., latency, error rates, token counts).
*   **Logs**: Record detailed, structured information about specific events.
*   **Events**: Represent the discrete state changes and actions within the agent.

### The ADK Plugin System

**Plugins** are modular, reusable classes that intercept and observe the events flowing through an agent's execution without modifying the agent's core logic. They provide a clean separation of concerns, allowing you to add logging, metrics, and other observability features without cluttering your agent's business logic.

**Plugin System Architecture:**
```text
+--------------+      +-----------------+      +----------------+
| User Request |----->|   ADK Runner    |----->|  Agent Core    |
|              |      | (with plugins)  |      | (Business Logic) |
+--------------+      +-------+---------+      +-------+--------+
                              |                        |
                              v                        v
                      +-----------------+      +----------------+
                      |  Plugin System  |      |  Model & Tools |
                      | - MetricsPlugin |      +----------------+
                      | - AlertingPlugin|
                      | - ProfilingPlugin|
                      +-------+---------+
                              |
                              v
                      +-----------------+
                      | Event Processing|
                      |  (Intercepted)  |
                      +-----------------+
```

#### How Plugins Work

1.  You create a class that inherits from `google.adk.plugins.BasePlugin`.
2.  You implement the `async def on_event_callback(self, *, event: Event, **kwargs)` method.
3.  This method is automatically called by the runner for **every event** that occurs during the agent's execution.
4.  Inside this method, you can inspect the event and perform actions like logging to a file, incrementing a metric counter, or sending an alert.
5.  You register your plugin globally when you instantiate the `App`: `App(root_agent=..., plugins=[MyMetricsPlugin()])`.

This event-driven, plugin-based architecture is the foundation for building sophisticated, enterprise-grade monitoring for your agents.

### Key Takeaways
- The ADK **Plugin System** provides a modular way to add observability features like logging, metrics, and tracing without modifying the agent's core logic.
- Plugins are classes that inherit from `BasePlugin` and implement the `on_event_callback` method to intercept and process all events during an agent's execution.
- This event-driven architecture allows for a clean separation of concerns between the agent's business logic and its monitoring infrastructure.
- You register plugins by passing them to the `App`'s constructor: `App(plugins=[...])`.
- **Advantage of Plugin System:** The primary benefit of using the Plugin System for observability is the **Separation of Concerns**. Observability code (e.g., sending metrics to Prometheus, logging to Splunk) is completely isolated from the agent's business logic. This makes both systems easier to test, update, and maintain, promotes reusability of plugins across different agents, and keeps the agent's core logic clean and focused on its primary task.
- **Performance Considerations for `on_event_callback`:** In a high-traffic production system, the code within `on_event_callback` must be as fast and efficient as possible, as the agent's runtime will await its completion. It's crucial to avoid blocking synchronous I/O operations (e.g., disk writes, blocking API calls) and to minimize processing. Costly operations should be delegated to asynchronous processing (using `await`) or separate threads/processes (e.g., a queue worker) to prevent slowing down the entire agent execution.
- **Tracking LLM Tokens:** To extend the `MetricsCollectorPlugin` to track LLM token usage, you would inspect `llm_call_complete` events (or `request_complete` if token data is propagated there). The `Event` object or its `response.usage_metadata` attribute typically contains `prompt_token_count` and `candidates_token_count`. This data can then be added to the `RequestMetrics` for the corresponding `invocation_id` and aggregated.