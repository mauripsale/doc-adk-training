from pathlib import Path
from dotenv import load_dotenv
from google.adk import Agent
from .tools.calculator import add, subtract, multiply, divide

load_dotenv(Path(__file__).with_name(".env"), override=True)

root_agent = Agent(
    name="calculator_agent",
    model="gemini-3.8-flash",
    description="An agent node that can perform arithmetic calculations.",
    instruction="""
You are a helpful calculator assistant.
When the user asks you to perform a calculation, you MUST use the appropriate tool.
Clearly state the result to the user.
If the user asks something else, politely decline.
""",
    tools=[add, subtract, multiply, divide],
)
