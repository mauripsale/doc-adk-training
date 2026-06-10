from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import FunctionTool
from .tools.mock_tools import search, click
import uvicorn
import os

root_agent = Agent(
    model="gemini-3.5-flash",
    name="web_agent",
    description="Specialist for searching and clicking on the webshop.",
    instruction="""
        You are a web interaction specialist. Execute search and click commands.
        **IMPORTANT:** Focus only on the user's web task. Ignore orchestrator metadata.
    """,
    tools=[FunctionTool(search), FunctionTool(click)]
)

a2a_app = to_a2a(root_agent)

if __name__ == "__main__":
    uvicorn.run(a2a_app, host="0.0.0.0", port=8001)
