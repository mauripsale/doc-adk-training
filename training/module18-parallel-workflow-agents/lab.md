---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 18: Building a Smart Travel Planner

## Goal

In this lab, you will build a **Smart Travel Planner** using a high-performance **Graph Workflow**. You will use the **Fan-out/Join** pattern to concurrently search for flights, hotels, and activities, and then use a final node to synthesize the results into a complete travel itinerary.

### The Fan-Out/Join Pattern

This lab implements a modern, efficient graph architecture.

```
        ┌──── Node 1 (flights) ────┐
START ──┼──── Node 2 (hotels) ─────┼──→ JoinNode → Merger Node → END
        └──── Node 3 (activities) ─┘
```

### Step 1: Create the Project Structure

1.  **Create a new project:**
    ```shell
    adk create travel_planner
    ```

2.  **Navigate into the directory:**
    ```shell
    cd travel_planner
    ```

### Step 2: Assemble the Parallel Graph

**Exercise:** Open `agent.py`. The specialist agents and schemas have been provided. Your task is to assemble them into a functioning **Workflow** using a **JoinNode**.

```python
# In agent.py (Starter Code)

from __future__ import annotations
from pydantic import BaseModel, Field
from google.adk import Agent, Workflow
from google.adk.workflow import JoinNode

# ===== Specialist Agents (Provided for you) =====

# Example of a finder agent
flight_finder = Agent(
    name="flight_finder",
    model="gemini-3.5-flash",
    instruction="Suggest 2-3 flight options for the requested trip.",
    output_schema=FlightOptionsList,
    output_key="flight_options"
)

# Other agents (hotel_finder, activity_finder, itinerary_builder) are also provided...
hotel_finder = Agent(name="hotel_finder", ...)
activity_finder = Agent(name="activity_finder", ...)
itinerary_builder = Agent(name="itinerary_builder", ...)

# ============================================================================
# PARALLEL WORKFLOW ASSEMBLY
# ============================================================================

# TODO: 1. Create a `JoinNode` named `search_joiner`.
search_joiner = None

# TODO: 2. Create the `root_agent` Workflow.
# Define the edges to:
# - Fan-out from "START" to each finder, then to the JoinNode.
# - Fan-in from the JoinNode to the itinerary_builder.
root_agent = Workflow(
    name="TravelPlanningSystem",
    edges=[
        # Edge 1: START -> flight_finder -> joiner
        ("START", flight_finder, search_joiner),
        
        # Edge 2: START -> hotel_finder -> joiner
        ("START", ..., ...),
        
        # Edge 3: START -> activity_finder -> joiner
        ("START", ..., ...),
        
        # Edge 4: joiner -> itinerary_builder
        (..., ...)
    ]
)
```

### Step 3: Run and Test the Pipeline

1.  **Set up your `.env` file.**
2.  **Start the Dev UI:**
    ```shell
    adk web .
    ```
3.  **Interact with the planner:**
    *   "Plan a 7-day vacation to Honolulu".
4.  **Examine the Graph and Trace Tabs:**
    *   **Graph View:** Observe the "Fan-out" from START and the "Fan-in" at the JoinNode.
    *   **Trace View:** See how the three finders start their execution at the exact same time.

### Lab Summary

You have successfully built a high-performance multi-agent system! 
- You learned that **multiple edges from the same source** create parallel branches.
- You used a **JoinNode** to synchronize and gather data from those branches.
- You realized that graph-based workflows are more powerful and transparent than simple template agents.
