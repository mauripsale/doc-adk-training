---
sidebar_position: 2
title: "Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 4 Challenge: Customer Support Analyzer

## Goal
Your task is to build a **"Support Analyzer"** agent. Instead of returning plain text, the agent must analyze the user's support ticket and return a JSON object containing the categorization, sentiment, and a brief summary of the issue.

## Lab Tasks

<Setup/>

1.  Open your terminal, ensure you are in your `adk-training` directory, and run the following command to scaffold a new agent:
    ```shell
    uv run adk create support_analyzer
    ```
2.  Navigate into the newly created `support_analyzer` directory.
3.  **Define a Pydantic Schema:** In `agent.py`, create a class named `SupportAnalysis` that defines three fields:
    *   `category`: A string (e.g., "billing", "technical", "general").
    *   `sentiment`: A string (e.g., "positive", "negative", "neutral").
    *   `summary`: A string containing a 1-sentence summary of the user's issue.
4.  **Update the Agent Configuration:**
    *   Set the `output_schema` to your `SupportAnalysis` class.
    *   Set the `output_key` to `"last_ticket_analysis"`.
5.  **Refine Instructions:** Update the agent's `instruction` to ensure it understands its job is to extract these three specific pieces of information from the user's input.
6.  **Run and Verify:** Run the agent using `uv run adk web support_analyzer` (from the parent directory). In the Dev UI, test it with a phrase like *"My screen is completely broken and I'm very angry about it!"* and verify the response is a valid JSON object.
7.  **Inspect State:** After a few interactions, check the "Session State" in the Dev UI to confirm that `"last_ticket_analysis"` is being populated correctly.

### Python Approach (Primary)
Modify `agent.py` to include the Pydantic model and updated `Agent` parameters.

```python
from pydantic import BaseModel
from google.adk import Agent

# TODO: Define your Pydantic schema
class SupportAnalysis(BaseModel):
    # TODO: Add fields (category, sentiment, summary)
    pass

root_agent = Agent(
    name="support_analyzer_agent",
    model="gemini-3.5-flash",
    instruction="...", # TODO: Update instructions for categorization, sentiment, and summary
    output_schema=...,  # TODO: Link the schema
    output_key=...      # TODO: Set the output key
)
```

### Self-Reflection Questions
- Why is it better to use `output_schema` instead of just asking the LLM to "respond in JSON" in the text instructions?
- Can the agent still call tools while `output_schema` is set? What exactly does `output_schema` constrain, and what does it leave free?
- Look at the Dev UI's "Session State". How could another agent in a future multi-agent system use the data stored in the `"last_ticket_analysis"` key?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMDQtYWdlbnQtZGVlcC1kaXZlL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module04-agent-deep-dive/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
