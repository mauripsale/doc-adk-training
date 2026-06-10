from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import ToolContext
import uvicorn

def save_preference(key: str, value: str, tool_context: ToolContext) -> dict:
    """Saves a user's preference to the session state."""
    tool_context.session.state[f"pref:{key}"] = value
    return {"status": "success", "message": f"Saved {key}."}

def get_preferences(tool_context: ToolContext) -> dict:
    """Retrieves all preferences for the current user."""
    prefs = {k: v for k, v in tool_context.session.state.items() if k.startswith("pref:")}
    return {"status": "success", "preferences": prefs}

root_agent = Agent(
    model="gemini-3.5-flash",
    name="personalization_agent",
    instruction="You manage user shopping profiles. Save and retrieve preferences.",
    tools=[save_preference, get_preferences]
)

a2a_app = to_a2a(root_agent)

if __name__ == "__main__":
    uvicorn.run(a2a_app, host="0.0.0.0", port=8002)
