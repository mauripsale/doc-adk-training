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
from google.adk import Agent, Workflow, Context
from google.adk.workflow import node
from typing import Literal

# 1. Define the Classification Schema
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

# 4. Wrap the classifier so it can set ctx.route.
# A plain Agent never sets ctx.route on its own, even with a Pydantic
# output_schema -- this small @node wrapper is what makes the Router
# Dictionary below actually work.
@node(rerun_on_resume=True)
async def classify_and_route(ctx: Context, node_input: str):
    result = await ctx.run_node(classifier, node_input)  # a dict, not a MarketRoute instance
    ctx.route = result["currency"]
    return node_input

# 5. Build the Deterministic Workflow
# The 'edges' list defines the explicit structure of the graph.
root_agent = Workflow(
    name="MarketSystem",
    edges=[
        # Rule 1: The workflow always starts by running classify_and_route.
        ("START", classify_and_route),
        
        # Rule 2: Route based on the ctx.route value classify_and_route set.
        (classify_and_route, {
            "USD": usd_analyst,
            "EUR": eur_analyst,
            "GBP": gbp_analyst
        })
    ]
)
```

### Self-Reflection Answers

1.  **What happens if `classify_and_route` sets `ctx.route` to a value that isn't in your dictionary (e.g., "JPY")?**
    *   **Answer:** No edge matches, so the branch simply ends there — the workflow logs a warning ("Node ... has conditional/DEFAULT edges but none were matched") and no specialist ever runs. This is why using `Literal` in the Pydantic schema matters: it constrains what the classifier can legally output, which is what `ctx.route` gets set to, minimizing (though not eliminating — a mismatch between your `Literal` values and your dictionary keys is still possible) the chance of an unmatched route.

2.  **Can you add an `"other"` key to the dictionary to handle unknown inputs?**
    *   **Answer:** Yes! You could update your `MarketRoute` schema to include `"OTHER"` and then add a corresponding entry in the `edges` dictionary to point to a general-purpose agent. Since `ctx.route` is set explicitly by your own code in `classify_and_route`, you could even add a fallback there — e.g. `ctx.route = result.get("currency", "OTHER")` — as an extra safety net regardless of what the schema allows.

3.  **`classify_and_route` is a `@node` function, just like in Module 18 -- so what's actually different about this pattern compared to a full Dynamic Workflow?**
    *   **Answer:** The scope of the hand-written code. In this lab, exactly one `@node` function exists, and its only job is to run the classifier and set `ctx.route` — the *routing itself* (which specialist runs next) is still declared in the `Workflow`'s `edges`, visible at a glance and shown in the Dev UI's Graph View. In a full Dynamic Workflow (Module 18), the orchestrator node contains the `if`/`else` routing logic itself, so the destination of a branch is only knowable by reading the Python code, not by looking at a graph. This pattern is a middle ground: you pay the small one-time cost of a `@node` wrapper to get an LLM classification into `ctx.route`, but the actual multi-way branching stays declarative.
