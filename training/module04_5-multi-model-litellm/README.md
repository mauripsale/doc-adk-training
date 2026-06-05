---
sidebar_position: 4.5
title: "Module 4.5: Professional Model Configuration & Resiliency"
---

# Module 4.5: Professional Model Configuration & Resiliency

## Theory

Until now, we've passed models to our agents using simple strings (e.g., `model="gemini-3.5-flash"`). While this is great for prototyping, building **production-grade** agents requires a more robust approach to handle network flakiness, rate limits, and regional deployments.

In this module, we will explore the three levels of model configuration in the ADK, inspired by enterprise best practices.

### Level 1: Simple Strings (Prototype)
The simplest way. Ideal for learning and quick tests.
```python
agent = Agent(model="gemini-3.5-flash", ...)
```

### Level 2: The `Gemini` Class (Professional)
By importing `Gemini` from `google.adk.models`, you gain access to the model's underlying connection settings, most importantly **Retry Logic**.

In production, LLM APIs can occasionally time out or return rate-limit errors (429). The `Gemini` class allows you to define a retry policy so the agent doesn't just crash when a request fails.

```python
from google.adk import Agent
from google.adk.models import Gemini
from google.genai import types

resilient_model = Gemini(
    model='gemini-3.5-flash',
    # Automatically retry failed requests up to 3 times
    retry_options=types.HttpRetryOptions(initial_delay=1, attempts=3)
)

agent = Agent(model=resilient_model, ...)
```

### Level 3: Custom Subclasses (Enterprise Expert)
For large projects, you often want to centralize configurations like the Google Cloud project ID, specific regions, or advanced HTTP options across all your agents. The expert pattern is to **subclass** the `Gemini` model.

This allows you to lock in production settings (like forcing the `global` location or adding "Jitter" to retries to prevent server hammering) in a single reusable class.

```python
from functools import cached_property
from google.adk import Agent
from google.adk.models import Gemini
from google.genai import Client, types
import os

class ProductionGemini(Gemini):
    """Custom model subclass for enterprise deployments."""
    
    @cached_property
    def api_client(self) -> Client:
        return Client(
            project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            location="us-central1", # Centralize your deployment region
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(
                    max_delay=10, # Maximum time to wait between retries
                    exp_base=2.0,  # Exponential backoff base
                    jitter=0.5,    # Random delay to avoid thundering herd
                )
            ),
        )

# Use your expert class anywhere in your app
agent = Agent(model=ProductionGemini(model="gemini-3.5-flash"), ...)
```

---

### When to use LiteLLM?
While the `Gemini` class offers the best performance and deepest integration with Google services, you should use the **`LiteLlm`** class (from `google.adk.models.lite_llm`) when your primary goal is **Model Agnosticism**. 

Use `LiteLlm` if you need to:
1.  Run **local models** (via Ollama) during development to save costs.
2.  Switch between different cloud providers (OpenAI, Anthropic) without changing your code structure.

### Key Takeaways
- **Resiliency is mandatory:** Never deploy an agent without a retry policy.
- **The `Gemini` class** is the key to configuring retries, locations, and custom project settings.
- **Subclassing `Gemini`** is an expert pattern for centralizing production configurations.
- **`LiteLlm`** is the tool for maximum portability across providers.
