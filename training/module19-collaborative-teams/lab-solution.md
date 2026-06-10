---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 21.7 Solution: Building a Collaborative Travel Team

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
    instruction="Provide a brief, enthusiastic 3-day weather forecast for the user's destination."
)

# 2. Define the Flight Booker
# We use 'task' mode because the agent might need to ask 
# clarification questions before it considers its task "complete".
flight_agent = Agent(
    name="flight_booker",
    model="gemini-3.5-flash",
    mode="task",
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
