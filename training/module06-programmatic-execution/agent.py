import asyncio
from google.adk import Agent
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.genai import types

import os
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()
model_name = os.getenv("MODEL", "gemini-3.5-flash")

# Create an async main function
async def main():
    # 2. Define Your Agent
    root_agent = Agent(
        model=model_name,
        name="trivia_agent",
        instruction="Answer questions concisely.",
    )

    # 3. Create the App
    app = App(name="trivia_app", root_agent=root_agent)

    # 4. Create a Runner
    runner = InMemoryRunner(app=app)

    # 5. Prepare a function to run the agent
    async def run_prompt(user_id: str, new_message: str):
        print(f'** User ({user_id}) says: {new_message}')
        # In ADK 2.0, we use run_debug for simple string interactions
        # or run_async for full control over the event stream.
        async for event in runner.run_async(
            user_id=user_id,
            new_message=new_message,
        ):
            if event.is_final_response():
                print(f'** {event.author}: {event.content.parts[0].text}')

    # 6. Run queries
    await run_prompt("user1", "What is the capital of France?")
    await run_prompt("user2", "What is the capital of Italy?")

if __name__ == "__main__":
    asyncio.run(main())
