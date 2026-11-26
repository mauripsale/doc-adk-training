---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 38: Production Best Practices & Patterns — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 38: Building a Production-Ready Agent with ADK 2.0

## Goal

In this lab, you will build a **Best Practices Agent** that demonstrates several production-ready patterns: Fail-Closed Input Validation, Framework-Level Retries, and Per-Query Caching.

### Step 1: Create the Project Structure

1.  **Create a new project:**

    <Setup/>

    ```shell
    uv run adk create best_practices_v2
    ```
    This prompts for a model choice (any option is fine, you'll write `agent.py` below) and, if needed, a backend -- `agent.py`/Code is already the default.

2.  **Navigate into the new directory:**
    ```shell
    cd best_practices_v2
    ```

3.  **Ensure ADK 2.14+ is installed:**
    ```shell
    uv add "google-adk>=2.14.0"
    ```

### Step 2: Implement the Production-Ready Nodes

**Exercise:** Open `best_practices_v2/agent.py`. Your task is to apply the best practices of fail-closed validation, framework-level resilience, and per-query caching using the `# TODO` comments as a guide. Pay close attention to **data threading**: `validate_input_node` and `flaky_api_node` must forward the validated `query` string (received via each `@node`'s `node_input: str` pass-through parameter) so `cache_node` keys `_slow_query(query)` on the actual user query rather than on a constant status message!

```python
# In best_practices_v2/agent.py (Starter Code)
import json
import time
import random
import functools
from pydantic import BaseModel, Field, constr

from google.adk import Workflow
from google.adk.workflow import node, RetryConfig

# --- 1. Input Validation with Pydantic (Fail-Closed) ---

class ValidatedInput(BaseModel):
    """A Pydantic model to validate incoming user payloads."""
    # TODO: Define user_id as a string with regex pattern r"^[a-zA-Z0-9_-]{3,50}$".
    # Define query as a non-empty string with min_length=1 and max_length=1000.
    pass

# IMPORTANT: the Workflow Runner always delivers the entry node's input as
# the raw user message coerced to `str` — never as a `dict`. Also note that
# in ADK 2.14's default `@node` binding mode, the parameter named literally
# `node_input` receives the upstream node's return value directly (whereas
# differently named parameters are looked up in `ctx.state`).
@node
def validate_input_node(node_input: str) -> str:
    """Validates inputs using a Pydantic model and returns the validated query."""
    # TODO 1: Parse node_input as JSON (json.loads). Wrap it in a try/except
    #   json.JSONDecodeError and re-raise as a ValueError with a clear
    #   "Malformed input" message (also check isinstance(payload, dict)).
    # TODO 2: Instantiate `validated = ValidatedInput(**payload)`.
    #   If either step fails, an exception propagates and the workflow stops
    #   immediately (Fail-Closed).
    # TODO 3: Return `validated.query` so downstream nodes receive the actual
    #   user query string via `node_input`!
    pass

# --- 2. Resilience with Framework-Level Retries ---

# TODO: Add retry_config=RetryConfig(max_attempts=4) directly to @node(...)!
@node
async def flaky_api_node(node_input: str) -> str:
    """Simulates an API call that might fail transiently."""
    query = node_input
    print(f"Attempting to call the flaky API for query={query!r}...")
    if random.random() > 0.33:  # 67% chance of failure
        print("API call failed! Raising exception for framework retry...")
        # TODO: Raise a ConnectionError. DO NOT catch it here (and never use bare `except:`)!
        pass
    print("API call succeeded!")
    # TODO: Return `query` so `cache_node` receives the validated user query
    # (do NOT return a constant string, or every query will hit the same cache key!).
    pass

# --- 3. Performance with Query-Keyed Caching ---

@functools.lru_cache(maxsize=128)
def _slow_query(query: str) -> str:
    print(f"Performing slow backend query for: {query!r}...")
    time.sleep(2)
    return f"Verified results for '{query}'"

@node
def cache_node(node_input: str) -> str:
    # TODO: Pass `query = node_input` into `_slow_query(query)` and return
    # f"Cached Result: {result}".
    pass

# --- 4. The Orchestrator Workflow ---

# TODO: Define a Workflow wiring:
#   ("START", validate_input_node) -> (validate_input_node, flaky_api_node) -> (flaky_api_node, cache_node)
# IMPORTANT: put `retry_config=RetryConfig(max_attempts=4)` directly on
# `flaky_api_node`'s `@node(...)` decorator above, NOT on the `Workflow(...)`
# container (`Workflow.retry_config` does NOT cascade to child nodes).

root_agent = Workflow(
    name="BestPracticesSystem",
    edges=[
        # ("START", validate_input_node), ...
    ]
)
```

### Step 3: Run and Test the Agent

1.  **Navigate to the parent directory and start the Dev UI:**
    ```shell
    cd ..
    uv run adk web
    ```
    Select `best_practices_v2` in the Dev UI dropdown.
2.  **Interact and Observe:**
    *   **Test Validation (Fail-Closed):** Send a valid JSON payload matching `ValidatedInput`, such as `{"user_id": "student_01", "query": "laptops"}`. It should pass validation and proceed through the pipeline. Now test two malformed inputs and verify the Workflow halts immediately both times:
        1.  Non-JSON text (e.g., `hello`) — rejected by your `json.loads` check with a clear `ValueError`.
        2.  Schema-invalid JSON (e.g., `{"user_id": "a", "query": "laptops"}` where `user_id` is under 3 characters) — rejected by Pydantic's `ValidationError`.
    *   **Test Retries:** Watch your terminal logs when sending a valid JSON message. Whenever the 67% simulated failure triggers, you will see `"Attempting to call the flaky API..."` multiple times as the **ADK Workflow Runtime** automatically retries `flaky_api_node`.
    *   **Test Per-Query Caching:**
        1.  Send `{"user_id": "student_01", "query": "laptops"}` once — notice `"Performing slow backend query for: 'laptops'..."` and the 2-second delay.
        2.  Send the **same** `{"user_id": "student_01", "query": "laptops"}` again — once `flaky_api_node` succeeds, `cache_node` returns **instantly** without printing `"Performing slow backend query..."`!
        3.  Now send a **different** query, `{"user_id": "student_01", "query": "headphones"}` — notice it triggers a fresh 2-second lookup because `_slow_query` is properly keyed on `query`.

### Lab Summary
You have successfully built an agent system that leverages the native resilience of ADK 2.0. You have learned:
*   How to use `Pydantic` for "Fail-Closed" security and thread validated fields cleanly across `@node` edges.
*   How to use **Framework Retries** by propagating exceptions instead of catching them.
*   How to use `lru_cache` keyed on the actual user query for local performance gains.

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

from google.adk import Workflow
from google.adk.workflow import node, RetryConfig

# --- 1. Input Validation with Pydantic (Fail-Closed) ---


class ValidatedInput(BaseModel):
    """A Pydantic model to validate incoming user payloads."""
    user_id: constr(pattern=r"^[a-zA-Z0-9_-]{3,50}$")
    query: str = Field(..., min_length=1, max_length=1000)


@node
def validate_input_node(node_input: str) -> str:
    """Validates inputs using a Pydantic model and forwards the validated query.

    The Workflow Runner always delivers the entry node's input as the raw
    user message coerced to `str` (never as a `dict`), so we parse it as
    JSON here first. A malformed JSON payload, or one that fails the
    ValidatedInput schema, raises — the workflow engine catches this and
    stops execution (Fail-Closed). Returning `validated.query` threads the
    actual user query through `node_input` along the downstream edges so
    caching is keyed per query rather than on a constant status string.
    """
    try:
        payload = json.loads(node_input)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Malformed input: expected a JSON object, got: {node_input!r}"
        ) from e
    if not isinstance(payload, dict):
        raise ValueError(
            f"Malformed input: expected a JSON object mapping, got: {type(payload).__name__}"
        )
    # Instantiating the model raises a ValidationError if inputs are invalid.
    validated = ValidatedInput(**payload)
    return validated.query


# --- 2. Resilience with Framework-Level Retries ---


# NOTE on @node parameter binding in ADK 2.14: in default binding mode, the
# parameter named literally `node_input` receives the upstream node's return
# value (`validated.query`) directly, whereas any other parameter name would
# be looked up in `ctx.state`. Keep `node_input: str` here to receive the
# validated query string cleanly!
@node(retry_config=RetryConfig(max_attempts=4))
async def flaky_api_node(node_input: str) -> str:
    """Simulates an upstream API pre-check that might fail transiently."""
    query = node_input
    print(f"Attempting to call the flaky API for query={query!r}...")
    if random.random() > 0.33:  # 67% chance of transient failure
        print("API call failed! Raising exception for framework retry...")
        # Propagate standard exceptions — NEVER catch them here or use bare `except:`.
        raise ConnectionError("The external API is temporarily unavailable.")

    print("API call succeeded!")
    # Forward the validated `query` so `cache_node` caches per actual user query!
    return query


# --- 3. Performance with Query-Keyed Caching ---


@functools.lru_cache(maxsize=128)
def _slow_query(query: str) -> str:
    """A deterministic backend lookup with per-query in-memory LRU caching."""
    print(f"Performing slow backend query for: {query!r}...")
    time.sleep(2)  # Simulate expensive I/O latency on cache miss
    return f"Verified results for '{query}'"


@node
def cache_node(node_input: str) -> str:
    """Executes the query through the LRU cache keyed by the user's `query`."""
    query = node_input
    result = _slow_query(query)
    return f"Cached Result: {result}"


# --- 4. The Orchestrator Workflow ---

# Assemble the components into a deterministic Graph:
# START -> validate_input_node (extracts `query`) -> flaky_api_node (retries, forwards `query`) -> cache_node (`_slow_query(query)`)
root_agent = Workflow(
    name="BestPracticesSystem",
    edges=[
        ("START", validate_input_node),
        (validate_input_node, flaky_api_node),
        (flaky_api_node, cache_node),
    ],
    # NOTE: retry_config is set on `flaky_api_node` itself (above), not here.
    # `Workflow` extends `BaseNode`, so it accepts `retry_config` too — but
    # that only governs retries of the Workflow *as a node* (if nested inside
    # a parent graph). It does NOT cascade to the nodes inside its own graph.
)
```

### Key Takeaways Explained

1.  **Fail-Closed Security & Clean Data Threading:** By validating JSON at the entry node with Pydantic and returning `validated.query`, malformed payloads halt immediately while valid requests pass the clean `query` string downstream via each `@node`'s `node_input: str` pass-through parameter.
2.  **Native Resilience:** ADK 2.0's `RetryConfig` separates business logic from error handling. Nodes stay clean without manual retry loops, and avoiding bare `except:` ensures both `ConnectionError` retries and `NodeInterruptedError` (`BaseException`) HITL pauses work seamlessly.
3.  **Per-Query Caching:** Because `validate_input_node` and `flaky_api_node` forward `query` rather than a static string, `_slow_query(query)` caches results per distinct user query—giving an instant cache hit when repeating `"laptops"` while still computing fresh results for `"headphones"`.
4.  **Deterministic Routing:** Using a `Workflow` graph instead of an LLM router for fixed pipelines eliminates unnecessary token cost and routing latency.

### Self-Reflection Answers

1.  **Why is it better to let the framework handle retries rather than writing manual loops in your tool functions?**
    *   **Answer:** Centralized retry logic ensures consistent behavior across all nodes, surfaces every retry attempt in ADK's Trace View for debugging, and lets you tune backoff policy declaratively via `RetryConfig` without cluttering business logic.
2.  **What happens if you catch the exception inside `flaky_api_node` with a `try/except` block and return an error string? Does the framework still retry?**
    *   **Answer:** No. The framework only triggers `RetryConfig` if an unhandled exception escapes the node. Catching it and returning a string marks the node run as "Successful" and passes that error string straight into `cache_node` (which would even poison your cache with the error message!).
3.  **In a production environment (like Cloud Run), why is `lru_cache` only a partial solution for performance?**
    *   **Answer:** Cloud Run is serverless and scales horizontally across isolated container instances. `functools.lru_cache` lives only in one process's RAM—if Request 1 lands on Instance A and Request 2 lands on Instance B (or Instance A scales to zero), the cache misses. Production multi-instance deployments use a shared distributed cache like Google Cloud Memorystore for Redis.

</SolutionVault>
