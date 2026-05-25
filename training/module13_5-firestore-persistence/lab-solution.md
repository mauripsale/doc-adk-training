---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 13.5: Implementing Firestore Persistence Solution

Below is the complete `agent.py` script upgraded to use `FirestoreSessionService`.

```python
# agent.py (Solution)
import asyncio
import os
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
# 1. Import Runner and FirestoreSessionService
from google.adk.runners import Runner
from google.adk.sessions import FirestoreSessionService
from google.adk.tools import ToolContext, FunctionTool
from google.genai import types

load_dotenv()

def remember_name(name: str, tool_context: ToolContext) -> str:
    """Saves the user's name to memory."""
    tool_context.session.state["user_name"] = name
    return f"I have successfully remembered that your name is {name}."

agent = LlmAgent(
    model="gemini-3.5-flash",
    name="MemoryAgent",
    instruction="You are a helpful assistant. Use the remember_name tool if the user tells you their name.",
    tools=[remember_name]
)

async def main():
    app_name = "persistence_demo"
    user_id = "test_user_001"
    
    # 2. Get the Project ID from the environment
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable must be set.")
    
    # 3. Initialize the Firestore Session Service
    print(f"Initializing Firestore in project: {project_id}")
    firestore_service = FirestoreSessionService(project_id=project_id)
    
    # 4. Use the base Runner with the firestore_service
    runner = Runner(
        agent=agent, 
        session_service=firestore_service
    )
    
    # 1. Create or get the session
    session = await runner.session_service.create_session(app_name=app_name, user_id=user_id)
    
    print(f"--- Session ID: {session.id} ---")
    
    # 2. Start a simple loop
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        content = types.Content(role="user", parts=[types.Part.from_text(text=user_input)])
        
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=content
        ):
            if event.content and event.content.parts and event.content.parts[0].text:
                print(f"Agent: {event.content.parts[0].text}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Self-Reflection Answers

1.  **Why is it important to use the same `user_id` and `app_name` when testing persistence across script restarts?**
    *   **Answer:** The `FirestoreSessionService` uses a combination of the `app_name`, `user_id`, and `session_id` to uniquely locate the correct conversation document in the database. If you change the `user_id` or `app_name` when you restart the script, the ADK will create a brand new, empty session document instead of loading the old one, making it look like the persistence failed.
2.  **If you open the Google Cloud Console and look at your Firestore database, what kind of structure (Collections/Documents) do you see the ADK has created?**
    *   **Answer:** By default, you will see a root collection named `adk_sessions`. Inside this collection, there are documents where the document ID corresponds to the `session_id`. Inside these session documents, you will find the serialized `state` dictionary and sub-collections (like `events`) containing the individual messages of the conversation history.
