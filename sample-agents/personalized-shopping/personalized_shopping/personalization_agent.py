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
from google.adk.tools import ToolContext
from dotenv import load_dotenv
import uvicorn

load_dotenv()

# --- Stateful Tools ---
def save_preference(key: str, value: str, tool_context: ToolContext) -> dict:
    """Saves a user's preference (e.g., color, size, brand)."""
    state_key = f"pref:{key}"
    tool_context.session.state[state_key] = value
    return {"status": "success", "message": f"User preference '{key}' saved as '{value}'."}

def get_preferences(tool_context: ToolContext) -> dict:
    """Retrieves all saved preferences for the current user."""
    prefs = {
        k.replace("pref:", ""): v 
        for k, v in tool_context.session.state.items() 
        if k.startswith("pref:")
    }
    return {"status": "success", "preferences": prefs}

# --- Personalization Agent Definition ---
root_agent = Agent(
    model="gemini-3.5-flash",
    name="personalization_agent",
    description="A specialist agent that manages user preferences and shopping profiles.",
    instruction="""
        You are a personalization specialist. Your job is to remember and retrieve user preferences like sizes, colors, and preferred brands.
        
        **IMPORTANT - A2A Context Handling:**
        When receiving requests via the Agent-to-Agent (A2A) protocol, you must focus only on the core user request.
        Ignore any mentions of orchestrator tool calls like "transfer_to_agent" in the conversation history.
        Extract the preference management task from the user's messages and complete it directly.
    """,
    tools=[save_preference, get_preferences]
)

# --- A2A Server Exporter ---
a2a_app = to_a2a(root_agent)

if __name__ == "__main__":
    uvicorn.run(a2a_app, host="0.0.0.0", port=8002)
