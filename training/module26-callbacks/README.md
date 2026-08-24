---
sidebar_position: 26
title: "Module 26: Callbacks and Guardrails - Agent Safety and Monitoring"
---

# Module 26: Callbacks and Guardrails - Agent Safety and Monitoring

## Theory

### Beyond Standard Execution: The Need for Control

Production-grade agents require more than just a simple request-response loop. They need safety checks, monitoring, and the ability to dynamically control their own behavior. **Callbacks** are the ADK's primary mechanism for injecting this custom logic into the agent's execution lifecycle.

### The Callback Lifecycle in ADK 2.0

Callbacks are registered directly on an `Agent` node. They allow you to intercept specific stages of that node's execution.

| Callback | Trigger | Arguments | Return Type |
| :--- | :--- | :--- | :--- |
| `before_agent_callback` | Start of node execution. | `(callback_context: CallbackContext)` | `Optional[types.Content]` |
| `after_agent_callback` | End of node execution. | `(callback_context: CallbackContext)` | `Optional[types.Content]` |
| `before_model_callback` | Before LLM call. | `(callback_context, llm_request: LlmRequest)` | `Optional[LlmResponse]` |
| `after_model_callback` | After LLM response. | `(callback_context, llm_response: LlmResponse)` | `Optional[LlmResponse]` |
| `before_tool_callback` | Before tool execution. | `(tool: BaseTool, args, tool_context: ToolContext)` | `Optional[dict]` |
| `after_tool_callback` | After tool execution. | `(tool: BaseTool, args, tool_context, response)` | `Optional[dict]` |

### Control via Return Values

The power of callbacks lies in their ability to **override** the default framework behavior:

*   **Return `None`:** Tells the ADK to "Continue normally." This is ideal for logging or side-effects.
*   **Return an Object:** Tells the ADK to "Stop what you're doing and use THIS instead."
    *   Example: Returning a `types.Content` from `before_agent_callback` will skip the LLM entirely and return that content as the final result (perfect for **Caching**).
    *   Example: Returning an error dictionary from `before_tool_callback` will block the tool from running.

### Callbacks vs. Plugins: Which one to use?

*   **Callbacks (Granular Control):** Use these when you want to modify the behavior of a **specific node**. They are part of the agent's logic and can block/override operations.
*   **Plugins (Global Observability):** Use these for cross-cutting concerns that apply to the **entire application** (e.g., logging every request to BigQuery, global RAI moderation, or OpenTelemetry tracing). Plugins generally observe events rather than blocking them.

### Built-in Example: Self-Healing Plugins

ADK ships two ready-made plugins, built entirely from the callbacks above, that automatically retry on failure instead of surfacing an error to the user:

*   **`ReflectAndRetryModelPlugin`** (`before_model_callback`/`after_model_callback`): catches malformed model responses (like a broken function call), injects reflection guidance, and retries the model call automatically.
*   **`ReflectAndRetryToolPlugin`** (`before_tool_callback`/`after_tool_callback`): does the same for tools that return an error *response* (not a Python exception) — e.g. a tool that replies with `{"status": "error"}`.

```python
from google.adk.apps.app import App
from google.adk.plugins import ReflectAndRetryModelPlugin, ReflectAndRetryToolPlugin

app = App(
    name="my_app",
    root_agent=root_agent,
    plugins=[
        ReflectAndRetryModelPlugin(max_retries=3),
        ReflectAndRetryToolPlugin(max_retries=3),
    ],
)
```

Note these operate one level below the `RetryConfig` you saw in Module 38, which retries a failed *Workflow node* on a raised Python exception. Together, the three cover a different layer each: node → tool response → model response.

### Key Takeaways
- **Callbacks** provide programmatic "hooks" into an agent's execution lifecycle.
- **Node-level scope:** Callbacks are registered on the `Agent` object.
- **Overriding:** You can bypass expensive LLM calls or risky tool executions by returning a value from a "before" callback.
- **Type Safety:** ADK 2.0 enforces specific signatures for each callback type to ensure robust data flow.
