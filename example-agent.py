"""Improve Engagement agent — A2A client coordinating Data + Intervention agents.

Deploys to Agent Engine via `adk deploy agent_engine`. The Improve Engagement agent is
NOT an A2A server — it is the user-facing agent that delegates data questions
to the Data Agent and intervention creation to the Intervention Agent, both via
their Cloud Run A2A endpoints.
"""

import logging
import os
import warnings
from functools import cached_property

from dotenv import load_dotenv

load_dotenv()

import google.auth
import google.auth.transport.requests
import google.oauth2.id_token
import httpx
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.models import Gemini
from google.adk.tools.agent_tool import AgentTool
from google.genai import Client, types

from .prompt_task3 import IMPROVE_ENGAGEMENT_INSTRUCTION

# --- Environment configuration ---
PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
DATA_AGENT_URL = os.environ["DATA_AGENT_URL"]  # Cloud Run base URL
INTERVENTION_AGENT_URL = os.environ["INTERVENTION_AGENT_URL"]  # Cloud Run base URL

# Suppress repetitive ADK experimental-feature warnings and noisy INFO logs
warnings.filterwarnings("ignore", message=r"\[EXPERIMENTAL\]")
logging.getLogger("google.adk").setLevel(logging.WARNING)
logging.getLogger("google.genai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


class Gemini3(Gemini):
    """Gemini subclass that forces location='global' for Gemini 3 models."""

    @cached_property
    def api_client(self) -> Client:
        return Client(
            project=os.environ["GOOGLE_CLOUD_PROJECT"],
            location="global",
            http_options=types.HttpOptions(
                headers=self._tracking_headers(),
                retry_options=types.HttpRetryOptions(
                    max_delay=7,
                    exp_base=1.5,
                    jitter=.5,
                )
            ),
        )

class _CloudRunAuth(httpx.Auth):
    """httpx Auth that attaches OIDC identity tokens for Cloud Run."""

    def __init__(self, audience: str):
        self._audience = audience

    def auth_flow(self, request):
        if request.url.host in ("localhost", "127.0.0.1"):
            yield request
            return
    
        auth_request = google.auth.transport.requests.Request()
        token = google.oauth2.id_token.fetch_id_token(
            auth_request, audience=self._audience
        )
        request.headers["Authorization"] = f"Bearer {token}"
        yield request


# --- Remote Data Agent (A2A client) ---
_data_agent_http = httpx.AsyncClient(
    auth=_CloudRunAuth(DATA_AGENT_URL),
    timeout=httpx.Timeout(timeout=600.0),
)

data_agent = RemoteA2aAgent(
    name="data_agent",
    description=(
        "Cymbal Meet data domain expert. Accepts natural language questions "
        "and translates them to SQL, executes via BigQuery, "
        "and returns structured results. Delegate ALL data-related questions "
        "to this agent — never attempt to query data directly."
    ),
    agent_card=f"{DATA_AGENT_URL}/.well-known/agent.json",
    httpx_client=_data_agent_http,
)


# --- Remote Intervention Agent (A2A client) ---
_intervention_agent_http = httpx.AsyncClient(
    auth=_CloudRunAuth(INTERVENTION_AGENT_URL),
    timeout=httpx.Timeout(timeout=600.0),
)

intervention_agent = RemoteA2aAgent(
    name="intervention_agent",
    description=(
        "Cymbal Meet intervention specialist. Accepts customer engagement data "
        "(customer_id, customer_name, problem_profile, engagement_metrics), "
        "searches for relevant best-practice content via Vertex AI Search, "
        "and generates a personalized intervention PDF uploaded to GCS. "
        "Delegate ALL intervention creation to this agent."
    ),
    agent_card=f"{INTERVENTION_AGENT_URL}/.well-known/agent.json",
    httpx_client=_intervention_agent_http,
)

data_tool = AgentTool(agent=data_agent)
intervention_tool = AgentTool(agent=intervention_agent)


# --- Improve Engagement agent agent ---
root_agent = LlmAgent(
    model=Gemini3(model="gemini-3-flash-preview"),
    name="improve_engagement_agent",
    description=(
        "Cymbal Meet Customer Engagement Improve Engagement agent. Interprets user "
        "requests about customer engagement, delegates data queries to "
        "specialized agents, and presents actionable insights."
    ),
    instruction=IMPROVE_ENGAGEMENT_INSTRUCTION,
    tools=[data_tool, intervention_tool],
)
