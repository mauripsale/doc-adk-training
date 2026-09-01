---
sidebar_position: 6
title: "Challenge Lab"
---

import { ChainSetup } from '../_chain-setup-snippet.mdx';

# Lab 4.5 Challenge: Professional Model Configuration, Resiliency & Portability

## Goal
In this lab, you will upgrade your **"Support Analyzer"** agent to a production-ready state, in place -- keeping its Module 4 structured-output contract (`SupportAnalysis`, `output_schema`, `output_key`) fully working. You will learn how to implement advanced retry logic using a custom `Gemini` subclass and how to provide a multi-model fallback using `LiteLlm`, layered on top of the agent you already built.

## Prerequisites

<ChainSetup module={4} project="support_analyzer" />

1.  **Navigate to your `support_analyzer` project and install LiteLLM:**
    ```shell
    cd /path/to/your/adk-training/support_analyzer
    uv add "litellm==1.96.0"
    ```
    > **Note:** We pin to `litellm==1.96.0` here. Newer `litellm` releases (1.97.0+, as of this writing) have known issues on Python 3.10 — 1.98.0 raises `ImportError: cannot import name 'NotRequired' from 'typing'` the moment the `LiteLlm` model path is actually exercised, and 1.97.0 hits an unrelated Pydantic model-definition error. `1.96.0` has been verified to work cleanly with `google-adk` on Python 3.10.

## Lab Tasks

1.  **Create a Resilient Subclass:**
    *   In your `support_analyzer/agent.py`, create a class named `ResilientGemini` that inherits from `Gemini`.
    *   Override the `api_client` property.
    *   Configure it with a `HttpRetryOptions` policy: `max_delay=10`, `exp_base=2.0`, and `jitter=0.5`.

2.  **Implement Multi-Model Fallback:**
    *   Update your agent's `model` logic.
    *   If the environment variable `USE_LOCAL_MODEL` is set to `"1"`, use `LiteLlm` with `ollama_chat/mistral`.
    *   Otherwise, use your new `ResilientGemini` class.

3.  **Keep the Module 4 structured output intact:**
    *   Your `SupportAnalysis` Pydantic model, `output_schema=SupportAnalysis`, and `output_key="last_ticket_analysis"` from Module 4 should still be set on `root_agent` -- you're only changing *which model* powers the agent, not the fact that it returns structured JSON.

4.  **Verify the Configuration:**
    *   Run the agent using `uv run adk run support_analyzer`.
    *   Verify it still returns a schema-conforming JSON response, exactly like it did at the end of Module 4. (Note: You won't "see" the retries unless a network error occurs, but your code is now protected!).

### Python Approach (Primary)
Modify `agent.py` to use the advanced configuration patterns, on top of the `SupportAnalysis` schema you already built in Module 4.

```python
import os
from functools import cached_property
from pydantic import BaseModel
from google.adk import Agent
from google.adk.models import Gemini
from google.adk.models.lite_llm import LiteLlm
from google.genai import Client, types

# Carried over from Module 4 -- keep this working!
class SupportAnalysis(BaseModel):
    category: str
    sentiment: str
    summary: str

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

root_agent = Agent(
    name="support_analyzer_agent",
    model=model_to_use,
    instruction="Analyze customer support issues.",
    output_schema=SupportAnalysis,  # TODO: Keep this from Module 4
    output_key="last_ticket_analysis",  # TODO: Keep this from Module 4
)
```

## Self-Reflection Questions
- Why is "Jitter" important in a retry policy for a high-traffic production application?
- What are the advantages of centralizing model configuration in a subclass instead of passing parameters to every agent instance?
- In which scenario would you prefer using the native `Gemini` class over the `LiteLlm` abstraction?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMDRfNS1tdWx0aS1tb2RlbC1saXRlbGxtL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module04_5-multi-model-litellm/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
