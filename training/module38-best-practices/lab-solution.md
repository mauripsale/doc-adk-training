---
sidebar_position: 3
title: "Lab Solution"
---

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
