---
sidebar_position: 39
title: "Module 39: ADK Plugins"
---

# Module 39: Advanced Recovery with Built-In Plugins

![Modular Agent Plugins & Dynamic Hook Architecture Banner (Light)](img/hero-light.webp#gh-light-mode-only)
![Modular Agent Plugins & Dynamic Hook Architecture Banner (Dark)](img/hero-dark.webp#gh-dark-mode-only)

## Theory

### Building on Custom Plugins

Having previously built custom plugins for **Observability (Module 25)** and **Responsible AI Guardrails (Module 25.5)**, you are already familiar with how the ADK's plugin architecture cleanly separates cross-cutting infrastructure concerns from your core agent prompt logic. 

![Plugin Lifecycle & Hook Execution Architecture (Light)](img/plugin-lifecycle-architecture-light.webp#gh-light-mode-only)
![Plugin Lifecycle & Hook Execution Architecture (Dark)](img/plugin-lifecycle-architecture-dark.webp#gh-dark-mode-only)
*Figure: Plugin registration, hook interception pipeline, and reflect-and-retry error recovery flow.*

As a reminder, **Plugins** inherit from `BasePlugin` and register on the **App** (or Runner) to globally intercept and inspect events. They operate using three primary patterns:

1.  **Observing (Return `None`):** Watches the data flow (e.g., your custom `AlertingPlugin` from Module 25).
2.  **Intervening (Return an Object):** Blocks execution and overrides standard behavior (e.g., caching or PII blocking from Module 25.5).
3.  **Amending (Modify in place):** Amends the conversation history or configuration before execution.

In this module, we will explore one of the most powerful **built-in framework plugins** that uses a combination of *Intervening* and *Amending* to handle a critical production issue: **tool hallucination**.

### The Problem: Fragile Tool Use

One of the most common issues with LLM agents is **hallucination** or **misuse of tools**.
*   **Hallucinated Names:** The model might try to call `calculate_sum` when the tool is actually named `add_numbers`.
*   **Invalid Arguments:** The model might pass a string "five" when the tool expects the integer `5`.
*   **Transient Errors:** An API might fail temporarily with a 500 error.

Normally, these errors would cause your agent to crash or stop.

### The Solution: Built-In Framework Plugins

ADK 2.0 provides a suite of pre-packaged, production-grade plugins ready to be attached to your `App` definition.

#### 1. `ReflectAndRetryToolPlugin` (Self-Healing Tool Execution)

Acts as a safety net globally across all your tools when the LLM makes a formatting error or hallucination:
*   **Intercept & Detect:** Catches tool execution exceptions and argument mismatches.
*   **Reflect:** Amends the trajectory, feeding the error back to the LLM (e.g., *"Error: Tool 'calc' not found. Available tools: 'calculator'"*).
*   **Retry:** The LLM re-evaluates and issues a corrected tool call within `max_retries`.

#### 2. `BigQueryAgentAnalyticsPlugin` (Enterprise Telemetry)

Automatically streams invocation telemetry, token utilization, latency metrics, and execution paths directly into Google BigQuery for enterprise compliance, cost attribution, and quality audits without custom logging code.

#### 3. `GlobalInstructionPlugin` (Universal Governance)

Appends mandatory system instructions (e.g., brand guidelines, safety rules, regulatory compliance) across **all** agents managed by the application root orchestrator.

#### 4. `ContextFilterPlugin` (Token Budgeting)

Applies intelligent filtering and pruning rules to incoming prompt history, discarding irrelevant intermediate turns to preserve token budget.

### Using Built-In Plugins in ADK 2.0

To use plugins, instantiate them and add them to your `App` configuration:

```python
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
- **Plugins** provide global, cross-cutting functionality (logging, retries, security) across your entire application.
- They inherit from `BasePlugin` and use three patterns: **Observing**, **Intervening**, and **Amending**.
- Plugins are registered globally on the `App` object, running before any agent-level callbacks.
- **Built-in Plugins** like `ReflectAndRetryToolPlugin`, `BigQueryAgentAnalyticsPlugin`, and `GlobalInstructionPlugin` provide production-grade reliability out of the box.
