---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 17 Solution: Market Analyst with Deterministic Edges

## Goal

This file contains the complete code for the `agent.py` script using the ADK 2.0 Deterministic Workflow pattern.

### `market_analyst/agent.py`

```python
from __future__ import annotations
from pydantic import BaseModel
from google.adk import Agent, Workflow
from typing import Literal

# 1. Define the Classification Schema
# Using Pydantic is CRITICAL here because the Workflow router 
# matches the node's output against the dictionary keys.
class MarketRoute(BaseModel):
    currency: Literal["USD", "EUR", "GBP"]

# 2. Create the Classifier Node
classifier = Agent(
    name="classifier",
    model="gemini-3.5-flash",
    instruction="Extract the currency (USD, EUR, or GBP) from the user's request. Return ONLY the JSON.",
    output_schema=MarketRoute
)

# 3. Create Specialist Agents (Nodes)
usd_analyst = Agent(
    name="usd_analyst",
    model="gemini-3.5-flash",
    instruction="Provide a brief, bullish outlook for the US Dollar."
)

eur_analyst = Agent(
    name="eur_analyst",
    model="gemini-3.5-flash",
    instruction="Provide a brief, cautious outlook for the Euro."
)

gbp_analyst = Agent(
    name="gbp_analyst",
    model="gemini-3.5-flash",
    instruction="Provide a brief, neutral outlook for the British Pound."
)

# 4. Build the Deterministic Workflow
# The 'edges' list defines the explicit structure of the graph.
# Tip: You can use the agent object directly or its name as a string (e.g., "usd_analyst").
root_agent = Workflow(
    name="MarketSystem",
    edges=[
        # Rule 1: The workflow always starts by running the classifier.
        ("START", classifier),
        
        # Rule 2: Route the output of the classifier to a specialist.
        # ADK 2.0 automatically looks at the 'currency' field of the 
        # MarketRoute object returned by the classifier.
        (classifier, {
            "USD": usd_analyst,
            "EUR": eur_analyst,
            "GBP": gbp_analyst
        })
    ]
)
```

### Self-Reflection Answers

1.  **What happens if the `classifier` returns a value that isn't in your dictionary (e.g., "JPY")?**
    *   **Answer:** The workflow will fail with a routing error because the graph engine doesn't know where to go next. This is why using `Literal` in Pydantic is so important—it forces the LLM to choose from your defined paths.

2.  **Can you add an `"other"` key to the dictionary to handle unknown inputs?**
    *   **Answer:** Yes! You could update your `MarketRoute` schema to include `"OTHER"` and then add a corresponding entry in the `edges` dictionary to point to a general-purpose agent.

3.  **How does this approach compare to the `@node` dynamic workflow in terms of code complexity?**
    *   **Answer:** The deterministic `Workflow` is much more concise for simple routing. You don't have to write `async def`, handle `Context`, or manually call `await ctx.run_node()`. The framework handles all the plumbing for you. However, it is less flexible if you need complex Python logic (like loops) between nodes.
