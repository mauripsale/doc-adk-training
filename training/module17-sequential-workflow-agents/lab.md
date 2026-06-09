---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 17: Building a Blog Post Generator Pipeline Challenge

## Goal

### Goal

In this lab, you will build a multi-step content creation pipeline using an ADK 2.0 **Workflow**. This will demonstrate how to chain multiple specialist agents together in a linear graph, passing data from one to the next.

### The Pipeline Stages
1.  **Research Agent:** Gathers key facts about a topic.
2.  **Writer Agent:** Creates a draft blog post from the research.
3.  **Editor Agent:** Reviews the draft and suggests improvements.
4.  **Formatter Agent:** Applies the edits and formats the final post in Markdown.

### Step 1: Create the Project Structure

1.  **Create a new project:**
    ```shell
    uv run adk create blog_pipeline
    ```
    When prompted, choose the **Programmatic (Python script)** option.

2.  **Navigate into the new directory:**
    ```shell
    cd blog_pipeline
    ```

### Step 2: Assemble the Pipeline

**Exercise:** Open `agent.py`. The four specialist agents (`research_agent`, `writer_agent`, etc.) have been provided for you. Your task is to assemble them into a functioning pipeline using a `Workflow`.

```python
# In agent.py (Starter Code)

from __future__ import annotations
from pydantic import BaseModel, Field
from google.adk import Agent, Workflow

# ===== Structured Data Schemas (Provided for you) =====
class ResearchFindings(BaseModel):
    topic: str = Field(description="The topic being researched")
    facts: list[str] = Field(description="List of 5-7 key facts or insights")

class BlogDraft(BaseModel):
    title: str = Field(description="Engaging title for the blog post")
    paragraphs: list[str] = Field(description="3-4 paragraphs of the draft")

class EditorialFeedback(BaseModel):
    improvements: list[str] = Field(description="List of specific improvements. Empty if none.")
    is_ready: bool = Field(description="True if no revisions are needed, False otherwise")

# ===== Specialist Agents (Provided for you) =====

research_agent = Agent(
    name="researcher", model="gemini-3.5-flash",
    instruction="...", # Gathers facts into structured output
    output_schema=ResearchFindings,
    output_key="research_findings"
)
writer_agent = Agent(
    name="writer", model="gemini-3.5-flash",
    instruction="...writes a draft based on structured JSON {research_findings}...",
    output_schema=BlogDraft,
    output_key="draft_post"
)
editor_agent = Agent(
    name="editor", model="gemini-3.5-flash",
    instruction="...reviews the JSON {draft_post}...",
    output_schema=EditorialFeedback,
    output_key="editorial_feedback"
)
formatter_agent = Agent(
    name="formatter", model="gemini-3.5-flash",
    instruction="...applies JSON {editorial_feedback} to the JSON {draft_post}...",
    output_key="final_post"
)

# ===== Create the Sequential Pipeline =====

# TODO: 1. Create a `Workflow` named `blog_creation_pipeline`.
# TODO: 2. Define the `edges` to connect the agents in the correct
# logical order: START -> research -> write -> edit -> format.
blog_creation_pipeline = None

# TODO: 3. Set the `root_agent` to be your `blog_creation_pipeline`.
root_agent = None
```
*(Note: The full agent instructions are in the `lab-solution.md` if you need to inspect them, but you don't need to change them for this exercise.)*

### Step 3: Run and Test the Pipeline

1.  **Set up your `.env` file.**
2.  **Navigate to the parent directory** (`cd ..`) and start the Dev UI:
    ```shell
    uv run adk web blog_pipeline
    ```
3.  **Interact with the pipeline:**
    *   Send a topic to write about, like: "the history of the internet".
4.  **Examine the Trace and State Tabs:**
    *   **Trace View:** Expand the trace to see the `Workflow` running its four nodes in order.
    *   **State View:** After the run, inspect the state to see the output of each step (`research_findings`, `draft_post`, etc.).

### Having Trouble?

If you get stuck, you can find the complete, working code in the `lab-solution.md` file.

### Lab Summary

You have successfully built a deterministic, multi-agent pipeline using an ADK 2.0 Workflow. You have learned to:
*   Configure a `Workflow` with linear edges to orchestrate multiple sub-agents.
*   Understand how `output_key` and state variables (`{key}`) are used to pass data between nodes in a sequence.
*   Analyze the execution of a pipeline using the Trace and State views.

### Self-Reflection Questions
- A `Workflow` with linear edges is deterministic. What does this mean, and why is it a desirable property for a workflow like content creation?
- What do you think would happen if you forgot to add the `output_key` to the `research_agent`? How would the `writer_agent` behave?
- How could you modify this pipeline to include a human-in-the-loop? For example, what if you wanted a human to approve the `draft_post` before the `editor_agent` runs?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMTctc2VxdWVudGlhbC13b3JrZmxvdy1hZ2VudHMvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module17-sequential-workflow-agents/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
