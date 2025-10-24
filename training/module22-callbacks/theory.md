# Module 22: Intercepting Execution with Callbacks

## Theory

### Going Beyond the Standard Flow

So far, you've interacted with the ADK's execution flow in a standard way: a user sends a message, the agent runs, it might use a tool, and it produces a response. This is a powerful loop, but what if you need to inject your own custom logic *during* this process?

What if you wanted to:
*   Log every single prompt that is sent to the LLM for auditing purposes?
*   Prevent the agent from using a specific tool if the user doesn't have the right permissions?
*   Modify the response from a tool before the LLM sees it?
*   Implement a profanity filter on the user's input before the agent even starts?

This is where **Callbacks** come in. Callbacks are a powerful, advanced feature of the ADK that allow you to "hook into" the agent's execution lifecycle at specific, predefined points.

### What are Callbacks?

A callback is a Python function that you write and then register with an agent. The ADK framework promises to "call back" to your function at a specific moment during the agent's run.

Think of them as checkpoints or interception points in the agent's process. The ADK defines several of these checkpoints, the most common of which are:
*   **`before_model_callback`:** Runs just before a request is sent to the LLM.
*   **`after_model_callback`:** Runs just after a response is received from the LLM.
*   **`before_tool_callback`:** Runs just before a tool is executed.
*   **`after_tool_callback`:** Runs just after a tool has been executed.

### The Two Main Uses of Callbacks

Callbacks can be used in two primary ways: for **observation** and for **control**.

#### 1. Observation
This is the simplest use case. Your callback function can inspect the data at a certain checkpoint without changing it. This is perfect for:
*   **Logging:** Printing the LLM prompt or the tool arguments to the console.
*   **Metrics:** Recording how long a tool took to execute.
*   **Debugging:** Examining the agent's state at a specific point in the process.

To use a callback for observation, you simply have your function perform its action (like logging) and then `return None`. Returning `None` tells the ADK framework, "Thanks for the info, now carry on with the normal execution."

#### 2. Control
This is the more advanced and powerful use case. A callback can not only inspect the data, but it can also **change the flow of execution**. It does this by returning a specific type of object instead of `None`.

*   **`before_model_callback`:** If this callback returns an `LlmResponse` object, the ADK will **skip the actual call to the LLM** and use the response you provided instead. This is a powerful way to implement input guardrails (blocking a harmful prompt) or caching (returning a saved response for a common question).
*   **`before_tool_callback`:** If this callback returns a dictionary, the ADK will **skip the actual execution of the tool** and use the dictionary you provided as the tool's result. This is useful for validating tool arguments or mocking tool behavior during tests.
*   **`after_model_callback` / `after_tool_callback`:** These callbacks can **replace** the result from the LLM or a tool by returning a new `LlmResponse` or `dict`, respectively. This is useful for sanitizing outputs or reformatting data.

By using callbacks, you gain fine-grained control over the agent's internal workings, allowing you to implement complex logic, enforce policies, and deeply integrate the agent with external systems without modifying the core ADK framework.
