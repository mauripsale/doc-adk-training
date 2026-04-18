---
sidebar_position: 1
title: "Module 12: Built-in Tools and Grounding"
---

# Module 12: Built-in Tools and Grounding

## Theory

### Why Built-in Tools Matter

Traditional AI models have a knowledge cutoff date—they don't know about recent events, current news, or real-time information. Built-in tools solve this by allowing models to **ground** their responses in current web data. This process of retrieving external information to enhance the LLM's generation is the foundation of **Retrieval Augmented Generation (RAG)** systems.

**Key Advantages**:
*   **Current Information:** Access to up-to-date web content.
*   **No Local Execution:** Tools run inside the model's environment (managed by Google), requiring no local code execution or infrastructure from you.
*   **Automatic Integration:** The LLM seamlessly incorporates the search results into its final response, often providing citations.
*   **Production Ready:** These tools are used by real-world, enterprise applications for grounding.

**Important:** Built-in tools are a feature of Gemini 2.0 and newer models and will raise errors with older versions.

### `google_search`: Web Grounding

The `google_search` tool is a built-in capability that allows a Gemini 2.0+ model to search the web to find information. When you add this tool to your agent, the model can autonomously decide to use it when a user's query requires current information.

In the modern ADK, using web grounding is incredibly simple. You can mix built-in tools like `google_search` directly with your own custom Python functions in the same agent.

### Seamless Tool Integration

Unlike earlier versions of the framework that required complex wrappers, you can now simply import the built-in tools and list them alongside your custom functions:

```python
from google.adk.agents import LlmAgent
from google.adk.tools import google_search

def my_custom_tool(item_id: str) -> dict:
    """Looks up internal warehouse data."""
    return {"status": "success", "stock": 42}

# You can mix built-in and custom tools freely!
agent = LlmAgent(
    name="grounded_agent",
    model="gemini-2.5-flash",
    instruction="Search the web and check our warehouse.",
    tools=[
        google_search, 
        my_custom_tool
    ]
)
```

The ADK handles the complexity of merging these different tool types for you. When the user asks a question, the LLM will decide whether to look at the public web using `google_search` or query your internal database using `my_custom_tool`.

### `google_maps_grounding`: Location-Based Queries

The `google_maps_grounding` tool enables agents to answer location-based queries, such as finding nearby places, getting directions, or understanding geographic context. This tool is currently only available when using the **Vertex AI API**.

### Key Takeaways
- Built-in tools like `google_search` allow agents to access real-time information from the web, overcoming the LLM's knowledge cutoff.
- These tools run within the model's environment, making them easy to set up and scale.
- Modern ADK allows you to **mix built-in tools and custom functions directly** in the agent's `tools` list without any workarounds.
