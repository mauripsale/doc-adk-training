---
sidebar_position: 25
title: "Module 25: Callbacks and Guardrails - Agent Safety and Monitoring"
pagination_label: "Module 25: Callbacks & Safety Guardrails — 📖 Theory & Overview"
---

# Module 25: Callbacks and Guardrails - Agent Safety and Monitoring

![Agent Execution Callbacks & Runtime Guardrails (Light)](img/hero-light.webp#gh-light-mode-only)
![Agent Execution Callbacks & Runtime Guardrails (Dark)](img/hero-dark.webp#gh-dark-mode-only)

## Theory

### Beyond Standard Execution: The Need for Control

Production-grade agents require more than just a simple request-response loop. They need safety checks, monitoring, and the ability to dynamically control their own behavior. **Callbacks** are the ADK's primary mechanism for injecting this custom logic into the agent's execution lifecycle.

### The Callback Lifecycle in ADK 2.0

![Six-Stage Callback Lifecycle Hooks Matrix (Light)](img/callback-lifecycle-hooks-matrix-light.webp#gh-light-mode-only)
![Six-Stage Callback Lifecycle Hooks Matrix (Dark)](img/callback-lifecycle-hooks-matrix-dark.webp#gh-dark-mode-only)
*Figure: Six-stage callback lifecycle hooks matrix intercepting agent nodes, model calls, and tool executions.*

Callbacks are registered directly on an `Agent` node. They allow you to intercept specific stages of that node's execution.

| Callback | Trigger | Arguments | Return Type |
| :--- | :--- | :--- | :--- |
| `before_agent_callback` | Start of node execution. | `(callback_context: CallbackContext)` | `Optional[types.Content]` |
| `after_agent_callback` | End of node execution. | `(callback_context: CallbackContext)` | `Optional[types.Content]` |
| `before_model_callback` | Before LLM call. | `(callback_context, llm_request: LlmRequest)` | `Optional[LlmResponse]` |
| `after_model_callback` | After LLM response. | `(callback_context, llm_response: LlmResponse)` | `Optional[LlmResponse]` |
| `before_tool_callback` | Before tool execution. | `(tool: BaseTool, args, tool_context: ToolContext)` | `Optional[dict]` |
| `after_tool_callback` | After tool execution. | `(tool: BaseTool, args, tool_context, tool_response)` | `Optional[dict]` |

### Control via Return Values

The power of callbacks lies in their ability to **override** the default framework behavior:

*   **Return `None`:** Tells the ADK to "Continue normally." This is ideal for logging or side-effects.
*   **Return an Object:** Tells the ADK to "Stop what you're doing and use THIS instead."
    *   Example: Returning a `types.Content` from `before_agent_callback` will skip the LLM entirely and return that content as the final result (perfect for **Caching**).
    *   Example: Returning an error dictionary from `before_tool_callback` will block the tool from running.

### Callbacks vs. Plugins: Which one to use?

*   **`Agent` Callbacks (Node-Scoped Control):** Registered directly on a single `Agent(before_*=..., after_*=...)`. Use callbacks when behavior is specific to **one agent node** (such as per-agent response caching, custom prompt shaping, or single-node tool argument rules).
*   **`App` Plugins (Fleet-Wide Governance & Telemetry):** Registered once on `App(plugins=[...])` by subclassing `BasePlugin` (`from google.adk.plugins import BasePlugin`). Plugins wrap **every** agent, sub-agent, and workflow node in the application and execute *before* node-level callbacks—making them the standard architecture for organization-wide RAI/PII guardrails (**Module 25.5**) and OpenTelemetry/AgentOps observability (**Module 26**).

#### Signature Bridge: `Agent` Function Callbacks vs. `BasePlugin` Methods

Notice one subtle difference you will use immediately in **Modules 25.5 and 26**:
*   Standalone `Agent` callbacks can be plain `def` (or `async def`) functions taking positional arguments—e.g., `def before_model_callback(callback_context, llm_request):`.
*   `BasePlugin` lifecycle methods are **`async def`** methods that receive **keyword-only arguments (`*`)**—so include `*, ...` and `**kwargs` for clean forward compatibility:

```python
from google.adk.apps import App
from google.adk.plugins import BasePlugin

class MyPlugin(BasePlugin):
    def __init__(self, name: str = "my_plugin"):
        super().__init__(name)

    # Note the keyword-only `*` signature used by BasePlugin hooks in Modules 25.5 & 26!
    async def before_model_callback(self, *, callback_context, llm_request, **kwargs):
        print(f"[Plugin] Intercepting LLM request for agent: {callback_context.agent_name}")
        return None  # Return None to continue, or an LlmResponse to short-circuit

app = App(name="my_app", root_agent=root_agent, plugins=[MyPlugin()])
```

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

Note these operate one level below the `RetryConfig` you'll see in Module 38, which retries a failed *Workflow node* on a raised Python exception. Together, the three cover a different layer each: node → tool response → model response.

These two plugins *recover* from errors. If you only need to be *notified* of an unrecoverable one — e.g. to page on-call before the app crashes — `BasePlugin` also exposes `on_agent_error_callback` and `on_run_error_callback`, notification-only hooks that always re-raise the original exception.

<KnowledgeCheck
  id="m25-lifecycle-callback-overrides"
  question="In ADK 2.0, what happens when a before_tool_callback returns a dictionary with an error payload instead of None?"
  options={[
    "The underlying tool execution is intercepted and blocked; the returned dictionary is provided to the agent as the tool result",
    "The entire Python process crashes with an unhandled CallbackException",
    "The agent resets its session state to turn 0",
    "The tool runs anyway in the background and ignores the callback return"
  ]}
  correctIndex={0}
  hint="Recall how 'before' callbacks can override or short-circuit execution."
  explanation="Returning a non-None value from a before_tool_callback short-circuits the actual tool execution. ADK treats the returned object as the tool's result, effectively acting as an active security guardrail or interceptor."
/>

### Key Takeaways
- **Callbacks** provide programmatic "hooks" into an agent's execution lifecycle (`before_agent`, `after_agent`, `before_model`, `after_model`, `before_tool`, `after_tool`).
- **Node-level scope:** Callbacks are registered directly on an `Agent` object for single-node customization and caching.
- **Overriding:** You can bypass expensive LLM calls or risky tool executions by returning a replacement object instead of `None` from a "before" callback.
- **Bridge to `BasePlugin`:** When you need these exact lifecycle hooks applied across *every* agent in an `App`, package them into a `BasePlugin`—which is exactly what we'll build next in **Module 25.5 (Responsible AI & Safety Plugins)** for fail-closed enterprise security and **Module 26 (Observability & AgentOps)** for fleet-wide telemetry!
