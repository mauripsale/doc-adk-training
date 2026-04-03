---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 12 Solution: Building a Research Assistant with Web Search

## Goal

This file contains the complete code for the `agent.py` script in the Research Assistant lab.

### `research_assistant/agent.py`

```python
"""
Research Assistant with Web Grounding
Searches web, extracts key information, provides citations.
"""

from datetime import datetime
from google.adk.agents import Agent
from google.adk.tools import FunctionTool, GoogleSearchAgentTool

# --- Custom Tools ---

def format_research_notes(topic: str, findings: str) -> dict:
    """Formats research findings into a document."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    document = f"""
# Research Report: {topic}
Generated: {timestamp}

## Findings
{findings}
    """.strip()
    return {"status": "success", "document": document}

def extract_key_facts(text: str, num_facts: int = 5) -> list[str]:
    """Extract key facts from text (simplified)."""
    sentences = text.split('.')
    # Filter out empty strings that may result from splitting
    return [s.strip() for s in sentences if s.strip()][:num_facts]

# --- Agent Definition ---

# Create search tool (using workaround for mixing with custom tools)
search_tool = GoogleSearchAgentTool()

# Create research assistant
root_agent = Agent(
    model='gemini-2.5-flash',
    name='research_assistant',
    description='Conducts web research and compiles findings',
    instruction="""
You are an expert research assistant with access to:
1. Web search via search_tool
2. Fact extraction via extract_key_facts
3. Note formatting via format_research_notes

When given a research topic:
1. Use search_tool to find current information.
2. Extract key facts using extract_key_facts.
3. Format the research using format_research_notes.
4. Present the final, formatted document to the user as your answer.
    """.strip(),
    tools=[
        search_tool,
        FunctionTool(extract_key_facts),
        FunctionTool(format_research_notes)
    ]
)
```

### Self-Reflection Answers

1.  **The `GoogleSearchAgentTool` is a workaround for a current limitation. Why is it architecturally cleaner to have a wrapper like this instead of building the search logic directly into your own custom tool?**
    *   **Answer:** Using a wrapper like `GoogleSearchAgentTool` maintains separation of concerns. The search logic (connecting to Google's API, handling authentication, parsing search results) is complex and best managed by the framework or a dedicated component. If you built this into your own custom tool, you would be duplicating code and increasing maintenance burden. The wrapper allows you to treat the search capability as a modular "black box" that just works, keeping your agent definition clean and focused on orchestration.

2.  **Our `extract_key_facts` tool is very simple. How could you make it more robust? (Hint: Could another LLM be used for this task?)**
    *   **Answer:** The current implementation just splits text by sentences, which is very fragile. A much more robust approach would be to use an LLM for this specific task. You could create a second agent (a "Summarizer Agent") whose sole instruction is to "Extract the top 5 key facts from the provided text." Your main agent would then call this sub-agent as a tool. This would leverage the semantic understanding of the LLM to identify actual "facts" rather than just grammatical sentences.

3.  **The agent's instruction defines a specific, sequential workflow. What might happen if you didn't specify the order of the tool calls in the instruction?**
    *   **Answer:** Without a specified order, the agent might try to call tools out of sequence or skip steps. For example, it might try to format notes before it has even searched for information, or it might search and then just dump the raw search results to the user without extracting facts. Explicitly defining the workflow ("First do X, then Y, then Z") acts as a "Chain of Thought" prompt, guiding the agent's reasoning process and ensuring a reliable, structured output.