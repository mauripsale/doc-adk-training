# Filename: agent.py
import os
from google.adk import Agent
from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams
from mcp import StdioServerParameters

# Get the absolute path to our server script.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_TO_SERVER = os.path.join(CURRENT_DIR, "cart_server.py")

root_agent = Agent(
    model='gemini-3.5-flash',
    name='shopping_agent',
    instruction='You are a shopping assistant. Help the user by adding items to their cart and showing them their cart contents.',
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='python3', # Ensure python3 is available in student's path
                    args=[PATH_TO_SERVER],
                ),
            ),
        )
    ],
)
