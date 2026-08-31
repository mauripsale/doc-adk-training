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
from google.adk import Agent

# Define the structured output schema
class SupportAnalysis(BaseModel):
    category: str
    sentiment: str
    summary: str

# Define the root agent with ADK 2.0 structured features
root_agent = Agent(
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

2.  **Can the agent still call tools while `output_schema` is set? What exactly does `output_schema` constrain, and what does it leave free?**
    *   **Answer:** Yes -- ADK 2.0 supports using `output_schema` and `tools` together. The agent can still call tools freely during its thought loop to gather information; `output_schema` only constrains the *final* response, forcing it to validate against the Pydantic model. So the reasoning/tool-use phase is unrestricted, and structure is enforced only at the very last step, when the agent produces its answer.

3.  **Look at the Dev UI's "Session State". How could another agent in a future multi-agent system use the data stored in the `"last_ticket_analysis"` key?**
    *   **Answer:** In a multi-agent workflow (like a `Workflow` with sequential edges), the next node in the chain can access `ctx.session.state["last_ticket_analysis"]`. For example, if the category is "billing", the workflow could route the user to a Billing Agent. If the sentiment is "negative," it could route them to a Human Escalation Agent, all without having to re-parse the original message.
