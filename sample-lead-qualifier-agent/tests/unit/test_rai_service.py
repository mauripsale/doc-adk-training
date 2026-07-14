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
from unittest.mock import MagicMock, AsyncMock, patch
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from app.rai_service import ResponsibleAIPlugin

@pytest.fixture
def mock_ctx():
    # Mock per InvocationContext e CallbackContext (entrambi hanno .state o .session.state)
    ctx = MagicMock()
    ctx.session.state = {}
    ctx.state = ctx.session.state
    return ctx

@pytest.fixture
def plugin():
    # Patch the Async client instead of the sync one
    with patch("google.cloud.language_v1.LanguageServiceAsyncClient"), \
         patch("app.rai_service.config") as mock_config:
        # Mock della configurazione
        mock_config.get.side_effect = lambda key, default: {
            "rai.threshold": 0.6,
            "rai.categories": ["Toxic", "Insult", "Profanity", "Violent", "Sexual", "Hate Speech", "Harassment"],
            "rai.messages.fallback": "FALLBACK",
            "rai.messages.input_blocked": "INPUT_BLOCKED"
        }.get(key, default)
        
        p = ResponsibleAIPlugin()
        # Initialize moderate_text as an AsyncMock
        p.client.moderate_text = AsyncMock()
        return p

@pytest.mark.asyncio
async def test_after_model_callback_no_violation(plugin, mock_ctx):
    mock_response = MagicMock()
    cat1 = MagicMock()
    cat1.name = "Toxic"
    cat1.confidence = 0.1
    mock_response.moderation_categories = [cat1]
    plugin.client.moderate_text.return_value = mock_response

    clean_content = types.Content(role="model", parts=[types.Part.from_text(text="Safe")])
    llm_response = LlmResponse(content=clean_content)

    result = await plugin.after_model_callback(callback_context=mock_ctx, llm_response=llm_response)
    assert result is None

@pytest.mark.asyncio
async def test_after_model_callback_with_violation(plugin, mock_ctx):
    mock_response = MagicMock()
    cat = MagicMock()
    cat.name = "Toxic"
    cat.confidence = 0.9
    mock_response.moderation_categories = [cat]
    plugin.client.moderate_text.return_value = mock_response

    bad_content = types.Content(role="model", parts=[types.Part.from_text(text="Bad")])
    llm_response = LlmResponse(content=bad_content)

    result = await plugin.after_model_callback(callback_context=mock_ctx, llm_response=llm_response)
    assert result is not None
    assert result.content.parts[0].text == "FALLBACK"

@pytest.mark.asyncio
async def test_on_user_message_callback_with_violation(plugin, mock_ctx):
    mock_response = MagicMock()
    cat = MagicMock()
    cat.name = "Insult"
    cat.confidence = 0.8
    mock_response.moderation_categories = [cat]
    plugin.client.moderate_text.return_value = mock_response

    user_message = types.Content(role="user", parts=[types.Part.from_text(text="Bad")])

    result = await plugin.on_user_message_callback(invocation_context=mock_ctx, user_message=user_message)
    assert result is not None
    assert mock_ctx.session.state["rai_input_blocked"] is True

@pytest.mark.asyncio
async def test_before_agent_callback_blocking(plugin, mock_ctx):
    mock_ctx.state["rai_input_blocked"] = True
    mock_agent = MagicMock()
    mock_agent.name = "agent"
    
    result = await plugin.before_agent_callback(agent=mock_agent, callback_context=mock_ctx)
    
    assert result is not None
    assert result.parts[0].text == "INPUT_BLOCKED"
    assert mock_ctx.state["rai_input_blocked"] is False
