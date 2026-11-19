---
sidebar_position: 19
title: "Module 19: Collaborative Teams - Using Modes and Hand-offs"
pagination_label: "Module 19: Collaborative Teams (Modes & Handoffs) — 📖 Theory & Overview"
---

# Module 19: Collaborative Teams - Using Modes and Hand-offs

![Collaborative Teams Hero (Light)](img/collaborative-teams-hero-light.webp#gh-light-mode-only)
![Collaborative Teams Hero (Dark)](img/collaborative-teams-hero-dark.webp#gh-dark-mode-only)
*Figure: Native conversational hand-offs and collaboration modes between primary triage agents and specialized domain experts.*


## Theory

In Modules 16–18, you orchestrated agents from the outside using `Workflow` graphs. In this module, you let an **orchestrator `Agent`** collaborate directly with a team of specialist `sub_agents` using **Collaboration Modes** and **Native Hand-offs**.

### 1. Collaboration Modes (`chat`, `single_turn`, `task`)

Think of a **Coordinator** managing two specialists — a **Weather Checker** and a **Flight Booker**. When the coordinator delegates to a sub-agent, the **`mode`** parameter controls **who holds the microphone** and **when control returns to the coordinator**:

| Mode | Behavior | Best For |
| :--- | :--- | :--- |
| **`"chat"`** *(default)* | **Full hand-off.** The sub-agent takes over the conversation and keeps control until it decides to transfer elsewhere. No automatic return. | Final routing transfers (e.g., transferring a customer permanently to a billing desk). |
| **`"single_turn"`** | **Quick call-and-return.** The sub-agent never talks directly to the user; it runs one reasoning step, returns the result, and the coordinator stays in control. | Fast background lookups (e.g., checking weather, querying a database) so the coordinator can combine multiple results. |
| **`"task"`** | **Interactive sub-task with guaranteed return.** The sub-agent can ask the user clarifying questions across as many turns as needed. Once finished, it calls ADK's built-in `finish_task` tool and **control automatically returns to the coordinator** in that same turn. | Multi-turn sub-tasks (e.g., gathering flight preferences before handing back to the main travel planner). |

### 2. Using `mode="task"` and `rerun_on_resume=True`

When a `task`-mode sub-agent pauses to ask the user a question and resumes on the next turn, ADK wakes up the dispatch chain. Because of this, **every agent in a `sub_agents` chain using `task` mode must set `rerun_on_resume=True`**:

```python
from google.adk import Agent

# Specialist in 'task' mode: can ask the user questions, then returns control automatically
researcher = Agent(
    name="researcher",
    model="gemini-3.8-flash",
    mode="task",
    rerun_on_resume=True,
    instruction="Research the topic, ask clarifying questions if needed, and summarize."
)

# Coordinator: delegates to researcher and automatically regains control afterward
root_agent = Agent(
    name="coordinator",
    model="gemini-3.8-flash",
    rerun_on_resume=True,
    sub_agents=[researcher],  # ADK automatically injects delegation tools
    instruction="Delegate research to the specialist, then write a final conclusion."
)
```

### 3. How Hand-offs Work Under the Hood

![Collaboration Native Hand-Off Pipeline (Light)](img/collaborative-teams-pipeline-light.webp#gh-light-mode-only)
![Collaboration Native Hand-Off Pipeline (Dark)](img/collaborative-teams-pipeline-dark.webp#gh-dark-mode-only)
*Figure: Seamless control transfer pipeline preserving session memory, context serialization, and telemetry.*

When you list specialists in `sub_agents=[...]`, ADK automatically injects delegation tools (such as `transfer_to_agent` or `request_task_<agent_name>`) into the coordinator.

*   With default **`mode="chat"`**, control transfers to the sub-agent; local sub-agents *can* choose to transfer back to the coordinator or a sibling, but the framework does not enforce it.
*   With **`mode="task"`** or **`mode="single_turn"`**, returning control to the coordinator is **guaranteed by the framework** — so a coordinator can reliably consult multiple specialists in sequence and synthesize their answers.

### 4. Local vs. Remote Specialists: When to Use `AgentTool`

For **local** specialists (Python `Agent` objects in your codebase), `sub_agents=[...]` with `mode="single_turn"` or `mode="task"` is the recommended approach.

For **remote** specialists running as separate network services via the A2A (Agent-to-Agent) protocol (`RemoteA2aAgent`, covered in depth in Module 21), a bare `sub_agents` transfer has no automatic way back within the same turn (and `mode="task"` requires the remote service to explicitly implement a `finish_task` signal). In that case, wrap the remote agent with **`AgentTool`** inside `tools=[...]`:

```python
from google.adk import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools.agent_tool import AgentTool

# Remote A2A services exposed via their Agent Cards
preferences_specialist = RemoteA2aAgent(
    name="preferences_specialist",
    agent_card="https://preferences-service.example.com/a2a/agent-card.json",
)
catalog_specialist = RemoteA2aAgent(
    name="catalog_specialist",
    agent_card="https://catalog-service.example.com/a2a/agent-card.json",
)

# AgentTool wraps each remote agent as a regular tool: call, get result, stay in control!
orchestrator = Agent(
    name="orchestrator",
    model="gemini-3.8-flash",
    instruction="""
    1. Call `preferences_specialist` to check what the user likes.
    2. Call `catalog_specialist` to search for matching products.
    3. Combine both results into one recommendation.
    """,
    tools=[
        AgentTool(agent=preferences_specialist),
        AgentTool(agent=catalog_specialist),
    ],
)
```

With `AgentTool`, the orchestrator calls each remote specialist like a standard function tool, receives its answer, and **never loses control** — making it effortless to combine multiple remote services in one turn.

### Why Use Collaborative Teams?

*   **Predictability:** `single_turn` and `task` modes guarantee when and how control returns to your coordinator.
*   **Natural Conversation:** Context and session history are preserved seamlessly across hand-offs.
*   **Cleaner Prompts:** You don't need fragile prompt hacks telling sub-agents to "transfer back when done."

### Key Takeaways
- **Collaboration Modes (`chat`, `single_turn`, `task`)** control who holds the conversation and whether control returns automatically.
- Use **`mode="single_turn"`** for fast, non-interactive lookups and **`mode="task"`** for multi-turn sub-tasks with guaranteed return (`finish_task`).
- Set **`rerun_on_resume=True`** on every agent in a `task`-mode `sub_agents` chain.
- Prefer **`sub_agents` + `mode`** for local agents, and **`AgentTool`** when composing multiple remote `RemoteA2aAgent` services.
