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
from google.adk.agents import Agent
from google.adk.tools import AgentTool
from app.agents.researcher import ricercatore_azienda
from app.agent import root_agent

def test_researcher_configuration():
    """
    Verifica che il sub-agente ricercatore sia configurato correttamente.
    """
    assert ricercatore_azienda.name == "ricercatore_azienda"
    # Verifica che abbia il tool google_search
    tool_names = [tool.name for tool in ricercatore_azienda.tools]
    assert "google_search" in tool_names

def test_root_agent_delegation_tool():
    """
    Verifica che l'agente principale abbia il ricercatore tra i suoi tool.
    """
    # Cerchiamo l'AgentTool tra i tool del root_agent
    agent_tools = [tool for tool in root_agent.tools if isinstance(tool, AgentTool)]
    
    assert len(agent_tools) > 0, "Root agent non ha tool di delegazione (AgentTool)"
    
    # Verifica che l'agente delegato sia quello corretto
    researcher_tool = next((t for t in agent_tools if t.agent.name == "ricercatore_azienda"), None)
    assert researcher_tool is not None, "Il sub-agente ricercatore non è presente nei tool del root_agent"

def test_prompts_loading():
    """
    Verifica che le istruzioni siano caricate correttamente dai prompt.
    """
    from app.prompts import RESEARCHER_INSTRUCTION, INSTRUCTION
    
    assert ricercatore_azienda.instruction == RESEARCHER_INSTRUCTION
    assert root_agent.instruction == INSTRUCTION
    assert "ricercatore_azienda" in root_agent.instruction, "Il prompt principale deve menzionare la delegazione"

@pytest.mark.asyncio
async def test_agent_tool_description():
    """
    Verifica che la descrizione dell'AgentTool sia presente, 
    fondamentale perché il Root Agent sappia quando chiamarlo.
    """
    agent_tools = [tool for tool in root_agent.tools if isinstance(tool, AgentTool)]
    researcher_tool = next((t for t in agent_tools if t.agent.name == "ricercatore_azienda"), None)
    
    # La descrizione dell'agente viene usata dal modello per decidere la delegazione
    assert "Ricerca informazioni dettagliate su un'azienda" in researcher_tool.agent.description
