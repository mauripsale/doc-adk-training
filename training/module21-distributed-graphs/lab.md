---
sidebar_position: 2
title: "Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 21: Building a Distributed Research System Challenge

## Goal

In this lab, you will build a distributed multi-agent system. You will create a main **Orchestrator** agent and a separate, standalone **Research Specialist** agent. The Orchestrator will delegate tasks to the Research Specialist over the network using the ADK's A2A capabilities.

### Step 1: Create the Project Structure

<Setup/>

1.  **Create two separate agent projects** that will run independently.
    ```shell
    uv run adk create a2a_orchestrator
    uv run adk create research_specialist
    ```

2.  **Install Server Dependencies:**
    From your `adk-training` root, install `uvicorn`, which is needed to run the agent as a web server (plain `pip install` fails on PEP 668-managed Pythons and doesn't reach your `uv`-managed venv anyway):
    ```shell
    uv add uvicorn sse-starlette "google-adk[a2a]"
    ```

### Step 2: Build the Research Specialist (The Server)

**Exercise:** Navigate into the `research_specialist` directory. Open `agent.py` and implement the specialist agent and expose it as an A2A server.

```python
# In research_specialist/agent.py (Starter Code)
from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import google_search
from dotenv import load_dotenv
load_dotenv()

# TODO: 1. Define the agent (The Node), passing google_search in its tools list
# - Remember to include the A2A Context Handling instruction!
root_agent = Agent(...)

# TODO: 2. Expose as an A2A web application using 'to_a2a'
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
# Hint: use f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}"
# Hint: pass use_legacy=False to opt into the reliability-fixed A2A executor
remote_researcher = ...

# TODO: 2. Define the Local Coordinator Node and register 'remote_researcher'
coordinator = ...

# TODO: 3. Build the Distributed Workflow Graph (edges START -> coordinator)
root_agent = ...
```
**Action:** Confirm the `.env` file `adk create` generated in this directory is configured for the orchestrator's Gemini model.

### Step 4: Run and Test the Distributed System

This requires two separate terminals.

1.  **Terminal 1 (Specialist Server):**
    *   Navigate to the `research_specialist` directory.
    *   Run `uvicorn agent:a2a_app --host localhost --port 8001`.

2.  **Terminal 2 (Orchestrator Client):**
    *   Navigate to the parent `adk-training` directory.
    *   Run `uv run adk web a2a_orchestrator`.

3.  **Interact with the System:**
    *   Open the Dev UI for the orchestrator (`http://localhost:8000` -- `adk web`'s default port).
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

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="21">

# Lab 21 Solution: Building a Distributed Research System

## Goal

This file contains the complete code for the two separate agent projects using ADK 2.0 graph patterns.

### `research_specialist/agent.py` (The Remote Node)

```python
from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import google_search
from dotenv import load_dotenv
load_dotenv()

# 1. Specialist Node
root_agent = Agent(
    model="gemini-3.5-flash",
    name="research_specialist",
    description="A specialist node that conducts web research using Google Search.",
    instruction="""
You are a research specialist. Use the search tool to answer the user's query.
Provide a comprehensive summary and cite your sources.

**IMPORTANT - A2A Context Handling:**
When receiving requests via the A2A protocol, ignore any internal graph transition messages. 
Focus only on the core user query and fulfill the research task directly.
""",
    tools=[google_search]
)

# 2. Expose as A2A service
a2a_app = to_a2a(root_agent, port=8001)
```

### `a2a_orchestrator/agent.py` (The Main Workflow)

```python
from google.adk import Agent, Workflow
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from dotenv import load_dotenv
load_dotenv()

# 1. Define the Proxy Node
# Points to the Agent Card generated by the research specialist.
remote_researcher = RemoteA2aAgent(
    name="remote_researcher",
    description="A remote specialist that can conduct web research.",
    agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}",
    use_legacy=False,
)

# 2. Define the Coordinator Node
coordinator = Agent(
    model="gemini-3.5-flash",
    name="coordinator",
    instruction="Analyze the user request. If research is needed, delegate to 'remote_researcher'.",
    sub_agents=[remote_researcher]
)

# 3. Build the Root Workflow
# This orchestrates both local and remote nodes in a single graph.
root_agent = Workflow(
    name="DistributedSupportSystem",
    edges=[("START", coordinator)]
)
```

### Self-Reflection Answers

1.  **What are the main benefits of running the `research_specialist` as a separate service?**
    *   **Answer:** It enables a "**Graph of Graphs**" architecture. You can have a team maintain the Research Specialist independently, scaling it on Cloud Run without affecting your main orchestrator. It also allows the same Research node to be reused across many different agentic workflows.

2.  **Why is "A2A Context Handling" even more important in a graph architecture?**
    *   **Answer:** In ADK 2.0, the conversation history can include detailed events from the Workflow Runtime (like node transitions or state updates). Without explicit instructions to ignore these, the remote node might try to "help" with the orchestration logic instead of performing its specific task.

3.  **How does `RemoteA2aAgent` simplify building distributed systems?**
    *   **Answer:** It abstracts the network layer. To the `Workflow` engine, `RemoteA2aAgent` is just another node. You don't have to manually write HTTP requests or handle JSON serialization; you just define the edge in the graph, and ADK handles the rest.

</SolutionVault>
