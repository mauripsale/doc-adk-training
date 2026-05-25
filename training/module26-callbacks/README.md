---
sidebar_position: 26
title: "Module 26: Callbacks and Guardrails - Agent Safety and Monitoring"
---

# Module 26: Callbacks and Guardrails - Agent Safety and Monitoring

## Theory

### Beyond Standard Execution: The Need for Control

Production-grade agents require more than just a simple request-response loop. They need safety checks, monitoring, and the ability to dynamically control their own behavior. **Callbacks** are the ADK's primary mechanism for injecting this custom logic into the agent's execution lifecycle.

### What are Callbacks?

Callbacks are Python functions that you register with an agent to run at specific "checkpoints" during its execution. They allow you to:

*   **Observe:** Log LLM prompts, tool calls, and agent responses for auditing and debugging.
*   **Control:** Intercept and block or modify operations before they happen.
*   **Implement Guardrails:** Enforce safety policies, such as preventing the generation of harmful content or the use of tools with invalid arguments.

### The Callback Lifecycle and Control Flow

The ADK provides a rich set of callbacks. The key to using them for control is the value your function returns:

*   **Return `None`:** The default behavior. This tells the ADK to continue the execution flow normally. This is used for observation (e.g., logging).
*   **Return an Object:** This **overrides** the default behavior. The agent will skip the standard operation (e.g., calling the LLM, running a tool) and use the object you returned instead.

Here are the primary callbacks for an `LlmAgent`:

| Callback | Trigger | Control Action (Return Value) | Use Case |
| :--- | :--- | :--- | :--- |
| `before_agent_callback` | Before the agent starts. | `Content` object | Skip the entire agent run and return a canned response (e.g., for maintenance mode, or **caching** to skip the LLM call entirely). |
| `before_model_callback` | Before calling the LLM. | `LlmResponse` object | **Input Guardrail:** Block an inappropriate prompt and return a safety message. |
| `after_model_callback` | After the LLM responds. | `LlmResponse` object | **Output Filtering:** Modify the LLM's response to remove sensitive information (PII) before the user sees it. |
| `before_tool_callback` | Before a tool is executed. | `dict` | **Argument Validation:** Block a tool call with invalid arguments and return an error dictionary. |
| `after_tool_callback` | After a tool runs. | `dict` | **Result Modification:** Change the result of a tool before it's sent back to the LLM for the next step. |
| `after_agent_callback` | After the agent finishes. | `Content` object | Add a standard disclaimer or footer to every final agent response. |

By mastering this "return None vs. return Object" pattern, you can build robust, production-ready agents with sophisticated safety and monitoring capabilities.

### Key Takeaways
- **Callbacks** are functions that run at specific checkpoints in an agent's execution lifecycle, allowing for observation and control.
- Returning `None` from a callback allows the agent to continue its normal execution, which is used for logging and monitoring.
- Returning an object from a callback **overrides** the agent's default behavior, allowing you to block or modify operations.
- Callbacks are the primary mechanism for implementing safety **guardrails**, such as blocking inappropriate content (`before_model_callback`) or validating tool arguments (`before_tool_callback`).
- They can also be used for output filtering (e.g., PII redaction in `after_model_callback`) and adding standard content to all responses (`after_agent_callback`).
- **Callbacks vs. Plugins:** The key difference lies in their scope and primary role. **Callbacks** are agent-specific, designed for control, modification, and implementing guardrails within a single agent's logic. **Plugins** are global (registered at the `Runner` level), designed for observation and telemetry (metrics, logging, alerting) across all agents in an application. Choose a callback to modify or block an agent's specific operations; choose a plugin to monitor behavior across the entire system.
- **Importance of Return Type:** When a callback (like `before_model_callback`) returns a specific object type (e.g., `types.GenerateContentResponse`), it signals a clear override instruction to the ADK framework. This allows the framework to skip the standard operation (like calling the LLM) and use the returned object as a direct substitute, ensuring the data flow remains consistent and predictable. Returning a simple string or dictionary would break this control flow, as the framework would not know how to handle the unstructured data.
- **Reliability and Safety:** Using callbacks for guardrails and validation significantly enhances an agent's reliability and safety. They reduce the dependency on the LLM's non-deterministic reasoning for critical safety checks. `before_model_callback` can prevent harmful content from ever reaching the LLM, while `after_model_callback` can filter sensitive data (PII) from the final response. Similarly, `before_tool_callback` can validate tool arguments to prevent runtime errors and crashes, leading to a more stable and secure production deployment.
