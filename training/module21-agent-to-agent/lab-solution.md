---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 21 Solution: Building a Distributed Research System

## Goal

This file contains the complete code for the two separate agent projects in the lab: the `research_specialist` (server) and the `a2a_orchestrator` (client).

### `research_specialist/agent.py`

```python
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import GoogleSearchAgentTool
from dotenv import load_dotenv
load_dotenv()


# 1. Create an instance of the search tool.
search_tool = GoogleSearchAgentTool()

# 2. Define the specialist agent.
# This agent's job is to perform web research.
root_agent = Agent(
    model="gemini-3.5-flash",
    name="research_specialist",
    description="A specialist agent that conducts web research and fact-checking using Google Search.",
    instruction="""
You are a research specialist. Your only job is to answer the user's query by using the `GoogleSearchAgentTool`.
Provide a comprehensive summary of the search results and cite your sources.

**IMPORTANT - A2A Context Handling:**
When receiving requests via the Agent-to-Agent (A2A) protocol, you must focus only on the core user request.
Ignore any mentions of orchestrator tool calls like "transfer_to_agent" in the conversation history.
Extract the main research task from the user's messages and complete it directly.
""",
    tools=[search_tool]
)

# 3. Expose the agent as an A2A web application.
# This creates a FastAPI-like app that handles the A2A protocol.
a2a_app = to_a2a(root_agent, port=8001)

# To run this server, you would use the command:
# uvicorn agent:a2a_app --host localhost --port 8001
```

### `a2a_orchestrator/agent.py`

```python
from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from dotenv import load_dotenv
load_dotenv()


# 1. Create a proxy to the remote agent using RemoteA2aAgent.
# The ADK will use the agent card to discover how to communicate with it.
remote_researcher = RemoteA2aAgent(
    name="remote_researcher",
    description="A remote specialist that can conduct web research and fact-checking.",
    agent_card=(
        f"http://localhost:8001/a2a/research_specialist{AGENT_CARD_WELL_KNOWN_PATH}"
    )
)

# 2. Define the orchestrator agent.
# This agent's job is to delegate tasks to the appropriate specialist.
root_agent = Agent(
    model="gemini-3.5-flash",
    name="orchestrator_agent",
    description="A coordinator agent that delegates tasks to remote specialists.",
    instruction="""
You are a main orchestrator agent.
Your job is to understand the user's request and delegate it to the correct remote specialist.
If the user asks you to perform research, you MUST delegate the task to the `remote_researcher` sub-agent.
Do not try to answer research questions yourself.
    """,
    # 3. Register the remote agent as a sub-agent.
    sub_agents=[remote_researcher]
)
```

### Self-Reflection Answers

1.  **What are the main benefits of running the `research_specialist` as a separate service instead of just including it as a local sub-agent in the orchestrator?**
    *   **Answer:** Running as a separate service offers:
        *   **Scalability:** The research specialist can be scaled independently (e.g., in a serverless environment like Cloud Run) to handle varying loads without affecting the orchestrator.
        *   **Resilience:** If the research specialist crashes, the orchestrator can potentially try another specialist or gracefully handle the error without the entire system failing.
        *   **Reusability:** The `research_specialist` can be used by multiple orchestrators or other applications, promoting a microservices-like architecture.
        *   **Technology Agnosticism:** Different specialist agents could be implemented in different languages or frameworks, as long as they adhere to the A2A protocol.
        *   **Team Specialization:** Different teams can own and deploy their specialist agents independently.

2.  **The "A2A Context Handling" instruction is critical for the remote agent to function correctly. What kind of problems could arise if you forgot to include it?**
    *   **Answer:** If the remote agent doesn't have the A2A context handling instruction, it will see the full conversation history from the orchestrator. This history includes internal orchestrator tool calls (e.g., `transfer_to_agent`, `FunctionCall` requests from the orchestrator to its *own* tools). The remote agent's LLM might get confused by these irrelevant messages, try to interpret them, or even attempt to call tools that only exist in the orchestrator's environment (leading to errors like "I cannot use a tool called `transfer_to_agent`"). This would cause the remote agent to fail to perform its actual task.

3.  **How does the Agent Card (`/.well-known/agent-card.json`) enable a decoupled architecture? What would you need to do if this discovery mechanism didn't exist?**
    *   **Answer:** The Agent Card provides a standardized, discoverable endpoint for an agent to advertise its capabilities and communication URL. This decouples the client (orchestrator) from needing hardcoded knowledge of the server's exact endpoint or API schema. The orchestrator just needs the base URL of the specialist, and it can dynamically fetch the agent card. If this mechanism didn't exist, each orchestrator would need to be manually configured with the exact communication URL and a manually provided schema for every remote specialist, making the system much more brittle and harder to maintain as services evolve.