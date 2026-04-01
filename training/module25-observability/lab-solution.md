---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 25 Solution: Building an Observability System with Plugins

## Goal

This file contains the complete code for the `agent.py` script in the Observability System with Plugins lab.

### `observability-agent/agent.py`

```python
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.runners import InMemoryRunner
from google.adk.plugins import BasePlugin
from google.adk.events import Event
from google.genai import types

# --- Data Classes for Metrics ---

@dataclass
class RequestMetrics:
    """Metrics for a single agent request."""
    request_id: str
    start_time: float
    end_time: Optional[float] = None
    latency: Optional[float] = None
    success: bool = True
    error: Optional[str] = None

@dataclass
class AggregateMetrics:
    """Aggregate metrics across all requests."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency: float = 0.0
    requests: List[RequestMetrics] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0: return 0.0
        return self.successful_requests / self.total_requests

    @property
    def avg_latency(self) -> float:
        if self.total_requests == 0: return 0.0
        return self.total_latency / self.total_requests

# --- Custom Observability Plugins ---

class MetricsCollectorPlugin(BasePlugin):
    """A plugin to collect request/response metrics."""
    def __init__(self, name: str = 'metrics_collector_plugin'):
        super().__init__(name)
        self.metrics = AggregateMetrics()
        self.current_requests: Dict[str, RequestMetrics] = {}

    async def on_event_callback(self, *, event: Event, **kwargs):
        if hasattr(event, 'event_type'):
            if event.event_type == 'request_start':
                request_id = event.invocation_id
                metrics = RequestMetrics(request_id=request_id, start_time=time.time())
                self.current_requests[request_id] = metrics
                print(f"✔️ [METRICS] Request {request_id} started.")

            elif event.event_type == 'request_complete':
                request_id = event.invocation_id
                if request_id in self.current_requests:
                    metrics = self.current_requests.pop(request_id)
                    metrics.end_time = time.time()
                    metrics.latency = metrics.end_time - metrics.start_time

                    self.metrics.total_requests += 1
                    self.metrics.successful_requests += 1
                    self.metrics.total_latency += metrics.latency
                    self.metrics.requests.append(metrics)
                    print(f"✔️ [METRICS] Request {request_id} completed in {metrics.latency:.2f}s.")

class AlertingPlugin(BasePlugin):
    """A plugin for alerting on anomalies like consecutive errors."""
    def __init__(self, name: str = 'alerting_plugin', error_threshold: int = 3):
        super().__init__(name)
        self.error_threshold = error_threshold
        self.consecutive_errors = 0

    async def on_event_callback(self, *, event: Event, **kwargs):
        if hasattr(event, 'event_type'):
            if event.event_type == 'request_complete':
                self.consecutive_errors = 0 # Reset on success
            elif event.event_type == 'request_error':
                self.consecutive_errors += 1
                print(f"🚨 [ALERT] Error detected. Consecutive errors: {self.consecutive_errors}")
                if self.consecutive_errors >= self.error_threshold:
                    print(f"🔥 [CRITICAL ALERT] {self.consecutive_errors} consecutive errors detected!")

class PerformanceProfilerPlugin(BasePlugin):
    """A plugin for detailed performance profiling of tool calls."""
    def __init__(self, name: str = 'performance_profiler_plugin'):
        super().__init__(name)
        self.current_profile: Optional[Dict] = None

    async def on_event_callback(self, *, event: Event, **kwargs):
        if hasattr(event, 'event_type'):
            if event.event_type == 'tool_call_start':
                self.current_profile = {
                    'tool': getattr(event, 'tool_name', 'unknown'),
                    'start_time': time.time()
                }
                print(f"⏱️ [PROFILER] Tool call '{self.current_profile['tool']}' started.")

            elif event.event_type == 'tool_call_complete':
                if self.current_profile:
                    duration = time.time() - self.current_profile['start_time']
                    print(f"⏱️ [PROFILER] Tool call '{self.current_profile['tool']}' finished in {duration:.3f}s.")
                    self.current_profile = None

# --- Agent Definition ---

root_agent = Agent(
    model='gemini-2.5-flash',
    name='observability_agent',
    instruction="You are a helpful assistant. Your responses are being monitored for quality and performance.",
)

# --- Main Execution Block (for `adk web`) ---

# In a real application, you would likely run this in a separate script.
# For this lab, we include it to show how plugins are registered.
def main():
    """Demonstrates how to register plugins with the App."""

    # Instantiate plugins
    metrics_plugin = MetricsCollectorPlugin()
    alerting_plugin = AlertingPlugin()
    profiler_plugin = PerformanceProfilerPlugin()

    # Register plugins with the App
    app = App(
        name="observability_app",
        root_agent=root_agent,
        plugins=[metrics_plugin, alerting_plugin, profiler_plugin]
    )

    runner = InMemoryRunner(app=app)

    # The `adk web` command will automatically discover this runner
    # and use it, enabling all the plugins. When `adk web` starts, it looks
    # for a `main()` function in your `agent.py` to allow for this kind of
    # custom runner configuration.
    print("App with observability plugins is configured.")
    print("Run `adk web` and interact with the agent to see plugin output in the console.")

if __name__ == "__main__":
    main()
```

### Self-Reflection Answers

1.  **What is the main advantage of using the Plugin System for observability instead of adding logging and metrics code directly inside your agent and tool functions?**
    *   **Answer:** The primary advantage is **Separation of Concerns**. By using plugins, your observability code (e.g., sending metrics to Prometheus, logging to Splunk) is completely isolated from the agent's business logic. This makes both systems easier to test, update, and maintain. It promotes reusability of plugins across different agents and keeps the agent's core logic clean and focused on its primary task.

2.  **The `on_event_callback` method is called for every single event. In a high-traffic production system, what performance considerations would you need to keep in mind for the code you write inside this method?**
    *   **Answer:** The `on_event_callback` method is awaited by the agent's runtime, meaning its execution directly impacts the agent's overall latency. Therefore, any code within it must be extremely efficient. Key considerations:
        *   **Avoid Blocking I/O:** Do not perform synchronous disk writes, network calls, or other blocking operations.
        *   **Minimize CPU Usage:** Keep computations minimal. Avoid complex data transformations or heavy processing.
        *   **Asynchronous Delegation:** For costly operations (e.g., sending data to a remote monitoring service), delegate them to asynchronous tasks (using `asyncio.create_task`) or offload them to separate threads/processes (e.g., a message queue) so they don't block the main event loop.
        *   **Batching/Buffering:** Instead of sending every single event immediately, buffer events and send them in batches if possible.

3.  **How could you extend the `MetricsCollectorPlugin` to track not just latency, but also the number of tokens used in each LLM call? (Hint: Inspect the `Event` objects for token information).**
    *   **Answer:** You would extend the `RequestMetrics` dataclass to include fields like `prompt_token_count: Optional[int]` and `completion_token_count: Optional[int]`. Then, in the `on_event_callback` method, specifically for `request_complete` events (or `llm_call_complete` events if available and more granular), you would inspect the `event.response` object. The token information is typically found within `event.response.usage_metadata` or a similar attribute, which holds `prompt_token_count` and `candidates_token_count`. You would extract these values and store them in the `RequestMetrics` instance before appending it to the `AggregateMetrics`. This would provide detailed token usage per request, which is vital for cost analysis.