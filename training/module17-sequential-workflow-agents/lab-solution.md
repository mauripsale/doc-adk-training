---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 17 Solution: Building a Blog Post Generator Pipeline

## Goal

This file contains the complete code for the `agent.py` script in the Blog Post Generator Pipeline lab.

### `blog-pipeline/agent.py`

```python
from __future__ import annotations

from pydantic import BaseModel, Field
from google.adk.agents import Agent, SequentialAgent

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

# ===== Agent 1: Research Agent =====
# Gathers key facts about the topic
research_agent = Agent(
    name="researcher",
    model="gemini-2.5-flash",
    description="Researches a topic and gathers key information",
    instruction=(
        "You are a research assistant. Your task is to gather key facts and information "
        "about the topic requested by the user."
    ),
    output_schema=ResearchFindings,
    output_key="research_findings"  # Saves JSON structured data to state!
)

# ===== Agent 2: Writer Agent =====
# Writes blog post draft from structured research
writer_agent = Agent(
    name="writer",
    model="gemini-2.5-flash",
    description="Writes a blog post draft based on research findings",
    instruction=(
        "You are a creative blog writer. Write an engaging blog post based on "
        "the structured research findings below.\n"
        "\n"
        "**Research Findings (JSON):**\n"
        "{research_findings}\n"  # Reads structured JSON from state!
        "\n"
        "Write a draft that:\n"
        "- Has an engaging introduction\n"
        "- Incorporates the key facts naturally\n"
        "- Has a conclusion that wraps up the topic\n"
        "- Uses a friendly, conversational tone"
    ),
    output_schema=BlogDraft,
    output_key="draft_post"  # Saves structured JSON to state!
)

# ===== Agent 3: Editor Agent =====
# Reviews the structured draft and suggests improvements
editor_agent = Agent(
    name="editor",
    model="gemini-2.5-flash",
    description="Reviews blog post draft and provides editorial feedback",
    instruction=(
        "You are an experienced editor. Review the blog post draft below and provide "
        "constructive feedback.\n"
        "\n"
        "**Draft Blog Post (JSON):**\n"
        "{draft_post}\n"  # Reads structured JSON from state!
        "\n"
        "Analyze the post for clarity, flow, grammar, and engagement.\n"
        "Provide your feedback as a list of improvements. If the post is excellent, "
        "set 'is_ready' to true and leave the improvements list empty."
    ),
    output_schema=EditorialFeedback,
    output_key="editorial_feedback"  # Saves structured JSON to state!
)

# ===== Agent 4: Formatter Agent =====
# Applies edits and formats as markdown
formatter_agent = Agent(
    name="formatter",
    model="gemini-2.5-flash",
    description="Applies editorial feedback and formats the final blog post",
    instruction=(
        "You are a formatter. Create the final version of the blog post by applying "
        "the editorial feedback to improve the draft.\n"
        "\n"
        "**Original Draft (JSON):**\n"
        "{draft_post}\n"  # Reads structured JSON from state!
        "\n"
        "**Editorial Feedback (JSON):**\n"
        "{editorial_feedback}\n"  # Reads structured JSON from state!
        "\n"
        "Create the final blog post by applying the suggested improvements and formatting "
        "it as proper markdown with headings and paragraph breaks. "
        "Output ONLY the final formatted blog post in markdown (no JSON)."
    ),
    output_key="final_post"  # Saves final string to state!
)

# ===== Create the Sequential Pipeline =====
blog_creation_pipeline = SequentialAgent(
    name="BlogCreationPipeline",
    sub_agents=[
        research_agent,
        writer_agent,
        editor_agent,
        formatter_agent
    ],  # Executes in this EXACT order!
    description="Complete blog post creation pipeline from research to publication"
)

# MUST be named root_agent for ADK
root_agent = blog_creation_pipeline
```

### Self-Reflection Answers

1.  **The `SequentialAgent` is deterministic. What does this mean, and why is it a desirable property for a workflow like content creation?**
    *   **Answer:** "Deterministic" means the outcome is predictable and repeatable. Given the same starting conditions, a `SequentialAgent` will always execute the same agents in the exact same order. This is desirable for content pipelines because it ensures quality control (e.g., every post *must* be edited) and reliability (e.g., the formatter will always have an approved draft to work on). It eliminates the "unpredictability" of an LLM deciding which step to take next.

2.  **What do you think would happen if you forgot to add the `output_key` to the `research_agent`? How would the `writer_agent` behave?**
    *   **Answer:** If `research_agent` has no `output_key`, its output (the structured JSON) would not be saved to the shared state. When the `writer_agent` runs, it would try to interpolate `{research_findings}` into its prompt. Since that key is missing from the state, the ADK (or the underlying Python f-string logic) would likely raise an error or insert a blank/placeholder value. This would cause the writer to hallucinate facts or fail to write a relevant post because it lacks the necessary input context.

3.  **How could you modify this pipeline to include a human-in-the-loop? For example, what if you wanted a human to approve the `draft_post` before the `editor_agent` runs?**
    *   **Answer:** You could insert a custom `FunctionTool` or a specialized "HumanAgent" between the writer and the editor. This component would pause the execution (if the runtime supports it) or present the draft to a UI and wait for a signal (like a button press or a specific input) before proceeding. In a simpler implementation, you could split the pipeline into two `SequentialAgent`s: one that generates the draft and stops, and a second one that takes the approved draft and runs the edit/format steps, with the human step happening manually in between.
