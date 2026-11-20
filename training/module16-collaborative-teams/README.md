---
sidebar_position: 16
title: "Module 16: Collaborative Teams - Modes and Hand-offs"
pagination_label: "Module 16: Collaborative Teams (Modes & Handoffs) — 📖 Theory & Overview"
---

# Module 16: Collaborative Teams - Modes and Hand-offs

> **🧭 Where We Are in Part 3:** In **Module 15**, your `router_agent` handed off the conversation to a specialist (`sub_agents`), and that specialist stayed active afterward (`mode="chat"`). Here in **Module 16**, we complete **Chapter A (LLM-Driven Agent Teams)** by learning how **`mode="single_turn"`** and **`mode="task"`** automatically return control to your coordinator so multiple specialists can collaborate on one plan!

![Collaborative Teams Hero (Light)](img/collaborative-teams-hero-light.webp#gh-light-mode-only)
![Collaborative Teams Hero (Dark)](img/collaborative-teams-hero-dark.webp#gh-dark-mode-only)
*Figure: Native conversational hand-offs and collaboration modes between primary triage agents and specialized domain experts.*

## Theory

When a coordinator needs input from **two or more** specialists to fulfill a single user request — for example, scouting an event venue *and* customizing a catering menu — a plain one-way hand-off isn't enough. You need a guarantee that each specialist finishes its job and hands the microphone back to the coordinator.

ADK 2.0 solves this declaratively with **Collaboration Modes**.

### 1. Collaboration Modes (`chat`, `single_turn`, `task`)

When you register a sub-agent, the **`mode`** parameter controls **who holds the microphone** and **when control returns to the coordinator**:

| Mode | Behavior | Best For |
| :--- | :--- | :--- |
| **`"chat"`** *(default)* | **Full hand-off.** The sub-agent takes over the conversation and keeps control until it decides to transfer elsewhere. No automatic return. | One-way triage transfers (like Module 15's Greeting Router or transferring permanently to a billing desk). |
| **`"single_turn"`** | **Quick call-and-return.** The sub-agent never talks directly to the user; it runs one reasoning step, returns the result, and the coordinator stays in control. | Fast background lookups (e.g., checking venue capacity, querying a database) so the coordinator can combine multiple results. |
| **`"task"`** | **Interactive sub-task with guaranteed return.** The sub-agent can ask the user clarifying questions across as many turns as needed. Once finished, it calls ADK's built-in `finish_task` tool and **control automatically returns to the coordinator** in that same turn. | Multi-turn sub-tasks (e.g., gathering dietary preferences for catering before handing back to the main event coordinator). |

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
    instruction="Research the topic, ask clarifying questions if needed, and summarize.",
)

# Coordinator: delegates to researcher and automatically regains control afterward
root_agent = Agent(
    name="coordinator",
    model="gemini-3.8-flash",
    rerun_on_resume=True,
    sub_agents=[researcher],  # ADK automatically injects delegation tools
    instruction="Delegate research to the specialist, then write a final conclusion.",
)
```

### 3. How Hand-offs Work Under the Hood

![Collaboration Native Hand-Off Pipeline (Light)](img/collaborative-teams-pipeline-light.webp#gh-light-mode-only)
![Collaboration Native Hand-Off Pipeline (Dark)](img/collaborative-teams-pipeline-dark.webp#gh-dark-mode-only)
*Figure: Seamless control transfer pipeline preserving session memory, context serialization, and telemetry.*

When you list specialists in `sub_agents=[...]`, ADK automatically injects delegation tools (such as `transfer_to_agent` or `request_task_<agent_name>`) into the coordinator:

*   With default **`mode="chat"`**, control transfers to the sub-agent; local sub-agents *can* choose to transfer back, but the framework does not enforce it.
*   With **`mode="task"`** or **`mode="single_turn"`**, returning control to the coordinator is **guaranteed by the framework** — so a coordinator can reliably consult multiple specialists in sequence and synthesize their answers.

> **Alternative Tool Wrapper (`AgentTool`):** ADK also provides `AgentTool(agent=...)` (from `google.adk.tools.agent_tool`), which wraps an agent inside `tools=[...]`. For **local** Python agents, ADK recommends preferring `sub_agents` with `mode="single_turn"` (and reserving `AgentTool` for external service proxies covered in Module 21).

<KnowledgeCheck
  id="m16-collaboration-modes"
  question="Which Collaboration Mode allows a specialist sub-agent to ask the user follow-up questions across multiple turns and then automatically return control to the coordinator as soon as the sub-task is complete?"
  options={[
    "mode='chat'",
    "mode='single_turn'",
    "mode='task'",
    "mode='static'"
  ]}
  correctIndex={2}
  hint="Think about which mode injects `finish_task` so an interactive specialist returns control automatically when done."
  explanation="`mode='task'` lets the specialist converse with the user across as many turns as needed to gather details, and immediately returns control to the parent coordinator the moment it invokes `finish_task`."
/>

### Why Use Collaborative Teams?

*   **Predictability:** `single_turn` and `task` modes guarantee when and how control returns to your coordinator.
*   **Natural Conversation:** Context and session history are preserved seamlessly across hand-offs.
*   **Cleaner Prompts:** You don't need fragile prompt hacks telling sub-agents to "transfer back when done."

### Key Takeaways
- **Collaboration Modes (`chat`, `single_turn`, `task`)** control who holds the conversation and whether control returns automatically.
- Use **`mode="single_turn"`** for fast, non-interactive lookups and **`mode="task"`** for multi-turn sub-tasks with guaranteed return (`finish_task`).
- Set **`rerun_on_resume=True`** on every agent in a `task`-mode `sub_agents` chain.
