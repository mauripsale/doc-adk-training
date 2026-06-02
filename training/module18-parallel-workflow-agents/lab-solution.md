---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 18 Solution: Building a Smart Travel Planner

## Goal

This file contains the complete code for the `agent.py` script using the ADK 2.0 **Workflow** pattern for parallel execution.

### `travel_planner/agent.py`

```python
from __future__ import annotations

from pydantic import BaseModel, Field
from google.adk import Agent, Workflow
from google.adk.workflow import JoinNode

# ============================================================================ 
# STRUCTURED DATA SCHEMAS
# ============================================================================ 
class FlightOption(BaseModel):
    airline: str
    price: float

class HotelOption(BaseModel):
    name: str
    price_per_night: float

class ActivityOption(BaseModel):
    name: str
    cost: float

class FlightOptionsList(BaseModel):
    options: list[FlightOption]

class HotelOptionsList(BaseModel):
    options: list[HotelOption]

class ActivityOptionsList(BaseModel):
    options: list[ActivityOption]

# ============================================================================ 
# PARALLEL SEARCH NODES
# ============================================================================ 

flight_finder = Agent(
    name="flight_finder",
    model="gemini-3.5-flash",
    instruction="Suggest 2-3 flight options for the requested trip.",
    output_schema=FlightOptionsList,
    output_key="flight_options"
)

hotel_finder = Agent(
    name="hotel_finder",
    model="gemini-3.5-flash",
    instruction="Suggest 2-3 hotel options for the requested trip.",
    output_schema=HotelOptionsList,
    output_key="hotel_options"
)

activity_finder = Agent(
    name="activity_finder",
    model="gemini-3.5-flash",
    instruction="Suggest 3-4 activities for the destination.",
    output_schema=ActivityOptionsList,
    output_key="activity_options"
)

# ============================================================================ 
# SYNTHESIS NODE
# ============================================================================ 

itinerary_builder = Agent(
    name="itinerary_builder",
    model="gemini-3.5-flash",
    instruction="""
    Create a travel itinerary based on these results:
    Flights: {flight_options}
    Hotels: {hotel_options}
    Activities: {activity_options}
    """
)

# ============================================================================ 
# GRAPH ASSEMBLY
# ============================================================================ 

# 1. Define the Join point
search_joiner = JoinNode(name="search_joiner")

# 2. Define the Workflow with Parallel Edges
root_agent = Workflow(
    name="TravelPlanningSystem",
    edges=[
        # Fan-out from START to all finders, converging at the JoinNode
        ("START", flight_finder, search_joiner),
        ("START", hotel_finder, search_joiner),
        ("START", activity_finder, search_joiner),
        
        # Fan-in: Once all finders are done, run the builder
        (search_joiner, itinerary_builder)
    ]
)
```

### Self-Reflection Answers

1.  **What is the performance advantage of using parallel edges?**
    *   **Answer:** In a graph where multiple nodes are connected from the same source (like "START"), ADK 2.0 runs them concurrently. The total execution time for the parallel section is roughly equal to the **slowest** single node, rather than the sum of all nodes. This is much faster for tasks involving external API or LLM calls.

2.  **Why do we use a `JoinNode`?**
    *   **Answer:** The `JoinNode` acts as a synchronization point. It ensures that the `itinerary_builder` only starts after **all** the preceding finders have finished. Without it, the builder might start as soon as just one finder finishes, leading to incomplete data.

3.  **How is data passed from the parallel finders to the final builder?**
    *   **Answer:** In this solution, we use `output_key` to save the results of each finder into the global session state. The `itinerary_builder` then interpolates those keys (`{flight_options}`, etc.) into its instruction. While the `JoinNode` also collects outputs, using the session state is more flexible for building complex prompts in the final node.
