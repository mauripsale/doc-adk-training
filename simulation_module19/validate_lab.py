from agent import weather_agent, flight_agent, root_agent
from google.adk import Agent

def test_agent_config():
    # Verify Weather Agent
    assert weather_agent.name == "weather_checker"
    assert weather_agent.mode == "single_turn"
    print("✓ Weather Specialist configured correctly with mode='single_turn'")

    # Verify Flight Booker
    assert flight_agent.name == "flight_booker"
    assert flight_agent.mode == "task"
    print("✓ Flight Booker configured correctly with mode='task'")

    # Verify Coordinator
    assert root_agent.name == "travel_planner"
    assert len(root_agent.sub_agents) == 2
    assert weather_agent in root_agent.sub_agents
    assert flight_agent in root_agent.sub_agents
    print("✓ Coordinator configured correctly with sub-agents")

if __name__ == "__main__":
    try:
        test_agent_config()
        print("\nModule 19 Simulation Successful!")
    except AssertionError as e:
        print(f"\nSimulation Failed: {e}")
        exit(1)
