---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 11: Building a "Global Market Analyst" Challenge

## Goal

In this lab, you will build an agent that can retrieve live currency exchange rates from a public REST API. You will learn how to use the `OpenAPIToolset` to automatically generate the necessary tools from an OpenAPI specification.

### Step 1: Create the Agent Project

We will continue using the modern `uv` workflow.

1.  **Initialize the project:**
    ```shell
    uv init market_analyst --python 3.10
    cd market_analyst
    uv add "google-adk>=2.1.0" python-dotenv
    ```

2.  **Set up your API key** in the `.env` file for the Gemini model. (The Frankfurter Currency API we are using is completely free and requires no authentication).

### Step 2: Define the OpenAPI Specification

**Exercise:** Open `agent.py`. A skeleton for the OpenAPI specification is provided below. Your task is to complete the spec for the `/latest` endpoint's `get` operation. You can deduce the necessary parameters from the Frankfurter API documentation (or the theory section).

```python
# In agent.py
import json
from google.adk import Agent
from google.adk.tools.openapi_tool import OpenAPIToolset

# ============================================================================
# OPENAPI SPECIFICATION
# ============================================================================
# The `operationId` is critical. The ADK uses it to generate the tool's name
# (e.g., `operationId: "get_latest_rates"` becomes the `get_latest_rates` tool).

FRANKFURTER_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Frankfurter Currency API",
        "description": "Free API for current and historical foreign exchange rates",
        "version": "1.0.0"
    },
    "servers": [{"url": "https://api.frankfurter.app"}],
    "paths": {
        "/latest": {
            "get": {
                # TODO: Complete this section for the "/latest" endpoint.
                # - The operationId should be "get_latest_rates".
                # - The summary should be "Get latest exchange rates".
                # - It needs a "parameters" list with query parameters: "amount", "from", "to".
            }
        }
    }
}

# ============================================================================
# AGENT NODE DEFINITION
# ============================================================================

# TODO: 1. Create the OpenAPIToolset instance.
# TODO: 2. Define the root Agent node and register the toolset.
root_agent = Agent(...)
```

### Step 3: Run and Test Your Agent

1.  **Start the agent in terminal mode:** 
    ```bash
    uv run adk run agent.py
    ```
2.  **Interact with the agent:**
    *   Test its capabilities:
        *   "Convert 100 USD to EUR."
        *   "How many Japanese Yen (JPY) can I get for 50 British Pounds (GBP)?"
        *   "Convert 500 AUD to USD and EUR." *(Notice if it calls the API twice or handles it smartly!)*
    *   Observe the logs to see the agent constructing and executing the HTTP requests perfectly based on your spec.

### Having Trouble?

If you get stuck, you can find the complete, working code in the `lab-solution.md` file.

### Lab Summary

You have successfully integrated a live REST API into your agent without writing a single manual tool function. You have learned:
*   How to translate API documentation into an OpenAPI specification.
*   How to use `OpenAPIToolset` to automatically generate tools from a spec.
*   How to instruct your agent to use the new, auto-generated tools.

### Self-Reflection Questions
- What are the main advantages of using `OpenAPIToolset` compared to writing a custom Python function (like `requests.get(...)`) for each API endpoint?
- The `operationId` in the OpenAPI spec is very important. What do you think would happen if two different paths in the spec had the same `operationId`?
- Many modern web services publish their own OpenAPI specifications (often as a URL like `api.example.com/openapi.json`). How does this widespread adoption of the OpenAPI standard make it easier to build powerful, integrated AI agents?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMTEtb3BlbmFwaS10b29scy9sYWItc29sdXRpb24=`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module11-openapi-tools/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
