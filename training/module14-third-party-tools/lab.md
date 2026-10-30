---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 14: Integrating Third-Party Tools — 🧪 Challenge Lab"
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
# - Give it a name, model (`gemini-3.8-flash`), and description.
# - Write an instruction to use the Wikipedia tool for factual questions.
# - Add your wrapped `wikipedia_tool` to its `tools` list.
root_agent = Agent(
    name="fact_finder_agent",
    model="gemini-3.8-flash",
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

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="14">

# Lab 14 Solution: Integrating a LangChain Wikipedia Tool

## Goal

This file contains the complete code for the `agent.py` file in the Fact-finder Agent lab.

### `fact_finder_agent/agent.py`

```python
from google.adk import Agent
from google.adk.integrations.langchain import LangchainTool
import wikipedia
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# Wikimedia now rate-limits the wikipedia package's generic default User-Agent
# (it's shared by every user of the package). Setting a distinctive one fixes
# the `requests.exceptions.JSONDecodeError` you'd otherwise see when the tool runs.
wikipedia.set_user_agent("adk-training-fact-finder/1.0 (https://github.com/adk-training; contact@example.com)")

# 1. According to LangChain documentation, instantiate the tool.
# This sets up the connection to the Wikipedia API.
api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=2000)
langchain_tool_instance = WikipediaQueryRun(api_wrapper=api_wrapper)

# 2. Wrap the LangChain tool instance with the ADK's LangchainTool wrapper.
# The wrapper automatically inspects the tool and creates the schema for the LLM.
wikipedia_tool = LangchainTool(tool=langchain_tool_instance)

# 3. Define the ADK agent and include the wrapped tool in its tools list.
root_agent = Agent(
    name="fact_finder_agent",
    model="gemini-3.8-flash",
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

</SolutionVault>
