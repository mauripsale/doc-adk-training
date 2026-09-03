---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 12 Solution: Building a Research Assistant with Web Search

## Goal

This file contains the complete code for `agent.py` and `main.py` in the Research Assistant lab: two agents, called in sequence, since `google_search` can't share an agent with custom function tools.

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

# --- Agent 1: Search Specialist ---
# Only google_search -- it cannot be mixed with custom function tools in the
# same agent (a Gemini API restriction: a mixed tools list constructs fine in
# Python but fails at the first real model call with
# `400 INVALID_ARGUMENT: Multiple tools are supported only when they are all
# search tools.`).

research_agent = Agent(
    model='gemini-3.5-flash',
    name='research_agent',
    instruction=(
        "You are a research assistant. Use google_search to find current "
        "information on the topic you're given, then summarize the key "
        "findings in a few plain-text sentences."
    ),
    tools=[google_search],
)

# --- Agent 2: Formatter ---
# Only the custom tools -- no google_search here.

formatter_agent = Agent(
    model='gemini-3.5-flash',
    name='formatter_agent',
    instruction="""
You are a report formatter. The user will give you a topic and some research
findings as plain text.
1. Call extract_key_facts on the findings text to pull out the most important points.
2. Call format_research_notes with the topic and those facts to produce a final report.
Present the final formatted document as your answer, verbatim.
""",
    tools=[extract_key_facts, format_research_notes],
)
```

### `research_assistant/main.py`

```python
import asyncio
from google.adk.runners import InMemoryRunner
from google.genai import types
from agent import research_agent, formatter_agent

async def run_agent(agent, app_name: str, message_text: str) -> str:
    runner = InMemoryRunner(agent=agent, app_name=app_name)
    await runner.session_service.create_session(app_name=app_name, user_id="student", session_id="s1")

    final_text = ""
    async for event in runner.run_async(
        user_id="student",
        session_id="s1",
        new_message=types.Content(role="user", parts=[types.Part(text=message_text)]),
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_text = part.text
    return final_text

async def main():
    topic = "the latest AI developments from Google"

    findings = await run_agent(research_agent, "research_app", f"Research this topic: {topic}")
    print("--- RESEARCH FINDINGS ---")
    print(findings)

    report = await run_agent(formatter_agent, "formatter_app", f"Topic: {topic}\n\nFindings: {findings}")
    print("\n--- FINAL REPORT ---")
    print(report)

if __name__ == "__main__":
    asyncio.run(main())
```

### Testing the Solution

1.  Create the agent project:
    ```bash
    uv run adk create research_assistant
    cd research_assistant
    ```
2.  Configure `.env` for Vertex AI.
3.  Run the script:
    ```bash
    uv run python main.py
    ```

---

## Self-Reflection Answers

1.  **Why is `google_search` considered a "built-in" tool while `format_research_notes` is a "custom" tool?**
    *   **Answer:** `google_search` runs inside Google's own infrastructure, invoked directly by the model with no code of yours executing -- Google built, hosts, and maintains it. `format_research_notes` is a plain Python function you wrote and control entirely; the ADK just exposes it to the model as a callable tool via its signature and docstring.

2.  **What are the benefits of having the model perform the search inside its own environment rather than you writing a Python script to scrape Google results?**
    *   **Answer:** `google_search` runs inside Google's own infrastructure, so you get results that are already fresh, ranked, and grounded -- no scraping code to write or maintain, no HTML to parse, no risk of a page layout change silently breaking your tool, and no separate API key or rate-limit budget to manage. It also stays legally and ethically clean (no ToS-violating scraping), and the model gets structured, citation-ready grounding metadata back instead of raw markup it would have to interpret itself.

3.  **`main.py` passes `findings` between the two agents as a plain string. What would you have to change if you instead wanted `formatter_agent` to be able to ask `research_agent` follow-up questions?**
    *   **Answer:** A one-way string handoff can't support a back-and-forth. You'd need `formatter_agent` to actually invoke `research_agent` as a *tool call*, not just receive its output as a static string -- for example, by wrapping `research_agent` as a sub-agent it can transfer control to and back, or by exposing a `call_research_agent(question: str)` function tool that internally runs `research_agent` and returns its answer. Either way, this pushes you from "sequential composition" into genuine multi-agent orchestration -- which is exactly what Module 15 covers next.
