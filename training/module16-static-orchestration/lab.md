---
sidebar_position: 2
title: "Challenge Lab"
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

### Lab Summary

You have built a hybrid multi-agent graph!
- You mastered **Fan-out** by defining multiple edges from START.
- You mastered **Fan-in** using the **`JoinNode`**.
- You learned that sequential and parallel execution are just different edge configurations.

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMTYtc3RhdGljLW9yY2hlc3RyYXRpb24vbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module16-static-orchestration/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
