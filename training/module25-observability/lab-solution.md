---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 25 Solution: Building an Observability System with Plugins

## Goal

This file contains the complete code for the `agent.py` script in the Observability System with Plugins lab.

### `observability_agent/agent.py`

```python
import os
from google.adk import Agent
from google.adk.apps import App
from google.adk.plugins import BasePlugin
from google.adk.events import Event
from google.adk.telemetry.google_cloud import get_gcp_exporters
from google.adk.telemetry.setup import maybe_set_otel_providers
from dotenv import load_dotenv

load_dotenv()

# --- 1. Custom Business Logic Plugin ---

class AlertingPlugin(BasePlugin):
    """Alerts after 3 consecutive request errors."""
    def __init__(self, name: str = 'alerting_plugin', threshold: int = 3):
        super().__init__(name)
        self.error_threshold = threshold
        self.consecutive_errors = 0

    async def on_event_callback(self, *, event: Event, **kwargs):
        # We only care about request-level events
        if event.event_type == 'request_complete':
            self.consecutive_errors = 0
            
        elif event.event_type == 'request_error':
            self.consecutive_errors += 1
            print(f"⚠️ [ALERT] Request Error ({self.consecutive_errors}/{self.error_threshold})")
            
            if self.consecutive_errors >= self.error_threshold:
                print("🔥 [CRITICAL ALERT] Persistent errors detected!")

# --- 2. Enterprise Telemetry Configuration ---

# Enable Cloud Trace and Monitoring
otel_hooks = get_gcp_exporters(
    enable_cloud_tracing=True,
    enable_cloud_metrics=True
)

# Initialize OpenTelemetry providers
maybe_set_otel_providers(otel_hooks_to_setup=[otel_hooks])

# --- 3. App Definition ---

root_agent = Agent(
    name="monitored_agent",
    model="gemini-3.5-flash",
    instruction="Answer the user. If they say 'FAIL', trigger an error."
)

app = App(
    name="observability_demo",
    root_agent=root_agent,
    plugins=[AlertingPlugin()]
)
```

### Self-Reflection Answers

1.  **What is the main advantage of using the Plugin System for observability?**
    *   **Answer:** **Separation of Concerns**. You can add complex logging, metrics, or security checks without touching the agent's core instructions or tools. This makes the code cleaner and the observability logic reusable across multiple agents.

2.  **How does ADK 2.0 improve tracing for complex workflows?**
    *   **Answer:** Every event in ADK 2.0 contains **`node_info`**. In a distributed trace (Cloud Trace), this allows you to see exactly which node in a graph (e.g., a specific specialist in a MAS) triggered which event. It transforms a "flat" list of logs into a hierarchical, graph-aware view of execution.

3.  **When should you use a Plugin vs. Native Telemetry?**
    *   **Answer:** Use **Native Telemetry (OTel)** for standard performance monitoring (latency, error rates, system health) that needs to be aggregated in dashboards like Cloud Monitoring. Use **Plugins** for logic that requires custom Python code, such as sending a message to Slack after a specific business failure or calculating session-specific metrics that OTel doesn't handle natively.