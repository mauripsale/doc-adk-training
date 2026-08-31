---
sidebar_position: 19
title: "Module 19: Collaborative Teams - Using Modes and Hand-offs"
---

# Module 19: Collaborative Teams - Using Modes and Hand-offs

## Theory

So far, you have learned how to define a graph structure from the outside. But what if the nodes themselves could decide how to collaborate? 

ADK 2.0 introduces **Collaboration Modes** and **Native Hand-offs** to create fluid, self-managing agent teams.

### 1. Collaboration Modes

When you add a sub-agent to an `Agent` or `Workflow`, you can specify its **`mode`**. This setting controls how the sub-agent behaves and how it returns control to the parent.

*   **`chat` (Default):** Full multi-turn interaction. The sub-agent keeps control until it explicitly performs another transfer.
*   **`task`:** The sub-agent can ask the user questions but **automatically returns control** to the parent once its task is complete.
*   **`single_turn`:** No user interaction allowed. The sub-agent performs a single reasoning step and returns the result immediately.

### 2. The Power of `task` Mode

In ADK 1.x, you often had to prompt your sub-agents to "hand back control." In ADK 2.0, using `mode="task"`, this is handled by the framework.

```python
from google.adk import Agent

# Specialist in 'task' mode
researcher = Agent(
    name="researcher",
    mode="task", # 🔄 Automatic return to parent!
    rerun_on_resume=True, # Required whenever a node can pause/resume across turns
    instruction="Research the topic and provide a summary."
)

# Coordinator
root_agent = Agent(
    name="coordinator",
    rerun_on_resume=True, # Required: the coordinator is part of the same dispatch chain
    sub_agents=[researcher], # Framework auto-injects 'request_task_researcher' tool
    instruction="Delegate research to the specialist, then write a conclusion."
)
```

### 3. Agent Transfer (The "Hand-off")

Even without modes, an agent can decide to hand over the entire conversation to another node in the graph. This is the **Agent Transfer** pattern. 

The framework automatically injects tools like `request_task_<agent_name>` into the parent's toolkit based on the `sub_agents` list. The LLM then "calls" these tools to perform the hand-off.

**Without a `mode`, this is a permanent, one-way handoff.** A bare `sub_agents=[...]` entry defaults to `chat` mode -- once control transfers, that sub-agent becomes the active agent for the rest of the run, with no framework-enforced way back. As Section 1 showed, setting `mode="task"` or `mode="single_turn"` fixes this for *local* agents: the framework enforces the return, so a coordinator can call several `task`/`single_turn` sub-agents in sequence and combine their results (exactly what this lab's `travel_planner` does with `weather_checker` and `flight_booker`).

### 4. Call-and-Return for Remote Agents: `AgentTool`

`mode` is a field on every agent, including a `RemoteA2aAgent` -- but for remote agents, ADK 2.0 gives you a second, often clearer way to get the same call-and-return behavior: **`AgentTool`**. It wraps another agent (local or remote) as a normal entry in a `tools=[...]` list. The calling agent invokes it like any other function tool, gets a result back, and *stays in control* -- free to call another `AgentTool`, or the same one again, before composing a final answer. Unlike a hand-off, it shows up in the trace as an explicit tool call, not an implicit transfer -- and you don't have to reason about which `mode` a remote agent should run in.

```python
from google.adk import Agent
from google.adk.tools.agent_tool import AgentTool

# sub_agents, default mode: a permanent, one-way handoff to whichever
# specialist is chosen -- right when delegation is genuinely final.
coordinator_handoff = Agent(
    name="coordinator",
    instruction="Route the user to the right specialist.",
    sub_agents=[billing_specialist, tech_specialist],
)

# AgentTool: call-and-return, explicit, no mode to configure. The
# orchestrator can consult BOTH specialists in the same turn and combine
# their results itself.
orchestrator = Agent(
    name="orchestrator",
    instruction="""
    1. Call `preferences_specialist` to check what the user likes.
    2. Call `catalog_specialist` to search for matching products.
    3. Combine both results into one recommendation.
    """,
    tools=[AgentTool(agent=preferences_specialist), AgentTool(agent=catalog_specialist)],
)
```

Picture a shopping assistant that must both check a user's saved preferences *and* search a product catalog before it can answer, where both specialists are `RemoteA2aAgent`s running as separate services. Wired with a bare `sub_agents=[...]` (default `chat` mode), the orchestrator would transfer to `preferences_specialist`, get its answer -- and get stuck there, with no way to also consult `catalog_specialist` in the same turn. `mode="task"` on each `RemoteA2aAgent` would fix that, but `AgentTool` gets you there without touching `mode` at all, and reads more naturally when you're composing several remote capabilities like tools. This exact mix-up -- registering multiple specialists via bare `sub_agents` and expecting call-and-return -- is a real, common bug in multi-agent designs: an orchestrator that silently stops after consulting only the first specialist it was supposed to combine.

### Why use Collaborative Teams?

*   **Predictability:** You know exactly when and how control will flow back to your main orchestrator.
*   **Natural Conversation:** The transition is seamless for the user, as the context is preserved across nodes.
*   **Cleaner Prompts:** You no longer need to write complex instructions about "how to return control."

### Key Takeaways
- **Collaboration Modes** (`chat`, `task`, `single_turn`) manage sub-agent lifecycle.
- **`mode="task"`** is the standard for delegation where you want the specialist to finish and "come back" to the main flow.
- The framework handles the low-level tool injection (`request_task_...`) automatically.
- **`sub_agents` vs. `AgentTool`:** a bare `sub_agents` entry (default `chat` mode) is a permanent, one-way handoff -- use it when delegation is final. `mode="task"`/`"single_turn"` gives local sub-agents call-and-return semantics; `AgentTool` gives the same call-and-return semantics explicitly, without configuring `mode`, and is the natural choice for composing remote (`RemoteA2aAgent`) specialists as tools.
