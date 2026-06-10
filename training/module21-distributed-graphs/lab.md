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
    uv run adk create a2a_orchestrator
    uv run adk create research_specialist
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
from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import GoogleSearchAgentTool
from dotenv import load_dotenv
load_dotenv()

# TODO: 1. Create an instance of the GoogleSearchAgentTool.

# TODO: 2. Define the agent (The Node)
# - Remember to include the A2A Context Handling instruction!
root_agent = Agent(...)

# TODO: 3. Expose as an A2A web application using 'to_a2a'
# Hint: a2a_app = to_a2a(root_agent, port=8001)
```

### Step 3: Build the Orchestrator (The Client)

**Exercise:** Navigate into the `a2a_orchestrator` directory. Open `agent.py` and implement the orchestrator using a **Workflow** and a **RemoteA2aAgent**.

```python
# In a2a_orchestrator/agent.py (Starter Code)
from google.adk import Agent, Workflow
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from dotenv import load_dotenv
load_dotenv()

# TODO: 1. Define the Proxy Node (RemoteA2aAgent) pointing to the specialist server
# Hint: use f"http://localhost:8001/a2a/research_specialist{AGENT_CARD_WELL_KNOWN_PATH}"
remote_researcher = ...

# TODO: 2. Define the Local Coordinator Node and register 'remote_researcher'
coordinator = ...

# TODO: 3. Build the Distributed Workflow Graph (edges START -> coordinator)
root_agent = ...
```
**Action:** Create a `.env` file in this directory for the orchestrator's Gemini model.

### Step 4: Run and Test the Distributed System

This requires two separate terminals.

1.  **Terminal 1 (Specialist Server):**
    *   Navigate to the `research_specialist` directory.
    *   Run `uvicorn agent:a2a_app --host localhost --port 8001`.

2.  **Terminal 2 (Orchestrator Client):**
    *   Navigate to the parent `adk-training` directory.
    *   Run `uv run adk web a2a_orchestrator`.

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
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMjEtZGlzdHJpYnV0ZWQtZ3JhcGhzL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module21-distributed-graphs/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
