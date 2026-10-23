---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 11 Solution: Building a "Global Market Analyst" Agent

## Goal

This file contains the complete, working code for the **Global Market Analyst** that can automatically convert currencies using an OpenAPI specification.

### Complete `agent.py` Code

Here is the fully implemented `agent.py` file. Notice how the `/latest` path is defined in the `FRANKFURTER_SPEC` dictionary and how we initialize the `OpenAPIToolset`.

```python
# agent.py
import json
from google.adk import Agent
from google.adk.tools.openapi_tool import OpenAPIToolset

# ============================================================================
# OPENAPI SPECIFICATION
# ============================================================================
FRANKFURTER_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Frankfurter Currency API",
        "description": "Free API for current and historical foreign exchange rates",
        "version": "1.0.0"
    },
    "servers": [{"url": "https://api.frankfurter.dev/v1"}],
    "paths": {
        "/latest": {
            "get": {
                "operationId": "get_latest_rates",
                "summary": "Get latest exchange rates",
                "parameters": [
                    {
                        "name": "amount",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "number"}
                    },
                    {
                        "name": "from",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "string"}
                    },
                    {
                        "name": "to",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        }
                    }
                }
            }
        }
    }
}

# ============================================================================
# OPENAPI TOOLSET
# ============================================================================
# Convert the Python dictionary to a JSON string for the ADK
spec_string = json.dumps(FRANKFURTER_SPEC)

# Initialize the Toolset
currency_toolset = OpenAPIToolset(
    spec_str=spec_string,
    spec_str_type="json"
)

# ============================================================================
# AGENT NODE DEFINITION
# ============================================================================
root_agent = Agent(
    name="market_analyst",
    model="gemini-3.5-flash",
    description="A specialist in global currency exchange rates.",
    instruction="""
You are an expert Global Market Analyst.
Use the `get_latest_rates` tool to convert currencies and check exchange rates for the user.
Always state the amount, the original currency, and the converted currency clearly.
""",
    tools=[currency_toolset]
)
```

### Running the Agent

1.  Make sure your `market_analyst` project exists and dependencies are installed. If you followed the steps above, this was already done for you via the `<Setup/>` block (which creates the `adk-training` project and installs `google-adk`/`python-dotenv`) followed by `uv run adk create market_analyst`. If you're picking this lab up fresh, run those two steps first.
2.  Make sure your `.env` file is configured for Vertex AI (consistent with the rest of the course), not just a bare API key:
    ```
    GOOGLE_GENAI_USE_VERTEXAI=1
    GOOGLE_CLOUD_PROJECT=<your_gcp_project>
    GOOGLE_CLOUD_LOCATION=us-central1
    ```
    Make sure you've also run `gcloud auth application-default login` so Application Default Credentials are available. (If you're using a plain Gemini API key instead, set `GOOGLE_API_KEY` in `.env` and omit the Vertex AI variables.)
3.  Run the interactive terminal:
    ```bash
    uv run adk run .
    ```

---

## Self-Reflection Answers

1.  **What are the main advantages of using `OpenAPIToolset` compared to writing a custom Python function?**
    *   **Answer:** Speed and maintainability. You don't have to write HTTP boilerplate code (`requests.get(...)`), handle URL encoding, or parse JSON responses manually. Furthermore, if the API provider updates their service, you just update the spec file (or download their new one) and your tools are automatically updated without changing your Python logic.

2.  **What do you think would happen if two different paths in the spec had the same `operationId`?**
    *   **Answer:** The ADK uses the `operationId` as the unique name for the tool (e.g., `get_latest_rates`). If there were duplicates, the tool registration would either fail with an error or overwrite the previous tool, leading to unpredictable agent behavior. `operationId` must always be unique across the entire spec.

3.  **How does the widespread adoption of the OpenAPI standard make it easier to build powerful AI agents?**
    *   **Answer:** Because almost all modern enterprise applications and SaaS platforms (like Stripe, GitHub, Salesforce) publish OpenAPI specifications, you can theoretically connect an ADK agent to *any* of them in minutes just by loading their spec file into an `OpenAPIToolset`. It bridges the gap between AI and traditional software ecosystems effortlessly.
