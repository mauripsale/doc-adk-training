---
sidebar_position: 2
title: "Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 17: Building a Market Analyst with Deterministic Edges

## Goal

In this lab, you will build a structured workflow that analyzes currency conversion requests. You will use a **Deterministic Workflow** with explicit edges to create a pipeline that classifies a request and routes it to a specific specialist tool.

This demonstrates how to create predictable AI pipelines in ADK 2.0 with just a few lines of routing glue code, instead of hand-writing full `if`/`else` orchestration for every branch.

### Step 1: Create the Project

<Setup/>

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
from google.adk import Agent, Workflow, Context
from google.adk.workflow import node
from typing import Literal

# 1. Define the Classification Schema
class MarketRoute(BaseModel):
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

# 4. Wrap the classifier so it can set ctx.route.
# A plain Agent never sets ctx.route on its own -- not even with a Pydantic
# output_schema -- so a small @node wrapper is what makes the Router
# Dictionary below actually work.
# TODO: Complete this function:
#   a. Call `await ctx.run_node(classifier, node_input)` and store the result.
#      Note: the result comes back as a plain dict, e.g. {"currency": "EUR"},
#      even though MarketRoute is a Pydantic model.
#   b. Set `ctx.route` to the "currency" value from that dict.
#   c. Return node_input (unchanged) so the chosen specialist still receives
#      the original user request.
@node(rerun_on_resume=True)
async def classify_and_route(ctx: Context, node_input: str):
    ...
```

### Step 3: Build the Deterministic Workflow

**Exercise:** Complete the `root_agent` definition using the `edges` parameter. 

You need to:
1.  Connect `"START"` to `classify_and_route` (not `classifier` directly -- it's the wrapper that sets `ctx.route`).
2.  Create a **Router Dictionary** that connects `classify_and_route` to the three specialist agents based on the route it set.

```python
# TODO: Complete the Workflow definition
root_agent = Workflow(
    name="MarketSystem",
    edges=[
        # Edge 1: Start at the classify_and_route node
        ("START", ...),
        
        # Edge 2: Route based on ctx.route
        (classify_and_route, {
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
- You used **Pydantic** to ensure the classifier's output is one of your router keys.
- You learned that Router Dictionaries match against `ctx.route`, not a node's raw output -- and that a plain `Agent` needs a small `@node` wrapper to set it.
- You defined **explicit edges** to create a transparent execution graph, where only the classifier needed custom code and the specialist branches stayed fully declarative.

### Self-Reflection Questions
- What happens if `classify_and_route` sets `ctx.route` to a value that isn't in your dictionary (e.g., "JPY")?
- Can you add an `"other"` key to the dictionary to handle unknown inputs?
- `classify_and_route` is a `@node` function, just like in Module 18 -- so what's actually different about this pattern compared to a full Dynamic Workflow?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMTctc3RydWN0dXJlZC1yb3V0aW5nL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module17-structured-routing/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
