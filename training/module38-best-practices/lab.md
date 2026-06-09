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
    Choose the **Programmatic (Python script)** option.

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

@node
def validate_input_node(node_input: dict):
    """Validates inputs using a Pydantic model."""
    # TODO: Instantiate ValidatedInput(**node_input). 
    # If it fails, Pydantic will raise a ValidationError and the workflow will stop (Fail-Closed).
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
    *   **Test Validation:** Send malformed input to the 'validate' step. Observe how the Workflow fails immediately with a validation error.
    *   **Test Retries:** Run the 'flaky_call' step. Watch your terminal logs. You should see "Attempting..." multiple times as the **ADK Framework** automatically retries the node after the exception.

### Lab Summary
You have successfully built an agent system that leverages the native resilience of ADK 2.0. You have learned:
*   How to use `Pydantic` for "Fail-Closed" security.
*   How to use **Framework Retries** by propagating exceptions instead of catching them.
*   How to use `lru_cache` for local performance gains.

### Self-Reflection Questions
- Why is it better to let the framework handle retries rather than writing manual loops in your tool functions?
- What happens if you catch the exception inside `flaky_api_node` with a `try/except` block and return an error string? Does the framework still retry?
- In a production environment (like Cloud Run), why is `lru_cache` only a partial solution for performance?

<hr/>
🕵️ HIDDEN SOLUTION: L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMzgtYmVzdC1wcmFjdGljZXMvbGFiLXNvbHV0aW9u
