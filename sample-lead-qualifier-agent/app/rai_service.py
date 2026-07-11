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

"""
Responsible AI Service using Google Cloud Natural Language API.
Configured via environment-specific YAML files.
"""

import logging
from typing import Optional, TYPE_CHECKING

from google.cloud import language_v1
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.models.llm_response import LlmResponse
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

from .app_utils.config import config

if TYPE_CHECKING:
    from google.adk.agents.invocation_context import InvocationContext
    from google.adk.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

# Categorie aggiuntive per una protezione più robusta
DEFAULT_SENSITIVE_CATEGORIES = [
    "Toxic", "Insult", "Profanity", "Violent", "Sexual", 
    "Hate Speech", "Harassment", "Death, Harm & Tragedy"
]

class ResponsibleAIPlugin(BasePlugin):
    """
    Plugin per intercettare e moderare le risposte dell'agente tramite NLP API.
    Le soglie e le categorie sono lette dalla configurazione dell'ambiente.
    """

    def __init__(self):
        super().__init__(name="responsible_ai")
        self._client: Optional[language_v1.LanguageServiceAsyncClient] = None
        
        # Carichiamo le configurazioni dal file YAML dell'ambiente
        self.threshold = config.get("rai.threshold", 0.6)
        self.sensitive_categories = set(config.get("rai.categories", DEFAULT_SENSITIVE_CATEGORIES))
        
        # Messaggi di fallback configurabili
        self.fallback_message = config.get(
            "rai.messages.fallback", 
            "Spiacente, ma non posso fornire questa risposta in quanto non conforme ai principi di Responsible AI."
        )
        self.input_blocked_message = config.get(
            "rai.messages.input_blocked", 
            "Spiacente, ma il tuo messaggio è stato bloccato in quanto non conforme ai nostri principi di Responsible AI."
        )
        
        logger.info(f"RAI Plugin initialized with threshold {self.threshold}")

    @property
    def client(self) -> language_v1.LanguageServiceAsyncClient:
        """
        Inizializzazione pigra del client per evitare problemi di event loop (specialmente nei test).
        """
        if self._client is None:
            self._client = language_v1.LanguageServiceAsyncClient()
        return self._client

    async def on_user_message_callback(
        self, 
        *, 
        invocation_context: "InvocationContext", 
        user_message: types.Content
    ) -> Optional[types.Content]:
        """
        Modera il messaggio dell'utente prima che venga elaborato dall'agente.
        """
        if not user_message or not user_message.parts:
            return None

        text_to_moderate = " ".join(part.text for part in user_message.parts if part.text)

        if not text_to_moderate:
            return None

        try:
            document = language_v1.Document(
                content=text_to_moderate,
                type_=language_v1.Document.Type.PLAIN_TEXT
            )
            response = await self.client.moderate_text(request={"document": document})

            blocked = False
            for category in response.moderation_categories:
                if category.name in self.sensitive_categories and category.confidence > self.threshold:
                    blocked = True
                    logger.warning(f"RAI Input Violation: {category.name} ({category.confidence:.2%})")
                    break

            if blocked:
                logger.warning(f"RAI Blocked input message: {text_to_moderate[:50]}...")
                invocation_context.session.state["rai_input_blocked"] = True
                return types.Content(
                    role="user",
                    parts=[types.Part.from_text(text="[BLOCKED BY RAI]")]
                )

        except Exception as e:
            logger.error(f"Errore durante la moderazione RAI (input): {e}")
            # Fail-closed approach: block input if moderation fails
            invocation_context.session.state["rai_input_blocked"] = True
            return types.Content(
                role="user",
                parts=[types.Part.from_text(text="[BLOCKED BY RAI]")]
            )

        return None

    async def before_agent_callback(
        self, 
        *, 
        agent: "BaseAgent", 
        callback_context: CallbackContext
    ) -> Optional[types.Content]:
        """
        Blocca l'esecuzione dell'agente se l'input è stato segnalato come violazione RAI.
        """
        if callback_context.state.get("rai_input_blocked"):
            logger.info(f"RAI Blocking agent {agent.name} due to input violation.")
            callback_context.state["rai_input_blocked"] = False
            return types.Content(
                role="model",
                parts=[types.Part.from_text(text=self.input_blocked_message)]
            )
        return None

    async def after_model_callback(
        self, 
        *, 
        callback_context: CallbackContext, 
        llm_response: LlmResponse
    ) -> Optional[LlmResponse]:
        """
        Modera la risposta del modello prima che venga restituita all'utente.
        """
        if not llm_response.content or not llm_response.content.parts:
            return None

        text_to_moderate = " ".join(part.text for part in llm_response.content.parts if part.text)

        if not text_to_moderate:
            return None

        try:
            document = language_v1.Document(
                content=text_to_moderate,
                type_=language_v1.Document.Type.PLAIN_TEXT
            )
            response = await self.client.moderate_text(request={"document": document})

            blocked = False
            triggered_categories = []

            for category in response.moderation_categories:
                if category.name in self.sensitive_categories and category.confidence > self.threshold:
                    blocked = True
                    triggered_categories.append(f"{category.name} ({category.confidence:.2%})")

            if blocked:
                logger.warning(
                    f"RAI Blocked response. Categories triggered: {', '.join(triggered_categories)}"
                )
                new_content = types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=self.fallback_message)]
                )
                return LlmResponse(content=new_content)

        except Exception as e:
            logger.error(f"Errore durante la moderazione RAI: {e}")
            # Fail-closed approach: block output if moderation fails
            new_content = types.Content(
                role="model",
                parts=[types.Part.from_text(text=self.fallback_message)]
            )
            return LlmResponse(content=new_content)

        return None
