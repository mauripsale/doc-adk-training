---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 25: Observability & Tracing Plugins — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 25: Building an Observability System with Plugins Challenge

## Goal

In this lab, you will build a production-style observability layer for an agent using the ADK's **Plugin System** (`AgentOpsMetricsPlugin`) combined with native **Google Cloud Trace** OpenTelemetry hooks.

### Step 1: Create the Agent Project

<Setup/>

From your `adk-training` workspace directory, create the `observability_agent` package *(stay inside `adk-training` for all subsequent steps!)*:

```shell
uv run adk create observability_agent
```
This prompts for a model/backend choice (any option is fine—you'll set `gemini-3.8-flash` explicitly in `observability_agent/agent.py` below).

### Step 2: Implement a Business Logic Plugin

**Exercise:** Open `observability_agent/agent.py`. We will start by creating an **AgentOps Alerting & Metrics Plugin** that detects consecutive errors and tracks telemetry events locally.

```python
# In agent.py (Starter Code)
from google.adk import Agent
from google.adk.apps import App
from google.adk.plugins import BasePlugin
from google.adk.events import Event

# A tool that can genuinely fail, so there's a real exception for the
# plugin to observe -- not just a simulated one.
def risky_operation(should_fail: bool) -> dict:
    """Performs an operation that can be made to fail, for testing error handling."""
    if should_fail:
        raise ValueError("Simulated failure in risky_operation!")
    return {"status": "success", "result": "Operation completed without errors."}

class AgentOpsMetricsPlugin(BasePlugin):
    """An AgentOps observability plugin that tracks errors, tool calls, and turn health."""
    def __init__(self, name: str = 'agentops_metrics_plugin', threshold: int = 3):
        super().__init__(name)
        self.error_threshold = threshold
        self.consecutive_errors = 0
        self.total_tool_calls = 0
        self._had_error_this_turn = False
        self.telemetry_events = []

    async def on_tool_error_callback(self, *, tool, tool_args, tool_context, error):
        # TODO: Implement AgentOps alerting and tracking logic here.
        # 1. Mark that this turn had an error (self._had_error_this_turn = True).
        # 2. Increment self.consecutive_errors and self.total_tool_calls.
        # 3. Log a record to self.telemetry_events.
        # 4. Print an alert, escalating to a critical alert once you hit the threshold.
        # 5. Return a dict (e.g. {"status": "error", "message": str(error)})
        #    so the agent recovers gracefully instead of crashing the run.
        pass

    async def on_event_callback(self, *, event: Event, **kwargs):
        # TODO: When event.is_final_response() is True, if this turn had NO
        # error, reset self.consecutive_errors to 0 -- a clean turn means we've
        # recovered. Record the turn outcome in self.telemetry_events and reset self._had_error_this_turn.
        pass

# --- Create a simple Agent ---
root_agent = Agent(
    name="agentops_monitored_agent",
    model="gemini-3.8-flash",
    instruction="You have a risky_operation tool. If the user says 'FAIL', call it with should_fail=True. Otherwise, call it with should_fail=False.",
    tools=[risky_operation],
)

# --- Register Plugin with App ---
app = App(
    name="observability_agent",
    root_agent=root_agent,
    plugins=[AgentOpsMetricsPlugin()]
)
```

### Step 3: Configure Enterprise Telemetry

**Exercise:** Now, let's enable native **Cloud Trace** integration. Install the `gcp` extra first:

```shell
uv add "google-adk[gcp]"
```

```python
# Add this to your observability_agent/agent.py imports
from google.auth.exceptions import DefaultCredentialsError
from google.adk.telemetry.google_cloud import get_gcp_exporters
from google.adk.telemetry.setup import maybe_set_otel_providers

# TODO: Inside a `try ... except DefaultCredentialsError:` block (so local API-key runs don't fail):
# 1. Call get_gcp_exporters(enable_cloud_tracing=True, enable_cloud_metrics=True).
# 2. Pass the returned hook into maybe_set_otel_providers(otel_hooks_to_setup=[...]).
```

### Step 4: Run and Verify

1.  **Launch the Dev UI from your `adk-training` workspace directory:**
    ```shell
    uv run adk web
    ```
    Select **`observability_agent`** from the agent dropdown (`adk web` automatically loads `app` with its registered `AgentOpsMetricsPlugin`!).
2.  **Test the Alerting Plugin:**
    Send prompts and verify the console output.
3.  **Inspect the Trace Metadata:**
    In the Dev UI, open the **Trace** tab. Notice how ADK 2.0 provides detailed information about each event, which is exactly what gets sent to Cloud Trace.


### Having Trouble?
If you get stuck, unlock the **Reference Solution Vault** at the bottom of this page.

### Lab Summary
You have successfully built a modular observability system using the ADK's Plugin System and OpenTelemetry. You have learned to:
*   Create custom plugins by inheriting from `BasePlugin`.
*   Implement `on_tool_error_callback` to intercept a tool's exception, recover gracefully, and still observe what failed.
*   Use `on_event_callback` with `event.is_final_response()` to detect a clean turn (no errors) and reset your own tracking state.
*   Configure enterprise-grade telemetry using **Cloud Trace** hooks.
*   Register plugins and telemetry with the `App` object.

### Self-Reflection Questions
- What is the main advantage of using the Plugin System for observability instead of adding logging and metrics code directly inside your agent and tool functions?
- How does ADK 2.0's `node_info` field improve your ability to debug complex multi-agent graphs?
- When should you use a custom Plugin versus native OpenTelemetry hooks?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="25">

## Lab 25 Solution: Building an Observability System with Plugins

## Goal

This file contains the complete code for the `agent.py` script in the Observability System with Plugins lab.

### `observability_agent/agent.py`

```python
from google.auth.exceptions import DefaultCredentialsError
from google.adk import Agent
from google.adk.apps import App
from google.adk.plugins import BasePlugin
from google.adk.events import Event
from google.adk.telemetry.google_cloud import get_gcp_exporters
from google.adk.telemetry.setup import maybe_set_otel_providers

# A tool that can genuinely fail, so there's a real exception for the
# plugin to observe -- not just a simulated one.
def risky_operation(should_fail: bool) -> dict:
    """Performs an operation that can be made to fail, for testing error handling."""
    if should_fail:
        raise ValueError("Simulated failure in risky_operation!")
    return {"status": "success", "result": "Operation completed without errors."}

# --- 1. Custom AgentOps Telemetry & Alerting Plugin ---

class AgentOpsMetricsPlugin(BasePlugin):
    """An AgentOps observability plugin that tracks errors, tool calls, and turn health."""
    def __init__(self, name: str = 'agentops_metrics_plugin', threshold: int = 3):
        super().__init__(name)
        self.error_threshold = threshold
        self.consecutive_errors = 0
        self.total_tool_calls = 0
        self._had_error_this_turn = False
        self.telemetry_events = []

    async def on_tool_error_callback(self, *, tool, tool_args, tool_context, error):
        self._had_error_this_turn = True
        self.consecutive_errors += 1
        self.total_tool_calls += 1
        
        event_record = {
            "type": "TOOL_ERROR",
            "tool": tool.name,
            "args": tool_args,
            "error": str(error),
            "consecutive_errors": self.consecutive_errors
        }
        self.telemetry_events.append(event_record)
        print(f"⚠️ [AgentOps Log] Tool Error ({self.consecutive_errors}/{self.error_threshold}): {error}")

        if self.consecutive_errors >= self.error_threshold:
            print("🔥 [AgentOps ALERT] Critical: Persistent error threshold reached!")

        # Returning a dict recovers gracefully; returning None would
        # propagate the original exception and crash the run.
        return {"status": "error", "message": f"Operation failed: {error}"}

    async def on_event_callback(self, *, event: Event, **kwargs):
        if event.is_final_response():
            if not self._had_error_this_turn:
                self.consecutive_errors = 0
            
            turn_record = {
                "type": "TURN_COMPLETED",
                "had_error": self._had_error_this_turn,
                "current_consecutive_errors": self.consecutive_errors
            }
            self.telemetry_events.append(turn_record)
            self._had_error_this_turn = False

# --- 2. Enterprise Telemetry Configuration (Cloud Trace / Monitoring) ---

# Enable Cloud Trace and Monitoring exporters (gracefully skipped if running with GOOGLE_API_KEY only)
try:
    otel_hooks = get_gcp_exporters(
        enable_cloud_tracing=True,
        enable_cloud_metrics=True,
    )
    maybe_set_otel_providers(otel_hooks_to_setup=[otel_hooks])
except DefaultCredentialsError:
    print("ℹ️ Running locally without GCP ADC; skipping Cloud Trace export.")

# --- 3. App Definition ---

root_agent = Agent(
    name="agentops_monitored_agent",
    model="gemini-3.8-flash",
    instruction="You are a monitored assistant. Call risky_operation with should_fail=True if asked to fail, else False.",
    tools=[risky_operation],
)

app = App(
    name="observability_agent",
    root_agent=root_agent,
    plugins=[AgentOpsMetricsPlugin()]
)
```

### Self-Reflection Answers

1.  **What is the main advantage of using the Plugin System for observability?**
    *   **Answer:** **Separation of Concerns**. You can add complex logging, metrics, or security checks without touching the agent's core instructions or tools. This makes the code cleaner and the observability logic reusable across multiple agents.

2.  **How does ADK 2.0 improve tracing for complex workflows?**
    *   **Answer:** Every event in ADK 2.0 contains **`node_info`**. In a distributed trace (Cloud Trace), this allows you to see exactly which node in a graph (e.g., a specific specialist in a MAS) triggered which event. It transforms a "flat" list of logs into a hierarchical, graph-aware view of execution.

3.  **When should you use a Plugin vs. Native Telemetry?**
    *   **Answer:** Use **Native Telemetry (OTel)** for standard performance monitoring (latency, error rates, system health) that needs to be aggregated in dashboards like Cloud Monitoring. Use **Plugins** for logic that requires custom Python code, such as sending a message to Slack after a specific business failure or calculating session-specific metrics that OTel doesn't handle natively.

</SolutionVault>
