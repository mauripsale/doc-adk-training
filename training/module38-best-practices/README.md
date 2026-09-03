---
sidebar_position: 38
title: "Module 38: Best Practices & Production Patterns (ADK 2.0)"
---

# Module 38: Best Practices & Production Patterns

## Theory

### From Prototype to Production

Building a working agent is the first step. Building a **production-ready** agent requires a focus on architecture, performance, security, and reliability. This module summarizes the essential best practices for taking your agent from a prototype to a robust, scalable, and maintainable application, aligned with the **ADK 2.0 Workflow Runtime**.

### 1. Architectural Best Practices: Thinking in Graphs

In ADK 2.0, every component is a **Node** in a **Workflow Graph**. Choosing the right structure is your most critical design decision.

| Pattern | When to use it | Key Characteristics |
| :--- | :--- | :--- |
| **`Agent`** | Natural language reasoning and dynamic tool calling. | Non-deterministic, flexible. Best for high-level decision making. |
| **`Workflow` (Static) ** | Fixed, predictable pipelines (Sequential/Parallel). | Deterministic. Reduced latency and cost by avoiding LLM routing where logic is known. |
| **`@node` (Dynamic)** | Complex, code-based orchestration (Loops, If/Else). | Maximum control. Allows arbitrary Python logic between agent executions. |

*   **Small, Focused Tools:** Design your tools to follow the single-responsibility principle. A tool should do one thing well.
*   **Progressive Disclosure with Skills:** Don't overload an agent with 50 tools. Group related tools into **Skills** and only activate them when needed.
*   **Deterministic Routing:** If you *know* that Step B always follows Step A, don't ask an LLM to decide. Use a `Workflow` or a Dynamic `@node`.

### 2. Resilience: Framework-Level Error Handling

ADK 2.0 changes the way we handle failures. Instead of writing complex `try...except` logic inside every tool, we now leverage the **Workflow Runtime**.

#### The "Let it Fail" Pattern
In ADK 1.x, you were taught to catch all exceptions in tools. In ADK 2.0, you should **allow standard exceptions to propagate** out of your tools. 

**Why?**
1.  **Automatic Retries:** If a tool fails with an exception, the ADK framework can automatically retry the execution based on a `RetryConfig`.
2.  **Human-in-the-Loop (HITL):** Broad `except Exception:` blocks can accidentally trap `NodeInterruptedError`, which the framework uses to pause workflows for user input.

#### Configuring Retries
You configure retry logic per-node, on the node itself (either as a constructor argument like `Agent(..., retry_config=...)`, or via `@node(retry_config=...)` for function nodes):

```python
from google.adk.workflow import RetryConfig

# Framework handles retries for you!
my_agent_node = Agent(
    ...,
    retry_config=RetryConfig(max_attempts=3, initial_delay=2.0)
)
```

**Important:** `retry_config` does not cascade from a container to the nodes inside it. Setting `retry_config` on a `Workflow(...)` only governs retries of that `Workflow` *as a node* (relevant if it's nested inside a parent graph) — it has no effect on the nodes in its own `edges`. If you want a specific node inside a `Workflow` to retry, put `retry_config` directly on that node.

### 3. Performance Optimization

*   **Model Selection Hierarchy:** Use `gemini-3.5-flash` for routing, classification, and simple tool calling. Save `gemini-3.1-pro-preview` for complex multi-step reasoning.
*   **Caching with `before_agent_callback`:** Implement a caching layer to skip LLM calls entirely if a similar request was recently processed.
*   **Async Everything:** Always use `async` tool definitions to prevent blocking the event loop during I/O-bound tasks (API calls, DB queries).

### 4. Security & Safety

*   **Fail-Closed Validation:** Use Pydantic schemas for both `input_schema` and `output_schema`. If validation fails, the node fails immediately (preventing prompt injection or malformed data from propagating).
*   **Secrets Management:** Use Google Secret Manager or `.env` files. **Never** log sensitive data or return it in an agent response.
*   **HITL for Side Effects:** Any tool that performs a destructive action (deleting data, making a payment) **must** yield a `RequestInput` for human confirmation.

### Key Takeaways
- **Think in Nodes:** Break logic into discrete, testable nodes orchestrated by a Workflow.
- **Framework Resilience:** Propagate exceptions to enable ADK 2.0 automatic retries and HITL.
- **Model Efficiency:** Match the model capability to the task complexity.
- **Strict Schemas:** Use Pydantic to enforce "fail-closed" security at every node boundary.
