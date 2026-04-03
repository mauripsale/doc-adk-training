---
sidebar_position: 6
title: "Challenge Lab"
---

# Lab 4.5 Challenge: Switching Between LLM Providers

## Goal
In this lab, you will learn how to make your ADK agents model-agnostic. You will build a single agent and test it using different models from different providers (e.g., Gemini and Ollama/Mistral) using the `LiteLlm` wrapper.

## Requirements

1.  **Prepare the Environment:**
    *   Install the required dependency:
        ```shell
        pip install litellm
        ```
    *   (Optional but recommended) Ensure you have [Ollama](https://ollama.com/) installed and running with the `mistral` model:
        ```shell
        ollama run mistral
        ```

2.  **Scaffold the Agent:**
    *   Create a new agent named `multi_model_agent`:
        ```shell
        adk create multi_model_agent
        ```
    *   Navigate into the directory: `cd multi_model_agent`

3.  **Implement the Agent using `LiteLlm`:**
    *   Open `agent.py`.
    *   Import `LiteLlm` from `google.adk.models`.
    *   Define a `root_agent` that uses a `LiteLlm` instance instead of a string.
    *   **Task 1:** Configure it to use `ollama_chat/mistral` (or another local model you have).
    *   **Task 2:** Update your `.env` file with any necessary keys (if testing OpenAI/Anthropic).

4.  **Verify the Switch:**
    *   Run the agent using `adk web multi_model_agent`.
    *   Check your terminal logs. When using Ollama, you should see the local server receiving the requests.
    *   Switch the `model` parameter back to a Gemini string (e.g., `"gemini-1.5-flash"`) and verify it still works.

### Python Skeleton (`agent.py`)

```python
from google.adk.agents import LlmAgent
from google.adk.models import LiteLlm

# TODO: Initialize the LiteLlm wrapper for a local model
local_model = LiteLlm(model="ollama_chat/mistral")

# TODO: Define the root agent
root_agent = LlmAgent(
    name="multi_model_agent",
    model=local_model, # Using the wrapper
    instruction="You are a helpful assistant that knows which model is powering you."
)
```

### Self-Reflection Questions
- How does the `LiteLlm` integration simplify the process of testing an agent with different models?
- If you were deploying an agent to production, what are the security implications of using an external provider like OpenAI versus a local model like Ollama?
- Why is it important for the ADK to remain "model-agnostic"?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMDQuNS1tdWx0aS1tb2RlbC1saXRlbGxtL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module04.5-multi-model-litellm/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
