---
sidebar_position: 1
title: "Module 18: Parallel Processing with ParallelAgent"
---

# Module 18: Parallel Processing with ParallelAgent

## Theory

### `ParallelAgent`: Concurrent Execution

The `ParallelAgent` is a workflow agent that executes all of its `sub_agents` at the same time (concurrently). This is a powerful pattern for improving performance when your workflow involves multiple independent tasks that can be performed simultaneously.

**Key Concepts:**
*   **Execution Order:** Not guaranteed. The agents run in parallel, and their execution may interleave. The `ParallelAgent` completes only when its *slowest* sub-agent has finished.
*   **Shared State:** All sub-agents in a `ParallelAgent` share the same session state. They can all read the initial state, and they can all write their results back to the state.
*   **Avoiding Conflicts:** When using a `ParallelAgent`, it's crucial to ensure that the sub-agents write their results to *different* keys in the state to avoid race conditions (where one agent's result overwrites another's).

**When to Use `ParallelAgent`:**
*   When tasks are independent and can run in any order.
*   When you need to gather data from multiple sources concurrently to save time.
*   When tasks do not need each other's outputs to run.

### The Fan-Out/Gather Pattern

A common and highly effective architecture is the **fan-out/gather** pattern, which combines the strengths of both parallel and sequential agents:

1.  **Fan-Out (`ParallelAgent`):** A `ParallelAgent` runs multiple data-gathering agents concurrently. Each agent is responsible for a specific, independent task (e.g., searching for flights, hotels, and activities).
2.  **Gather (`SequentialAgent`):** A final `LlmAgent` runs *after* the `ParallelAgent` has completed. Its job is to read all the results from the session state and synthesize them into a single, coherent response.

This gives you both **speed** (from parallel data gathering) and **synthesis** (from a final merging step).

```
        ┌──── Agent 1 (flights) ────┐
User ───┼──── Agent 2 (hotels) ─────┼──→ Merger Agent → Final Result
        └──── Agent 3 (activities) ─┘

      ParallelAgent (fast!)       SequentialAgent (combine)
```

### Key Takeaways
- The `ParallelAgent` is a workflow agent that executes its sub-agents concurrently, improving performance for independent tasks.
- **Performance Note:** The total execution time of a `ParallelAgent` is limited by the slowest of its sub-agents, including the latency of LLM calls and tool executions. This makes `ParallelAgent` particularly advantageous for workflows involving multiple, potentially slow LLM/Tool interactions, as they run simultaneously rather than sequentially.
- **Structured Parallel Data:** Just like in sequential workflows, using `output_schema` ensures that the gathering agents return clean JSON objects to the shared state, making it much easier for the final synthesis agent to process the combined data.
- It's crucial to use different `output_key`s for each sub-agent in a `ParallelAgent` to avoid overwriting data in the shared state.
- The "fan-out/gather" pattern, which combines a `ParallelAgent` for data collection and a `SequentialAgent` for synthesis, is a powerful architecture for building efficient, complex agents.
