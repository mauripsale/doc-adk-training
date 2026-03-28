---
sidebar_position: 1
title: "Module 20: Iterative Refinement with Loop Agents"
---

# Module 20: Iterative Refinement with Loop Agents

## Theory

### The Need for Iteration

Many complex tasks aren't solved in a single pass. They require a process of iterative refinement: creating a draft, reviewing it, making improvements, and repeating until the result meets a quality standard. Examples include:
*   Refining a piece of code until it passes all tests.
*   Improving an essay based on editorial feedback.
*   Developing a plan and adjusting it based on new information.

While you could try to prompt a single `LlmAgent` to do this, it's not reliable. For robust, predictable looping, the ADK provides the `LoopAgent`.

### The `LoopAgent`

The `LoopAgent` is a workflow agent that executes its `sub_agents` sequentially, over and over again, until a termination condition is met.

**Key Concepts:**
*   **Execution:** In each iteration, sub-agents run in order, just like in a `SequentialAgent`.
*   **Shared State:** The `LoopAgent` passes the same session state to its `sub_agents` on every iteration. This is crucial, as it allows agents to read the output of the previous iteration and write a refined result back to the same state key.

### The Critic -> Refiner Pattern

The most common and powerful pattern for a `LoopAgent` is the **Critic -> Refiner** loop:

1.  **Critic Agent:** Evaluates the current state of the work (e.g., an essay draft) against a set of criteria. It then outputs its feedback.
2.  **Refiner Agent:** Reads the original work and the critic's feedback. It then applies the feedback to create an improved version of the work, overwriting the previous version in the state.
3.  **Repeat:** The loop continues, with the Critic evaluating the newly refined work in the next iteration.

This creates a self-improving system where the quality of the output gets progressively better with each loop.

### Terminating a Loop

An infinite loop is a bug. Every `LoopAgent` MUST have a way to stop.

1.  **`max_iterations` (Safety Net):**
    This is a required safeguard. You must specify the maximum number of times the loop can run.
    ```python
    loop = LoopAgent(
        sub_agents=[critic, refiner],
        max_iterations=5  # Stops after 5 iterations MAX
    )
    ```

2.  **Smart Termination (Exit Tool):**
    For intelligent control, you can create a tool that signals the loop to stop.
    *   The **Critic** agent can be instructed to output a specific phrase (e.g., "APPROVED") when the work is complete.
    *   The **Refiner** agent can be instructed to call an `exit_loop` tool when it sees this approval phrase.
    *   The `exit_loop` tool uses `tool_context.actions.escalate = True` to tell the `LoopAgent` to terminate immediately. This is the official v1.0 pattern for "breaking" out of a loop from within a tool call.
    > **Note on Tool Output:** Even when a tool signals the end of an agent's execution (e.g., via `tool_context.actions.escalate = True`), it must still return a valid, albeit minimal, dictionary output (e.g., `{"text": "Loop exited successfully."}`). This ensures the backend always produces a valid `LlmResponse` and completes the request's lifecycle gracefully.

Using both `max_iterations` and an exit tool is the best practice for creating robust and efficient loops.

### Key Takeaways
- The `LoopAgent` is a workflow agent for tasks that require iterative refinement.
- It repeatedly executes its sub-agents until a termination condition is met.
- The "Critic -> Refiner" pattern is a common and powerful way to structure a `LoopAgent` for self-improving tasks.
- **Explicit Escalation:** Using `tool_context.actions.escalate = True` within a tool is the most robust way to exit a loop based on logic (e.g., quality check passed) rather than just reaching a count.
- All `LoopAgent`s must have a termination condition, which should include a `max_iterations` safety net and, ideally, a smart termination mechanism using an exit tool.
