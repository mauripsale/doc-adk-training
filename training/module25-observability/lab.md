---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 25: Building an Observability System with Plugins Challenge

## Goal

In this lab, you will build a comprehensive observability system for an agent using the ADK's **Plugin System**. You will implement separate plugins for metrics collection, alerting, and performance profiling.

### Step 1: Create the Agent Project

1.  **Create the agent project:**
    ```shell
    uv run adk create observability_agent
    ```
    When prompted to choose a type for the root agent, choose **2. Code**.

2.  **Navigate into the new directory:**
    ```shell
    cd observability_agent
    ```

### Step 2: Implement a Business Logic Plugin

**Exercise:** Open `agent.py`. We will start by creating an **Alerting Plugin** that detects consecutive errors.

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
        raise ValueError("Simulated failure!")
    return {"status": "success"}

class AlertingPlugin(BasePlugin):
    """A plugin that prints an alert after 3 consecutive request errors."""
    def __init__(self, name: str = 'alerting_plugin'):
        super().__init__(name)
        self.error_count = 0
        self._had_error_this_turn = False

    async def on_tool_error_callback(self, *, tool, tool_args, tool_context, error):
        # TODO: Implement alerting logic here.
        # 1. Mark that this turn had an error (self._had_error_this_turn = True).
        # 2. Increment self.error_count and print an alert, escalating to a
        #    critical alert once you hit the threshold.
        # 3. Return a dict (e.g. {"status": "error", "message": str(error)})
        #    so the agent recovers gracefully instead of crashing the run --
        #    returning None here would let the exception propagate.
        pass

    async def on_event_callback(self, *, event: Event, **kwargs):
        # TODO: When event.is_final_response() is True, if this turn had NO
        # error, reset self.error_count to 0 -- a clean turn means we've
        # recovered. Don't forget to reset self._had_error_this_turn too.
        pass

# --- Create a simple Agent ---
agent = Agent(
    name="monitored_agent",
    model="gemini-3.5-flash",
    instruction="You have a risky_operation tool. If the user says 'FAIL', call it with should_fail=True. Otherwise, call it with should_fail=False.",
    tools=[risky_operation],
)

# --- Register Plugin with App ---
app = App(
    name="observability_demo",
    root_agent=agent,
    plugins=[AlertingPlugin()]
)
```

### Step 3: Configure Enterprise Telemetry

**Exercise:** Now, let's enable native **Cloud Trace** integration. In a real production environment, this would send data to Google Cloud. Here, we will configure the hooks.

```python
# Add this to your agent.py imports
from google.adk.telemetry.google_cloud import get_gcp_exporters
from google.adk.telemetry.setup import maybe_set_otel_providers

# TODO: 1. Use get_gcp_exporters to enable cloud tracing and metrics.
# TODO: 2. Call maybe_set_otel_providers to register the hooks.
```

### Step 4: Run and Verify

1.  **Launch the Dev UI:**
    ```shell
    uv run adk web .
    ```
2.  **Test the Alerting Plugin:**
    Send prompts and verify the console output.
3.  **Inspect the Trace Metadata:**
    In the Dev UI, open the **Trace** tab. Notice how ADK 2.0 provides detailed information about each event, which is exactly what gets sent to Cloud Trace.


### Having Trouble?
If you get stuck, you can find the complete, working code in the `lab-solution.md` file.

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

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMjUtb2JzZXJ2YWJpbGl0eS9sYWItc29sdXRpb24=`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module25-observability/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
