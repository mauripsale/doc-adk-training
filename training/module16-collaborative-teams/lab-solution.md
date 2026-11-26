---
sidebar_position: 3
title: "Lab Solution"
---

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
