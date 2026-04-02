---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 12: Building a Research Assistant with Web Search Challenge

## Goal

### Goal

In this lab, you will build a **Research Assistant** that can access up-to-date information from the internet. You will learn how to use the `GoogleSearchAgentTool` wrapper to combine web search with your own custom tools.

### Prerequisites
*   **Note on Costs:** This lab requires the Vertex AI API, which may incur small costs on your Google Cloud bill.

### Step 1: Create and Prepare the Project

1.  **Create the agent project:**
    ```shell
    adk create research_assistant
    ```
    When prompted, choose the **Programmatic (Python script)** option.

2.  **Navigate into the new directory:**
    ```shell
    cd research_assistant
    ```

3.  **Create the `.env` file:**
    The `GoogleSearchAgentTool` requires a Vertex AI configuration. Create a `.env` file in this directory with the following content, replacing `<your_gcp_project>` with your actual Google Cloud project ID.
    ```
    GOOGLE_GENAI_USE_VERTEXAI=1
    GOOGLE_CLOUD_PROJECT=<your_gcp_project>
    GOOGLE_CLOUD_LOCATION=us-central1
    ```

### Step 2: Define the Agent and Tools

**Exercise:** Open `agent.py`. The custom tools have been provided for you. Your task is to complete the agent definition by instantiating the search tool and writing the agent's instructions.

```python
# In agent.py (Starter Code)

from datetime import datetime
from google.adk.agents import Agent
from google.adk.tools import FunctionTool, GoogleSearchAgentTool

# --- Custom Tools (Provided for you) ---

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
    return [s.strip() for s in sentences if s.strip()][:num_facts]

# --- Agent Definition ---

# TODO: 1. Create an instance of the GoogleSearchAgentTool.
search_tool = ...

# TODO: 2. Define the `root_agent`.
root_agent = Agent(
    model='gemini-2.5-flash',
    name='research_assistant',
    description='Conducts web research and compiles findings',
    instruction="""
    # TODO: 3. Write an instruction that tells the agent to perform the research
    # workflow in the correct order:
    # 1. Use search_tool to find information.
    # 2. Use extract_key_facts on the search results.
    # 3. Use format_research_notes on the extracted facts.
    # 4. Present the final document as the answer.
    """,
    tools=[
        # TODO: 4. Add the `search_tool` and the two custom tools
        # (`extract_key_facts`, `format_research_notes`) to this list.
    ]
)
```

### Step 3: Run and Test the Research Assistant

1.  **Navigate to the parent directory:**
    ```shell
    cd ..
    ```

2.  **Start the Dev UI:**
    ```shell
    adk web research-assistant
    ```

3.  **Interact with the agent:**
    *   Give the agent a research topic, like "What are the latest developments in AI in 2025?"

4.  **Analyze the Trace View:**
    *   Expand the trace for your query. You should see a sequence of tool calls: `GoogleSearchAgentTool`, then `extract_key_facts`, then `format_research_notes`.

### Having Trouble?

If you get stuck, you can find the complete, working code in the `lab-solution.md` file.

### Lab Summary

You have successfully built an agent that can access real-world, current information from the internet and process it using custom logic. You have learned:
*   How to use the `GoogleSearchAgentTool` wrapper to combine built-in search with custom `FunctionTool`s.
*   How to write an instruction that orchestrates a sequence of different tool types.

### Self-Reflection Questions
- The `GoogleSearchAgentTool` is a workaround for a current limitation. Why is it architecturally cleaner to have a wrapper like this instead of building the search logic directly into your own custom tool?
- Our `extract_key_facts` tool is very simple. How could you make it more robust? (Hint: Could another LLM be used for this task?)
- The agent's instruction defines a specific, sequential workflow. What might happen if you didn't specify the order of the tool calls in the instruction?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMTItYnVpbHQtaW4tdG9vbHMtZ3JvdW5kaW5nL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module12-built-in-tools-grounding/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
