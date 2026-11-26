---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 16: Collaborative Teams (Modes & Handoffs) — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 16: Building a Collaborative Travel Team

## Goal

In this lab, you will build a **Travel Planning Team** consisting of a **Coordinator**, a **Weather Specialist**, and a **Flight Booker**. You will learn how to use the `mode` parameter to create a system where sub-agents fulfill specific tasks and then automatically return control to the main planner.

### The Scenario
- **Coordinator** receives the user's travel request.
- It delegates to the **Weather Specialist** (in `single_turn` mode, equipped with `google_search`) to fetch a grounded real-world forecast.
- It then delegates to the **Flight Booker** (in `task` mode, also equipped with `google_search`) to look up real flight options and gather user preferences across multiple turns before returning control.
- Finally, the Coordinator synthesizes the complete travel plan.

> **Important (`google_search` Grounding & Scope):** Both specialists use ADK's built-in `google_search` tool (`from google.adk.tools import google_search`) so weather forecasts and flight schedule lookups return grounded real-world results. Running `google_search` requires a valid `GOOGLE_API_KEY` (or an authenticated Vertex AI GCP project). While flight options and schedules are looked up live via Google Search, actual ticket purchase/booking is of course simulated and never performed.

### Step 1: Create the Project

<Setup/>

```shell
uv run adk create travel_team
cd travel_team
```

### Step 2: Implement the Collaborative Specialists

Open `agent.py`. Your task is to define the team, attach `tools=[google_search]` to both specialists, and configure their collaboration `mode`s correctly.

**Exercise:** Complete the agent definitions by setting the appropriate `mode` and `tools` for each specialist.

```python
# In agent.py (Starter Code)
from google.adk import Agent
from google.adk.tools import google_search

# Note: every agent below needs rerun_on_resume=True. Any agent that's part
# of a sub_agents dispatch chain can be "woken up" when a task-mode
# sub-agent pauses and resumes across turns -- without the flag on ALL
# three agents (coordinator included), you'll hit:
# "ValueError: A node must have rerun_on_resume=True."

# 1. Define the Weather Specialist
# Hint: Use 'single_turn' mode for a quick, non-interactive lookup, and
# attach tools=[google_search] for grounded real-world forecasts.
weather_agent = Agent(
    name="weather_checker",
    model="gemini-3.8-flash",
    mode=...,  # TODO: Set collaboration mode for a quick 1-step lookup
    rerun_on_resume=True,
    tools=[...],  # TODO: Equip with google_search for real-world weather forecasts
    instruction="""
    # TODO: Write instructions to use google_search to provide a brief,
    # grounded 3-day weather forecast for the requested destination.
    """
)

# 2. Define the Flight Booker
# Hint: Use 'task' mode to allow the agent to ask the user questions about
# flight preferences before finishing, and attach tools=[google_search] to
# look up real flight options (without performing an actual ticket purchase).
flight_agent = Agent(
    name="flight_booker",
    model="gemini-3.8-flash",
    mode=...,  # TODO: Set collaboration mode for multi-turn task with auto-return
    rerun_on_resume=True,
    tools=[...],  # TODO: Equip with google_search to look up real flight options
    instruction="""
    # TODO: Write instructions to help the user select a flight:
    # 1. Ask about preferred airline or departure time if not provided.
    # 2. Use google_search to look up realistic flight options/schedules.
    # 3. Present a clear itinerary confirmation (note: no real ticket is purchased).
    """
)

# 3. Define the Coordinator
# Hint: Coordinator should NOT have a mode set (it's the root), but it
# still needs rerun_on_resume=True (see note above).
root_agent = Agent(
    name="travel_planner",
    model="gemini-3.8-flash",
    rerun_on_resume=True,
    instruction="""
    # TODO: Write instructions to coordinate the team.
    # 1. Get weather from weather_checker.
    # 2. Arrange flight options via flight_booker.
    # 3. Present the final cohesive plan.
    """,
    # TODO: Register your specialists here
    sub_agents=[] 
)
```

### Step 3: Run and Test

1.  **Return to the parent directory and launch the Dev UI:**
    ```shell
    cd ..
    uv run adk web
    ```
    *(Select `travel_team` from the agent dropdown in the UI).*
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
- Why would you use `single_turn` instead of `task` for a database lookup specialist?
- What happens to the conversation history when a sub-agent is in `task` mode? (Hint: Check the Trace tab).
- How does the `mode` setting improve the reliability of complex, multi-step workflows compared to standard `chat` mode?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="16">

# Lab 16 Solution: Building a Collaborative Travel Team

## Goal

This file contains the complete code for the `agent.py` script using ADK 2.0 Collaboration Modes.

### `travel_team/agent.py`

*(Note: `google_search` requires a valid `GOOGLE_API_KEY` or an authenticated Vertex AI GCP project. Flight lookups use live search grounding, while actual ticket booking is simulated and not performed.)*

```python
from google.adk import Agent
from google.adk.tools import google_search

# 1. Define the Weather Specialist
# We use 'single_turn' because this is a quick data retrieval task
# with no need for further user interaction.
weather_agent = Agent(
    name="weather_checker",
    model="gemini-3.8-flash",
    mode="single_turn",
    # Required on every agent in a sub_agents dispatch chain -- without it:
    # "ValueError: A node must have rerun_on_resume=True."
    rerun_on_resume=True,
    tools=[google_search],
    instruction=(
        "Use google_search to look up current weather conditions and provide "
        "a brief, grounded 3-day weather forecast for the user's destination."
    ),
)

# 2. Define the Flight Booker
# We use 'task' mode because the agent might need to ask
# clarification questions before it considers its task "complete".
flight_agent = Agent(
    name="flight_booker",
    model="gemini-3.8-flash",
    mode="task",
    # Required for any node that might pause and resume across turns --
    # without it: "ValueError: A node must have rerun_on_resume=True."
    rerun_on_resume=True,
    tools=[google_search],
    instruction="""
    Help the user find and select a flight.
    1. Ask for their departure city, preferred airline, or departure time if not provided.
    2. Use google_search to look up real-world flight routes and schedule options.
    3. Once the user confirms their choice, summarize the selected flight details (simulated booking only -- no actual ticket is purchased) and finish the task.
    """,
)

# 3. Define the Coordinator
# The root agent manages the high-level flow.
# It doesn't need a mode.
root_agent = Agent(
    name="travel_planner",
    model="gemini-3.8-flash",
    # The coordinator itself also needs this -- it's part of the same
    # dispatch chain and can be "woken up" when a sub-agent's task resumes.
    rerun_on_resume=True,
    instruction="""
    You are a travel planning coordinator.
    Your goal is to build a complete plan for the user.

    PROCESS:
    1. Call `weather_checker` to get a grounded weather forecast.
    2. Call `flight_booker` to research flight options and gather user preferences.
    3. Once both sub-tasks are done, present a final cohesive travel summary to the user.
    """,
    sub_agents=[weather_agent, flight_agent],
)
```

### Self-Reflection Answers

1.  **Why would you use `single_turn` instead of `task` for a database lookup specialist?**
    *   **Answer:** Efficiency. `single_turn` is faster and cheaper because it forbids any further interaction. If a node's job is purely to fetch data and return it, `single_turn` ensures it doesn't accidentally start a conversation with the user, which would waste tokens and time.

2.  **What happens to the conversation history when a sub-agent is in `task` mode?**
    *   **Answer:** In ADK 2.0, task-mode agents operate in a "branch" of the session. While they have access to the relevant history to perform their task, the parent agent remains the "source of truth." When the task completes, the results are bubbled up to the parent's context.

3.  **How does the `mode` setting improve the reliability of complex workflows?**
    *   **Answer:** It makes the "Return to Parent" behavior deterministic. Instead of hoping the LLM will remember to hand back control, the framework **enforces** the return based on the mode. This prevents "lost in thought" scenarios where a sub-agent continues chatting with the user indefinitely instead of returning to the main workflow.

### Bonus Solution: `weather_checker` as an `AgentTool`

```python
from google.adk import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

# No mode needed -- AgentTool doesn't use the sub_agents lifecycle at all.
weather_agent = Agent(
    name="weather_checker",
    model="gemini-3.8-flash",
    tools=[google_search],
    instruction=(
        "Use google_search to look up current weather conditions and provide "
        "a brief, grounded 3-day weather forecast for the user's destination."
    ),
)

flight_agent = Agent(
    name="flight_booker",
    model="gemini-3.8-flash",
    mode="task",
    rerun_on_resume=True,
    tools=[google_search],
    instruction=(
        "Help the user find a flight using google_search, ask for preferences if needed, "
        "confirm the simulated selection (no actual ticket purchase), and finish the task."
    ),
)

root_agent = Agent(
    name="travel_planner",
    model="gemini-3.8-flash",
    rerun_on_resume=True,
    instruction="""
    You are a travel planning coordinator.
    1. Call the `weather_checker` tool to get the forecast.
    2. Call the `flight_booker` to arrange travel.
    3. Once both sub-tasks are done, present a final summary to the user.
    """,
    tools=[AgentTool(agent=weather_agent)],
    sub_agents=[flight_agent],
)
```
Verified live: the result is the same forecast text, but the Trace tab shows no separate `weather_checker` author entry -- the call and its result appear as a single function call/response pair inside `travel_planner`'s own turn, exactly like calling a regular tool.

</SolutionVault>
