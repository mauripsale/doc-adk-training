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

### Step 2: Implement the Observability Plugins

**Exercise:** Open `agent.py`. Skeletons for three plugins are provided. Your task is to implement the logic inside the `on_event_callback` method for each one, and then register them with the App.

```python
# In agent.py (Starter Code)
import asyncio
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.runners import InMemoryRunner
from google.adk.plugins import BasePlugin
from google.adk.events import Event

# --- Data Classes (Provided for you) ---
@dataclass
class RequestMetrics:
    request_id: str
    start_time: float
    end_time: Optional[float] = None
    latency: Optional[float] = None

@dataclass
class AggregateMetrics:
    total_requests: int = 0
    total_latency: float = 0.0
    requests: List[RequestMetrics] = field(default_factory=list)

# --- Custom Observability Plugins ---

class MetricsCollectorPlugin(BasePlugin):
    """A plugin to collect request/response metrics."""
    def __init__(self, name: str = 'metrics_collector_plugin'):
        super().__init__(name)
        self.metrics = AggregateMetrics()
        self.current_requests: Dict[str, RequestMetrics] = {}

    async def on_event_callback(self, *, event: Event, **kwargs):
        # TODO: 1. Check if event.event_type is 'request_start'.
        # If so, create a RequestMetrics object and store it in `self.current_requests`
        # using the event.invocation_id as the key.
        
        # TODO: 2. Check if event.event_type is 'request_complete'.
        # If so, retrieve the metric, calculate latency, update aggregate metrics,
        # and print a confirmation.
        pass

class AlertingPlugin(BasePlugin):
    """A plugin for alerting on anomalies."""
    def __init__(self, name: str = 'alerting_plugin', error_threshold: int = 3):
        super().__init__(name)
        self.error_threshold = error_threshold
        self.consecutive_errors = 0

    async def on_event_callback(self, *, event: Event, **kwargs):
        # TODO: 3. Check for 'request_complete' and 'request_error' event types.
        # - On success, reset `self.consecutive_errors` to 0.
        # - On error, increment the counter.
        # - If the counter reaches the threshold, print a CRITICAL ALERT.
        pass

class PerformanceProfilerPlugin(BasePlugin):
    """A plugin for performance profiling of tool calls."""
    def __init__(self, name: str = 'performance_profiler_plugin'):
        super().__init__(name)
        self.current_profile: Optional[Dict] = None

    async def on_event_callback(self, *, event: Event, **kwargs):
        # TODO: 4. Check for 'tool_call_start' and 'tool_call_complete'.
        # - On start, record the tool name and start time.
        # - On complete, calculate and print the duration.
        pass

# --- Agent Definition (Provided for you) ---
root_agent = Agent(
    model='gemini-2.5-flash',
    name='observability_agent',
    instruction="You are a helpful assistant.",
)

# --- Main Execution Block ---
def main():
    """Demonstrates how to register plugins with the App."""
    # TODO: 5. Instantiate your three plugins.
    
    # TODO: 6. Create an App instance and pass your plugins
    # to its `plugins` list, along with the root_agent.
    
    # TODO: 7. Create an InMemoryRunner passing the app.
    
    # The `adk web` command will automatically discover this runner and use it,
    # enabling all the plugins. When `adk web` starts, it looks for a `main()`
    # function in your `agent.py` to allow for this kind of custom runner
    # configuration.
    print("App with observability plugins is configured.")
    print("Run `adk web observability-agent` from the parent directory and interact with the agent to see plugin output in the console.")

if __name__ == "__main__":
    main()
```

### Step 3: Run and Test the Plugin System

1.  **Set up your `.env` file** and run `adk web`.
2.  **Interact with the Agent and Observe the Console:**
    *   Open the Dev UI and send a few prompts.
    *   Check the console where `adk web` is running. You should see the `[METRICS]`, `[ALERT]`, and `[PROFILER]` logs from your plugins.

### Having Trouble?
If you get stuck, you can find the complete, working code in the `lab-solution.md` file.

### Lab Summary
You have successfully built a modular observability system using the ADK's Plugin System. You have learned to:
*   Create custom plugins by inheriting from `BasePlugin`.
*   Implement the `on_event_callback` method to intercept and process agent events.
*   Filter events based on their `event_type` to implement specific logic.
*   Register plugins with the `App` object.

### Self-Reflection Questions
- What is the main advantage of using the Plugin System for observability instead of adding logging and metrics code directly inside your agent and tool functions?
- The `on_event_callback` method is called for every single event. In a high-traffic production system, what performance considerations would you need to keep in mind for the code you write inside this method?
- How could you extend the `MetricsCollectorPlugin` to track not just latency, but also the number of tokens used in each LLM call? (Hint: Inspect the `Event` objects for token information).

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMjUtb2JzZXJ2YWJpbGl0eS9sYWItc29sdXRpb24=`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module25-observability/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
