---
sidebar_position: 11
title: "Module 11: Enterprise Integration with OpenAPI Tools"
---

# Module 11: Enterprise Integration with OpenAPI Tools

## Theory

### Connecting to the Enterprise Ecosystem

Modern enterprises run on RESTful APIs. Whether it's a CRM, an ERP, or a custom internal service, these systems often expose their functionality through **OpenAPI** specifications. To build truly useful AI agents, you must know how to connect them to these existing enterprise services.

### From Specification to Node

In ADK 2.0, an OpenAPI tool is often used as a specialized **Node** in your graph or as a tool attached to an **Agent**.

#### 1. Generating the Client
You typically use a tool like `openapi-python-client` to generate a robust, type-safe Python client from your `.json` or `.yaml` specification.

#### 2. Wrapping in a Function Tool
Once you have the client, you write a small wrapper function that initializes the client and makes the API call. This wrapper follows the standard ADK 2.0 tool pattern (Pydantic models and `ToolContext`).

```python
from google.adk import Agent
from my_api_client import Client, AuthenticatedClient
from my_api_client.api.default import get_data

def fetch_external_data(query: str) -> dict:
    """Fetches data from the production API."""
    client = AuthenticatedClient(base_url="https://api.example.com", token="...")
    response = get_data.sync(client=client, q=query)
    return response.to_dict()

# Register with Agent
agent = Agent(name="api_expert", tools=[fetch_external_data], ...)
```

### Key Takeaways
- **OpenAPI** is the industry standard for describing REST APIs.
- Use **Code Generation** to create type-safe Python clients from specs.
- Wrap the generated client in an ADK **Function Tool** for easy integration.
- This pattern allows your agent node to securely and reliably communicate with any enterprise service.
