---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 21.6: Building a Market Analyst with Deterministic Edges

## Goal

In this lab, you will build a structured workflow that analyzes currency conversion requests. You will use a **Deterministic Workflow** with explicit edges to create a pipeline that classifies a request and routes it to a specific specialist tool.

This demonstrates how to create predictable AI pipelines in ADK 2.0 without writing complex routing code.

### Step 1: Create the Project

1.  **Create a new project:**
    ```shell
    uv run adk create market_analyst
    ```
2.  **Navigate into the directory:**
    ```shell
    cd market_analyst
    ```

### Step 2: Define the Specialist Nodes

Open `agent.py`. We will create three main components:
1.  **A Classifier Agent:** To detect the target currency.
2.  **Specialist Tools:** To handle the "market analysis" (simulated).

```python
from __future__ import annotations
from pydantic import BaseModel
from google.adk import Agent, Workflow, Context, Event
from typing import Literal

# 1. Define the Classification Schema
class MarketRoute(BaseModel):
    # The output of this agent must be one of these keys for the router to work!
    currency: Literal["USD", "EUR", "GBP"]

# 2. Create the Classifier Node
# TODO: Define the 'classifier' agent.
# Use MarketRoute as output_schema.
# Write instructions to extract the currency (USD, EUR, or GBP).
classifier = ...

# 3. Create Specialist Agents (Nodes)
# TODO: Define usd_analyst, eur_analyst, and gbp_analyst.
# Give each one a brief, unique instruction for their currency.
usd_analyst = ...
eur_analyst = ...
gbp_analyst = ...
```

### Step 3: Build the Deterministic Workflow

**Exercise:** Complete the `root_agent` definition using the `edges` parameter. 

You need to:
1.  Connect `"START"` to the `classifier`.
2.  Create a **Router Dictionary** that connects the `classifier` to the three specialist agents based on the `currency` field in the `MarketRoute` object.

```python
# TODO: Complete the Workflow definition
root_agent = Workflow(
    name="MarketSystem",
    edges=[
        # Edge 1: Start at the classifier
        ("START", ...),
        
        # Edge 2: Route based on classifier output
        (classifier, {
            "USD": ...,
            "EUR": ...,
            "GBP": ...
        })
    ]
)
```

### Step 4: Run and Test

1.  **Launch the Dev UI:**
    ```shell
    uv run adk web .
    ```
2.  **Test the routing:**
    - "What is happening with the Dollar?" -> Should run `usd_analyst`.
    - "Give me news on the Euro." -> Should run `eur_analyst`.
3.  **Inspect the Graph:**
    Observe how ADK 2.0 visualizes the deterministic paths in the **Graph View**.

### Lab Summary

You have successfully built a deterministic workflow!
- You used **Pydantic** to ensure the classifier's output matches your router keys.
- You defined **explicit edges** to create a transparent execution graph.
- You learned that ADK 2.0 handles the data passing between nodes automatically.

### Self-Reflection Questions
- What happens if the `classifier` returns a value that isn't in your dictionary (e.g., "JPY")?
- Can you add an `"other"` key to the dictionary to handle unknown inputs?
- How does this approach compare to the `@node` dynamic workflow in terms of code complexity?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMTctc3RydWN0dXJlZC1yb3V0aW5nL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module17-structured-routing/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
