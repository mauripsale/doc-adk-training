---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 38: Building a Production-Ready Agent with ADK 2.0

## Goal

In this lab, you will build a **Best Practices Agent** that demonstrates several production-ready patterns: Input Validation, Framework-Level Retries, and Caching.

### Step 1: Create the Project Structure

1.  **Create a new project:**
    ```shell
    uv run adk create best_practices_v2
    ```
    When prompted to choose a type for the root agent, choose **2. Code**.

2.  **Navigate into the new directory:**
    ```shell
    cd best_practices_v2
    ```

3.  **Ensure ADK 2.0 is installed:**
    ```shell
    uv pip install -U "google-adk>=2.1.0"
    ```

### Step 2: Implement the Production-Ready Nodes

**Exercise:** Open `agent.py`. Your task is to apply the best practices of validation, framework-level resilience, and caching using the `# TODO` comments as a guide.

```python
# In agent.py (Starter Code)
import json
import time
import random
import functools
from pydantic import BaseModel, Field, constr

from google.adk import Agent, Workflow, Context, Event
from google.adk.workflow import node, RetryConfig

# --- 1. Input Validation with Pydantic (Fail-Closed) ---

class ValidatedInput(BaseModel):
    """A Pydantic model to validate inputs for a tool."""
    # TODO: Define user_id as a string with regex for alphanumeric and 3-50 chars.
    # Define query as a string with max_length 1000.
    pass

# IMPORTANT: the Workflow Runner always delivers the entry node's input as
# the raw user message coerced to `str` — never as a `dict`. Annotating this
# node's parameter as `dict` will crash with a Pydantic ValidationError on
# EVERY invocation (not just malformed ones), because a `types.Content`/`str`
# is never a valid `dict`. Accept `str`, and parse it as JSON yourself.
@node
def validate_input_node(node_input: str):
    """Validates inputs using a Pydantic model."""
    # TODO 1: Parse node_input as JSON (json.loads). Wrap it in a try/except
    #   json.JSONDecodeError and re-raise as a ValueError with a clear
    #   "malformed input" message — this is what makes a bad/non-JSON chat
    #   message fail gracefully instead of an unhandled crash.
    # TODO 2: Instantiate ValidatedInput(**payload).
    # If either step fails, an exception propagates and the workflow stops
    # (Fail-Closed).
    return "Input is valid!"

# --- 2. Resilience with Framework-Level Retries ---

@node
async def flaky_api_node(node_input: str):
    """Simulates an API call that might fail."""
    print("Attempting to call the flaky API...")
    if random.random() > 0.33: # 67% chance of failure
        print("API call failed! Raising exception for framework retry...")
        # TODO: Raise a ConnectionError. DO NOT catch it here!
        pass
    print("API call succeeded!")
    return "Data retrieved successfully."

# --- 3. Performance with Caching ---

@functools.lru_cache(maxsize=128)
def _slow_query(item_id: str):
    print(f"Performing slow query for: {item_id}...")
    time.sleep(2)
    return f"Result for {item_id}"

@node
def cache_node(node_input: str):
    # TODO: Call the cached _slow_query and return the result.
    pass

# --- 4. The Orchestrator Workflow ---

# TODO: Define a Workflow that includes:
# 1. A 'validate' step.
# 2. A 'flaky_call' step configured with a RetryConfig(max_attempts=4).
#    IMPORTANT: put `retry_config=RetryConfig(max_attempts=4)` directly on
#    `flaky_api_node`'s `@node(...)` decorator, NOT on the `Workflow(...)`
#    container. `Workflow` accepts `retry_config` too (it's a `BaseNode`
#    field like any other node), but that only retries the Workflow *as a
#    node* if it's nested inside a parent graph — it does NOT cascade to the
#    nodes inside its own graph. A failing node without its own
#    `retry_config` still fails after exactly one attempt.
# 3. A 'caching' step.

root_agent = Workflow(
    name="BestPracticesSystem",
    edges=[
        # ("START", validate_input_node, ...),
    ]
)
```

### Step 3: Run and Test the Agent

1.  **Start the Dev UI:**
    ```shell
    uv run adk web .
    ```
2.  **Interact and Observe:**
    *   **Test Caching:** Run the 'caching' step twice. Notice the 2-second delay the first time, and the instant response the second time.
    *   **Test Validation:** Since the whole pipeline starts at `validate_input_node`, send your chat message as a JSON object matching the `ValidatedInput` schema, e.g. `{"user_id": "student_01", "query": "hello"}`. That should sail through to the rest of the pipeline. Now try two kinds of "malformed input" and confirm the Workflow fails immediately (Fail-Closed) both times:
        1.  Non-JSON text (e.g. just typing `hello`) — rejected by the `json.loads` parse step.
        2.  Valid JSON that violates the schema (e.g. `{"user_id": "a", "query": "hello"}` — `user_id` is too short for the regex) — rejected by `ValidatedInput`'s own Pydantic validation.
    *   **Test Retries:** Run the 'flaky_call' step. Watch your terminal logs. You should see "Attempting..." multiple times as the **ADK Framework** automatically retries the node after the exception.

### Lab Summary
You have successfully built an agent system that leverages the native resilience of ADK 2.0. You have learned:
*   How to use `Pydantic` for "Fail-Closed" security.
*   How to use **Framework Retries** by propagating exceptions instead of catching them.
*   How to use `lru_cache` for local performance gains.

### Step 4: Bonus Challenge - Prompt Optimization

Refactor a previous lab's agent (e.g., the `researcher_agent` from Module 8) to optimize its token usage.
1.  **Analyze:** Run the agent and check the token counts in the Dev UI or logs.
2.  **Optimize:** Rewrite the instructions using the techniques learned in the Best Practices theory (e.g., more concise constraints, removing redundant examples).
3.  **Validate:** Re-run the same prompt and compare the token usage. Did you manage to reduce cost without losing quality?

### Self-Reflection Questions
- Why is it better to let the framework handle retries rather than writing manual loops in your tool functions?
- What happens if you catch the exception inside `flaky_api_node` with a `try/except` block and return an error string? Does the framework still retry?
- In a production environment (like Cloud Run), why is `lru_cache` only a partial solution for performance?

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMzgtYmVzdC1wcmFjdGljZXMvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module38-best-practices/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
