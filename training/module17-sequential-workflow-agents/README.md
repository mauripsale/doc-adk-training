---
sidebar_position: 1
title: "Module 17: Sequential Workflows - Building Agent Pipelines"
---

# Module 17: Sequential Workflows - Building Agent Pipelines

## Theory

### Beyond a Single Agent

Complex problems often require multiple steps or areas of expertise. Instead of creating one massive, monolithic agent, the ADK allows you to build **multi-agent systems** where several specialized agents collaborate.

For processes that follow a fixed, predictable sequence, the ADK provides the `SequentialAgent`.

### `SequentialAgent`: Building Pipelines

The `SequentialAgent` is a **Workflow Agent**, meaning it is not powered by an LLM. It is a deterministic controller that executes its `sub_agents` one after another, in the exact order they are defined. It's the foundation for creating multi-step pipelines where the output of one step becomes the input for the next.

**Key Concepts:**
*   **Execution Order:** Guaranteed to be top-to-bottom.
*   **Shared State:** The `SequentialAgent` passes the *same* session state to each sub-agent. This is how you pass data between steps.
*   **Data Flow with `output_key`:** An agent can define an `output_key` in its configuration. When it finishes, the ADK automatically saves its response (which can be a structured object if `output_schema` is used) to `state['your_key']`. The next agent in the sequence can then read this value by using `{your_key}` in its instruction prompt.

**When to Use `SequentialAgent`:**
*   When tasks MUST happen in a specific order.
*   When each step depends on the previous step's output.
*   When you need predictable, deterministic execution.
*   For building pipelines (e.g., ETL, content creation, review processes).

### Key Takeaways
- The `SequentialAgent` is a deterministic workflow agent that executes sub-agents in a fixed order.
- It is ideal for building multi-step pipelines where each step depends on the previous one.
- Data is passed between agents in the sequence using the shared session state.
- **Structured Output Passing:** By combining `output_schema` (Pydantic models) with `output_key`, you pass robust JSON objects between agents instead of fragile strings, avoiding manual parsing.
- An agent's `output_key` is used to save its result to the state, and the next agent can read it using `{key}` syntax in its prompt.
- **Advanced Level - Code Organization:** For larger Python-based multi-agent systems, it's a best practice to define your specialist sub-agents in separate Python modules (e.g., `specialists.py`) and then import them into your main `agent.py` file. This improves modularity and keeps your main pipeline definition clean.
