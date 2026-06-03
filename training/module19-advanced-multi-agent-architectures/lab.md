---
sidebar_position: 2
title: "Challenge Lab"
---

# Module 19: Advanced Multi-Agent Architectures

## Lab 19: Building a Content Publishing System

### Goal

In this lab, you will build a sophisticated **Content Publishing System** that demonstrates a complex multi-agent architecture. You will combine sequential and parallel patterns to create a system that researches a topic from multiple angles concurrently and then synthesizes the findings into a final article. This is a capstone exercise for the multi-agent section of the course.

### The Architecture

1.  **Phase 1: Parallel Research (Fan-Out)**
    Three independent, sequential sub-workflows will run concurrently:
    *   **News Workflow:** Fetches current events, then summarizes the key points.
    *   **Social Workflow:** Gathers trending topics, then analyzes the insights.
    *   **Expert Workflow:** Finds expert opinions, then extracts key quotes.

2.  **Phase 2: Content Creation (Gather)**
    Once all sub-workflows complete at a **JoinNode**, a final sequence of agents runs:
    *   **Writer Agent:** Combines all research into a draft.
    *   **Editor Agent:** Reviews and improves the draft.
    *   **Formatter Agent:** Formats the final article.

### Step 2: Assemble the Nested Workflows

**Exercise:** Open `agent.py`. Your task is to assemble the agents into **Sub-Workflows** and then combine them into a **Root Workflow**.

```python
# In agent.py (Starter Code)

from google.adk import Agent, Workflow
from google.adk.workflow import JoinNode

# [Specialist Agents are provided for you...]

# =====================================================
# ASSEMBLE THE SUB-WORKFLOWS
# =====================================================

# TODO: 1. Create the three sequential research sub-workflows.
# Use linear edges for each.
news_workflow = Workflow(
    name="NewsWorkflow",
    edges=[("START", news_fetcher, news_summarizer)]
)

# TODO: Create social_workflow and expert_workflow
social_workflow = Workflow(...)
expert_workflow = Workflow(...)

# =====================================================
# ASSEMBLE THE ROOT WORKFLOW
# =====================================================

# TODO: 2. Create a JoinNode to synchronize the research branches.
research_joiner = JoinNode(name="research_joiner")

# TODO: 3. Create the root workflow.
# - Fan-out from START to each sub-workflow, then to the joiner.
# - From joiner, run writer -> editor -> formatter.
root_agent = Workflow(
    name="ContentPublishingSystem",
    edges=[
        # Parallel Research Phase
        ("START", news_workflow, research_joiner),
        ("START", ..., ...),
        ("START", ..., ...),
        
        # Sequential Creation Phase
        (research_joiner, article_writer, article_editor, article_formatter)
    ]
)
```

### Step 3: Run and Test the System

1.  **Start the Dev UI:**
    ```shell
    adk web .
    ```
2.  **Analyze the Trace:**
    Expand the trace in the Dev UI. You will see "sub-traces" for each of the three research workflows. Notice how they run in parallel, and how the root workflow waits for all of them at the `research_joiner` before proceeding to the writer.


### Having Trouble?

If you get stuck, you can find the complete, working code in the `lab-solution.md` file.

### Lab Summary

You have successfully built and orchestrated a complex, production-quality multi-agent system. You have learned:
*   How to nest `SequentialAgent` workflows inside a `ParallelAgent`.
*   How to combine parallel and sequential patterns to create a fan-out/gather architecture.
*   How to analyze the execution of a complex, nested trace in the Dev UI.

### Self-Reflection Questions
- In this architecture, a single `GoogleSearchAgentTool` instance is shared across multiple agents. What are the benefits of this approach compared to each agent creating its own instance?
- The final output of this system is a fully formatted article. How could you modify the system to produce a different type of output, such as a slide presentation or a podcast script, while reusing the parallel research phase?
- This system is fully automated. Where would be the most logical place to insert a human-in-the-loop step if you wanted a person to approve the research before the `article_writer` begins its work?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMTktYWR2YW5jZWQtbXVsdGktYWdlbnQtYXJjaGl0ZWN0dXJlcy9sYWItc29sdXRpb24=`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module19-advanced-multi-agent-architectures/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
