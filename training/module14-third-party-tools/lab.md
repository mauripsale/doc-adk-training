---
sidebar_position: 2
title: "Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 14: Integrating a LangChain Wikipedia Tool Challenge

## Goal

In this lab, you will learn how to integrate a tool from a popular third-party library, LangChain, into your ADK agent. You will build a "Fact-finder" agent that can look up information on Wikipedia.

### Step 1: Create the Agent Project and Install Dependencies

<Setup/>

1.  **Create the agent scaffold:**
    ```shell
    uv run adk create --type=config fact_finder_agent
    cd fact_finder_agent
    ```

2.  **Install LangChain dependencies:**
    ```shell
    uv add langchain_community wikipedia
    ```

### Step 2: Write the Agent Code

Because we are importing Python objects, we need to define our agent in a Python file.

**Exercise:** Create a new file named `agent.py`. Inside this file, complete the `# TODO` items to build the agent. You will need to instantiate the LangChain tool, wrap it, and then define your agent to use the wrapped tool.

> **Heads-up: Wikipedia now requires a distinctive `User-Agent`.** Wikimedia rate-limits the generic default `User-Agent` string that the `wikipedia` package sends (it's shared by every user of the package, so Wikimedia throttles it collectively). Without a fix, calls to the tool fail with a `requests.exceptions.JSONDecodeError`. The fix is one line: call `wikipedia.set_user_agent("your-app-name/1.0 (contact-info)")` once, before the tool makes any requests. It's already included in the starter code below.

```python
# In agent.py (Starter Code)

from google.adk import Agent
from google.adk.integrations.langchain import LangchainTool
import wikipedia
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# Wikimedia now rate-limits the wikipedia package's generic default User-Agent.
# Set a distinctive one before making any requests.
wikipedia.set_user_agent("adk-training-fact-finder/1.0 (https://github.com/adk-training; contact@example.com)")

# TODO: 1. Instantiate the LangChain tool.
# - Create a WikipediaAPIWrapper.
# - Create a WikipediaQueryRun instance using the wrapper.
# (Refer to LangChain documentation if needed).
langchain_tool_instance = None

# TODO: 2. Wrap the LangChain tool instance with the ADK's `LangchainTool` wrapper.
wikipedia_tool = None

# TODO: 3. Define the `root_agent` as an `Agent`.
# - Give it a name, model (`gemini-3.5-flash`), and description.
# - Write an instruction to use the Wikipedia tool for factual questions.
# - Add your wrapped `wikipedia_tool` to its `tools` list.
root_agent = Agent(
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

> **If the tool call still fails** with a network or JSON error even after setting the `User-Agent`, wait a few seconds and try again. Wikimedia occasionally rate-limits shared or cloud IP ranges (like Cloud Shell or CI runners) regardless of a correctly-set `User-Agent` -- this is a separate, transient issue from the User-Agent fix above, and it usually clears up on retry.

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
