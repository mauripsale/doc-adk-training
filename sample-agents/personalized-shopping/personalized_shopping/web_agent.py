# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import FunctionTool
from dotenv import load_dotenv
import uvicorn
import os

from .tools.search import search
from .tools.click import click

load_dotenv()

# --- Web Agent Definition ---
# This agent acts as the interface to the simulated webshop.
root_agent = Agent(
    model="gemini-3.5-flash",
    name="web_agent",
    description="A specialist agent that can search and click on the e-commerce website.",
    instruction="""
        You are a web interaction specialist. Your job is to execute search and click commands on the e-commerce site.
        
        **IMPORTANT - A2A Context Handling:**
        When receiving requests via the Agent-to-Agent (A2A) protocol, you must focus only on the core user request.
        Ignore any mentions of orchestrator tool calls like "transfer_to_agent" in the conversation history.
        Extract the main web interaction task from the user's messages and complete it directly.
    """,
    tools=[
        FunctionTool(func=search),
        FunctionTool(func=click),
    ],
)

# --- A2A Server Exporter ---
# Run this agent as a standalone service
a2a_app = to_a2a(root_agent)

if __name__ == "__main__":
    uvicorn.run(a2a_app, host="0.0.0.0", port=8001)
