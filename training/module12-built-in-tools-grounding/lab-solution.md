---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 12 Solution: Building a Research Assistant with Web Search

## Goal

This file contains the complete code for the `agent.py` script in the Research Assistant lab, using ADK 2.0 practices.

### `research_assistant/agent.py`

```python
"""
Research Assistant with Web Grounding
Searches web, extracts key information, and formats a report.
"""

from datetime import datetime
from google.adk import Agent
from google.adk.tools import google_search

# --- Custom Tools ---

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
    # Filter for meaningful sentences
    facts = [s.strip() for s in sentences if len(s.strip()) > 10][:num_facts]
    return {"status": "success", "facts": facts}

# --- Agent Definition ---

root_agent = Agent(
    model='gemini-3.5-flash',
    name='research_assistant',
    description='Conducts web research and compiles findings',
    instruction="""
You are an expert research assistant.
You have access to the web via `google_search` and custom text processing tools.

When given a research topic, follow this workflow:
1. Use `google_search` to find current information on the web.
2. Use `extract_key_facts` to pull the most important points from the search results.
3. Use `format_research_notes` to compile these facts into a professional report.
4. Present the final, formatted document to the user as your final answer.
""",
    # In ADK 2.0, you can mix built-in and custom tools directly!
    tools=[
        google_search,
        extract_key_facts,
        format_research_notes
    ]
)
```

### Testing the Solution

1.  Initialize the project:
    ```bash
    uv init research_assistant --python 3.10
    cd research_assistant
    uv add "google-adk>=2.1.0" python-dotenv
    ```
2.  Configure `.env` for Vertex AI.
3.  Run the agent:
    ```bash
    uv run adk run agent.py
    ```

---

## Self-Reflection Answers

1.  **Earlier versions of ADK required a `GoogleSearchAgentTool` wrapper. Why is it better to mix tools directly now?**
    *   **Answer:** It simplifies the architecture. Treating `google_search` just like any other Python function makes the developer experience consistent and intuitive.

2.  **Our `extract_key_facts` tool is very simple. How could you make it more robust?**
    *   **Answer:** A better approach would be to use a separate **Agent** node (perhaps a smaller model like Gemini Flash) to perform semantic extraction from the search results.

3.  **The agent's instruction defines a specific, sequential workflow. What might happen if you didn't specify the order?**
    *   **Answer:** The LLM might try to call tools out of sequence or skip steps. Explicitly defining the process (Search -> Extract -> Format) ensures reliable behavior.
