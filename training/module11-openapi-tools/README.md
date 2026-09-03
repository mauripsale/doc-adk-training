---
sidebar_position: 11
title: "Module 11: Enterprise Integration with OpenAPI Tools"
---

# Module 11: Enterprise Integration with OpenAPI Tools

## Theory

### Connecting to the Enterprise Ecosystem

Modern enterprises run on RESTful APIs. Whether it's a CRM, an ERP, or a custom internal service, these systems often expose their functionality through **OpenAPI** specifications. To build truly useful AI agents, you must know how to connect them to these existing enterprise services.

### From Specification to Tools, Automatically

In ADK 2.0, you don't hand-write a wrapper function per endpoint. Instead, you hand the ADK an OpenAPI spec and it generates the tools for you: **`OpenAPIToolset`** parses the spec and creates one callable tool per operation, named after each operation's `operationId`.

#### 1. Provide the Spec
The spec can come from a `.json`/`.yaml` file, or -- just as commonly -- a plain Python `dict` you build inline and pass through `json.dumps()`. Each operation needs a unique `operationId` (this becomes the tool's name) and a `responses` block describing at least the success case.

#### 2. Instantiate `OpenAPIToolset`
Pass the spec string to `OpenAPIToolset`, then hand the toolset directly to your agent's `tools=[...]` list -- no wrapper function needed.

```python
import json
from google.adk import Agent
from google.adk.tools.openapi_tool import OpenAPIToolset

MY_API_SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "My API", "version": "1.0.0"},
    "servers": [{"url": "https://api.example.com"}],
    "paths": {
        "/data": {
            "get": {
                "operationId": "fetch_external_data",
                "parameters": [{"name": "query", "in": "query", "schema": {"type": "string"}}],
                "responses": {"200": {"description": "OK", "content": {"application/json": {"schema": {"type": "object"}}}}}
            }
        }
    }
}

toolset = OpenAPIToolset(spec_str=json.dumps(MY_API_SPEC), spec_str_type="json")

# Register with Agent -- the toolset itself goes in tools=[], not a wrapper function
agent = Agent(name="api_expert", tools=[toolset], ...)
```

The ADK handles the HTTP request, query/path parameter encoding, and JSON parsing for you -- your Python code never touches `requests` directly.

### Key Takeaways
- **OpenAPI** is the industry standard for describing REST APIs.
- **`OpenAPIToolset`** generates tools automatically from a spec (dict or file) -- no client generation, no hand-written wrapper functions.
- Each operation's `operationId` becomes the tool's name the agent sees and calls -- it must be unique across the spec.
- This pattern lets your agent securely and reliably communicate with any enterprise service that publishes an OpenAPI spec, and stays in sync automatically when the spec is updated.
