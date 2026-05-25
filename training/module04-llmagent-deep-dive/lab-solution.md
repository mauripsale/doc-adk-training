---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 4 Solution: Customer Support Analyzer

## Goal

In this lab, we built a Customer Support Analyzer. We used a Pydantic schema to force the agent to return structured data (JSON) containing the ticket category, sentiment, and summary, and we used `output_key` to persist that data in the session state.

### `support_analyzer/agent.py`

```python
from pydantic import BaseModel
from google.adk.agents import LlmAgent

# Define the structured output schema
class SupportAnalysis(BaseModel):
    category: str
    sentiment: str
    summary: str

# Define the root agent with v1.0 structured features
root_agent = LlmAgent(
    name="support_analyzer_agent",
    model="gemini-3.5-flash",
    description="An agent that categorizes customer support tickets and extracts sentiment.",
    instruction="""
      You are an expert customer support analyzer. Your task is to:
      1. Determine the category of the user's issue ("billing", "technical", or "general").
      2. Analyze the sentiment of the message ("positive", "negative", or "neutral").
      3. Write a concise, 1-sentence summary of the user's issue.
      
      You MUST respond only with a JSON object matching the requested schema. Do not try to solve their problem.
    """,
    output_schema=SupportAnalysis, # Force the LLM to follow the Pydantic model
    output_key="last_ticket_analysis" # Automatically save the JSON to session state
)
```

### Key Changes Explained

1.  **Pydantic Model:** By defining `SupportAnalysis`, we create a formal contract for the agent's output. The ADK uses this to tell the model exactly how to format the JSON.
2.  **`output_schema`:** This parameter activates the "Structured Output" mode. It simplifies parsing because the ADK handles the validation. If the model returns malformed JSON, the ADK will automatically try to correct it (or throw a clear error).
3.  **`output_key`:** By setting this to `"last_ticket_analysis"`, every time the agent finishes a turn, the resulting JSON is stored in `ctx.session.state["last_ticket_analysis"]`. This makes the data available for debugging or for other agents in the same session.

### Self-Reflection Answers

1.  **Why is it better to use `output_schema` instead of just asking the LLM to "respond in JSON" in the text instructions?**
    *   **Answer:** While text instructions work occasionally, they are unreliable. LLMs often add preamble (e.g., "Sure, here is your JSON:") or slightly vary the keys. `output_schema` leverages the model's native constrained decoding capabilities (when supported) or applies strict validation and automatic retries by the ADK, ensuring the output is always 100% valid JSON that your code can depend on.

2.  **What happened to the agent's ability to use tools once you enabled `output_schema`? Why does the ADK enforce this restriction?**
    *   **Answer:** The agent can no longer use tools. The ADK enforces this because structured output mode optimizes the model's generation process specifically for following a schema. Mixing tool-calling (which involves a separate "reasoning" loop) with strict JSON generation is complex and error-prone. If you need both, you should use a multi-agent system: one agent to use tools and another to format the final result into JSON.

3.  **Look at the Dev UI's "Session State". How could another agent in a future multi-agent system use the data stored in the `"last_ticket_analysis"` key?**
    *   **Answer:** In a multi-agent workflow (like a `SequentialAgent`), the next agent in the chain can access `ctx.session.state["last_ticket_analysis"]`. For example, if the category is "billing", the workflow could route the user to a Billing Agent. If the sentiment is "negative," it could route them to a Human Escalation Agent, all without having to re-parse the original message.
