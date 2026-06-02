---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 19 Solution: Building a Content Publishing System

## Goal

This file contains the complete code for the `agent.py` script using the ADK 2.0 **Nested Workflow** pattern.

### `content_publisher/agent.py`

```python
from __future__ import annotations

from google.adk import Agent, Workflow
from google.adk.workflow import JoinNode
from google.adk.tools import GoogleSearchAgentTool

# ===== SHARED TOOLS =====
search_tool = GoogleSearchAgentTool()

# ===== RESEARCH NODES (Branch 1: News) =====
news_fetcher = Agent(
    name="news_fetcher", model="gemini-3.5-flash", tools=[search_tool],
    instruction="Search for 3-4 current news articles about the topic.",
    output_key="raw_news"
)
news_summarizer = Agent(
    name="news_summarizer", model="gemini-3.5-flash",
    instruction="Summarize news from {raw_news}.",
    output_key="news_summary"
)

# ===== RESEARCH NODES (Branch 2: Social) =====
social_monitor = Agent(
    name="social_monitor", model="gemini-3.5-flash", tools=[search_tool],
    instruction="Find trending social media discussions about the topic.",
    output_key="raw_social"
)
sentiment_analyzer = Agent(
    name="sentiment_analyzer", model="gemini-3.5-flash",
    instruction="Analyze sentiment from {raw_social}.",
    output_key="social_insights"
)

# ===== RESEARCH NODES (Branch 3: Expert) =====
expert_finder = Agent(
    name="expert_finder", model="gemini-3.5-flash", tools=[search_tool],
    instruction="Find industry expert statements about the topic.",
    output_key="raw_experts"
)
quote_extractor = Agent(
    name="quote_extractor", model="gemini-3.5-flash",
    instruction="Extract key quotes from {raw_experts}.",
    output_key="expert_quotes"
)

# ===== CREATION NODES =====
article_writer = Agent(
    name="article_writer", model="gemini-3.5-flash",
    instruction="Write an article using {news_summary}, {social_insights}, and {expert_quotes}.",
    output_key="draft_article"
)
article_editor = Agent(
    name="article_editor", model="gemini-3.5-flash",
    instruction="Edit {draft_article} for clarity.",
    output_key="edited_article"
)
article_formatter = Agent(
    name="article_formatter", model="gemini-3.5-flash",
    instruction="Format {edited_article} as Markdown.",
    output_key="published_article"
)

# =====================================================
# ASSEMBLE NESTED WORKFLOWS
# =====================================================

# In ADK 2.0, a Workflow is just another Node!
news_wf = Workflow(name="NewsWF", edges=[("START", news_fetcher, news_summarizer)])
social_wf = Workflow(name="SocialWF", edges=[("START", social_monitor, sentiment_analyzer)])
expert_wf = Workflow(name="ExpertWF", edges=[("START", expert_finder, quote_extractor)])

# =====================================================
# ASSEMBLE THE ROOT WORKFLOW
# =====================================================
research_joiner = JoinNode(name="research_joiner")

root_agent = Workflow(
    name="ContentPublishingSystem",
    edges=[
        # Phase 1: Parallel Research (Sub-Workflows running concurrently)
        ("START", news_wf, research_joiner),
        ("START", social_wf, research_joiner),
        ("START", expert_wf, research_joiner),
        
        # Phase 2: Sequential Creation (Multiple nodes in sequence)
        (research_joiner, article_writer, article_editor, article_formatter)
    ]
)
```

### Self-Reflection Answers

1.  **What is the benefit of nesting workflows as nodes?**
    *   **Answer:** Modularity and reusability. You can develop and test the `NewsWF` independently. If you later build a news-only agent, you can reuse the exact same workflow object. It also keeps the `root_agent` graph clean and high-level.

2.  **How does the Dev UI handle these nested structures?**
    *   **Answer:** The Dev UI provides a "drill-down" experience. In the Trace view, you see the root workflow nodes. You can expand a workflow node (like `NewsWF`) to see its internal execution (the fetcher and summarizer nodes).

3.  **Where would you insert a Human-in-the-Loop step?**
    *   **Answer:** A logical place would be between the `research_joiner` and the `article_writer`. You could insert a node that presents the gathered research to a human for approval. Because this is a graph, you could even add an edge that routes *back* to the research workflows if the human is not satisfied with the data!