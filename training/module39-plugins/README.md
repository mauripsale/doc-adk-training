---
sidebar_position: 39
title: "Module 39: ADK Plugins"
---

# Module 39: Enhancing Agents with ADK Plugins

## Theory

### What are Plugins?

As you build more complex agents, you'll find that certain functionality is needed across *all* your agents and tools. Features like logging, error handling, context filtering, and global policy enforcement are "cross-cutting concerns"—they don't belong in the core logic of a single agent, but rather in the infrastructure that runs them.

In the ADK, **Plugins** are reusable modules that hook into the execution lifecycle (via global callbacks) to provide this functionality. 

Unlike agent-specific callbacks (like `before_model_callback` on a single `Agent`), a Plugin is registered on the **App** (or Runner), and its logic applies globally to *every* step of the workflow, for *every* agent in the application.

### The Three Plugin Patterns

Plugins in ADK v1.0 inherit from `BasePlugin` and operate using three primary patterns based on what their hook methods return:

1.  **Observing (Return `None`):** The plugin watches the data flow without changing it. Useful for logging, analytics (like `BigQueryAgentAnalyticsPlugin`), or debugging.
2.  **Intervening (Return an Object):** The plugin blocks the standard execution and forces the system to use a different result. Useful for global guardrails or caching.
3.  **Amending (Modify in place):** The plugin modifies the request or response objects before they are passed along. Useful for injecting global system instructions (`GlobalInstructionPlugin`) or redacting PII universally.

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

### Using Plugins in ADK v1.0

To use a plugin, you instantiate it and add it to your `App` configuration.

```python
from google.adk.apps.app import App
from google.adk.runners import Runner
from google.adk.plugins import ReflectAndRetryToolPlugin

# Configure the plugin
retry_plugin = ReflectAndRetryToolPlugin(
    max_retries=3  # Give agents 3 chances to fix their mistakes
)

# In ADK v1.0, plugins are registered on the App object
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
