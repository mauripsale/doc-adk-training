---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 17: Structured Routing (Edges & Dicts) — 🧪 Challenge Lab"
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

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="17">

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
    model="gemini-3.8-flash",
    instruction="Extract the currency (USD, EUR, or GBP) from the user's request. Return ONLY the JSON.",
    output_schema=MarketRoute
)

# 3. Create Specialist Agents (Nodes)
usd_analyst = Agent(
    name="usd_analyst",
    model="gemini-3.8-flash",
    instruction="Provide a brief, bullish outlook for the US Dollar."
)

eur_analyst = Agent(
    name="eur_analyst",
    model="gemini-3.8-flash",
    instruction="Provide a brief, cautious outlook for the Euro."
)

gbp_analyst = Agent(
    name="gbp_analyst",
    model="gemini-3.8-flash",
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

</SolutionVault>
