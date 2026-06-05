# Filename: agent.py
import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# Get the absolute path to our server script.
PATH_TO_SERVER = os.path.abspath("./cart_server.py")

root_agent = LlmAgent(
    model='gemini-3.5-flash',
    name='shopping_agent',
    instruction='You are a shopping assistant. Help the user by adding items to their cart and showing them their cart contents.',
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='python3',
                    args=[PATH_TO_SERVER],
                ),
            ),
        )
    ],
)
