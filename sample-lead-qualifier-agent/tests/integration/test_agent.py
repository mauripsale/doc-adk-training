# Copyright 2026 Google LLC
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

import time
import pytest
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.api_core import exceptions

from app.agent import root_agent

def run_with_retry(runner, message, user_id, session_id, max_retries=3):
    """
    Helper per eseguire l'agente con retry in caso di Resource Exhausted (429).
    """
    for attempt in range(max_retries):
        try:
            return list(
                runner.run(
                    new_message=message,
                    user_id=user_id,
                    session_id=session_id,
                    run_config=RunConfig(streaming_mode=StreamingMode.SSE),
                )
            )
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5 # Aspetta 5, 10 secondi...
                time.sleep(wait_time)
                continue
            raise e

def test_agent_stream() -> None:
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(user_id="test_user", app_name="test")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test")

    message = types.Content(role="user", parts=[types.Part.from_text(text="Buongiorno, chi sei?")])
    
    events = run_with_retry(runner, message, "test_user", session.id)
    
    assert len(events) > 0
    has_text = any(part.text for event in events if event.content for part in event.content.parts if part.text)
    assert has_text


def test_agent_multi_agent_delegation() -> None:
    """
    Test di integrazione con retry per gestire le quote API.
    """
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(user_id="test_user_del", app_name="test")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test")

    message = types.Content(role="user", parts=[types.Part.from_text(text="Lavoro per Ferrero Spa.")])

    # Usiamo il meccanismo di retry per evitare il fallimento della pipeline su 429
    events = run_with_retry(runner, message, "test_user_del", session.id)

    has_text = any(part.text for event in events if event.content for part in event.content.parts if part.text)
    assert has_text

def test_agent_final_qualification_flow() -> None:
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(user_id="test_user_save", app_name="test")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test")

    message = types.Content(role="user", parts=[types.Part.from_text(text="Siamo la Ferrero Spa, usiamo Adecco per 150 persone.")])

    events = run_with_retry(runner, message, "test_user_save", session.id)

    has_save_call = any(
        part.function_call and part.function_call.name == "salva_qualificazione"
        for event in events if event.content 
        for part in event.content.parts
    )
    
    has_confirmation = any(
        "salvat" in part.text.lower() 
        for event in events if event.content 
        for part in event.content.parts if part.text
    )

    assert has_save_call or has_confirmation
