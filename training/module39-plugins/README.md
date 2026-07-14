---
sidebar_position: 39
title: "Module 39: ADK Plugins"
---

# Module 39: Advanced Recovery with Built-In Plugins

## Theory

### Building on Custom Plugins

Having previously built custom plugins for **Observability (Module 25)** and **Responsible AI Guardrails (Module 25.5)**, you are already familiar with how the ADK's plugin architecture cleanly separates cross-cutting infrastructure concerns from your core agent prompt logic. 

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

### The Solution: Reflect and Retry

The **`ReflectAndRetryToolPlugin`** is a powerful built-in plugin designed to solve this exact problem using the *Intervening* and *Amending* patterns. It acts as a safety net globally across all your tools.

**How it works:**
1.  **Intercept:** When any Agent calls a tool, the plugin watches the execution.
2.  **Detect Failure:** If the tool raises an Exception (or a specific error), the plugin catches it.
3.  **Reflect:** The plugin intercepts the error and amends the conversation history, sending the error message *back* to the LLM as an observation (e.g., *"Error: Tool 'calc' not found. Available tools: 'calculator'"*).
4.  **Retry:** The LLM, seeing this error, "reflects" on its mistake and generates a *new* tool call with the corrected name or arguments.
5.  **Loop:** This process repeats up to a configured `max_retries` limit.

### Using Plugins in ADK 2.0

To use a plugin, you instantiate it and add it to your `App` configuration.

```python
from google.adk.apps.app import App
from google.adk.runners import Runner
from google.adk.plugins import ReflectAndRetryToolPlugin

# Configure the plugin
retry_plugin = ReflectAndRetryToolPlugin(
    max_retries=3  # Give agents 3 chances to fix their mistakes
)

# In ADK 2.0, plugins are registered globally on the App object
app = App(
    name="my_robust_app",
    root_agent=my_agent,
    plugins=[retry_plugin] # <--- Registered globally here
)

runner = Runner(app=app, session_service=...)
```

### Key Takeaways
- **Plugins** provide global, cross-cutting functionality (logging, retries, security) across your entire application.
- They inherit from `BasePlugin` and use three patterns: **Observing**, **Intervening**, and **Amending**.
- Plugins are registered globally on the `App` object, running before any agent-level callbacks.
- The **`ReflectAndRetryToolPlugin`** makes agents robust by automatically catching tool errors, feeding them back to the model, and allowing it to self-correct without crashing.
