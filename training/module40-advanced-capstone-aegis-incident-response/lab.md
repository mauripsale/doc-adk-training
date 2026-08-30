---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 40: Aegis Incident Response & AgentOps Multi-Agent System Challenge

## Goal
In this advanced capstone lab, you will build a sophisticated, distributed threat intelligence and incident remediation coordinator called **Aegis Guard**. You will implement three cooperative agents communicating via the Agent-to-Agent (A2A) protocol, an MCP server, and an **AgentOps** observability pattern.

This lab runs entirely on your local machine — no billing, no GCP project required. Model Armor, Vertex AI Search (RAG), the GCS upload, and the telemetry export are all represented with **simplified, simulated implementations** so you can focus on the part this capstone is actually testing: getting three independent ADK agents to cooperate correctly over A2A, with real AgentOps callback hooks. Every simulated piece is called out explicitly in the code, with a note on what the real integration would look like.

### Prerequisites
*   **Python 3.10+** and **[uv](https://github.com/astral-sh/uv#installation)**.
*   A `GEMINI_API_KEY` (or Agent Platform credentials) — same as every other module.
*   No GCP project, billing, or Google Cloud APIs are required for this lab.

### Step 0: Project Setup
1.  **Create three sibling agent projects:**
    ```shell
    uv run adk create threat_intel_agent
    uv run adk create orchestrator_agent
    uv run adk create mitigation_agent
    ```
2.  **Install dependencies** in each of the three directories:
    ```shell
    uv add "google-adk[a2a,mcp]" uvicorn mcp python-dotenv
    ```
3.  **Add your API key** to a `.env` file in each of the three directories.

---

### Exercise 1: Implement the Threat Intelligence Agent (with AgentOps Telemetry)
The **Threat Intelligence Agent** must expose a natural language interface to a (simulated) BigQuery security data source, sanitize sensitive output, and record AgentOps metrics (latency and a simulated telemetry export).

1.  **Create `threat_intel_agent/bigquery_mock_server.py`.** This is provided for you — a minimal local MCP server standing in for a real hosted BigQuery MCP server, so the lab doesn't require a real GCP project. You already built a server just like this in Module 28; no need to write another one from scratch here.

    ```python
    # In threat_intel_agent/bigquery_mock_server.py (provided — no changes needed)
    import asyncio
    import json
    from mcp import types as mcp_types
    from mcp.server.lowlevel import Server, NotificationOptions
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio

    app = Server("bigquery_security_audit_mock")

    # Simulated rows a real BigQuery security-audit query might return.
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

2.  **Skeleton for `threat_intel_agent/agent.py`:**
    Complete the `TODO` placeholders in the agent script below.

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

# Launches bigquery_mock_server.py as a local subprocess (same pattern as
# Module 27/28's StdioConnectionParams) — standing in for a real hosted
# BigQuery MCP server.
mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python3",
            args=[os.path.join(os.path.dirname(os.path.abspath(__file__)), "bigquery_mock_server.py")],
        ),
    ),
)

# TODO 1: Simulated Model Armor data masking.
# Scan the text for internal private IP addresses and mask them.
# E.g., '192.168.1.45' -> '192.168.1.***'
# A production system would call the real Model Armor API here instead.
def mask_security_secrets(text: str) -> str:
    """Masks sensitive internal IP addresses in agent output."""
    ...

# TODO 2: AgentOps "before" hook — mark the start time of the model call.
# Signature must match ADK's before_model_callback: (callback_context, llm_request) -> None
# Store time.time() in callback_context.state["start_time"].
def start_timer(callback_context: CallbackContext, llm_request: LlmRequest) -> None:
    ...

# TODO 3: AgentOps "after" hook — mask secrets and log (simulated) telemetry.
# Signature must match ADK's after_model_callback: (callback_context, llm_response) -> Optional[LlmResponse]
# - Compute elapsed time using callback_context.state.get("start_time", ...)
# - Print the latency and a line simulating an OpenTelemetry/Cloud Logging export
# - IMPORTANT: this agent's first LLM response is often a *function call*
#   (e.g. to query_security_audit_logs), not text. A function-call part has
#   llm_response.content.parts[0].text == None. Guard for this: if there's no
#   content, no parts, or the first part's .text is falsy, return None
#   immediately WITHOUT calling mask_security_secrets() on it (re.sub() on
#   None raises TypeError). Only attempt redaction when there is actual text.
# - Redact llm_response.content.parts[0].text via mask_security_secrets()
# - If the text was actually redacted, return a new LlmResponse via
#   llm_response.model_copy(update={"content": types.Content(parts=[types.Part(text=redacted_text)], role="model")})
#   Otherwise return None (no change).
def end_timer_and_sanitize(callback_context: CallbackContext, llm_response: LlmResponse):
    ...

# TODO 4: Construct the Threat Intel Agent, wiring up the two callbacks above.
threat_agent = Agent(
    model="gemini-3.5-flash",
    name="threat_intel_agent",
    instruction="""
        You are a Threat Intelligence log investigator.
        You can query the simulated security audit log tool for logins, scans, and injection attempts.
        Always summarize what you found before handing off to another agent.
    """,
    tools=[mcp_toolset],
    # before_model_callback=...,
    # after_model_callback=...,
)

a2a_app = to_a2a(threat_agent, port=8001)

if __name__ == "__main__":
    uvicorn.run(a2a_app, host="0.0.0.0", port=8001)
```

---

### Exercise 2: Implement the Aegis Orchestrator Agent (Distributed Trace Provider)
The **Orchestrator** coordinates the Threat Intelligence and Mitigation agents to run complete automated incident mitigation cycles.

1.  **Skeleton for `orchestrator_agent/agent.py`:**
    Complete the `TODO` placeholders to consume the two remote A2A services.

```python
from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from google.adk.apps.app import App
from google.adk.runners import InMemoryRunner
from google.adk.tools.agent_tool import AgentTool
from dotenv import load_dotenv

load_dotenv()

# TODO 1: Define the two Remote A2A Agent Gateways.
# Hint: agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}" — no extra
#   path segment; to_a2a() serves the well-known card at the server's root.
# Hint: pass use_legacy=False on both, to opt into the reliability-fixed A2A
#   executor (see Module 21) — this avoids known streaming-mode message
#   duplication bugs, which this lab's multi-hop orchestration is prone to.
threat_intel_service = ...
mitigation_service = ...

# TODO 2: Create the main Aegis Orchestrator Agent.
# IMPORTANT: wire the two remote agents in as `tools=[AgentTool(agent=...), ...]`,
# NOT as `sub_agents=[...]`. `sub_agents` wires ADK's `transfer_to_agent`
# mechanism, which is a *permanent*, one-way handoff: once the orchestrator
# transfers control to threat_intel_agent, threat_intel_agent becomes the
# active agent for the rest of the run and has no way to transfer onward to
# mitigation_agent or back to the orchestrator (it's a separate process with
# no knowledge of that agent tree) — so the documented 4-step flow would
# silently stop after step 1. `AgentTool` gives proper call-and-return
# semantics instead: the orchestrator calls each remote agent like a
# function, gets its result back, and stays in control to make the next call
# and synthesize the final combined answer.
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
    tools=[...],  # TODO: [AgentTool(agent=threat_intel_service), AgentTool(agent=mitigation_service)]
)

app = App(name="aegis_incident_response_system", root_agent=root_agent)
runner = InMemoryRunner(app=app)
```

---

### Exercise 3: Implement the Mitigation & Patching Agent
The **Mitigation Agent** receives an Incident Profile, looks up remediation playbooks, and drafts a patching script and executive brief.

1.  **Skeleton for `mitigation_agent/agent.py`:**

```python
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import ToolContext
from dotenv import load_dotenv
import uvicorn

load_dotenv()

# TODO 1: Write a tool to search Playbook reference documents.
# This simulates a Vertex AI Search (RAG) lookup over CIS/NIST playbooks —
# a production system would query a real Vertex AI Search app here.
def search_remediation_playbooks(vulnerability_type: str) -> str:
    """Searches the Security Remediation Playbooks (simulated RAG)."""
    ...

# TODO 2: Write a tool to render and (simulate) uploading the Action Plan brief.
# This simulates a signed GCS upload — a production system would render a
# real PDF and call a GCS MCP server or the Cloud Storage API here.
async def build_and_upload_mitigation_brief(target_node: str, incident_type: str, tool_context: ToolContext) -> dict:
    """Generates an executive security brief and simulates uploading it to GCS."""
    ...

# TODO 3: Construct the Mitigation Agent.
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

### Running the System
This requires three separate terminals.

1.  **Terminal 1 (Threat Intelligence Agent):**
    ```shell
    cd threat_intel_agent && uv run python agent.py
    ```
2.  **Terminal 2 (Mitigation Agent):**
    ```shell
    cd mitigation_agent && uv run python agent.py
    ```
3.  **Terminal 3 (Orchestrator):**
    ```shell
    cd orchestrator_agent && uv run adk web .
    ```
4.  **Interact with the system:** open the Dev UI and try: *"Detect any brute-force attacks on our billing databases and generate a patching plan."* Watch the Trace View to see the orchestrator hand off to both remote agents in turn.

### Self-Reflection Questions
- In AgentOps, why is trace context propagation critical for debugging multi-agent HTTP calls?
- What are the architectural differences between measuring token counts locally versus exporting OpenTelemetry span metrics to Google Cloud Monitoring?
- This lab simulates Model Armor, RAG, and the GCS upload with plain Python functions. What would have to change in `threat_intel_agent`, `mitigation_agent`, and their AgentOps hooks to call the real Google Cloud services instead?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlNDAtYWR2YW5jZWQtY2Fwc3RvbmUtYWVnaXMtaW5jaWRlbnQtcmVzcG9uc2UvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module40-advanced-capstone-aegis-incident-response/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
