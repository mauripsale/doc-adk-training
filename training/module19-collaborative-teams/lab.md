---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 19: Building a Collaborative Travel Team

## Goal

In this lab, you will build a **Travel Planning Team** consisting of a **Coordinator**, a **Weather Specialist**, and a **Flight Booker**. You will learn how to use the `mode` parameter to create a system where sub-agents fulfill specific tasks and then automatically return control to the main planner.

### The Scenario
- **Coordinator** receives the user's travel request.
- It delegates to the **Weather Specialist** (in `single_turn` mode) to get a quick forecast.
- It then delegates to the **Flight Booker** (in `task` mode) to find and "book" a flight (allowing for some back-and-forth about preferences).
- Finally, the Coordinator synthesizes the plan.

### Step 1: Create the Project

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
    - **Observe:** Then it should call the `flight_booker`. The flight booker might ask you "Which airline do you prefer?" or "Do you want a morning flight?". 
    - **Final Check:** After you answer, notice how control **automatically returns** to the `travel_planner` without any "hand-off" code.

### Lab Summary

You have built a Collaborative Agent Team!
- You used **`mode="single_turn"`** for background utility tasks.
- You used **`mode="task"`** for interactive sub-tasks with automatic return.
- You observed how the ADK 2.0 framework manages the hand-off lifecycle so you can focus on agent logic.

### Self-Reflection Questions
- Why would you use `single_turn` instead of `task` for a database lookup node?
- What happens to the conversation history when a sub-agent is in `task` mode? (Hint: Check the Trace tab).
- How does the `mode` setting improve the reliability of complex, multi-step workflows compared to standard `chat` mode?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMTktY29sbGFib3JhdGl2ZS10ZWFtcy9sYWItc29sdXRpb24=`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module19-collaborative-teams/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
