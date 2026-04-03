---
sidebar_position: 7
title: "Lab Solution"
---

# Lab 4.5 Solution: Switching Between LLM Providers

## Goal

In this lab, we successfully demonstrated the model-agnostic nature of the ADK. By using the `LiteLlm` wrapper, we were able to run the same agent on a local model (Ollama/Mistral) and discuss how to switch to other cloud providers like OpenAI.

### `multi_model_agent/agent.py`

```python
from google.adk.agents import LlmAgent
from google.adk.models import LiteLlm

# Initialize the LiteLlm wrapper for a local model running via Ollama
# The syntax is provider/model_name
local_model = LiteLlm(model="ollama_chat/mistral")

# Alternative: Define a cloud model (uncomment and add your API key to .env to use)
# cloud_model = LiteLlm(model="openai/gpt-4o")

root_agent = LlmAgent(
    name="multi_model_agent",
    model=local_model,
    instruction="""
        You are a helpful assistant.
        Always begin your response by stating which provider and model is currently powering you.
        For example: "I am powered by Mistral via Ollama."
    """
)
```

### Configuration: `.env` setup

To use models from other providers, your `.env` file must contain the appropriate API keys:

```text
# For OpenAI
OPENAI_API_KEY=your_key_here

# For Anthropic
ANTHROPIC_API_KEY=your_key_here

# For Ollama (Optional: only if running on a non-standard port/host)
# OLLAMA_API_BASE=http://localhost:11434
```

### Self-Reflection Answers

1.  **How does the `LiteLlm` integration simplify the process of testing an agent with different models?**
    *   **Answer:** It provides a unified interface. Without `LiteLlm`, you would have to rewrite your agent's code using different SDKs (e.g., switching from the Google GenAI SDK to the OpenAI SDK). With ADK + LiteLlm, you only change a single string in the `model` parameter, and the ADK handles all the underlying API translations.

2.  **If you were deploying an agent to production, what are the security implications of using an external provider like OpenAI versus a local model like Ollama?**
    *   **Answer:** Using an external provider (SaaS) means sending user data to a third-party server, which requires careful privacy agreements and handling of API keys. A local model (like Ollama) keeps all data within your infrastructure, which is highly secure and ideal for sensitive or regulated data, but it requires you to manage your own hardware/compute resources.

3.  **Why is it important for the ADK to remain "model-agnostic"?**
    *   **Answer:** It prevents vendor lock-in. It allows developers to choose the best model for their specific use case (balancing cost, speed, and intelligence) and ensures that the agent logic is portable. If a new, superior model is released by any provider, an ADK agent can switch to it almost instantly.
