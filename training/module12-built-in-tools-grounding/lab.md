---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 12: Building a Research Assistant with Web Search Challenge

## Goal

In this lab, you will build a **Research Assistant** that can access up-to-date information from the internet and process it using custom Python logic. You will learn how to mix built-in tools like `google_search` directly with your own custom tools.

### Prerequisites
*   **Vertex AI:** While `google_search` can work with AI Studio keys, the ADK standardizes on Vertex AI for grounding in enterprise scenarios. Ensure your `.env` is configured correctly (refer to Module 2).

### Step 1: Create and Prepare the Project

We will use the `uv` workflow to initialize our research project.

1.  **Initialize the project:**
    ```bash
    uv init research_assistant --python 3.10
    cd research_assistant
    uv add "google-adk>=2.1.0" python-dotenv
    ```

2.  **Configure Authentication:** Ensure your `.env` file has your project ID and location set for Vertex AI.

### Step 2: Define the Agent and Tools

**Exercise:** Create `agent.py`. The custom tools are provided below. Your task is to complete the agent definition by importing the built-in search tool and orchestrating the workflow.

```python
# In agent.py
from datetime import datetime
from google.adk import Agent
from google.adk.tools import google_search

# --- Custom Tools (Provided) ---

def format_research_notes(topic: str, findings: str) -> dict:
    """Formats research findings into a structured document."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    document = f"""
# Research Report: {topic}
Generated: {timestamp}

## Findings
{findings}
    """.strip()
    return {"status": "success", "document": document}

def extract_key_facts(text: str, num_facts: int = 5) -> dict:
    """Extracts key sentences from a block of text."""
    sentences = text.split('.')
    facts = [s.strip() for s in sentences if len(s.strip()) > 10][:num_facts]
    return {"status": "success", "facts": facts}

# --- Agent Definition ---

# TODO: Define the `root_agent` Node
# 1. Use 'gemini-3.5-flash'.
# 2. Add 'google_search', 'extract_key_facts', and 'format_research_notes' to tools.
# 3. Write instructions for a research workflow.

root_agent = Agent(...)
```

### Step 3: Run and Test the Research Assistant

1.  **Start the agent in interactive mode:** 
    ```bash
    uv run adk run agent.py
    ```

2.  **Interact with the agent:**
    *   "What are the latest AI developments from Google in 2025?"
    *   "Who won the most recent major sports championship?"

3.  **Observe the output:**
    *   Notice how the agent uses the internet to find information beyond its training data.
    *   The agent should first perform a search, then extract facts, and finally present a formatted Markdown report.

### Having Trouble?

If you get stuck, you can find the complete, working code in the `lab-solution.md` file.

### Lab Summary

You have successfully built an agent that bridges the knowledge gap of LLMs using built-in grounding tools. You have learned:
*   How to easily enable web search using the **`google_search`** built-in tool.
*   How to **mix built-in and custom tools** seamlessly in a single agent.
*   How to write instructions that guide an agent through a complex research and formatting workflow.

### Self-Reflection Questions
- Why is `google_search` considered a "built-in" tool while `format_research_notes` is a "custom" tool?
- What are the benefits of having the model perform the search inside its own environment rather than you writing a Python script to scrape Google results?
- How does providing a specific "workflow" in the instructions (Search -> Extract -> Format) improve the reliability of the agent's output?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMTItYnVpbHQtaW4tdG9vbHMtZ3JvdW5kaW5nL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module12-built-in-tools-grounding/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
