import asyncio
import os
import unittest
from unittest.mock import MagicMock, AsyncMock
from google.adk import Agent, Runner
from google.adk.apps import App
from firestore_provider import FirestoreSessionService
from dotenv import load_dotenv

load_dotenv()

agent = Agent(
    model="gemini-3.5-flash",
    name="PersistentAgent",
    instruction="You are a helpful assistant that remembers the user's favorite color."
)

async def main_simulation():
    # Setup metadata
    project_id = "test-project"
    app = App(name="extensibility_demo", root_agent=agent)
    
    # Mock Firestore Client
    mock_fs_client = MagicMock()
    mock_fs_client.collection = MagicMock()
    
    # Mock behavior for create_session/get_session
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_session_ref = AsyncMock()
    mock_session_ref.get.return_value = mock_doc
    mock_session_ref.set = AsyncMock()
    mock_fs_client.collection.return_value.document.return_value.collection.return_value.document.return_value.collection.return_value.document.return_value = mock_session_ref
    
    # Instantiate service with mocked client
    custom_fs = FirestoreSessionService(project_id=project_id)
    custom_fs._client = mock_fs_client
    
    runner = Runner(
        app=app, 
        session_service=custom_fs
    )
    
    print("🚀 [SIMULATION] Testing Runner with Custom Firestore Provider...")
    
    # Verify we can at least create the runner and it has the right service
    assert runner.session_service == custom_fs
    print("✅ Runner correctly injected with Custom Provider.")
    
    # Test session creation
    session = await custom_fs.create_session(app_name="test", user_id="user1")
    assert session.app_name == "test"
    print("✅ Session creation through Custom Provider works.")

    print("\n🏁 [SIMULATION] Module 13.5 Validation Complete!")

if __name__ == "__main__":
    asyncio.run(main_simulation())
