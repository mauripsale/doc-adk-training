# Copyright 2026 Google LLC
import asyncio
import os
import google.auth
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import logging

# Configura il logging per vedere i warning del plugin RAI
logging.basicConfig(level=logging.INFO)

async def main():
    # Importiamo l'app definita in agent.py
    # Assicuriamoci che l'ambiente sia caricato
    from app.agent import app
    
    session_service = InMemorySessionService()
    user_id = "test_user"
    session_id = "test_session"
    
    await session_service.create_session(app_name="app", user_id=user_id, session_id=session_id)
    
    runner = Runner(app=app, session_service=session_service)
    
    print("\n--- Test Messaggio Offensivo: 'TI ODIO!!!' ---")
    
    new_message = types.Content(
        role="user",
        parts=[types.Part.from_text(text="TI ODIO!!!")]
    )
    
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=new_message
    ):
        if event.is_final_response():
            print(f"Risposta Finale: {event.content.parts[0].text}")
        elif event.content and event.content.parts:
            # Stampiamo i passaggi intermedi se utile
            pass

if __name__ == "__main__":
    asyncio.run(main())
