---
sidebar_position: 2
title: "Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 38: Building a Production-Ready Agent with ADK 2.0

## Goal

In this lab, you will build a **Best Practices Agent** that demonstrates several production-ready patterns: Input Validation, Framework-Level Retries, and Caching.

### Step 1: Create the Project Structure

1.  **Create a new project:**

    <Setup/>

    ```shell
    uv run adk create best_practices_v2
    ```
    This prompts for a model choice (any option is fine, you'll set the real model in `agent.py` below) and, if needed, a backend -- there's no separate "type" prompt, `agent.py`/Code is already the default.

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

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="38">

# Lab 38 Solution: Building a Production-Ready Agent (ADK 2.0)

## Goal

This file contains the complete code for the `agent.py` script in the Best Practices lab, utilizing the ADK 2.0 Workflow Runtime and native resilience features.

### `best_practices_v2/agent.py`

```python
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
    user_id: constr(pattern=r'^[a-zA-Z0-9_-]{3,50}$')
    query: str = Field(..., max_length=1000)

@node
def validate_input_node(node_input: str):
    """Validates inputs using a Pydantic model.

    The Workflow Runner always delivers the entry node's input as the raw
    user message coerced to `str` (never as a `dict`), so we parse it as
    JSON here first. A malformed JSON payload, or one that fails the
    ValidatedInput schema, raises — the workflow engine catches this and
    stops execution (Fail-Closed).
    """
    try:
        payload = json.loads(node_input)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Malformed input: expected a JSON object, got: {node_input!r}"
        ) from e
    # Instantiating the model will raise a ValidationError if inputs are invalid.
    # The workflow engine will catch this and stop execution (Fail-Closed).
    ValidatedInput(**payload)
    return "Input is valid!"

# --- 2. Resilience with Framework-Level Retries ---

@node(retry_config=RetryConfig(max_attempts=4))
async def flaky_api_node(node_input: str):
    """Simulates an API call that might fail."""
    print("Attempting to call the flaky API...")
    if random.random() > 0.33: # 67% chance of failure
        print("API call failed! Raising exception for framework retry...")
        # We propagate the exception. We DO NOT catch it here.
        raise ConnectionError("The external API is temporarily unavailable.")
    
    print("API call succeeded!")
    return "Data retrieved successfully."

# --- 3. Performance with Caching ---

@functools.lru_cache(maxsize=128)
def _slow_query(item_id: str):
    """A standard Python function with local caching."""
    print(f"Performing slow query for: {item_id}...")
    time.sleep(2) # Simulate I/O latency
    return f"Result for {item_id}"

@node
def cache_node(node_input: str):
    # This node leverages the local memory cache
    result = _slow_query(node_input)
    return f"Cached Result: {result}"

# --- 4. The Orchestrator Workflow ---

# We assemble the components into a deterministic Graph.
root_agent = Workflow(
    name="BestPracticesSystem",
    edges=[
        # Sequence: Start -> Validate -> Flaky Call -> Caching
        ("START", validate_input_node),
        (validate_input_node, flaky_api_node),
        (flaky_api_node, cache_node)
    ],
    # NOTE: retry_config is set on `flaky_api_node` itself (above), not here.
    # `Workflow` extends the same `BaseNode` as every `@node`, so it accepts
    # `retry_config` too — but that only governs retries of the Workflow
    # *as a node* (relevant if this Workflow were nested inside a parent
    # graph). It does NOT cascade to the nodes inside its own graph: a node
    # that raises still fails after exactly one attempt unless that specific
    # node has its own `retry_config`.
)
```

### Key Takeaways Explained

1.  **Fail-Closed Security:** By using Pydantic schemas, we ensure that malformed or malicious data is blocked at the very first node. The workflow doesn't even attempt to call the LLM or external APIs if the input doesn't match the contract.
2.  **Native Resilience:** ADK 2.0's `RetryConfig` allows us to separate business logic from error handling. Your nodes stay "clean" (no messy loops or `try/except` boilerplate), while the framework ensures reliability.
3.  **Local Caching:** `lru_cache` is a simple, effective way to speed up repeated queries within the same process. For multi-instance production environments, you would replace this with a distributed cache like Redis.
4.  **Deterministic Routing:** Using a `Workflow` graph instead of a general `Agent` for this pipeline saves costs and reduces latency because we don't need an LLM to decide what the next step is.

### Self-Reflection Answers

1.  **Why is it better to let the framework handle retries rather than writing manual loops in your tool functions?**
    *   **Answer:** Centralized retry logic ensures consistent behavior across all tools, simplifies debugging (via framework traces), and allows for global configuration (e.g., changing the backoff strategy for the entire application in one place).
2.  **What happens if you catch the exception inside `flaky_api_node` with a `try/except` block and return an error string? Does the framework still retry?**
    *   **Answer:** No. The framework only retries if it "sees" the exception. If you catch it and return a string (even an error message), the framework considers the node execution "Successful" and proceeds to the next step.
3.  **In a production environment (like Cloud Run), why is `lru_cache` only a partial solution for performance?**
    *   **Answer:** Cloud Run is serverless and horizontal-scaling. Each instance has its own local memory. If User A hits Instance 1, the result is cached there. If User A's next request hits Instance 2, that cache is empty. For a truly production-grade system, a distributed cache (like Memorystore for Redis) is required.

</SolutionVault>
