---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 16: Static Orchestration (Linear & Parallel) — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 16: Building a Hybrid News Aggregator

## Goal

In this lab, you will build a sophisticated **News Aggregator** using a hybrid graph architecture. You will learn how to:
1.  Run two specialized research nodes in **parallel** (Fan-out).
2.  Synchronize the results using a **JoinNode** (Fan-in).
3.  Process the combined data in a **sequential** step.

### The Architecture

```
        ┌──── Node A (Tech News) ────┐
START ──┼                           ├──→ JoinNode → Summarizer → END
        └──── Node B (Market News) ──┘
```

### Step 1: Create the Project

<Setup/>

```bash
uv run adk create news_aggregator
cd news_aggregator
```

### Step 2: Implement the Specialist Nodes

Open `agent.py`. Your task is to define three agents: two for research and one for synthesis.

```python
# In agent.py (Starter Code)
from google.adk import Agent, Workflow
from google.adk.workflow import JoinNode

# TODO: Define 'tech_researcher'
# Instruction: Find 3 headlines about AI and Robotics.
# Output key: "tech_news"
tech_researcher = ...

# TODO: Define 'market_researcher'
# Instruction: Find 3 headlines about Stock Market trends.
# Output key: "market_news"
market_researcher = ...

# TODO: Define 'summarizer'
# Instruction: Combine {tech_news} and {market_news} into a newsletter.
summarizer = ...
```

### Step 3: Assemble the Hybrid Graph

**Exercise:** Complete the `root_agent` definition using the `edges` parameter to implement the Fan-out/Join pattern.

> **Tip:** A 3-element edge tuple `(A, B, C)` is shorthand for two chained edges, `A → B` and `B → C`. So a parallel branch that both starts at `"START"` and converges on the `syncer` can be written as one tuple, `("START", tech_researcher, syncer)`, instead of two separate tuples.

```python
# 1. Create the synchronization point
syncer = JoinNode(name="news_sync")

# 2. Build the Workflow
# TODO: Define the edges to:
# - Start both researchers in parallel from "START".
# - Converge both researchers at the 'syncer'.
# - Connect the 'syncer' to the 'summarizer'.
root_agent = Workflow(
    name="NewsSystem",
    edges=[
        # Parallel Branch 1
        ("START", ..., ...),
        
        # Parallel Branch 2
        (..., ..., ...),
        
        # Sequential Final Step
        (..., ...)
    ]
)
```

### Step 4: Run and Verify

1.  **Start the Dev UI:** `uv run adk web .`
2.  **Test:** Send the prompt "Give me today's update."
3.  **Inspect:** Open the **Graph View**. Verify that the researchers start at the same time and the summarizer only runs after both finish.

> **Known issue (upstream `google-adk` 2.8.0):** the main static **Graph View** tab works fine for `Workflow`/`JoinNode` graphs like this one. However, clicking into an individual event's Graph inspector (the per-event highlight view in the Trace) currently throws a 500 error -- `AttributeError: 'Workflow' object has no attribute '_graph'` -- for this graph type specifically. This is an upstream ADK tooling bug, not something you did wrong. Workaround: use the main Graph View tab to inspect the overall structure instead of the per-event inspector.

### Lab Summary

You have built a hybrid multi-agent graph!
- You mastered **Fan-out** by defining multiple edges from START.
- You mastered **Fan-in** using the **`JoinNode`**.
- You learned that sequential and parallel execution are just different edge configurations.
- **A few things worth internalizing:** the `JoinNode` waits for *every* incoming edge -- if one parallel branch fails, it won't fire, so production graphs need retry/error handling to guarantee convergence. Adding a third parallel branch (e.g. a `sports_researcher`) is just one more `("START", sports_researcher, syncer)` edge -- the `syncer` automatically waits for all of them. And `output_key` matters specifically *because* a `JoinNode` merges multiple upstream outputs into one: it saves each branch's result into session state under its own name, so the `summarizer` can reliably pull `{tech_news}` and `{market_news}` as separate variables instead of one ambiguous blob.

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="16">

# Lab 16 Solution: Building a Hybrid News Aggregator

## Goal

This file contains the complete code for the `agent.py` script using the ADK 2.0 Hybrid Graph pattern (Sequential + Parallel).

### `news_aggregator/agent.py`

```python
from google.adk import Agent, Workflow
from google.adk.workflow import JoinNode

# 1. Define Specialist Nodes
tech_researcher = Agent(
    name="tech_researcher",
    model="gemini-3.8-flash",
    instruction="Find 3 exciting headlines about AI and Robotics. Be concise.",
    output_key="tech_news"
)

market_researcher = Agent(
    name="market_researcher",
    model="gemini-3.8-flash",
    instruction="Find 3 key headlines about Stock Market trends. Be concise.",
    output_key="market_news"
)

summarizer = Agent(
    name="summarizer",
    model="gemini-3.8-flash",
    instruction="""
    You are a news editor. Create a brief newsletter using the data provided:
    TECH: {tech_news}
    MARKET: {market_news}
    
    Synthesize the information into a single, cohesive daily briefing.
    """
)

# 2. Define the Synchronization Point
syncer = JoinNode(name="news_sync")

# 3. Assemble the Workflow
# Parallel Fan-out + Sequential Fan-in
root_agent = Workflow(
    name="NewsSystem",
    edges=[
        # Both start at the same time and connect to the same JoinNode
        ("START", tech_researcher, syncer),
        ("START", market_researcher, syncer),
        
        # Once both are done, the syncer triggers the summarizer
        (syncer, summarizer)
    ]
)
```

### Self-Reflection Answers

1.  **What happens if one of the parallel researchers fails?**
    *   **Answer:** By default, the `JoinNode` waits for ALL incoming edges. If one fails, the `JoinNode` will not fire its outgoing edge, potentially stalling the workflow. In production, you would add retry logic or error handling to ensure the graph can still converge.

2.  **Can I add a third researcher (e.g., 'sports_researcher')?**
    *   **Answer:** Yes! You just define the agent and add a third edge: `("START", sports_researcher, syncer)`. The syncer will automatically wait for all three.

3.  **Why use `output_key` if data flows automatically?**
    *   **Answer:** While ADK 2.0 passes the output of one node to the next, a `JoinNode` receives multiple outputs. Using `output_key` saves individual results into the global session state, making it much easier for the `summarizer` to access specific variables like `{tech_news}` via string interpolation.

</SolutionVault>
