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

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.tools import google_search
from google.genai import types
from ..prompts import RESEARCHER_INSTRUCTION
from ..app_utils.config import config

# Configurazione del sub-agente ricercatore
# Note: Usiamo temperature 0.0 per la massima fedeltà ai dati cercati
ricercatore_azienda = Agent(
    name=config.get("agents.researcher.name", "ricercatore_azienda"),
    description="Ricerca informazioni dettagliate su un'azienda (settore, dimensioni, news) utilizzando Google Search.",
    model=Gemini(
        model=config.get("agents.researcher.model", "gemini-3-flash-preview"),
        config=types.GenerateContentConfig(
            temperature=config.get("agents.researcher.temperature", 0.0),
            max_output_tokens=config.get("agents.researcher.max_output_tokens", 500),
        )
    ),
    instruction=RESEARCHER_INSTRUCTION,
    tools=[google_search],
)
