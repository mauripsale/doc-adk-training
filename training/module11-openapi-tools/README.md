---
sidebar_position: 1
title: "Module 11: OpenAPI Tools"
---

# Module 11: OpenAPI Tools

## Theory

### Connecting Your Agent to Enterprise Systems

In the previous modules, you wrote custom Python functions (`FunctionTool`) to give your agent new capabilities. While powerful, writing a custom Python wrapper for every single endpoint of a large corporate API (like a CRM, an ERP, or a banking backend) is tedious and hard to maintain.

To connect your agent to the vast world of existing REST APIs, the ADK provides a much more efficient method: **OpenAPI Tools**.

### What is OpenAPI?

**OpenAPI** (formerly known as Swagger) is a standard specification for describing REST APIs. It's a machine-readable format, usually written in JSON or YAML, that defines an API's endpoints, operations (GET, POST), parameters, authentication methods, and response structures.

In most modern enterprises, backend teams automatically generate these `openapi.json` files for their services.

### How `OpenAPIToolset` Works

The ADK's `OpenAPIToolset` class ingests an OpenAPI specification and **automatically generates** a complete set of tools that your agent can use.

```
OpenAPI Spec (JSON/YAML) -> ADK Auto-Generation -> Tools Available to Agent
```

This process has massive benefits:
*   **No Manual Tool Writing:** You don't need to write a Python function for every single API endpoint.
*   **Always in Sync:** If the backend team updates the API and publishes a new spec, your agent instantly gets the updated tools.
*   **Automatic Handling:** The toolset automatically handles HTTP request construction, parameter validation, URL building, and response parsing.

### The Process in Detail

1.  **Provide the Spec:** You provide the `OpenAPIToolset` with the OpenAPI specification (as a JSON string, a file path, or a URL).
2.  **Tool Generation:** The ADK parses the `paths` and `operations` in the spec. For each operation, it creates a tool function in memory. 
    *   The **tool's name** is derived directly from the `operationId` in the spec (converted to `snake_case`).
    *   The **parameters** are derived from the API's query/path/body parameters.
3.  **Agent Integration:** You add the entire toolset to your agent's `tools` list.
4.  **Autonomous Use:** The LLM receives the schemas for all the auto-generated tools and can now decide to call them just like any standard function tool.

### Example: Currency Exchange API

Imagine you want to extend your "Wealth Planner" (from Module 10) to handle multiple currencies. Instead of writing custom HTTP requests, you find a public currency API (like Frankfurter) and its OpenAPI spec.

```python
import json
from google.adk.agents import LlmAgent
from google.adk.tools.openapi_tool import OpenAPIToolset

# 1. The OpenAPI Specification (Usually loaded from a .json file)
API_SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "Currency API", "version": "1.0.0"},
    "servers": [{"url": "https://api.frankfurter.app"}],
    "paths": {
        "/latest": {
            "get": {
                "operationId": "get_latest_rates", # -> Becomes the tool name!
                "summary": "Get latest exchange rates",
                "parameters": [
                    {"name": "amount", "in": "query", "schema": {"type": "number"}},
                    {"name": "from", "in": "query", "schema": {"type": "string"}},
                    {"name": "to", "in": "query", "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "Success"}}
            }
        }
    }
}

# 2. Create the Toolset
# We convert the dict to a JSON string for the ADK
currency_tools = OpenAPIToolset(
    spec_str=json.dumps(API_SPEC), 
    spec_str_type="json"
)

# 3. Add to Agent
agent = LlmAgent(
    name="global_market_analyst",
    model="gemini-2.5-flash",
    instruction="You are a market analyst. Use your tools to convert currencies.",
    tools=[currency_tools] # Automatically registers `get_latest_rates`
)
```

With just those few lines, the LLM now knows how to call `https://api.frankfurter.app/latest?amount=X&from=Y&to=Z` perfectly.

### Key Takeaways
- OpenAPI (Swagger) is a standard specification for describing REST APIs.
- The ADK's `OpenAPIToolset` automatically generates a full set of agent tools from an OpenAPI specification string or file.
- This eliminates the need to write manual Python HTTP clients for each API endpoint.
- The `operationId` in the OpenAPI spec determines the exact name of the tool generated for the LLM.
