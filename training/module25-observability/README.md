---
sidebar_position: 25
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

### Enterprise Telemetry in ADK 2.0

While custom plugins are great for specific logic, ADK 2.0 introduces native support for **OpenTelemetry (OTel)**. This allows you to export performance data and traces to industry-standard backends like **Google Cloud Trace** and **Cloud Monitoring**.

#### 1. The "Graph-Aware" Trace
In a complex ADK 2.0 Workflow, every event now carries a **`node_info`** field. When using OTel, these details are automatically attached to the spans, allowing you to see:
*   Which node in the graph is currently executing.
*   The exact input and output of that node.
*   How long each node took to process (latency profiling).

#### 2. Configuring Cloud Trace
To enable enterprise telemetry, you use the `google.adk.telemetry` module. You define which exporters you want and pass them to the framework setup.

```python
from google.adk.telemetry.google_cloud import get_gcp_exporters
from google.adk.telemetry.setup import maybe_set_otel_providers

# 1. Configure the GCP Exporters
# Requires: pip install "google-adk[gcp]>=2.1.0"
otel_hooks = get_gcp_exporters(
    enable_cloud_tracing=True,
    enable_cloud_metrics=True
)

# 2. Initialize the OTel Providers
maybe_set_otel_providers(otel_hooks_to_setup=[otel_hooks])

# 3. Your App now automatically sends telemetry!
app = App(name="production_agent", root_agent=my_agent)
```

### Key Takeaways
- **Standardized Pillars**: Use OTel for Traces, Metrics, and Logs.
- **Graph Visibility**: The `node_info` field in ADK 2.0 events provides deep insights into Workflow execution.
- **Custom vs. Native**:
    *   Use **Plugins** for business-specific logic (e.g., custom alerting, session-level metrics).
    *   Use **Native Telemetry** for infrastructure monitoring and performance profiling.
- **Separation of Concerns**: Infrastructure code stays outside your agent's core logic, ensuring maintainability.