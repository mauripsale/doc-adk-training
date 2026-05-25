---
sidebar_position: 6
title: "Challenge Lab"
---

# Lab 4.5 Challenge: Professional Model Configuration

## Goal
In this lab, you will upgrade your **"Support Analyzer"** agent to a production-ready state. You will learn how to implement advanced retry logic using a custom `Gemini` subclass and how to provide a multi-model fallback using `LiteLlm`.

## Prerequisites
1.  **Install LiteLLM:** 
    ```shell
    pip install litellm
    ```

## Lab Tasks

1.  **Create a Resilient Subclass:**
    *   In your `support_analyzer/agent.py`, create a class named `ResilientGemini` that inherits from `Gemini`.
    *   Override the `api_client` property.
    *   Configure it with a `HttpRetryOptions` policy: `max_delay=10`, `exp_base=2.0`, and `jitter=0.5`.

2.  **Implement Multi-Model Fallback:**
    *   Update your agent's `model` logic.
    *   If the environment variable `USE_LOCAL_MODEL` is set to `"1"`, use `LiteLlm` with `ollama_chat/mistral`.
    *   Otherwise, use your new `ResilientGemini` class.

3.  **Verify the Configuration:**
    *   Run the agent using `adk run support_analyzer`.
    *   Verify it works as expected. (Note: You won't "see" the retries unless a network error occurs, but your code is now protected!).

### Python Approach (Primary)
Modify `agent.py` to use the advanced configuration patterns.

```python
import os
from functools import cached_property
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.models.lite_llm import LiteLlm
from google.genai import Client, types

# TODO: Step 1 - Define the ResilientGemini subclass
class ResilientGemini(Gemini):
    @cached_property
    def api_client(self) -> Client:
        # TODO: Implement Client with HttpRetryOptions
        pass

# TODO: Step 2 - Implement the model selection logic
if os.getenv("USE_LOCAL_MODEL") == "1":
    # Use LiteLLM
    model_to_use = ...
else:
    # Use your ResilientGemini
    model_to_use = ...

root_agent = LlmAgent(
    name="support_analyzer_agent",
    model=model_to_use,
    instruction="Analyze customer support issues."
)
```

## Self-Reflection Questions
- Why is "Jitter" important in a retry policy for a high-traffic production application?
- What are the advantages of centralizing model configuration in a subclass instead of passing parameters to every agent instance?
- In which scenario would you prefer using the native `Gemini` class over the `LiteLlm` abstraction?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMDQuNS1tdWx0aS1tb2RlbC1saXRlbGxtL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module04_5-multi-model-litellm/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
