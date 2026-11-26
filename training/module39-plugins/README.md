---
sidebar_position: 39
title: "Module 39: ADK Plugins"
pagination_label: "Module 39: ADK Plugins Deep Dive — 📖 Theory & Overview"
---

# Module 39: Advanced Recovery with Built-In Plugins

![Modular Agent Plugins & Dynamic Hook Architecture Banner (Light)](img/hero-light.webp#gh-light-mode-only)
![Modular Agent Plugins & Dynamic Hook Architecture Banner (Dark)](img/hero-dark.webp#gh-dark-mode-only)

## Theory

### Building on Custom Plugins

Having previously implemented node-level **Callbacks (Module 25)** and custom app-level plugins for **Responsible AI Guardrails (Module 25.5)** and **Observability (Module 26)**, you are already familiar with how the ADK's plugin architecture cleanly separates cross-cutting infrastructure concerns from your core agent prompt logic.

![Plugin Lifecycle & Hook Execution Architecture (Light)](img/plugin-lifecycle-architecture-light.webp#gh-light-mode-only)
![Plugin Lifecycle & Hook Execution Architecture (Dark)](img/plugin-lifecycle-architecture-dark.webp#gh-dark-mode-only)
*Figure: Plugin registration, hook interception pipeline, and reflect-and-retry error recovery flow.*

As a reminder, **Plugins** inherit from `BasePlugin` and register on the **App** (or Runner) to globally intercept and inspect events across every agent in the hierarchy. They operate using three primary patterns:

1.  **Observing (Return `None`):** Watches the data flow without altering execution (e.g., your custom `AlertingPlugin` from **Module 26**).
2.  **Intervening (Return an Object):** Intercepts execution or errors and overrides standard behavior (e.g., PII egress blocking from **Module 25.5**).
3.  **Amending (Modify in place):** Amends the conversation request, instructions, or configuration before execution.

In this module, we explore ADK's **built-in framework plugins**—focusing on how `ReflectAndRetryToolPlugin` combines *Intervening* and *Amending* to self-heal **fragile tool calls and runtime argument errors**.

### The Problem: Fragile Tool Execution

Even well-prompted LLM agents frequently encounter tool execution errors in production:
*   **Malformed or Legacy Argument Syntax:** The model passes `"6 x 7"` using a legacy `'x'` multiplication symbol when a strict expression parser raises `ValueError("Legacy operator 'x' is not supported; retry using '*' instead.")`.
*   **Domain Validation Failures:** A tool raises a `ValueError` because a date range is inverted or an identifier violates a checksum rule.
*   **Transient Upstream Errors:** An external API raises a temporary `ConnectionError` or `TimeoutError`.

*(Note: In ADK 2.14+, calling a completely unregistered tool name returns a native tool-not-found dictionary to the model automatically, whereas **exceptions raised inside a tool function** propagate out and crash the invocation unless intercepted!)*

### The Solution: Built-In Framework Plugins

ADK 2.0 provides a suite of pre-packaged, production-grade plugins in `google.adk.plugins` ready to be attached to your `App` definition.

#### 1. `ReflectAndRetryToolPlugin` (Self-Healing Tool Execution)

Acts as a concurrency-safe global safety net across all tools registered in your `App`:
*   **Intercept & Detect (`on_tool_error_callback`):** Catches unhandled exceptions raised during tool execution (and can also inspect normal dictionary results if you subclass it and override `extract_error_from_result`).
*   **Reflect:** Packages the exception type, message, failed arguments, and numbered retry guidance into a structured `ToolFailureResponse` (`ERROR_HANDLED_BY_REFLECT_AND_RETRY_PLUGIN`) instead of crashing the runner.
*   **Retry:** Feeds that structured reflection prompt back to the LLM so it can reformulate its arguments and invoke the tool cleanly within `max_retries` (tracked per-invocation by default via `TrackingScope.INVOCATION`).

#### 2. `BigQueryAgentAnalyticsPlugin` (Enterprise Telemetry)

Automatically streams invocation telemetry, token utilization, latency metrics, and execution paths directly into Google BigQuery for enterprise compliance, cost attribution, and quality audits without custom logging code.
> **Optional Dependency Note:** `BigQueryAgentAnalyticsPlugin` requires the BigQuery analytics extra. Install it with `uv add "google-adk[bigquery-analytics]"` before importing it.

#### 3. `GlobalInstructionPlugin` (Universal Governance)

Injects mandatory system instructions (e.g., brand guidelines, safety rules, regulatory compliance headers) across **all** agents managed by the `App` container—accepting either a static string or a dynamic `InstructionProvider` callable via `GlobalInstructionPlugin(global_instruction=...)`.

#### 4. `ContextFilterPlugin` (Token Budgeting)

Applies intelligent filtering and pruning rules to incoming prompt history, discarding irrelevant intermediate turns to preserve token budget.

### Using Built-In Plugins in ADK 2.0

To use built-in plugins, instantiate them and pass them to `App(..., plugins=[...])`:

```python
# Note: BigQueryAgentAnalyticsPlugin requires `uv add "google-adk[bigquery-analytics]"`
from google.adk.apps.app import App
from google.adk.runners import Runner
from google.adk.plugins import (
    ReflectAndRetryToolPlugin,
    BigQueryAgentAnalyticsPlugin,
    GlobalInstructionPlugin,
)

# 1. Instantiate the desired built-in plugins
retry_plugin = ReflectAndRetryToolPlugin(max_retries=3)

analytics_plugin = BigQueryAgentAnalyticsPlugin(
    project_id="my-enterprise-gcp-project",
    dataset_id="agent_telemetry",
)

governance_plugin = GlobalInstructionPlugin(
    global_instruction="Always maintain strict corporate compliance and never disclose internal API endpoints."
)

# 2. Register plugins globally on the App object
app = App(
    name="enterprise_agent_app",
    root_agent=my_agent,
    plugins=[retry_plugin, analytics_plugin, governance_plugin],
)

runner = Runner(app=app, session_service=...)
```

### Key Takeaways
- **Plugins** provide global, cross-cutting functionality (self-healing retries, analytics, governance) across your entire `App`.
- They inherit from `BasePlugin` and use three patterns: **Observing**, **Intervening**, and **Amending**.
- Plugins are registered globally on the `App` object, executing across every agent and tool in the application.
- **Built-in Plugins** like `ReflectAndRetryToolPlugin`, `BigQueryAgentAnalyticsPlugin` (`google-adk[bigquery-analytics]`), and `GlobalInstructionPlugin` provide production-grade reliability out of the box.
