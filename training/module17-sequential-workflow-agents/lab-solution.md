---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 17 Solution: Building a Blog Post Generator Pipeline

## Goal

This file contains the complete code for the `agent.py` script using the ADK 2.0 **Workflow** pattern for sequential execution.

### `blog_pipeline/agent.py`

```python
from __future__ import annotations

from pydantic import BaseModel, Field
from google.adk import Agent, Workflow

# ===== Define Structured Schemas =====
class ResearchFindings(BaseModel):
    topic: str = Field(description="The topic being researched")
    facts: list[str] = Field(description="List of 5-7 key facts or insights")

class BlogDraft(BaseModel):
    title: str = Field(description="Engaging title for the blog post")
    paragraphs: list[str] = Field(description="3-4 paragraphs of the draft")

class EditorialFeedback(BaseModel):
    improvements: list[str] = Field(description="List of specific improvements. Empty if none.")
    is_ready: bool = Field(description="True if no revisions are needed, False otherwise")

# ===== Node 1: Research Agent =====
research_agent = Agent(
    name="researcher",
    model="gemini-3.5-flash",
    instruction="Gather facts about the topic requested by the user.",
    output_schema=ResearchFindings,
    output_key="research_findings"
)

# ===== Node 2: Writer Agent =====
writer_agent = Agent(
    name="writer",
    model="gemini-3.5-flash",
    instruction="Write a blog post based on these research findings: {research_findings}",
    output_schema=BlogDraft,
    output_key="draft_post"
)

# ===== Node 3: Editor Agent =====
editor_agent = Agent(
    name="editor",
    model="gemini-3.5-flash",
    instruction="Review this draft and provide feedback: {draft_post}",
    output_schema=EditorialFeedback,
    output_key="editorial_feedback"
)

# ===== Node 4: Formatter Agent =====
formatter_agent = Agent(
    name="formatter",
    model="gemini-3.5-flash",
    instruction="Apply this feedback {editorial_feedback} to this draft {draft_post}. Output Markdown.",
    output_key="final_post"
)

# ===== Create the Sequential Workflow =====
# In ADK 2.0, sequential execution is defined by linear edges in the Graph.
blog_creation_pipeline = Workflow(
    name="BlogCreationPipeline",
    edges=[
        ("START", research_agent),
        (research_agent, writer_agent),
        (writer_agent, editor_agent),
        (editor_agent, formatter_agent)
    ]
)

root_agent = blog_creation_pipeline
```

### Self-Reflection Answers

1.  **What does it mean for a Workflow to be deterministic, and why is this desirable?**
    *   **Answer:** A deterministic workflow has a fixed, predictable execution path. In this case, the linear edges guarantee that research *always* happens before writing, which *always* happens before editing. This is desirable because it ensures consistent quality and allows you to automate complex processes without the risk of an LLM "skipping" a step.

2.  **What is the role of `output_key` in this sequential pipeline?**
    *   **Answer:** Even though ADK 2.0 passes the output of one node directly to the next, `output_key` allows us to save results into the global session state. This is crucial when a later node (like the `formatter`) needs access to data from multiple previous steps (both the `draft_post` and the `editorial_feedback`).

3.  **How could you modify this pipeline to include a human-in-the-loop?**
    *   **Answer:** You could insert a custom `@node` function or a specialist agent between the writer and the editor that yields a `RequestInput` event. The workflow engine would then pause and wait for user approval before continuing to the editor node.
