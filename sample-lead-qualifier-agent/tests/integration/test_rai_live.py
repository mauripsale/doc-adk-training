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
import logging
from unittest.mock import MagicMock
from google.genai import types
from google.adk.models.llm_response import LlmResponse
from app.rai_service import ResponsibleAIPlugin

logger = logging.getLogger(__name__)

@pytest.fixture
def rai_plugin():
    """
    Inizializza il plugin RAI reale (senza mock del client NLP).
    """
    return ResponsibleAIPlugin()

@pytest.fixture
def mock_ctx():
    """
    Mock per InvocationContext/CallbackContext.
    """
    ctx = MagicMock()
    ctx.session.state = {}
    ctx.state = ctx.session.state
    return ctx

@pytest.mark.asyncio
async def test_rai_live_safe_input(rai_plugin, mock_ctx):
    """
    Verifica che un input sicuro NON venga bloccato dall'API reale.
    """
    safe_text = "Buongiorno, mi piacerebbe avere informazioni sui vostri servizi di recruiting."
    user_message = types.Content(role="user", parts=[types.Part.from_text(text=safe_text)])
    
    # Dovrebbe restituire None (non intercettato)
    result = await rai_plugin.on_user_message_callback(
        invocation_context=mock_ctx, 
        user_message=user_message
    )
    
    assert result is None
    assert mock_ctx.session.state.get("rai_input_blocked") is not True

@pytest.mark.asyncio
async def test_rai_live_unsafe_input(rai_plugin, mock_ctx):
    """
    Verifica che un input chiaramente violante venga bloccato dall'API reale.
    """
    # Usiamo una frase che tipicamente attiva le categorie di moderazione (es. Hate/Insult/Toxic)
    unsafe_text = "Siete dei completi idioti e vi odio dal profondo del cuore, brutti bastardi!"
    user_message = types.Content(role="user", parts=[types.Part.from_text(text=unsafe_text)])
    
    result = await rai_plugin.on_user_message_callback(
        invocation_context=mock_ctx, 
        user_message=user_message
    )
    
    # Dovrebbe restituire un contenuto marcato come [BLOCKED BY RAI]
    assert result is not None
    assert "[BLOCKED BY RAI]" in result.parts[0].text
    assert mock_ctx.session.state.get("rai_input_blocked") is True

@pytest.mark.asyncio
async def test_rai_live_safe_output(rai_plugin, mock_ctx):
    """
    Verifica che una risposta sicura NON venga bloccata.
    """
    safe_text = "Certamente, Randstad offre diverse soluzioni per la gestione del personale."
    safe_content = types.Content(role="model", parts=[types.Part.from_text(text=safe_text)])
    llm_response = LlmResponse(content=safe_content)
    
    result = await rai_plugin.after_model_callback(
        callback_context=mock_ctx, 
        llm_response=llm_response
    )
    
    assert result is None

@pytest.mark.asyncio
async def test_rai_live_unsafe_output(rai_plugin, mock_ctx):
    """
    Verifica che una risposta violante (anche se simulata dal modello) venga bloccata.
    """
    unsafe_text = "Questa è una risposta contenente incitamento alla violenza e odio estremo."
    unsafe_content = types.Content(role="model", parts=[types.Part.from_text(text=unsafe_text)])
    llm_response = LlmResponse(content=unsafe_content)
    
    result = await rai_plugin.after_model_callback(
        callback_context=mock_ctx, 
        llm_response=llm_response
    )
    
    # Dovrebbe restituire una LlmResponse con il messaggio di fallback configurato
    assert result is not None
    assert result.content.parts[0].text == rai_plugin.fallback_message
