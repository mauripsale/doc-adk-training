---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 40 Solution: Aegis Incident Response & AgentOps Multi-Agent System

This solution provides a complete, locally-runnable ADK 2.0 implementation of the Aegis Incident Response System (AIRS). As explained in `lab.md`, Model Armor, Vertex AI Search (RAG), the GCS upload, and the telemetry export are represented with simulated implementations — the code and comments call out exactly where a production system would swap in the real Google Cloud service.

---

### `threat_intel_agent/bigquery_mock_server.py` (provided, unchanged from `lab.md`)

```python
import asyncio
import json
from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio

app = Server("bigquery_security_audit_mock")

FAKE_AUDIT_LOGS = [
    {"timestamp": "2026-08-20T03:14:22Z", "source_ip": "192.168.1.45", "event": "failed_login", "target": "billing_db", "attempts": 47},
    {"timestamp": "2026-08-20T03:15:01Z", "source_ip": "192.168.1.45", "event": "sql_injection_attempt", "target": "mid_market_segment_logs", "query_snippet": "' OR '1'='1"},
]

@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    return [
        mcp_types.Tool(
            name="query_security_audit_logs",
            description="Runs a read-only query over BigQuery security audit logs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to look for, e.g. 'brute-force attacks on billing_db'."}
                },
                "required": ["query"],
            },
        )
    ]

@app.call_tool()
async def call_mcp_tool(name: str, arguments: dict) -> list[mcp_types.Content]:
    if name == "query_security_audit_logs":
        response_text = json.dumps({"status": "success", "rows": FAKE_AUDIT_LOGS})
        return [mcp_types.TextContent(type="text", text=response_text)]
    response_text = json.dumps({"status": "error", "message": f"Tool '{name}' not found."})
    return [mcp_types.TextContent(type="text", text=response_text)]

async def run_mcp_stdio_server():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=app.name,
                server_version="0.1.0",
                capabilities=app.get_capabilities(NotificationOptions(), {}),
            ),
        )

if __name__ == "__main__":
    asyncio.run(run_mcp_stdio_server())
```

### 1. Threat Intelligence Agent (`threat_intel_agent/agent.py`)

```python
import os
import re
import time
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.genai import types
from dotenv import load_dotenv
import uvicorn

load_dotenv()

mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python3",
            args=[os.path.join(os.path.dirname(os.path.abspath(__file__)), "bigquery_mock_server.py")],
        ),
    ),
)

def mask_security_secrets(text: str) -> str:
    """
    Simulated Model Armor sanitization: masks internal private IP addresses.
    A production system would call the real Model Armor API here instead.
    """
    ip_regex = r"\b(192\.168\.\d+)\.(\d+)\b"
    return re.sub(ip_regex, r"\1.***", text)

def start_timer(callback_context: CallbackContext, llm_request: LlmRequest) -> None:
    """AgentOps: mark the start of a model call to measure latency."""
    callback_context.state["start_time"] = time.time()
    print("[AgentOps] Starting query generation span...")

def end_timer_and_sanitize(callback_context: CallbackContext, llm_response: LlmResponse):
    """AgentOps: mask secrets in the response and log (simulated) telemetry export."""
    elapsed_time = time.time() - callback_context.state.get("start_time", time.time())
    print("[AgentOps] Agent execution completed successfully.")
    print(f"[AgentOps] Latency: {elapsed_time:.3f}s")
    print("[AgentOps] (Simulated) Exporting OpenTelemetry span and token usage to Cloud Logging...")

    # The model's first response here is often a function call (e.g. to
    # query_security_audit_logs) rather than text. A function-call part has
    # no text to sanitize, so skip masking entirely in that case instead of
    # crashing on re.sub(..., None).
    if not llm_response.content or not llm_response.content.parts:
        return None

    original_text = llm_response.content.parts[0].text
    if not original_text:
        return None

    redacted_text = mask_security_secrets(original_text)
    if redacted_text == original_text:
        return None
    return llm_response.model_copy(update={
        "content": types.Content(parts=[types.Part(text=redacted_text)], role="model")
    })

threat_agent = Agent(
    model="gemini-3.5-flash",
    name="threat_intel_agent",
    instruction="""
        You are a Threat Intelligence log investigator.
        You can query the simulated security audit log tool for logins, scans, and injection attempts.
        Always summarize what you found before handing off to another agent.
    """,
    tools=[mcp_toolset],
    before_model_callback=start_timer,
    after_model_callback=end_timer_and_sanitize,
)

a2a_app = to_a2a(threat_agent, port=8001)

if __name__ == "__main__":
    uvicorn.run(a2a_app, host="0.0.0.0", port=8001)
```

---

### 2. Aegis Orchestrator Agent (`orchestrator_agent/agent.py`)

```python
from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from google.adk.apps.app import App
from google.adk.runners import InMemoryRunner
from google.adk.tools.agent_tool import AgentTool
from dotenv import load_dotenv

load_dotenv()

threat_intel_service = RemoteA2aAgent(
    name="threat_intel_agent",
    agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}",
    use_legacy=False,
)

mitigation_service = RemoteA2aAgent(
    name="mitigation_agent",
    agent_card=f"http://localhost:8003{AGENT_CARD_WELL_KNOWN_PATH}",
    use_legacy=False,
)

root_agent = Agent(
    model="gemini-3.5-flash",
    name="aegis_orchestrator",
    instruction="""
        You are the master coordinator for the Aegis Incident Response System.

        1. First, consult the `threat_intel_agent` to search access logs and locate the details of any malicious logins or scans.
        2. For each security incident detected, compile an Incident Profile detailing:
           - Attacker IP / Target Node
           - Attack type (e.g. brute-force, SQLi)
        3. Send this profile to `mitigation_agent` to search playbooks, draft a patching script, and generate an Executive Security Brief.
        4. Present the resulting mitigation plan and brief details back to the SOC analyst.
    """,
    # NOTE: these two remote agents are wired as tools (AgentTool), NOT as
    # `sub_agents=[...]`. `sub_agents` wires ADK's `transfer_to_agent`
    # mechanism, which is a *permanent*, one-way handoff — once the
    # orchestrator transfers control to threat_intel_agent, threat_intel_agent
    # becomes the active agent for the rest of the run, and it has no way to
    # transfer onward to mitigation_agent or back to the orchestrator (it's a
    # separate process with no knowledge of that agent tree). AgentTool gives
    # proper call-and-return semantics instead: the orchestrator calls each
    # remote agent like a function, gets its result back, and stays in
    # control to make the next call and synthesize the final combined answer.
    tools=[AgentTool(agent=threat_intel_service), AgentTool(agent=mitigation_service)],
)

app = App(name="aegis_incident_response_system", root_agent=root_agent)
runner = InMemoryRunner(app=app)
```

---

### 3. Mitigation & Patching Agent (`mitigation_agent/agent.py`)

```python
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import ToolContext
from dotenv import load_dotenv
import uvicorn

load_dotenv()

def search_remediation_playbooks(vulnerability_type: str) -> str:
    """
    Simulated Vertex AI Search (RAG) lookup over CIS/NIST playbooks.
    A production system would query a real Vertex AI Search app here.
    """
    return "Remediation Playbook #40: For database log attacks, isolate port 3306, enable VPC Service Controls, and rotate target IAM passwords."

async def build_and_upload_mitigation_brief(target_node: str, incident_type: str, tool_context: ToolContext) -> dict:
    """
    Generates an executive security brief and simulates a signed upload to GCS.
    A production system would render a real PDF and call a GCS MCP server or
    the Cloud Storage API here.
    """
    gcs_dest_url = f"https://storage.googleapis.com/aegis-security-briefs/{target_node.lower().replace('.', '_')}_mitigation_brief.pdf"
    return {
        "status": "success",
        "brief_url": gcs_dest_url,
        "message": f"Successfully generated security patch script and uploaded executive brief to {gcs_dest_url}"
    }

mitigation_agent = Agent(
    model="gemini-3.5-flash",
    name="mitigation_agent",
    instruction="You generate patch scripts and executive briefings. Use the playbook search and brief-upload tools.",
    tools=[search_remediation_playbooks, build_and_upload_mitigation_brief]
)

a2a_app = to_a2a(mitigation_agent, port=8003)

if __name__ == "__main__":
    uvicorn.run(a2a_app, host="0.0.0.0", port=8003)
```

---

### Self-Reflection Answers

1.  **In AgentOps, why is trace context propagation critical for debugging multi-agent HTTP calls?**
    *   **Answer:** Since A2A nodes communicate over standard network HTTP protocols, a single user request results in cascading calls across different processes. Without trace context propagation (e.g. standard `traceparent` headers), each agent would log its activity as a completely isolated, disconnected event. Context propagation lets a tracing backend like Cloud Trace rebuild the execution tree, showing precisely how much of the total latency was spent in the orchestrator, in model generation, or in a remote agent's own tool calls.

2.  **What are the architectural differences between measuring token counts locally versus exporting OpenTelemetry span metrics to Google Cloud Monitoring?**
    *   **Answer:** Local token logging (like the `print()` calls in this lab) is useful for instant console debugging, but it doesn't scale or persist. Real OpenTelemetry metrics export these values as structured, queryable time-series data. That lets a platform team build dashboards tracking token cost across every agent and team, trigger alerts on anomalous spikes, and analyze trends over weeks or months — none of which is possible from a print statement in one terminal.

3.  **This lab simulates Model Armor, RAG, and the GCS upload with plain Python functions. What would have to change in `threat_intel_agent`, `mitigation_agent`, and their AgentOps hooks to call the real Google Cloud services instead?**
    *   **Answer:** `mask_security_secrets` would call the real Model Armor API instead of a local regex — same function signature, different implementation. `search_remediation_playbooks` would query a real Vertex AI Search app (via its client library or an MCP wrapper around it) instead of returning a fixed string. `build_and_upload_mitigation_brief` would actually render a PDF and call the Cloud Storage API (or a real GCS MCP server, following the same `McpToolset`/`StdioConnectionParams` or `StreamableHTTPConnectionParams` pattern already used for the BigQuery mock) to get a real signed URL. In the AgentOps hooks, the `print()` calls simulating telemetry export would be replaced with real OpenTelemetry SDK calls (spans and metrics), matching the pattern taught in Module 25 — the callback *signatures* (`before_model_callback`/`after_model_callback`) wouldn't need to change at all, only what happens inside them.

---

## You've Reached the End

Take a moment with that — forty modules ago, Module 1 was a "scavenger hunt" through documentation with no code at all. Here, you just got three independent agents talking to each other over A2A, backed by a real MCP server, with production-shaped observability hooks, to hunt down a simulated security incident end to end. Every concept in between — tools, state, multi-agent orchestration, evaluation, callbacks, MCP, streaming UIs, deployment — was a real building block for this, not a detour.

A few honest notes on what "done" means here:
*   **You know what's real and what's simulated in this capstone**, and — more usefully — exactly how to flip each simulated piece to real, because you've now built the real version of each one in an earlier module (Model Armor-style masking in Module 26, Vertex AI Search patterns throughout Part 5, GCS/MCP servers in Module 28, OpenTelemetry in Module 25, deployment in Part 6).
*   **The course itself keeps evolving.** ADK is under active development, and this repository gets updated as the framework changes — if something here ever looks off against a newer ADK release, that's worth an issue or a PR, not silent confusion.

If you're looking for where to go next:
*   Wire up one of the "Going Further" pieces above for real, in your own GCP project — it's the fastest way to turn "I followed a lab" into "I built something."
*   Revisit the course's root `README.md` (in the repository, not this docs site) for the full course map, the semantic-versioning policy for this repo, and how to contribute back.
*   Star and share the repo if it got you here — it's open source, and word of mouth is what keeps a self-service course like this alive.

Welcome to the other side of "Zero to Hero."
