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

# A tool that can genuinely fail, so there's a real exception for the
# plugin to observe -- not just a simulated one.
def risky_operation(should_fail: bool) -> dict:
    """Performs an operation that can be made to fail, for testing error handling."""
    if should_fail:
        raise ValueError("Simulated failure!")
    return {"status": "success"}

# --- 1. Custom Business Logic Plugin ---

class AlertingPlugin(BasePlugin):
    """Alerts after 3 consecutive request errors."""
    def __init__(self, name: str = 'alerting_plugin', threshold: int = 3):
        super().__init__(name)
        self.error_threshold = threshold
        self.consecutive_errors = 0
        self._had_error_this_turn = False

    async def on_tool_error_callback(self, *, tool, tool_args, tool_context, error):
        # Catching the exception here (instead of letting it crash the run)
        # is what lets the plugin observe it AND lets the agent recover.
        self._had_error_this_turn = True
        self.consecutive_errors += 1
        print(f"⚠️ [ALERT] Request Error ({self.consecutive_errors}/{self.error_threshold}): {error}")

        if self.consecutive_errors >= self.error_threshold:
            print("🔥 [CRITICAL ALERT] Persistent errors detected!")

        # Returning a dict recovers gracefully; returning None would
        # propagate the original exception and crash the run.
        return {"status": "error", "message": f"The operation failed: {error}"}

    async def on_event_callback(self, *, event: Event, **kwargs):
        if event.is_final_response():
            if not self._had_error_this_turn:
                self.consecutive_errors = 0
            self._had_error_this_turn = False

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
    instruction="You have a risky_operation tool. If the user says 'FAIL', call it with should_fail=True. Otherwise, call it with should_fail=False.",
    tools=[risky_operation],
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