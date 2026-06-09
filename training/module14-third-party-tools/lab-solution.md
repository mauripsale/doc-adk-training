---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 14 Solution: Integrating a LangChain Wikipedia Tool

## Goal

This file contains the complete code for the `agent.py` file in the Fact-finder Agent lab.

### `fact_finder_agent/agent.py`

```python
from google.adk.agents import LlmAgent
from google.adk.tools.langchain_tool import LangchainTool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# 1. According to LangChain documentation, instantiate the tool.
# This sets up the connection to the Wikipedia API.
api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=2000)
langchain_tool_instance = WikipediaQueryRun(api_wrapper=api_wrapper)

# 2. Wrap the LangChain tool instance with the ADK's LangchainTool wrapper.
# The wrapper automatically inspects the tool and creates the schema for the LLM.
wikipedia_tool = LangchainTool(tool=langchain_tool_instance)

# 3. Define the ADK agent and include the wrapped tool in its tools list.
root_agent = LlmAgent(
    name="fact_finder_agent",
    model="gemini-3.5-flash",
    description="An agent that can look up information on Wikipedia.",
    instruction="""You are a helpful fact-finding assistant.
If the user asks a question about a specific topic, person, or event, you MUST use the Wikipedia tool to find an accurate answer.
Summarize the information you find in a clear and concise way.""",
    tools=[wikipedia_tool]
)
```

### Running the Agent

Because this agent is defined in a Python file, you must delete the placeholder `root_agent.yaml` file from the project directory before running `uv run adk web`.

### Self-Reflection Answers

1.  **The `LangchainTool` wrapper works by inspecting the LangChain tool object. What attributes do you think the wrapper is looking for on the LangChain tool to automatically generate the schema for the ADK agent?**
    *   **Answer:** The wrapper typically looks for attributes like `.name`, `.description` (or `.desc`), and sometimes the input schema or `.args` definition of the LangChain tool. It uses these to construct the function declaration that the LLM (Gemini) requires, effectively translating the LangChain tool definition into the format expected by the ADK's function calling mechanism.

2.  **Besides Wikipedia, what other pre-built tools from the LangChain ecosystem can you find that would be useful to integrate into an ADK agent?**
    *   **Answer:** The LangChain ecosystem is vast. Some other highly useful tools include:
        *   `DuckDuckGoSearchRun`: For general web search (alternative to Google Search).
        *   `PythonREPL`: For executing Python code (though ADK has its own executors, this is a common one).
        *   `WolframAlphaQueryRun`: For advanced mathematical and scientific computations.
        *   `ArxivQueryRun`: For searching academic papers.
        *   `RequestsGetTool`: For making generic HTTP GET requests.

3.  **What are the potential downsides or risks of relying on third-party, community-maintained tools in a production application?**
    *   **Answer:** Risks include:
        *   **Maintenance & Stability:** Community tools might be abandoned, have breaking changes in updates, or have bugs that aren't quickly fixed.
        *   **Security:** You are trusting the code within that library. A malicious update or a vulnerability in the tool could compromise your agent.
        *   **Dependency Conflicts:** As mentioned in the module theory, adding large libraries like LangChain can introduce "dependency hell," where different parts of your application require incompatible versions of the same underlying package.
        *   **Control:** You have less control over exactly how the tool works compared to a custom function you wrote yourself.
