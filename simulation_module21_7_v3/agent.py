from google.adk import Agent

def get_weather(location: str):
    """Gets the weather for a location."""
    return f"The weather in {location} is sunny and 25°C."

def book_flight(destination: str, airline: str = "Any"):
    """Books a flight to a destination."""
    return f"Flight booked to {destination} with {airline}."

# 1. Define the Weather Specialist
weather_agent = Agent(
    name="weather_checker",
    model="gemini-3.5-flash",
    mode="single_turn", 
    instruction="Provide a brief weather forecast for the user's destination. Use the get_weather tool.",
    tools=[get_weather]
)

# 2. Define the Flight Booker
flight_agent = Agent(
    name="flight_booker",
    model="gemini-3.5-flash",
    mode="task",
    instruction="""
    Help the user book a flight. 
    1. Use the book_flight tool.
    2. Ask for their preferred airline if not provided.
    3. Once the flight is booked, stop.
    """,
    tools=[book_flight]
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
