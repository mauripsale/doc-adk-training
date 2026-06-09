import asyncio
import logging
from dotenv import load_dotenv

# --- Step 1: ADK Imports ---
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from agent import root_agent

# Optional: Suppress noisy ADK/httpx logs
logging.getLogger("google.adk").setLevel(logging.WARNING)

load_dotenv()

# --- Step 2: Infrastructure Setup ---
# 1. Create the App: App(name="...", root_agent=...)
app = App(name="support_app", root_agent=root_agent)

# 2. Create the Runner: InMemoryRunner(app=...)
runner = InMemoryRunner(app=app)

async def main():
    print("--- User A (Alice) ---")
    # --- Step 3: Run for Alice ---
    events_a = await runner.run_debug("I was overcharged $50", user_id="Alice")
    
    # --- Step 4: Process Events ---
    for event in events_a:
        if event.is_final_response():
            print(f"Agent to Alice: {event.content.parts[0].text}")

    print("\n--- User B (Bob) ---")
    # --- Step 5: Run for Bob ---
    events_b = await runner.run_debug("My wifi is slow", user_id="Bob")
    for event in events_b:
        if event.is_final_response():
            print(f"Agent to Bob: {event.content.parts[0].text}")

if __name__ == "__main__":
    asyncio.run(main())
