---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 40: Aegis Incident Response & AgentOps Multi-Agent System Challenge

## Goal
In this advanced capstone lab, you will build a sophisticated, distributed threat intelligence and incident remediation coordinator called **Aegis Guard**. You will implement three cooperative agents communicating via the Agent-to-Agent (A2A) protocol, utilizing MCP servers, Model Armor, and an enterprise **AgentOps** observability suite.

---

### Exercise 1: Implement the Threat Intelligence Agent (with AgentOps Telemetry)
The **Threat Intelligence Agent** must expose a natural language interface to BigQuery, sanitize output passwords or IP addresses using Model Armor rules, and record AgentOps metrics (latency and token counts).

1.  **Skeleton for `threat_intel_agent/agent.py`:**
    Complete the `TODO` placeholders in the agent script below.

```python
import os
import re
import time
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.mcp import McpToolset
from dotenv import load_dotenv
import uvicorn

load_dotenv()

# TODO 1: Load the BigQuery MCP Server configurations
mcp_toolset = McpToolset(
    mcp_server_url=os.getenv("BIGQUERY_MCP_SERVER_URL", "http://localhost:5001")
)

# TODO 2: Define Model Armor sensitive data masking rules
def mask_security_secrets(text: str) -> str:
    """
    Scans the response for internal private IP addresses or passwords
    and masks them.
    E.g., '192.168.1.45' -> '192.168.1.***'
    """
    ip_regex = r"\b(192\.168\.\d+)\.(\d+)\b"
    return re.sub(ip_regex, r"\1.***", text)

# TODO 3: Construct the Threat Intel Agent
threat_agent = Agent(
    model="gemini-3.5-flash",
    name="threat_intel_agent",
    instruction="""
        You are a Threat Intelligence log investigator.
        You can execute read-only queries on BigQuery security tables.
        Always describe the table metadata and fetch representative rows if unsure about schemas.
    """,
    tools=[mcp_toolset]
)

# TODO 4: Implement AgentOps Lifecycle Hooks for Observability
@threat_agent.before_request
def start_timer(event):
    # Store request start time in the event context
    event.state["start_time"] = time.time()
    print(f"[AgentOps] Starting query generation span for {event.request.contents[-1]}...")

@threat_agent.after_response
def end_timer_and_sanitize(event):
    if event.is_final_response():
        # Mask sensitive details
        event.content.parts[0].text = mask_security_secrets(event.content.parts[0].text)
        
        # Calculate execution latency
        elapsed_time = time.time() - event.state.get("start_time", time.time())
        
        # Track simulated Token count
        # In a real setup, access event.response_metadata (such as token metrics)
        print(f"[AgentOps] Agent execution completed successfully.")
        print(f"[AgentOps] Latency: {elapsed_time:.3f}s")
        print(f"[AgentOps] Exporting OpenTelemetry Span and logs to Cloud Logging...")

a2a_app = to_a2a(threat_agent)

if __name__ == "__main__":
    uvicorn.run(a2a_app, host="0.0.0.0", port=8001)
```

---

### Exercise 2: Implement the Aegis Orchestrator Agent (Distributed Trace Provider)
The **Orchestrator** coordinates the Threat Intelligence and Mitigation agents to run complete automated incident mitigation cycles.

1.  **Skeleton for `orchestrator_agent/agent.py`:**
    Complete the `TODO` placeholders to consume remote A2A services and track distributed traces.

```python
from google.adk.agents import Agent, RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from dotenv import load_dotenv

load_dotenv()

# TODO 1: Define Remote A2A Agent Gateways
threat_intel_service = RemoteA2aAgent(
    name="threat_intel_agent",
    agent_card=f"http://localhost:8001/a2a/threat_intel_agent{AGENT_CARD_WELL_KNOWN_PATH}"
)

mitigation_service = RemoteA2aAgent(
    name="mitigation_agent",
    agent_card=f"http://localhost:8003/a2a/mitigation_agent{AGENT_CARD_WELL_KNOWN_PATH}"
)

# TODO 2: Create the main Aegis Orchestrator Agent with tracing integration
root_agent = Agent(
    model="gemini-3.5-flash",
    name="aegis_orchestrator",
    instruction="""
        You are the master coordinator for the Aegis Incident Response System.
        
        1. First, consult the `threat_intel_agent` to search access logs and locate the details of any malicious logins or scans.
        2. For each security incident detected, compile an Incident Profile detailing:
           - Attacker IP / Target Node
           - Attack type (e.g. brute-force, SQLi)
        3. Send this profile to `mitigation_agent` to search playbooks, draft a patching script, and upload an Executive Security Brief PDF.
        4. Present the resulting mitigation plan and download links back to the SOC analyst.
    """,
    sub_agents=[threat_intel_service, mitigation_service]
)

app = App(name="aegis_incident_response_system", root_agent=root_agent)
runner = InMemoryRunner(app=app)
```

---

### Exercise 3: Implement the Mitigation & Patching Agent
The **Mitigation Agent** receives an Incident Profile, queries Vertex AI Search (RAG) for CIS playbooks, generates a patching script, and uploads the brief PDF to Google Cloud Storage.

1.  **Skeleton for `mitigation_agent/agent.py`:**

```python
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import ToolContext
from google.adk.mcp import McpToolset
import os
import uvicorn

# TODO 1: Initialize the GCS Storage MCP server
gcs_mcp_toolset = McpToolset(
    mcp_server_url=os.getenv("GCS_MCP_SERVER_URL", "http://localhost:5002")
)

# TODO 2: Write a tool to search Playbook reference documents
def search_remediation_playbooks(vulnerability_type: str) -> str:
    """Searches the Security Remediation Playbooks (RAG)."""
    # Simulate a playbook database lookup
    return f"Remediation Playbook #40: For database log attacks, isolate port 3306, enable VPC Service Controls, and rotate target IAM passwords."

# TODO 3: Write a tool to render and upload the Action Plan PDF
async def build_and_upload_mitigation_brief(target_node: str, incident_type: str, tool_context: ToolContext) -> dict:
    """Generates an executive security brief PDF and uploads it to GCS via MCP."""
    pdf_content = f"Aegis Remediation Brief for {target_node}\n\nIncident: {incident_type}".encode()
    
    # Mocking secure GCS destination URL
    gcs_dest_url = f"https://storage.googleapis.com/aegis-security-briefs/{target_node.lower().replace('.', '_')}_mitigation_brief.pdf"
    
    return {
        "status": "success",
        "brief_url": gcs_dest_url,
        "message": f"Successfully generated security patch script and uploaded executive brief to {gcs_dest_url}"
    }

# TODO 4: Construct the Mitigation Agent
mitigation_agent = Agent(
    model="gemini-3.5-flash",
    name="mitigation_agent",
    instruction="You generate patch scripts and executive briefings. Use Playbook search and GCS upload tools.",
    tools=[search_remediation_playbooks, build_and_upload_mitigation_brief, gcs_mcp_toolset]
)

a2a_app = to_a2a(mitigation_agent)

if __name__ == "__main__":
    uvicorn.run(a2a_app, host="0.0.0.0", port=8003)
```

---

### Self-Reflection Questions
- In AgentOps, why is trace context propagation critical for debugging multi-agent HTTP calls?
- What are the architectural differences between measuring token counts locally versus exporting OpenTelemetry span metrics to Google Cloud Monitoring?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlNDAtYWR2YW5jZWQtY2Fwc3RvbmUtYWVnaXMtaW5jaWRlbnQtcmVzcG9uc2UvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module40-advanced-capstone-aegis-incident-response/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
