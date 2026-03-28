---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 18 Solution: Building a Smart Travel Planner

## Goal

This file contains the complete code for the `agent.py` script in the Smart Travel Planner lab.

### `travel-planner/agent.py`

```python
from __future__ import annotations

from pydantic import BaseModel, Field
from google.adk.agents import Agent, ParallelAgent, SequentialAgent

# ============================================================================ 
# STRUCTURED DATA SCHEMAS
# ============================================================================ 
class FlightOption(BaseModel):
    airline: str
    departure_time: str
    arrival_time: str
    price: float

class HotelOption(BaseModel):
    name: str
    rating: int
    amenities: list[str]
    price_per_night: float

class ActivityOption(BaseModel):
    name: str
    description: str
    cost: float

class FlightOptionsList(BaseModel):
    options: list[FlightOption]

class HotelOptionsList(BaseModel):
    options: list[HotelOption]

class ActivityOptionsList(BaseModel):
    options: list[ActivityOption]

# ============================================================================ 
# PARALLEL SEARCH AGENTS
# ============================================================================ 

# ===== Parallel Branch 1: Flight Finder =====
flight_finder = Agent(
    name="flight_finder",
    model="gemini-2.5-flash",
    description="Searches for available flights",
    instruction=(
        "You are a flight search specialist. Based on the user's travel request, "
        "suggest 2-3 realistic flight options.\n"
    ),
    output_schema=FlightOptionsList,
    output_key="flight_options"  # UNIQUE key to avoid conflicts!
)

# ===== Parallel Branch 2: Hotel Finder =====
hotel_finder = Agent(
    name="hotel_finder",
    model="gemini-2.5-flash",
    description="Searches for available hotels",
    instruction=(
        "You are a hotel search specialist. Based on the user's travel request, "
        "suggest 2-3 realistic hotel options.\n"
    ),
    output_schema=HotelOptionsList,
    output_key="hotel_options"  # UNIQUE key to avoid conflicts!
)

# ===== Parallel Branch 3: Activity Finder =====
activity_finder = Agent(
    name="activity_finder",
    model="gemini-2.5-flash",
    description="Searches for local activities and attractions",
    instruction=(
        "You are a travel activity specialist. Based on the user's destination, "
        "suggest 3-4 must-do activities or attractions.\n"
    ),
    output_schema=ActivityOptionsList,
    output_key="activity_options"  # UNIQUE key to avoid conflicts!
)

# ============================================================================ 
# SYNTHESIS AGENT
# ============================================================================ 

# ===== Merger Agent: Itinerary Builder =====
itinerary_builder = Agent(
    name="itinerary_builder",
    model="gemini-2.5-flash",
    description="Compiles the final travel itinerary",
    instruction=(
        "You are an expert travel agent. Create a complete, day-by-day travel itinerary "
        "based on the structured options provided by your team.\n"
        "\n"
        "**Flight Options (JSON):**\n"
        "{flight_options}\n"
        "\n"
        "**Hotel Options (JSON):**\n"
        "{hotel_options}\n"
        "\n"
        "**Activity Options (JSON):**\n"
        "{activity_options}\n"
        "\n"
        "Create a cohesive itinerary that:\n"
        "1. Selects the best flight and hotel combination (explain your choice briefly).\n"
        "2. Organizes the activities into a logical daily schedule.\n"
        "3. Adds practical travel tips for the destination.\n"
        "\n"
        "Format the output as a beautiful, easy-to-read travel plan in markdown."
    )
)

# ============================================================================ 
# PIPELINE ASSEMBLY
# ============================================================================ 

# 1. Create the Parallel Step (Fan-Out)
parallel_search = ParallelAgent(
    name="parallel_search",
    sub_agents=[
        flight_finder,
        hotel_finder,
        activity_finder
    ],
    description="Executes all search agents concurrently"
)

# 2. Create the Sequential Pipeline (Gather)
travel_planning_system = SequentialAgent(
    name="TravelPlanningSystem",
    sub_agents=[
        parallel_search,   # Step 1: Get all data at once
        itinerary_builder  # Step 2: Synthesize the result
    ],
    description="Full travel planning workflow"
)

# 3. Define Root Agent
root_agent = travel_planning_system
```

### Self-Reflection Answers

1.  **What would be the performance impact if you replaced the `ParallelAgent` in this lab with a `SequentialAgent`?**
    *   **Answer:** The execution time would increase significantly. In a sequential setup, the total time would be the *sum* of all three search agents' execution times (Time_Flight + Time_Hotel + Time_Activity). With `ParallelAgent`, the total time is roughly equal to the *slowest* single agent (max(Time_Flight, Time_Hotel, Time_Activity)). For IO-bound tasks like LLM generation or API calls, parallel execution is much faster.

2.  **It is critical that the three finder agents have different `output_key`s. What would happen if they all had the same `output_key`, like `"search_result"`?**
    *   **Answer:** This would cause a **race condition**. Since they share the same session state object and are running at the same time, they would all try to write to `state['search_result']`. The final value in that key would be unpredictable—it would just be whichever agent happened to finish last, overwriting the results of the others. The `itinerary_builder` would then only see one partial result instead of all three.

3.  **Can you think of another real-world problem (besides travel planning) where the fan-out/gather pattern would be a highly effective architecture?**
    *   **Answer:**
        *   **Code Review:** Run a `SecurityScannerAgent`, `StyleCheckerAgent`, and `BugFinderAgent` in parallel on a pull request, then use a `SummaryAgent` to compile a final review report.
        *   **Medical Diagnosis:** Have specialist agents (Cardiologist, Neurologist, etc.) analyze a patient's chart concurrently, then have a Lead Doctor agent synthesize a diagnosis.
        *   **News Aggregation:** Search for "Politics", "Technology", and "Sports" news in parallel, then generate a "Daily Briefing" newsletter.
