# Module 13: Advanced Orchestration: Loop Agents

## Theory

### Handling Repetitive Tasks

Some processes aren't just a single sequence; they require repetition. Imagine an agent that needs to:
*   Poll a service until a job is complete.
*   Iteratively refine a piece of code until it passes a series of tests.
*   Play a game of tic-tac-toe, taking turns until there's a winner.

These are all examples of looping behavior. While you could try to prompt an `LlmAgent` to repeat a task, it's not a reliable method. For robust, predictable looping, the ADK provides the `LoopAgent`.

### The `LoopAgent`

The `LoopAgent` is the third type of workflow agent. Its purpose is to execute its list of `sub_agents` sequentially, over and over again, until a specific condition is met to stop the loop.

This allows you to build powerful patterns for iteration, refinement, and polling.

**Key Concepts:**
*   **Execution Order:** Within a single iteration, the `sub_agents` are executed sequentially, just like in a `SequentialAgent`.
*   **Shared State:** The `LoopAgent` passes the same session state to its sub-agents on every iteration. This is crucial, as it allows the agents inside the loop to modify the state (e.g., update a counter, refine a piece of text) and have that change be visible in the next iteration.

### Terminating a Loop

A loop that never ends isn't very useful. The `LoopAgent` has two primary mechanisms for termination:

#### 1. **`max_iterations`**
This is the simplest way to stop a loop. You can specify a maximum number of times the loop should run. This is a safety measure to prevent infinite loops.

```yaml
agent_class: LoopAgent
name: my_five_step_loop
max_iterations: 5
sub_agents:
  - config_path: do_something.yaml
```

#### 2. **Escalation**
This is the more dynamic and powerful way to control a loop. The loop will stop if any of its `sub_agents` (or a tool used by a sub-agent) signals to **"escalate."**

"Escalation" is a signal that a sub-agent sends up to its parent. For a `LoopAgent`, this signal is interpreted as "stop the loop."

How does an agent escalate?
*   **From a Custom Tool:** A tool can access the `tool_context.actions` and set `escalate=True`.
*   **From a Custom Agent:** A custom-coded agent (inheriting from `BaseAgent`) can create and yield an `Event` with the `escalate` flag set in its `EventActions`.

This allows you to create a "checker" or "validator" agent inside your loop. The loop might consist of:
1.  A "worker" agent that performs a task and updates the state.
2.  A "checker" agent that inspects the state and decides if the task is complete. If it is, the checker agent escalates, and the loop terminates.

This pattern of a worker and a checker inside a `LoopAgent` is extremely common for building iterative refinement and polling workflows.

In the lab for this module, you will build an agent that tries to guess a number, using a `LoopAgent` to continue guessing until it gets the right answer.
