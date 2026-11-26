---
sidebar_position: 38
title: "Module 38: Best Practices & Production Patterns (ADK 2.0)"
pagination_label: "Module 38: Production Best Practices & Patterns — 📖 Theory & Overview"
---

# Module 38: Best Practices & Production Patterns

![Production Agent Engineering Best Practices Banner (Light)](img/hero-light.webp#gh-light-mode-only)
![Production Agent Engineering Best Practices Banner (Dark)](img/hero-dark.webp#gh-dark-mode-only)

## Theory

### From Prototype to Production

Building a working agent is the first step. Building a **production-ready** agent requires a focus on architecture, performance, security, and reliability. This module summarizes the essential best practices for taking your agent from a prototype to a robust, scalable, and maintainable application, aligned with the **ADK 2.0 Workflow Runtime**.

![Production Reliability & Defense-in-Depth Matrix (Light)](img/defense-in-depth-matrix-light.webp#gh-light-mode-only)
![Production Reliability & Defense-in-Depth Matrix (Dark)](img/defense-in-depth-matrix-dark.webp#gh-dark-mode-only)
*Figure: Defense-in-depth architecture covering input validation, execution resilience, state integrity, and observability.*

### 1. Architectural Best Practices: Thinking in Graphs

In ADK 2.0, every component is a **Node** in a **Workflow Graph**. Choosing the right structure is your most critical design decision.

| Pattern | When to use it | Key Characteristics |
| :--- | :--- | :--- |
| **`Agent`** | Natural language reasoning and dynamic tool calling. | Non-deterministic, flexible. Best for high-level decision making. |
| **`Workflow` (Static)** | Fixed, predictable pipelines (Sequential/Parallel). | Deterministic. Reduced latency and cost by avoiding LLM routing where logic is known. |
| **`@node` (Dynamic)** | Complex, code-based orchestration (Loops, If/Else). | Maximum control. Allows arbitrary Python logic between agent executions. |

*   **Small, Focused Tools:** Design your tools to follow the single-responsibility principle. A tool should do one thing well.
*   **Progressive Disclosure with Skills:** Don't overload an agent with 50 tools. Group related domain workflows and instructions into **Skills** (`SkillToolset`, covered in depth in **Module 39.5**) and only activate them on demand when needed.
*   **Deterministic Routing:** If you *know* that Step B always follows Step A, don't ask an LLM to decide. Use a `Workflow` or a Dynamic `@node`.

### 2. Resilience: Framework-Level Error Handling

ADK 2.0 changes the way we handle failures. Instead of writing complex `try...except` logic inside every tool, we now leverage the **Workflow Runtime**.

#### The "Let it Fail" Pattern
In ADK 1.x, you were taught to catch all exceptions in tools. In ADK 2.0, you should **allow standard exceptions to propagate** out of your tools and workflow nodes.

**Why?**
1.  **Automatic Retries:** If a node or tool fails with an exception, the ADK framework can automatically retry the execution based on a `RetryConfig`.
2.  **Human-in-the-Loop (HITL) Interrupts:** When a workflow pauses for human input, ADK unwinds the node stack using `NodeInterruptedError`. In ADK 2.14, `NodeInterruptedError` inherits directly from Python's `BaseException` (rather than `Exception`) specifically so normal `except Exception:` blocks won't accidentally catch it—however, **never** write a bare `except:` or `except BaseException:` without re-raising, as swallowing `NodeInterruptedError` silently breaks workflow pause and resume!

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

*   **Model Selection Hierarchy:** Use `gemini-3.8-flash` for routing, classification, and simple tool calling. Save `gemini-3.1-pro-preview` for complex multi-step reasoning.
*   **Caching with `before_agent_callback` or Keyed Node Caches:** Implement a caching layer keyed on the normalized user query to skip redundant LLM or backend calls when an identical request was recently processed.
*   **Async Everything:** Always use `async` tool and node definitions to prevent blocking the event loop during I/O-bound tasks (API calls, DB queries).

### 4. Security & Safety

*   **Fail-Closed Validation:** Use Pydantic schemas for input and output contracts. If validation fails, the entry node raises immediately, preventing prompt injection or malformed data from propagating downstream.
*   **Secrets Management:** Use Google Secret Manager or `.env` files. **Never** log sensitive data or return it in an agent response.
*   **HITL for Side Effects:** Any action that performs a destructive or irreversible side effect (deleting data, executing a financial transfer) **must** pause for human approval using the right primitive for your layer:
    *   **Agent Tools (`FunctionTool`):** Wrap standard Python tool functions with `FunctionTool(my_fn, require_confirmation=True)` (Module 13) so ADK automatically emits a confirmation `RequestInput` event before executing the tool.
    *   **Workflow Nodes (`@node`):** Inside a generator `@node` function, explicitly `yield RequestInput(...)` (from `google.adk.events`) to pause the workflow graph until the user supplies confirmation or structured input.

### Key Takeaways
- **Think in Nodes:** Break logic into discrete, testable nodes orchestrated by a Workflow, and pass validated domain payloads cleanly from node to node.
- **Framework Resilience:** Propagate exceptions to enable ADK 2.0 automatic retries, and never swallow `BaseException` / `NodeInterruptedError`.
- **Model Efficiency:** Match the model capability to the task complexity, and use Skills (Module 39.5) for progressive context disclosure.
- **Strict Schemas & HITL:** Use Pydantic to enforce "fail-closed" security at node boundaries and `FunctionTool(..., require_confirmation=True)` or `@node` `yield RequestInput(...)` for destructive side effects.
