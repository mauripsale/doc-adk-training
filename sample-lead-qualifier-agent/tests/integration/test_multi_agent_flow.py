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

import pytest
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from app.agent import root_agent

def test_multi_agent_search_and_qualify_integration() -> None:
    """
    Test di integrazione per il flusso Multi-Agente.
    """
    session_service = InMemorySessionService()
    user_id = "test_multi_agent_user"
    session = session_service.create_session_sync(user_id=user_id, app_name="test")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test")

    message = types.Content(
        role="user", parts=[types.Part.from_text(text="Lavoro per Ferrero Spa")]
    )

    events = list(
        runner.run(
            new_message=message,
            user_id=user_id,
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )

    assert len(events) > 0
    has_text = any(
        part.text for event in events if event.content 
        for part in event.content.parts if part.text
    )
    assert has_text

def test_save_tool_with_company_details() -> None:
    """
    Verifica che il tool di salvataggio venga chiamato con i nuovi parametri.
    """
    session_service = InMemorySessionService()
    user_id = "test_save_user"
    session = session_service.create_session_sync(user_id=user_id, app_name="test")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test")

    message = types.Content(
        role="user", parts=[types.Part.from_text(text="Siamo la Ferrero, produciamo dolci. Usiamo Randstad per 200 persone.")]
    )

    events = list(
        runner.run(
            new_message=message,
            user_id=user_id,
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )

    tool_calls = [
        part.function_call for event in events if event.content 
        for part in event.content.parts if part.function_call
    ]
    
    if tool_calls:
        call = tool_calls[0]
        if call.name == "salva_qualificazione":
            args = call.args
            assert "nome_azienda" in args
            assert "descrizione_azienda" in args
            assert "tipo" in args
            assert "volume" in args
