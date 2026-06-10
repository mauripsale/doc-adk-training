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

from google.adk.agents import Agent, RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from dotenv import load_dotenv
import asyncio

load_dotenv()

# --- Remote Specialist Definitions ---

# 1. Web Agent (Discovered via A2A Card)
web_specialist = RemoteA2aAgent(
    name="web_agent",
    description="Specialist for searching and clicking on the e-commerce website.",
    agent_card=f"http://localhost:8001/a2a/web_agent{AGENT_CARD_WELL_KNOWN_PATH}"
)

# 2. Personalization Agent (Discovered via A2A Card)
personalization_specialist = RemoteA2aAgent(
    name="personalization_agent",
    description="Specialist for saving and retrieving user preferences (size, color, brands).",
    agent_card=f"http://localhost:8002/a2a/personalization_agent{AGENT_CARD_WELL_KNOWN_PATH}"
)

# --- Master Orchestrator Agent ---
root_agent = Agent(
    model="gemini-3.5-flash",
    name="shopping_orchestrator",
    instruction="""
        You are a master shopping assistant. Your job is to help users find and buy products by coordinating with specialists.
        
        **Workflow:**
        1.  **Initial Inquiry:** Ask the user what they are looking for. If they upload an image, describe it and ask to search for it.
        2.  **Consult Preferences:** Check if the user has any saved preferences (size, color) by delegating to the `personalization_agent`.
        3.  **Web Search:** Search for products by delegating to the `web_agent`.
        4.  **Interaction:** Guide the user through product exploration (descriptions, features, reviews) using the `web_agent`.
        5.  **Finalize:** Once the user is ready, help them select the right options and click "Buy Now" via the `web_agent`.
        
        **Guidelines:**
        - Always summarize the specialist's findings for the user.
        - Be professional and helpful.
    """,
    sub_agents=[web_specialist, personalization_specialist]
)

# --- Infrastructure ---
app = App(name="personalized_shopping", root_agent=root_agent)
runner = InMemoryRunner(app=app)

if __name__ == "__main__":
    # Note: Requires web_agent (port 8001) and personalization_agent (port 8002) to be running.
    async def main():
        print("🛍️  Personalized Shopping Orchestrator Started.")
        print("Type 'exit' to quit.")
        while True:
            user_input = input("User: ")
            if user_input.lower() == 'exit':
                break
            async for event in runner.run_async(user_id="default_user", message=user_input):
                if event.is_final_response():
                    print(f"Agent: {event.content.parts[0].text}")

    asyncio.run(main())
