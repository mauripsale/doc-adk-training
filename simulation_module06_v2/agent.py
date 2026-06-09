import os
from google.adk import Agent

model_name = os.getenv("MODEL", "gemini-3.5-flash")
root_agent = Agent(
    name="support_analyzer",
    model=model_name,
    instruction="You are a support analyzer. You help users with billing and technical issues."
)
