# ruff: noqa
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
Entry point dell'applicazione ADK.
Qui viene definito l'agente principale (Root Agent) e orchestrata la delegazione.
"""

import os
import google.auth

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import AgentTool
from google.genai import types

from .tools import salva_qualificazione
from .prompts import INSTRUCTION, MEMORY_INSTRUCTION_EXTENSION
from .agents.researcher import ricercatore_azienda
from .app_utils.config import config
from .rai_service import ResponsibleAIPlugin
from google.adk.tools.load_memory_tool import LoadMemoryTool
import logging

logger = logging.getLogger(__name__)

async def auto_save_session_to_memory_callback(callback_context):
    """
    Pattern ufficiale ADK per il salvataggio automatico in memoria.
    Viene invocato dopo l'esecuzione dell'agente.
    """
    try:
        # Accesso al memory service tramite l'invocation context interno
        inv_ctx = callback_context._invocation_context
        if inv_ctx.memory_service:
            # Stampo direttamente su stdout per visibilità immediata nel playground
            print(f"\n💾 [MEMORY] Ingestione sessione {inv_ctx.session.id} per utente {inv_ctx.session.user_id}...")
            await inv_ctx.memory_service.add_session_to_memory(inv_ctx.session)
            print("✅ [MEMORY] Salvataggio completato.\n")
    except Exception as e:
        print(f"❌ [MEMORY] Errore critico nel callback: {e}")

# Configurazione ambiente GCP
_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id

# Caricamento variabili d'ambiente configurate nel YAML
for k, v in config.get("env", {}).items():
    os.environ[k] = str(v)

# Safety settings comuni
def get_safety_settings():
    conf_safety = config.get("agents.root.safety_settings", {})
    settings = []
    for category, threshold in conf_safety.items():
        settings.append(
            types.SafetySetting(
                category=getattr(types.HarmCategory, f"HARM_CATEGORY_{category}"),
                threshold=getattr(types.HarmBlockThreshold, threshold),
            )
        )
    return settings

# Root Agent: Il "Direttore d'orchestra"
root_agent = Agent(
    name=config.get("agents.root.name", "qualificatore_commerciale"),
    model=Gemini(
        model=config.get("agents.root.model", "gemini-3-flash-preview"),
        config=types.GenerateContentConfig(
            temperature=config.get("agents.root.temperature", 0.2),
            safety_settings=get_safety_settings(),
        )
    ),
    instruction=INSTRUCTION + MEMORY_INSTRUCTION_EXTENSION,
    tools=[
        salva_qualificazione,
        AgentTool(ricercatore_azienda), # Delegazione modulare
        LoadMemoryTool() # Classe nativa per cercare nella memoria SOLO su richiesta
    ],
    after_agent_callback=auto_save_session_to_memory_callback,
)

app = App(
    root_agent=root_agent,
    name=config.get("app.name", "app"),
    plugins=[ResponsibleAIPlugin()],
)
