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
    adk create observability_agent
    ```
    When prompted, choose the **Programmatic (Python script)** option.

2.  **Navigate into the new directory:**
    ```shell
    cd observability_agent
    ```

### Step 2: Implement a Business Logic Plugin

**Exercise:** Open `agent.py`. We will start by creating an **Alerting Plugin** that detects consecutive errors.

```python
# In agent.py (Starter Code)
from google.adk import Agent, App, node, Context, Workflow
from google.adk.plugins import BasePlugin
from google.adk.events import Event

class AlertingPlugin(BasePlugin):
    """A plugin that prints an alert after 3 consecutive request errors."""
    def __init__(self, name: str = 'alerting_plugin'):
        super().__init__(name)
        self.error_count = 0

    async def on_event_callback(self, *, event: Event, **kwargs):
        # TODO: Implement alerting logic
        # 1. Check for 'request_complete' (reset counter)
        # 2. Check for 'request_error' (increment and alert)
        pass

# --- Create a simple Agent ---
agent = Agent(
    name="monitored_agent",
    model="gemini-3.5-flash",
    instruction="Answer the user. If they say 'FAIL', trigger an error (simulated)."
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
    adk web .
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
*   Implement the `on_event_callback` method to intercept and process agent events.
*   Filter events based on their `event_type` to implement specific logic.
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
