from google.adk.agents import Agent, RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from google.adk.apps import App
import os

# Define remote nodes
web_agent = RemoteA2aAgent(
    name="web_agent",
    agent_card=f"http://localhost:8001/a2a/web_agent{AGENT_CARD_WELL_KNOWN_PATH}"
)

personalization_agent = RemoteA2aAgent(
    name="personalization_agent",
    agent_card=f"http://localhost:8002/a2a/personalization_agent{AGENT_CARD_WELL_KNOWN_PATH}"
)

# Orchestrator
root_agent = Agent(
    model="gemini-3.5-flash",
    name="shopping_orchestrator",
    instruction="""
        You are a master assistant.
        1. Check preferences via `personalization_agent`.
        2. Search web via `web_agent`.
        3. Help user checkout.
    """,
    sub_agents=[web_agent, personalization_agent]
)

app = App(name="shopping_system", root_agent=root_agent)
