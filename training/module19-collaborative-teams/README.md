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
*   **`task`:** The sub-agent can ask the user questions but **automatically returns control** to the parent once its task is complete -- the model signals "complete" by calling the framework-injected `finish_task` tool, and the moment it does, the return to the parent happens immediately, within that same turn (not on a separate follow-up turn). Until the model calls `finish_task`, the sub-agent stays active across as many turns as it needs.
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

**Without a `mode`, there's no *automatic* return.** A bare `sub_agents=[...]` entry defaults to `chat` mode: once control transfers, that sub-agent becomes the active agent, and the framework does not force it back the way `task`/`single_turn` do. That's not the same as being stuck, though: every local agent's `transfer_to_agent` tool is, by default, aimed at its parent *and* its peers too (unless you set `disallow_transfer_to_parent`/`disallow_transfer_to_peers`), so a `chat`-mode sub-agent is free to transfer back to its coordinator, or sideways to a sibling, the moment the model decides to -- even chaining several hops together within one turn. Verified live: a coordinator with two plain local `sub_agents` and no `mode` set at all can have the first specialist transfer to the second, which then transfers back to the coordinator, all in a single turn, purely because the model chose to call `transfer_to_agent` each time. As Section 1 showed, `mode="task"` or `mode="single_turn"` upgrades that from "possible if the model decides to" to "guaranteed": the framework enforces the return after one step, so a coordinator can call several `task`/`single_turn` sub-agents in sequence and combine their results without depending on each one's judgment (exactly what this lab's `travel_planner` does with `weather_checker` and `flight_booker`).

### 4. Call-and-Return for Remote Agents: `AgentTool`

`RemoteA2aAgent` does expose a `mode` field, but it's much narrower than a local agent's: it only accepts `"task"` or `None` -- there is no `"chat"` or `"single_turn"` for a remote peer. With the default `None`, a `RemoteA2aAgent` is a plain `transfer_to_agent` target, and once the coordinator transfers to it, there is genuinely no framework-provided way back *within that turn*. That's not a matter of policy or configuration, it's structural: `RemoteA2aAgent` doesn't subclass `LlmAgent`, so it has no `disallow_transfer_to_parent`/`disallow_transfer_to_peers` fields, and it runs its own request/response loop against the remote HTTP service instead of ADK's usual LLM tool-calling flow -- so it never gets a `transfer_to_agent` tool injected once it becomes the active agent. And even that undersells it: the remote agent is a separate process running its own, independently-defined agent tree, with no notion of "the orchestrator that called me" or "the sibling agent next door" to transfer to, even in principle. `mode="task"` closes part of that gap -- it hands control back to the parent automatically once the remote task reaches a terminal state -- but only if the remote agent explicitly invokes a `finish_task` signal to report completion, which is a protocol both sides have to implement, not something you get for free the way local `task`/`single_turn` mode is.

ADK 2.0 gives you a second, often clearer way to get call-and-return behavior with any agent, local or remote: **`AgentTool`**. It wraps another agent as a normal entry in a `tools=[...]` list. The calling agent invokes it like any other function tool, gets a result back, and *stays in control* -- free to call another `AgentTool`, or the same one again, before composing a final answer. Unlike a hand-off, it shows up in the trace as an explicit tool call, not an implicit transfer -- and you don't have to configure `mode`, or implement a `finish_task` protocol on the remote side, at all.

```python
from google.adk import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools.agent_tool import AgentTool

# sub_agents, default (chat) mode: hands control to whichever specialist is
# chosen, and it stays active until it decides to transfer again -- a good
# fit when routing is meant to be final, like a support triage handoff.
coordinator_handoff = Agent(
    name="coordinator",
    instruction="Route the user to the right specialist.",
    sub_agents=[billing_specialist, tech_specialist],
)

# preferences_specialist and catalog_specialist are separate services --
# their own independently-defined agent trees, each running as its own
# process -- exposed over A2A, not plain local Agent objects. Each
# RemoteA2aAgent is constructed from the remote service's agent card (a URL
# or file path is fine; this module doesn't stand up real A2A servers, so
# treat the URLs below as illustrative).
preferences_specialist = RemoteA2aAgent(
    name="preferences_specialist",
    agent_card="https://preferences-service.example.com/a2a/agent-card.json",
)
catalog_specialist = RemoteA2aAgent(
    name="catalog_specialist",
    agent_card="https://catalog-service.example.com/a2a/agent-card.json",
)

# AgentTool: call-and-return, explicit, no mode to configure. The
# orchestrator can consult BOTH remote specialists in the same turn and
# combine their results itself. This is the case AgentTool is actually
# built for: composing several RemoteA2aAgents, which have no
# framework-injected transfer-back at all.
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

For **local** agents specifically, this isn't the recommended pattern: `AgentTool`'s own docstring (in `google/adk/tools/agent_tool.py`) says "direct usage of `AgentTool` is discouraged" for that case and tells you to prefer `mode="single_turn"` on a `sub_agents` entry instead, since the framework then exposes the sub-agent as a tool automatically -- verified live, a local coordinator with two `mode="single_turn"` sub_agents calls both specialists as tools and combines their results in one turn, identically to the `AgentTool` version above. `AgentTool`'s real strength is remote agents, which is why the example above uses `RemoteA2aAgent`.

Picture a shopping assistant that must both check a user's saved preferences *and* search a product catalog before it can answer, where both specialists are `RemoteA2aAgent`s running as separate services (as above). Wired with a bare `sub_agents=[...]` (default, `mode=None`), the orchestrator would transfer to `preferences_specialist`, get its answer -- and get stuck there, with no way to also consult `catalog_specialist` in the same turn: this is verified, reproducible behavior, not a hypothetical -- once `preferences_specialist` is active, there is no `transfer_to_agent` tool available to it at all, so it just answers from its own tools and the turn ends without `catalog_specialist` ever being consulted. `mode="task"` on each `RemoteA2aAgent` would fix that, provided both remote agents implement the `finish_task` signal it requires, but `AgentTool` gets you there without touching `mode`, or asking anything extra of the remote side, at all -- and it reads more naturally when you're composing several remote capabilities like tools. This exact mix-up -- registering multiple specialists via bare `sub_agents` and expecting call-and-return -- is a real, common bug in multi-agent designs: an orchestrator that silently stops after consulting only the first specialist it was supposed to combine.

### Why use Collaborative Teams?

*   **Predictability:** You know exactly when and how control will flow back to your main orchestrator.
*   **Natural Conversation:** The transition is seamless for the user, as the context is preserved across nodes.
*   **Cleaner Prompts:** You no longer need to write complex instructions about "how to return control."

### Key Takeaways
- **Collaboration Modes** (`chat`, `task`, `single_turn`) manage sub-agent lifecycle.
- **`mode="task"`** is the standard for delegation where you want the specialist to finish and "come back" to the main flow.
- The framework handles the low-level tool injection (`request_task_...`) automatically.
- **`sub_agents` vs. `AgentTool`:** a bare `sub_agents` entry (default `chat` mode) hands control to one agent at a time with no *automatic* return -- fine when delegation is meant to be final, and for **local** agents still reversible any time the active agent decides to transfer back (parent and peers are valid transfer targets by default). `mode="task"`/`"single_turn"` makes that return automatic for local sub-agents, and `AgentTool`'s own docstring says to prefer `mode="single_turn"` there instead of wrapping a local agent in `AgentTool` directly. For **remote** (`RemoteA2aAgent`) specialists, plain `sub_agents` has no framework-injected way back at all within a turn -- `mode="task"` is the only escape, and it requires the remote side to implement a `finish_task` signal -- so `AgentTool` is the natural choice for composing several remote capabilities that need to be consulted together.
