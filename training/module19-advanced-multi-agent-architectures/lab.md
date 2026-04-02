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
    Three independent, sequential pipelines will run concurrently:
    *   **News Pipeline:** Fetches current events, then summarizes the key points.
    *   **Social Pipeline:** Gathers trending topics, then analyzes the insights.
    *   **Expert Pipeline:** Finds expert opinions, then extracts key quotes.

2.  **Phase 2: Sequential Content Creation (Gather)**
    A final sequential pipeline will run after all research is complete:
    *   **Writer Agent:** Combines the summaries from all three research pipelines into a draft article.
    *   **Editor Agent:** Reviews and improves the draft.
    *   **Formatter Agent:** Formats the final article for publication.

### Step 1: Create and Prepare the Project

1.  **Create the agent project:**
    ```shell
    adk create content_publisher
    ```
    When prompted, choose the **Programmatic (Python script)** option.

2.  **Navigate into the new directory:**
    ```shell
    cd content_publisher
    ```
3.  **Create the `.env` file:**
    The search tools require a Vertex AI configuration. Create a `.env` file in this directory with the following content, replacing `<your_gcp_project>` with your actual Google Cloud project ID.
    ```
    GOOGLE_GENAI_USE_VERTEXAI=1
    GOOGLE_CLOUD_PROJECT=<your_gcp_project>
    GOOGLE_CLOUD_LOCATION=us-central1
    ```

### Step 2: Assemble the Multi-Agent System

**Exercise:** Open `agent.py`. All eight of the individual specialist agents have been provided for you below. Your task is to assemble them into the complete, multi-level architecture described above by completing the `TODO` sections at the bottom.

```python
# In agent.py (Starter Code)

from __future__ import annotations
from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.tools import GoogleSearchAgentTool

# ===== SHARED TOOLS =================================
search_tool = GoogleSearchAgentTool()

# ===== SPECIALIST AGENTS (Provided for you) =====

# --- Branch 1: News ---
news_fetcher = Agent(
    name="news_fetcher", model="gemini-2.5-flash", tools=[search_tool],
    instruction="You are a news researcher. Use the GoogleSearchAgentTool to find 3-4 current news articles about the user's topic.",
    output_key="raw_news"
)
news_summarizer = Agent(
    name="news_summarizer", model="gemini-2.5-flash",
    instruction="Summarize the news articles from {raw_news} into 2-3 key takeaways.",
    output_key="news_summary"
)

# --- Branch 2: Social Media ---
social_monitor = Agent(
    name="social_monitor", model="gemini-2.5-flash", tools=[search_tool],
    instruction="You are a social media analyst. Use the GoogleSearchAgentTool to find trending discussions and public sentiment about the user's topic.",
    output_key="raw_social"
)
sentiment_analyzer = Agent(
    name="sentiment_analyzer", model="gemini-2.5-flash",
    instruction="Analyze the social media data from {raw_social} and extract key insights on trends and sentiment.",
    output_key="social_insights"
)

# --- Branch 3: Expert Opinion ---
expert_finder = Agent(
    name="expert_finder", model="gemini-2.5-flash", tools=[search_tool],
    instruction="You are an expert opinion researcher. Use the GoogleSearchAgentTool to find what industry experts or academics are saying about the user's topic.",
    output_key="raw_experts"
)
quote_extractor = Agent(
    name="quote_extractor", model="gemini-2.5-flash",
    instruction="Extract the most impactful quotes from the expert opinions in {raw_experts}.",
    output_key="expert_quotes"
)

# --- Content Creation ---
article_writer = Agent(
    name="article_writer", model="gemini-2.5-flash",
    instruction="You are a professional writer. Write an engaging article using the research provided in {news_summary}, {social_insights}, and {expert_quotes}.",
    output_key="draft_article"
)
article_editor = Agent(
    name="article_editor", model="gemini-2.5-flash",
    instruction="You are an editor. Review and improve the draft article from {draft_article} for clarity, flow, and impact.",
    output_key="edited_article"
)
article_formatter = Agent(
    name="article_formatter", model="gemini-2.5-flash",
    instruction="Format the article from {edited_article} for publication with proper markdown, including a title and headings.",
    output_key="published_article"
)

# =====================================================
# ASSEMBLE THE MULTI-AGENT SYSTEM
# =====================================================

# TODO: 1. Create the three sequential research pipelines.
# - `news_pipeline` should contain `news_fetcher` then `news_summarizer`.
# - `social_pipeline` should contain `social_monitor` then `sentiment_analyzer`.
# - `expert_pipeline` should contain `expert_finder` then `quote_extractor`.
news_pipeline = SequentialAgent(...)
social_pipeline = SequentialAgent(...)
expert_pipeline = SequentialAgent(...)

# TODO: 2. Create the parallel research phase. This `ParallelAgent` should
# contain the three sequential pipelines you just defined.
parallel_research = ParallelAgent(...)

# TODO: 3. Create the final `SequentialAgent` for the entire system.
# It should run the `parallel_research` phase first, followed by the
# `article_writer`, `article_editor`, and `article_formatter` in order.
content_publishing_system = SequentialAgent(...)

# TODO: 4. Set the `root_agent` to be your final `content_publishing_system`.
root_agent = None
```

### Step 3: Run and Test the System

1.  **Navigate to the parent directory** (`cd ..`) and start the Dev UI:
    ```shell
    adk web content-publisher
    ```
2.  **Interact with the system:**
    *   Give it a topic, like: "The future of electric vehicles".
3.  **Analyze the Trace:**
    *   This is the most important step. Expand the trace to see the nested structure. Verify that the three research pipelines run in parallel, and that the content creation agents run sequentially after the parallel phase is complete.

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
