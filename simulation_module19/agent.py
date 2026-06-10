from google.adk import Agent

# 1. Define the Weather Specialist
weather_agent = Agent(
    name="weather_checker",
    model="gemini-3.5-flash",
    mode="single_turn", 
    instruction="Provide a brief, enthusiastic 3-day weather forecast for the user's destination."
)

# 2. Define the Flight Booker
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
