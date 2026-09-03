---
sidebar_position: 2
title: "Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 12: Building a Research Assistant with Web Search Challenge

## Goal

In this lab, you will build a **Research Assistant** that can access up-to-date information from the internet and process it using custom Python logic. Since `google_search` can't share an agent with custom function tools (a Gemini API restriction, not an ADK one -- see the README), you'll build this as **two agents called in sequence**: a search specialist, then a formatter that receives its output.

### Prerequisites
*   **Agent Platform:** While `google_search` can work with AI Studio keys, the ADK standardizes on Agent Platform for grounding in enterprise scenarios. Ensure your `.env` is configured correctly (refer to Module 2).

### Step 1: Create and Prepare the Project

<Setup/>

1.  **Create the agent project:**
    ```bash
    uv run adk create research_assistant
    cd research_assistant
    ```

2.  **Configure Authentication:** Ensure your `.env` file has your project ID and location set for Agent Platform.

### Step 2: Define the Two Agents

**Exercise:** Create `agent.py`. The custom tools and the `research_agent` are provided below. Your task is to complete `formatter_agent`.

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

# --- Agent 1: Search Specialist (Provided) ---
# Only google_search -- it cannot be mixed with the custom tools below.

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
# TODO: Define `formatter_agent`.
# 1. Use 'gemini-3.5-flash'.
# 2. Add `extract_key_facts` and `format_research_notes` to tools (do NOT
#    add google_search here -- that's the whole point of splitting these up).
# 3. Write an instruction telling it to: first call extract_key_facts on the
#    findings text it's given, then call format_research_notes with the
#    topic and those facts, then present the final document as its answer.

formatter_agent = Agent(...)
```

### Step 3: Orchestrate the Two Agents

Since these are two separate agents, you need a small script to run one after the other, passing the first agent's output as the second agent's input -- exactly like the programmatic execution pattern from Module 6.

**Exercise:** Create `main.py` and complete the `run_agent` TODO.

```python
# In main.py
import asyncio
from google.adk.runners import InMemoryRunner
from google.genai import types
from agent import research_agent, formatter_agent

async def run_agent(agent, app_name: str, message_text: str) -> str:
    # TODO: Implement this helper:
    # 1. Create an InMemoryRunner for `agent`.
    # 2. Create a session (user_id="student", session_id="s1" is fine).
    # 3. Call run_async with a user message built from `message_text`.
    # 4. Return the text of the final event you see (there's no need to
    #    check is_final_response() here -- just keep the latest text seen).
    ...

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

Run it with:
```bash
uv run python main.py
```

**Observe the output:** the first agent grounds itself in real web results beyond its training data; the second agent never touches `google_search` at all, only your custom tools -- yet the final report still incorporates the first agent's findings, because you're the one passing the data between them.

### Having Trouble?

If you get stuck, you can find the complete, working code in the `lab-solution.md` file.

### Lab Summary

You have successfully built a two-agent pipeline that bridges the knowledge gap of LLMs using built-in grounding tools. You have learned:
*   How to easily enable web search using the **`google_search`** built-in tool.
*   Why `google_search` can't share an agent with custom function tools, and how to work around that with **sequential composition** instead.
*   How to write instructions that guide each agent through its own focused part of a larger research-and-formatting workflow.

### Self-Reflection Questions
- Why is `google_search` considered a "built-in" tool while `format_research_notes` is a "custom" tool?
- What are the benefits of having the model perform the search inside its own environment rather than you writing a Python script to scrape Google results?
- `main.py` passes `findings` between the two agents as a plain string. What would you have to change if you instead wanted `formatter_agent` to be able to ask `research_agent` follow-up questions?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMTItYnVpbHQtaW4tdG9vbHMtZ3JvdW5kaW5nL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module12-built-in-tools-grounding/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
