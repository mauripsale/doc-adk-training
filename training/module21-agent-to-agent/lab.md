---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 21: Building a Distributed Research System Challenge

## Goal

### Goal

In this lab, you will build a distributed multi-agent system. You will create a main **Orchestrator** agent and a separate, standalone **Research Specialist** agent. The Orchestrator will delegate tasks to the Research Specialist over the network using the ADK's A2A capabilities.

### Step 1: Create the Project Structure

1.  **Create two separate agent projects** that will run independently.
    ```shell
    adk create a2a_orchestrator
    adk create research_specialist
    ```
    When prompted, choose the **Programmatic (Python script)** option for both.

2.  **Install Server Dependencies:**
    Navigate into the `research_specialist` directory and install `uvicorn`, which is needed to run the agent as a web server.
    ```shell
    cd research_specialist
    pip install uvicorn google-adk[a2a]
    cd ..
    ```

### Step 2: Build the Research Specialist (The Server)

**Exercise:** Navigate into the `research_specialist` directory. Open `agent.py` and implement the specialist agent and expose it as an A2A server.

```python
# In research_specialist/agent.py (Starter Code)
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import GoogleSearchAgentTool
from dotenv import load_dotenv
load_dotenv()


# TODO: 1. Create an instance of the GoogleSearchAgentTool.
search_tool = ...

# TODO: 2. Define the `root_agent`. It should be an `Agent` that:
# - Is named "research_specialist".
# - Has an instruction to act as a research specialist using the search tool.
# - **Crucially**, includes the A2A Context Handling instruction to ignore
#   orchestrator tool calls like `transfer_to_agent`.
# - Includes the `search_tool` in its `tools` list.
root_agent = Agent(
    model="gemini-3.5-flash",
    name="research_specialist",
    description="A specialist agent that conducts web research and fact-checking.",
    instruction="""
# Your instruction here...
# Remember to add the A2A Context Handling section!
""",
    tools=[...]
)

# TODO: 3. Use the `to_a2a()` function to wrap your `root_agent`.
# This exposes it as a web application on port 8001.
a2a_app = to_a2a(...)
```
**Action:** Create a `.env` file in this directory and configure it for **Vertex AI**, as the search tool requires it.

### Step 3: Build the Orchestrator (The Client)

**Exercise:** Navigate into the `a2a_orchestrator` directory. Open `agent.py` and implement the orchestrator agent that consumes the remote service.

```python
# In a2a_orchestrator/agent.py (Starter Code)
from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from dotenv import load_dotenv
load_dotenv()


# TODO: 1. Create a `RemoteA2aAgent` instance named `remote_researcher`.
# - Give it a name and a description.
# - Point its `agent_card` URL to the specialist server you will be running.
#   (Using the `AGENT_CARD_WELL_KNOWN_PATH` constant is recommended).
remote_researcher = RemoteA2aAgent(
    name="remote_researcher",
    description="A remote specialist that can conduct web research and fact-checking.",
    agent_card=f"..."
)

# TODO: 2. Define the `root_agent` as an orchestrator.
# - Its instruction should tell it to delegate research tasks to the `remote_researcher`.
# - Add the `remote_researcher` to its `sub_agents` list.
root_agent = Agent(
    model="gemini-3.5-flash",
    name="orchestrator_agent",
    description="A coordinator agent that delegates tasks to remote specialists.",
    instruction="""...""",
    sub_agents=[...]
)
```
**Action:** Create a `.env` file in this directory for the orchestrator's Gemini model.

### Step 4: Run and Test the Distributed System

This requires two separate terminals.

1.  **Terminal 1 (Specialist Server):**
    *   Navigate to the `research_specialist` directory.
    *   Run `uvicorn agent:a2a_app --host localhost --port 8001`.

2.  **Terminal 2 (Orchestrator Client):**
    *   Navigate to the parent `adk-training` directory.
    *   Run `adk web a2a_orchestrator`.

3.  **Interact with the System:**
    *   Open the Dev UI for the orchestrator (`http://localhost:8080`).
    *   Give it a research task, like: "Please research the latest advancements in quantum computing."
    *   Observe the **Trace View** to confirm that the `orchestrator_agent` successfully delegates the task to the `remote_researcher`.

### Having Trouble?
If you get stuck, you can find the complete, working code in the `lab-solution.md` file.

### Lab Summary
You have successfully built a distributed multi-agent system. You have learned to:
*   Expose an ADK agent as a network service using `to_a2a()`.
*   Connect to a remote agent using the `RemoteA2aAgent` class.
*   Orchestrate tasks between agents running in separate processes.

### Self-Reflection Questions
- What are the main benefits of running the `research_specialist` as a separate service instead of just including it as a local sub-agent in the orchestrator?
- The "A2A Context Handling" instruction is critical for the remote agent to function correctly. What kind of problems could arise if you forgot to include it?
- How does the Agent Card (`/.well-known/agent-card.json`) enable a decoupled architecture? What would you need to do if this discovery mechanism didn't exist?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMjEtYWdlbnQtdG8tYWdlbnQvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module21-agent-to-agent/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
