---
sidebar_position: 7
title: "Lab Solution"
---

# Lab 4.5 Solution: Professional Model Configuration

## Goal

In this lab, you learned how to transition from simple string-based model selection to a professional, enterprise-grade configuration using `Gemini` subclasses and `LiteLlm` abstractions.

### `support_analyzer/agent.py`

Here is the complete code implementing the resilient subclass and the multi-model fallback logic:

```python
import os
from functools import cached_property
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.models.lite_llm import LiteLlm
from google.genai import Client, types

# Step 1: Define the ResilientGemini subclass
class ResilientGemini(Gemini):
    """
    Expert pattern: Subclass Gemini to centralize production configurations
    like project, location, and advanced retry logic.
    """
    @cached_property
    def api_client(self) -> Client:
        return Client(
            project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            location="us-central1",
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(
                    max_delay=10, # Max seconds to wait between retries
                    exp_base=2.0,  # Base for exponential backoff
                    jitter=0.5,    # Jitter to prevent thundering herd
                )
            ),
        )

# Step 2: Implement the model selection logic
# This allows developers to toggle between cloud and local models via env vars.
if os.getenv("USE_LOCAL_MODEL") == "1":
    # Use LiteLLM abstraction for local development with Ollama
    model_to_use = LiteLlm(model="ollama_chat/mistral")
else:
    # Use the professional, native Gemini subclass for production
    model_to_use = ResilientGemini(model="gemini-2.5-flash")

root_agent = LlmAgent(
    name="support_analyzer_agent",
    model=model_to_use,
    instruction="""
        You are a customer support analyzer. 
        Analyze the incoming ticket and provide a structured JSON response.
    """
)
```

### Key Takeaways Explained

1.  **Centralization via Subclassing:** By creating `ResilientGemini`, you avoid repeating complex `HttpRetryOptions` for every agent in your codebase. If you need to change the region from `us-central1` to `global`, you only update it in one place.
2.  **The Thundering Herd Problem:** By adding `jitter=0.5`, you ensure that if multiple agent requests fail at the same time, they won't all retry at the exact same millisecond, which helps prevent overwhelming your API backend.
3.  **Environment-Driven Architecture:** Using `os.getenv("USE_LOCAL_MODEL")` makes your code highly portable. You can run it on your laptop using Ollama and then deploy it to the cloud without changing a single line of code—only the environment variables change.

### Self-Reflection Answers

1.  **Why is "Jitter" important in a retry policy for a high-traffic production application?**
    *   **Answer:** Without jitter, multiple failed requests would retry at the exact same intervals (e.g., exactly after 1s, 2s, 4s). In a high-traffic system, this creates "spikes" of traffic that can re-trigger rate limits or crash a recovering service. Jitter adds a random offset to each retry, spreading the load evenly over time.

2.  **What are the advantages of centralizing model configuration in a subclass instead of passing parameters to every agent instance?**
    *   **Answer:** It follows the DRY (Don't Repeat Yourself) principle. It makes the code easier to maintain, reduces the risk of configuration errors (e.g., having different retry policies in different agents), and allows for global changes (like swapping the production GCP project) to be made instantaneously across the entire system.

3.  **In which scenario would you prefer using the native `Gemini` class over the `LiteLlm` abstraction?**
    *   **Answer:** Use the native `Gemini` class when you are building a production system on Google Cloud and need the highest performance, lowest latency, and access to Gemini-specific features (like native speech config, context caching, or advanced grounding) that might not be fully mapped or supported by the general LiteLLM abstraction.
