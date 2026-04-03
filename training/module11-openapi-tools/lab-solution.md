---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 11 Solution: Building a Chuck Norris Fact Assistant

## Goal

This file contains the complete code for the `agent.py` script in the Chuck Norris Fact Assistant lab.

### `chuck_norris_agent/agent.py`

```python
"""
Chuck Norris Fact Assistant - OpenAPI Tools Demonstration

This agent demonstrates how to use OpenAPIToolset to automatically
generate tools from an API specification without writing tool functions.
"""

from google.adk.agents import Agent
from google.adk.tools.openapi_tool import OpenAPIToolset

# ============================================================================
# OPENAPI SPECIFICATION
# ============================================================================

# Chuck Norris API OpenAPI Specification
# Based on: https://api.chucknorris.io/
CHUCK_NORRIS_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Chuck Norris API",
        "description": "Free JSON API for hand curated Chuck Norris facts",
        "version": "1.0.0"
    },
    "servers": [
        {
            "url": "https://api.chucknorris.io/jokes"
        }
    ],
    "paths": {
        "/random": {
            "get": {
                "operationId": "get_random_joke",
                "summary": "Get a random Chuck Norris joke",
                "description": "Retrieve a random joke from the database. Can optionally filter by category.",
                "parameters": [
                    {
                        "name": "category",
                        "in": "query",
                        "description": "Filter jokes by category (optional)",
                        "required": False,
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "icon_url": {"type": "string"},
                                        "id": {"type": "string"},
                                        "url": {"type": "string"},
                                        "value": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/search": {
            "get": {
                "operationId": "search_jokes",
                "summary": "Search for jokes",
                "description": "Free text search for jokes containing the query term.",
                "parameters": [
                    {
                        "name": "query",
                        "in": "query",
                        "description": "Search query (3+ characters required)",
                        "required": True,
                        "schema": {
                            "type": "string",
                            "minLength": 3
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "total": {"type": "integer"},
                                        "result": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "icon_url": {"type": "string"},
                                                    "id": {"type": "string"},
                                                    "url": {"type": "string"},
                                                    "value": {"type": "string"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/categories": {
            "get": {
                "operationId": "get_categories",
                "summary": "Get all joke categories",
                "description": "Retrieve list of available joke categories.",
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                }
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

# Create OpenAPIToolset from specification
chuck_norris_toolset = OpenAPIToolset(spec_dict=CHUCK_NORRIS_SPEC)

# ============================================================================
# AGENT DEFINITION
# ============================================================================

root_agent = Agent(
    name="chuck_norris_agent",
    model="gemini-2.5-flash",
    description="A Chuck Norris fact assistant that can retrieve jokes/facts from the Chuck Norris API.",
    instruction="""
    You are a fun Chuck Norris fact assistant!

    CAPABILITIES:
    - Get random Chuck Norris jokes (optionally filtered by category)
    - Search for jokes containing specific keywords
    - List all available joke categories

    WORKFLOW:
    - For random requests -> use get_random_joke
    - For specific topics -> use search_jokes with query
    - To see categories -> use get_categories
    - For category-specific random -> use get_random_joke with category parameter

    IMPORTANT:
    - Always extract the 'value' field from the API response (that's the actual joke).
    - If a search finds 0 results, suggest trying a different keyword.
    """,
    tools=[chuck_norris_toolset]
)
```

### Self-Reflection Answers

1.  **What are the main advantages of using `OpenAPIToolset` compared to writing a custom Python function for each API endpoint?**
    *   **Answer:** The `OpenAPIToolset` dramatically reduces code volume and maintenance effort. Instead of manually writing boilerplate code to construct HTTP requests, handle parameters, and parse responses for every single endpoint, you simply provide a declarative specification. This ensures that your agent's tools are always perfectly synchronized with the API's capabilities, reducing the risk of implementation errors.

2.  **The `operationId` in the OpenAPI spec is very important. What do you think would happen if two different paths in the spec had the same `operationId`?**
    *   **Answer:** The ADK uses the `operationId` to generate the name of the tool function (e.g., `get_random_joke`). If two paths shared the same `operationId`, the ADK would attempt to create two functions with the same name, causing a conflict. The second one would likely overwrite the first, or the system would throw an error during initialization. Unique `operationId`s are essential for distinguishing tools.

3.  **Many modern web services publish their own OpenAPI specifications. How does this widespread adoption of the OpenAPI standard make it easier to build powerful, integrated AI agents?**
    *   **Answer:** The ubiquity of the OpenAPI standard means that millions of existing APIs are "agent-ready" right out of the box. Developers can instantly connect their agents to services like Stripe, GitHub, Twilio, or internal enterprise systems just by downloading the `openapi.json` file. This transforms the process of building integrations from a manual coding task into a configuration task, rapidly expanding the potential capabilities of AI agents.

4.  **The agent's instructions often need to specify which part of a tool's JSON response is important (e.g., "extract the 'value' field"). Why is this necessary, and what does it tell you about how the agent perceives the data it receives from a tool?**
    *   **Answer:** APIs often return verbose JSON objects containing metadata (like IDs, URLs, or timestamps) that isn't relevant to the user's question. The agent sees the entire raw JSON response. Without specific instructions, the agent might get "distracted" by this noise or simply dump the raw JSON to the user. Instructing the agent to focus on a specific field (like `value` for the joke text) helps it filter the information and provide a clean, human-readable answer. It highlights that while agents are smart, they still benefit from guidance on how to interpret and present data.