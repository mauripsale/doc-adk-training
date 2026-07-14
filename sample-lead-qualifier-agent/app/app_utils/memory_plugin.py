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

import logging
from typing import Optional, Any
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse

logger = logging.getLogger(__name__)

class MemoryPlugin(BasePlugin):
    """
    Plugin per gestire il salvataggio automatico delle sessioni nella memoria a lungo termine.
    I plugin sono più affidabili dei callback dei singoli agenti per operazioni globali.
    """

    def __init__(self, **kwargs: Any):
        super().__init__(name=kwargs.get("name", "memory_plugin"))

    async def after_model_callback(
        self, 
        *, 
        callback_context: CallbackContext, 
        llm_response: LlmResponse
    ) -> Optional[LlmResponse]:
        """
        Dopo che il modello ha risposto, salviamo lo stato aggiornato della sessione in memoria.
        """
        try:
            # L'oggetto Session nel callback_context è aggiornato con l'ultimo turno
            invocation_ctx = callback_context._invocation_context
            memory_service = invocation_ctx.memory_service
            session = invocation_ctx.session
            
            if memory_service:
                logger.info(f"💾 [MemoryPlugin] Ingestione sessione '{session.id}' per user '{session.user_id}'")
                await memory_service.add_session_to_memory(session)
                logger.info("✅ [MemoryPlugin] Sessione indicizzata correttamente.")
            else:
                logger.warning("⚠️ [MemoryPlugin] MemoryService non trovato.")
                
        except Exception as e:
            logger.error(f"❌ [MemoryPlugin] Errore durante l'ingestione della memoria: {e}")

        return None
