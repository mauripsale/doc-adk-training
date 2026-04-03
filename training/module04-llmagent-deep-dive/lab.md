---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 4 Challenge: Structured Haiku & Sentiment Analysis

## Goal
Your task is to evolve your "Haiku Poet" agent into a **"Structured Analyzer"**. Instead of returning plain text, the agent must now analyze the user's message and return a JSON object containing both a haiku and a sentiment analysis of the input.

## Requirements
1.  Navigate into your `haiku_poet_agent` directory (created by duplicating `echo_agent`).
2.  **Define a Pydantic Schema:** Create a class named `HaikuAnalysis` that defines two fields:
    *   `haiku`: A string containing the 5-7-5 poem.
    *   `sentiment`: A string (e.g., "positive", "negative", or "neutral").
3.  **Update the Agent Configuration:**
    *   Set the `output_schema` to your `HaikuAnalysis` class.
    *   Set the `output_key` to `"last_analysis"`.
4.  **Refine Instructions:** Update the agent's `instruction` to ensure it understands it must now categorize the sentiment in addition to writing the haiku.
5.  **Run and Verify:** Run the agent using `adk web haiku_poet_agent`. In the Dev UI, verify that the response is a valid JSON object.
6.  **Inspect State:** After a few interactions, check the "Session State" in the Dev UI to confirm that `"last_analysis"` is being populated correctly.

### Python Approach (Primary)
Modify `agent.py` to include the Pydantic model and updated `LlmAgent` parameters.

```python
from pydantic import BaseModel
from google.adk.agents import LlmAgent

# TODO: Define your Pydantic schema
class HaikuAnalysis(BaseModel):
    # TODO: Add fields
    pass

root_agent = LlmAgent(
    name="haiku_analyzer_agent",
    model="gemini-2.5-flash",
    instruction="...", # TODO: Update instructions for sentiment + haiku
    output_schema=...,  # TODO: Link the schema
    output_key=...      # TODO: Set the output key
)
```

### Self-Reflection Questions
- Why is it better to use `output_schema` instead of just asking the LLM to "respond in JSON" in the text instructions?
- What happened to the agent's ability to use tools once you enabled `output_schema`? Why does the ADK enforce this restriction?
- Look at the Dev UI's "Session State". How could another agent in a future multi-agent system use the data stored in the `"last_analysis"` key?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMDQtbGxtYWdlbnQtZGVlcC1kaXZlL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module04-llmagent-deep-dive/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
