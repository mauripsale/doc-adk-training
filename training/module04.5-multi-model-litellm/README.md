---
sidebar_position: 5
title: "Module 4.5: Multi-Model Support with LiteLLM"
---

# Module 4.5: Multi-Model Support with LiteLLM

## Theory

### Beyond Gemini: The Power of Choice

One of the greatest strengths of the Google Agent Development Kit (ADK) is its model-agnostic architecture. While it is optimized for Google Gemini models, production-grade applications often require flexibility. You might want to:
*   Use a **local model** (via Ollama) for privacy or cost savings during development.
*   Use a **specialized model** from another provider (like Anthropic Claude or OpenAI GPT) for specific tasks where they might excel.
*   Avoid **vendor lock-in** by making your agent easily portable across different cloud providers.

The ADK achieves this through a first-class integration with **LiteLLM**, a universal wrapper that translates ADK's standard calls into the specific APIs of over 100+ LLM providers.

### How it Works: The `LiteLlm` Wrapper

Instead of passing a simple string (like `"gemini-1.5-flash"`) to the `model` parameter of an agent, you can pass an instance of the `LiteLlm` class.

#### Example: Using Ollama (Local)
If you have Ollama running locally with the `mistral` model:

```python
from google.adk.models import LiteLlm
from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    name="local_assistant",
    model=LiteLlm(model="ollama_chat/mistral"), # Provider/Model syntax
    instruction="You are a helpful local assistant."
)
```

#### Example: Using OpenAI
```python
from google.adk.models import LiteLlm
from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    name="gpt_assistant",
    model=LiteLlm(model="openai/gpt-4o"),
    instruction="You are a helpful assistant powered by GPT."
)
```

### Configuration and Environment Variables

Each provider requires its own set of credentials. LiteLLM looks for standard environment variables in your `.env` file:

| Provider | Model Prefix | Required Variable |
| :--- | :--- | :--- |
| **Ollama** | `ollama_chat/` | `OLLAMA_API_BASE` (Defaults to http://localhost:11434) |
| **OpenAI** | `openai/` | `OPENAI_API_KEY` |
| **Anthropic** | `anthropic/` | `ANTHROPIC_API_KEY` |
| **Groq** | `groq/` | `GROQ_API_KEY` |

### Key Takeaways
- The ADK is **model-agnostic** thanks to the `LiteLlm` integration.
- You can switch providers by simply changing the `model` parameter to a `LiteLlm` instance.
- This allows for local development (Ollama), cost optimization, and high portability.
- **Dependencies:** To use this feature, you must install the litellm library: `pip install litellm`.
