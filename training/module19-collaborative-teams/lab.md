---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 19: Collaborative Teams (Modes & Handoffs) — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 19: Building a Collaborative Travel Team

## Goal

In this lab, you will build a **Travel Planning Team** consisting of a **Coordinator**, a **Weather Specialist**, and a **Flight Booker**. You will learn how to use the `mode` parameter to create a system where sub-agents fulfill specific tasks and then automatically return control to the main planner.

### The Scenario
- **Coordinator** receives the user's travel request.
- It delegates to the **Weather Specialist** (in `single_turn` mode) to get a quick forecast.
- It then delegates to the **Flight Booker** (in `task` mode) to find and "book" a flight (allowing for some back-and-forth about preferences).
- Finally, the Coordinator synthesizes the plan.

### Step 1: Create the Project

<Setup/>

```shell
uv run adk create travel_team
cd travel_team
```

### Step 2: Implement the Collaborative Nodes

Open `agent.py`. Your task is to define the team and configure their modes correctly.

**Exercise:** Complete the agent definitions by setting the appropriate `mode` for each specialist.

```python
# In agent.py (Starter Code)
from google.adk import Agent

# Note: every agent below needs rerun_on_resume=True. Any node that's part
# of a sub_agents dispatch chain can be "woken up" when a task-mode
# sub-agent pauses and resumes across turns -- without the flag on ALL
# three agents (coordinator included), you'll hit:
# "ValueError: A node must have rerun_on_resume=True."

# 1. Define the Weather Specialist
# Hint: Use 'single_turn' mode for a quick, non-interactive lookup.
weather_agent = Agent(
    name="weather_checker",
    model="gemini-3.5-flash",
    rerun_on_resume=True,
    instruction="""
    # TODO: Write instructions to provide a brief 3-day forecast 
    # for the requested destination.
    """
)

# 2. Define the Flight Booker
# Hint: Use 'task' mode to allow the agent to ask the user 
# questions about their flight preferences before finishing.
flight_agent = Agent(
    name="flight_booker",
    model="gemini-3.5-flash",
    rerun_on_resume=True,
    instruction="""
    # TODO: Write instructions to help the user book a flight. 
    # Ask about preferred airline or time if not provided.
    """
)

# 3. Define the Coordinator
# Hint: Coordinator should NOT have a mode set (it's the root), but it
# still needs rerun_on_resume=True (see note above).
root_agent = Agent(
    name="travel_planner",
    model="gemini-3.5-flash",
    rerun_on_resume=True,
    instruction="""
    # TODO: Write instructions to coordinate the team.
    # 1. Get weather from weather_checker.
    # 2. Book flight via flight_booker.
    # 3. Present the final cohesive plan.
    """,
    # TODO: Register your specialists here
    sub_agents=[] 
)
```

### Step 3: Run and Test

1.  **Launch the Dev UI:**
    ```shell
    uv run adk web .
    ```
2.  **Verify the Flow:**
    - Ask: "I want to go to Tokyo next week."
    - **Observe:** The `travel_planner` should call the `weather_checker`. 
    - **Observe:** Then it should call the `flight_booker`. The flight booker might ask you "Which airline do you prefer?" or "Do you want a morning flight?". Keep answering -- it may take more than one exchange before it has everything it needs.
    - **Final Check:** Watch the Trace tab for the turn where `flight_booker` decides it's done: it calls the framework-injected `finish_task` tool, and control **returns to `travel_planner` immediately, within that same turn** -- not on a separate follow-up turn -- with no "hand-off" code written by you. `travel_planner` then presents the final combined plan in that same response.

> **Bonus (optional):** Try rewiring `weather_checker` as an `AgentTool` instead of a `sub_agents` entry: drop `mode="single_turn"`, remove it from `sub_agents`, and instead give `travel_planner` `tools=[AgentTool(agent=weather_agent)]` (import from `google.adk.tools.agent_tool`). Re-run the same request and compare the Trace tab: with `AgentTool` the whole weather lookup happens *inside* `travel_planner`'s own function call -- there's no separate `weather_checker` author entry the way there was with `mode="single_turn"`. Same call-and-return result, different plumbing.

### Lab Summary

You have built a Collaborative Agent Team!
- You used **`mode="single_turn"`** for background utility tasks.
- You used **`mode="task"`** for interactive sub-tasks with automatic return.
- You observed how the ADK 2.0 framework manages the hand-off lifecycle so you can focus on agent logic.

### Self-Reflection Questions
- Why would you use `single_turn` instead of `task` for a database lookup node?
- What happens to the conversation history when a sub-agent is in `task` mode? (Hint: Check the Trace tab).
- How does the `mode` setting improve the reliability of complex, multi-step workflows compared to standard `chat` mode?
- In this lab, `travel_planner` consults two sub-agents (`weather_checker`, `flight_booker`) and combines their results, because both use `mode="task"`/`"single_turn"`, which forces the return to the coordinator. Now imagine `weather_checker` and `flight_booker` were both `RemoteA2aAgent`s -- separate services -- registered via a bare `sub_agents=[...]` with no `mode` set. What would happen the first time the coordinator delegated? What are two different ways to fix it?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="19">

# Lab 19 Solution: Building a Collaborative Travel Team

## Goal

This file contains the complete code for the `agent.py` script using ADK 2.0 Collaboration Modes.

### `travel_team/agent.py`

```python
from google.adk import Agent

# 1. Define the Weather Specialist
# We use 'single_turn' because this is a quick data retrieval task
# with no need for further user interaction.
weather_agent = Agent(
    name="weather_checker",
    model="gemini-3.5-flash",
    mode="single_turn",
    # Required on every agent in a sub_agents dispatch chain -- without it:
    # "ValueError: A node must have rerun_on_resume=True."
    rerun_on_resume=True,
    instruction="Provide a brief, enthusiastic 3-day weather forecast for the user's destination."
)

# 2. Define the Flight Booker
# We use 'task' mode because the agent might need to ask 
# clarification questions before it considers its task "complete".
flight_agent = Agent(
    name="flight_booker",
    model="gemini-3.5-flash",
    mode="task",
    # Required for any node that might pause and resume across turns --
    # without it: "ValueError: A node must have rerun_on_resume=True."
    rerun_on_resume=True,
    instruction="""
    Help the user book a flight. 
    1. Ask for their preferred airline or time if not provided.
    2. Once you have the info, confirm the 'booking' (simulated) and stop.
    """
)

# 3. Define the Coordinator
# The root agent manages the high-level flow. 
# It doesn't need a mode.
root_agent = Agent(
    name="travel_planner",
    model="gemini-3.5-flash",
    # The coordinator itself also needs this -- it's part of the same
    # dispatch chain and can be "woken up" when a sub-agent's task resumes.
    rerun_on_resume=True,
    instruction="""
    You are a travel planning coordinator.
    Your goal is to build a complete plan for the user.
    
    PROCESS:
    1. Call the `weather_checker` to get the forecast.
    2. Call the `flight_booker` to arrange travel.
    3. Once both sub-tasks are done, present a final summary to the user.
    """,
    sub_agents=[weather_agent, flight_agent] 
)
```

### Self-Reflection Answers

1.  **Why would you use `single_turn` instead of `task` for a database lookup node?**
    *   **Answer:** Efficiency. `single_turn` is faster and cheaper because it forbids any further interaction. If a node's job is purely to fetch data and return it, `single_turn` ensures it doesn't accidentally start a conversation with the user, which would waste tokens and time.

2.  **What happens to the conversation history when a sub-agent is in `task` mode?**
    *   **Answer:** In ADK 2.0, task-mode agents operate in a "branch" of the session. While they have access to the relevant history to perform their task, the parent agent remains the "source of truth." When the task completes, the results are bubbled up to the parent's context.

3.  **How does the `mode` setting improve the reliability of complex workflows?**
    *   **Answer:** It makes the "Return to Parent" behavior deterministic. Instead of hoping the LLM will remember to hand back control, the framework **enforces** the return based on the mode. This prevents "lost in thought" scenarios where a sub-agent continues chatting with the user indefinitely instead of returning to the main workflow.

4.  **If `weather_checker` and `flight_booker` were both `RemoteA2aAgent`s registered via a bare `sub_agents=[...]` with no `mode` set, what would happen the first time the coordinator delegated? What are two different ways to fix it?**
    *   **Answer:** A bare `sub_agents` entry defaults to `chat` mode, which is a permanent, one-way handoff. The coordinator would transfer to `weather_checker`, and `weather_checker` -- a separate remote service with no knowledge of `flight_booker` or the original coordinator -- would become the active agent for the rest of the run. `flight_booker` would never be called, and the coordinator would never regain control to combine the two results. Two fixes: (1) set `mode="task"` on each `RemoteA2aAgent` -- that's the only mode a `RemoteA2aAgent` accepts besides `None` (no `"single_turn"` there, unlike local agents), and it also requires the remote side to implement a `finish_task` signal; or (2) wrap both remote agents as `AgentTool(agent=...)` entries in the coordinator's `tools=[...]` list instead of `sub_agents`, which gives call-and-return semantics without configuring `mode`, or needing anything extra from the remote side, at all (see Module 19's README, Section 4).

### Bonus Solution: `weather_checker` as an `AgentTool`

```python
from google.adk import Agent
from google.adk.tools.agent_tool import AgentTool

# No mode needed -- AgentTool doesn't use the sub_agents lifecycle at all.
weather_agent = Agent(
    name="weather_checker",
    model="gemini-3.5-flash",
    instruction="Provide a brief, enthusiastic 3-day weather forecast for the user's destination."
)

root_agent = Agent(
    name="travel_planner",
    model="gemini-3.5-flash",
    rerun_on_resume=True,
    instruction="""
    You are a travel planning coordinator.
    1. Call the `weather_checker` tool to get the forecast.
    2. Call the `flight_booker` to arrange travel.
    3. Once both sub-tasks are done, present a final summary to the user.
    """,
    tools=[AgentTool(agent=weather_agent)],
    sub_agents=[flight_agent]
)
```
Verified live: the result is the same forecast text, but the Trace tab shows no separate `weather_checker` author entry -- the call and its result appear as a single function call/response pair inside `travel_planner`'s own turn, exactly like calling a regular tool.

</SolutionVault>
