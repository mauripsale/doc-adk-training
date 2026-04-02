---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 11: Building a Chuck Norris Fact Assistant Challenge

## Goal

### Goal

In this lab, you will build an agent that can retrieve Chuck Norris jokes from a public REST API. You will learn how to use the `OpenAPIToolset` to automatically generate the necessary tools from an OpenAPI specification.

### Step 1: Create the Agent Project

1.  **Create the agent project:**
    Choose the **Programmatic (Python script)** option when prompted.
    ```shell
    adk create chuck_norris_agent
    cd chuck_norris_agent
    ```

2.  **Set up your API key** in the `.env` file. (The Chuck Norris API is free, but the agent needs credentials for the Gemini model).

### Step 2: Define the OpenAPI Specification

**Exercise:** Open `agent.py`. A more complete skeleton for the OpenAPI specification is provided below. Your task is to complete the spec for the `/random` endpoint's `get` operation. You can find the necessary information from the API documentation at [https://api.chucknorris.io/](https://api.chucknorris.io/).

```python
# In agent.py (Starter Code)

from google.adk.agents import Agent
from google.adk.tools.openapi_tool import OpenAPIToolset

# ============================================================================
# OPENAPI SPECIFICATION
# ============================================================================
# The `operationId` is critical. The ADK uses it to generate the tool's name
# (e.g., `operationId: "get_random_joke"` becomes the `get_random_joke` tool).

CHUCK_NORRIS_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Chuck Norris API",
        "description": "Free JSON API for hand curated Chuck Norris facts",
        "version": "1.0.0"
    },
    "servers": [{"url": "https://api.chucknorris.io/jokes"}],
    "paths": {
        "/random": {
            "get": {
                # TODO: Complete this section for the "/random" endpoint.
                # - The operationId should be "get_random_joke".
                # - The summary should be "Get a random Chuck Norris joke".
                # - It needs a "parameters" list with one optional query
                #   parameter named "category".
                # - It needs a "responses" section for a "200" status code.
            }
        },
        # The other paths are provided for you.
        "/search": {
            "get": {
                "operationId": "search_jokes",
                "summary": "Search for jokes",
                "parameters": [{
                    "name": "query", "in": "query", "required": True,
                    "schema": {"type": "string", "minLength": 3}
                }],
                "responses": {"200": {"description": "Successful response"}}
            }
        },
        "/categories": {
            "get": {
                "operationId": "get_categories",
                "summary": "Get all joke categories",
                "responses": {"200": {"description": "Successful response"}}
            }
        }
    }
}

# ============================================================================
# OPENAPI TOOLSET
# ============================================================================

# TODO: Create an OpenAPIToolset instance from the spec dictionary.
chuck_norris_toolset = OpenAPIToolset(...)

# ============================================================================
# AGENT DEFINITION
# ============================================================================

# TODO: Define the root_agent.
# - Give it a name, model ('gemini-2.5-flash'), and description.
# - Write an instruction to be a fun Chuck Norris fact assistant.
# - Register the `chuck_norris_toolset` in its `tools` list.
root_agent = Agent(...)
```

### Step 3: Run and Test Your Agent

1.  **Navigate to the parent directory** (`cd ..`) and start the Dev UI: `adk web chuck_norris_agent`
2.  **Interact with the agent:**
    *   Test its capabilities:
        *   "Tell me a random Chuck Norris joke"
        *   "Find jokes about computers"
        *   "What joke categories exist?"
        *   "Give me a random movie joke"
    *   Inspect the **Events** tab to see the `FunctionCall` for your auto-generated tools.

### Having Trouble?

If you get stuck, you can find the complete, working code in the `lab-solution.md` file.

### Lab Summary

You have successfully integrated a live REST API into your agent without writing a single manual tool function. You have learned:
*   How to read API documentation to create an OpenAPI specification.
*   How to use `OpenAPIToolset` to automatically generate tools from a spec.
*   How to instruct your agent to use the new, auto-generated tools.

### Self-Reflection Questions
- What are the main advantages of using `OpenAPIToolset` compared to writing a custom Python function for each API endpoint?
- The `operationId` in the OpenAPI spec is very important. What do you think would happen if two different paths in the spec had the same `operationId`?
- Many modern web services publish their own OpenAPI specifications. How does this widespread adoption of the OpenAPI standard make it easier to build powerful, integrated AI agents?
- The agent's instructions often need to specify which part of a tool's JSON response is important (e.g., "extract the 'value' field"). Why is this necessary, and what does it tell you about how the agent perceives the data it receives from a tool?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMTEtb3BlbmFwaS10b29scy9sYWItc29sdXRpb24=`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module11-openapi-tools/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
