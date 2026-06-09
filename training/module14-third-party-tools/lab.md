---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 14: Integrating a LangChain Wikipedia Tool Challenge

## Goal

### Goal

In this lab, you will learn how to integrate a tool from a popular third-party library, LangChain, into your ADK agent. You will build a "Fact-finder" agent that can look up information on Wikipedia.

### Step 1: Create the Agent Project and Install Dependencies

1.  **Create the agent project:**
    ```shell
    uv run adk create --type=config fact_finder_agent
    cd fact_finder_agent
    ```

2.  **Install LangChain dependencies:**
    ```shell
    pip install langchain_community wikipedia
    ```

### Step 2: Write the Agent Code

Because we are importing Python objects, we need to define our agent in a Python file.

**Exercise:** Create a new file named `agent.py`. Inside this file, complete the `# TODO` items to build the agent. You will need to instantiate the LangChain tool, wrap it, and then define your agent to use the wrapped tool.

```python
# In agent.py (Starter Code)

from google.adk.agents import LlmAgent
from google.adk.tools.langchain_tool import LangchainTool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# TODO: 1. Instantiate the LangChain tool.
# - Create a WikipediaAPIWrapper.
# - Create a WikipediaQueryRun instance using the wrapper.
# (Refer to LangChain documentation if needed).
langchain_tool_instance = None

# TODO: 2. Wrap the LangChain tool instance with the ADK's `LangchainTool` wrapper.
wikipedia_tool = None

# TODO: 3. Define the `root_agent` as an `LlmAgent`.
# - Give it a name, model (`gemini-3.5-flash`), and description.
# - Write an instruction to use the Wikipedia tool for factual questions.
# - Add your wrapped `wikipedia_tool` to its `tools` list.
root_agent = LlmAgent(
    name="fact_finder_agent",
    model="gemini-3.5-flash",
    description="An agent that can look up information on Wikipedia.",
    instruction="""# Your instruction here...""",
    tools=[
        # Your tools here...
    ]
)
```

### Step 3: Configure and Run the Agent

1.  **Delete the placeholder `root_agent.yaml` file**, as your agent is now defined in `agent.py`.
    ```shell
    rm root_agent.yaml
    ```

2.  **Set up your `.env` file** with your API key.

3.  **Run the agent:**
    ```shell
    uv run adk web fact_finder_agent
    ```
    The ADK will automatically find the `root_agent` object in your `agent.py` file.

### Step 4: Test the Fact-Finder Agent

1.  **Interact with the agent** in the Dev UI. Ask it questions that require an encyclopedia:
    *   "Who was Marie Curie?"
    *   "What is the theory of relativity?"
2.  **Examine the Trace View** to confirm that the `WikipediaQueryRun` tool was called.

### Having Trouble?

If you get stuck, you can find the complete, working code in the `lab-solution.md` file.

### Lab Summary

You have successfully integrated a tool from an external library into your ADK agent. You have learned to:
*   Install third-party library dependencies.
*   Instantiate a tool from a library like LangChain.
*   Use an ADK wrapper (`LangchainTool`) to make the third-party tool compatible with your agent.
*   Define an agent in a Python file (`agent.py`) to handle the tool setup.

### Self-Reflection Questions
- The `LangchainTool` wrapper works by inspecting the LangChain tool object. What attributes do you think the wrapper is looking for on the LangChain tool to automatically generate the schema for the ADK agent?
- Besides Wikipedia, what other pre-built tools from the LangChain ecosystem can you find that would be useful to integrate into an ADK agent?
- What are the potential downsides or risks of relying on third-party, community-maintained tools in a production application?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMTQtdGhpcmQtcGFydHktdG9vbHMvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module14-third-party-tools/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
