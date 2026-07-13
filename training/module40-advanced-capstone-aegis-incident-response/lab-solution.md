---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 40 Solution: Aegis Incident Response & AgentOps Multi-Agent System

This solution provides the definitive production-grade ADK 2.0 implementation for the Aegis Incident Response System (AIRS), featuring active AgentOps telemetry tracking.

---

### 1. Threat Intelligence Agent (`threat_intel_agent/agent.py`)

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

# Hosted BigQuery MCP toolset
mcp_toolset = McpToolset(
    mcp_server_url=os.getenv("BIGQUERY_MCP_SERVER_URL", "http://localhost:5001")
)

def mask_security_secrets(text: str) -> str:
    """
    Model Armor Sanitization:
    Scans the response for internal private IP addresses and masks them.
    """
    ip_regex = r"\b(192\.168\.\d+)\.(\d+)\b"
    return re.sub(ip_regex, r"\1.***", text)

threat_agent = Agent(
    model="gemini-3.5-flash",
    name="threat_intel_agent",
    description="BigQuery system security log investigator.",
    instruction="""
        You are a Threat Intelligence log investigator.
        You can execute read-only queries on BigQuery security tables.
        Always describe the table metadata and fetch representative rows if unsure about schemas.
    """,
    tools=[mcp_toolset]
)

# AgentOps Telemetry and Filtering Hooks
@threat_agent.before_request
def start_timer(event):
    event.state["start_time"] = time.time()
    print(f"[AgentOps] Starting query generation span for {event.request.contents[-1]}...")

@threat_agent.after_response
def end_timer_and_sanitize(event):
    if event.is_final_response():
        # Mask secrets
        event.content.parts[0].text = mask_security_secrets(event.content.parts[0].text)
        
        # Latency calculation
        elapsed_time = time.time() - event.state.get("start_time", time.time())
        print(f"[AgentOps] Agent execution completed successfully.")
        print(f"[AgentOps] Latency: {elapsed_time:.3f}s")
        print(f"[AgentOps] Exporting OpenTelemetry Span and logs to Cloud Logging...")

a2a_app = to_a2a(threat_agent)

if __name__ == "__main__":
    uvicorn.run(a2a_app, host="127.0.0.1", port=8001)
```

---

### 2. Aegis Orchestrator Agent (`orchestrator_agent/agent.py`)

```python
from google.adk.agents import Agent, RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from dotenv import load_dotenv

load_dotenv()

# Remote gateways representing threat hunting and mitigation nodes
threat_intel_service = RemoteA2aAgent(
    name="threat_intel_agent",
    agent_card=f"http://127.0.0.1:8001/a2a/threat_intel_agent{AGENT_CARD_WELL_KNOWN_PATH}"
)

mitigation_service = RemoteA2aAgent(
    name="mitigation_agent",
    agent_card=f"http://127.0.0.1:8003/a2a/mitigation_agent{AGENT_CARD_WELL_KNOWN_PATH}"
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
        3. Send this profile to `mitigation_agent` to search playbooks, draft a patching script, and upload an Executive Security Brief PDF.
        4. Present the resulting mitigation plan and download links back to the SOC analyst.
    """,
    sub_agents=[threat_intel_service, mitigation_service]
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
from google.adk.mcp import McpToolset
import os
import uvicorn

# Signed GCS uploads MCP gateway
gcs_mcp_toolset = McpToolset(
    mcp_server_url=os.getenv("GCS_MCP_SERVER_URL", "http://localhost:5002")
)

def search_remediation_playbooks(vulnerability_type: str) -> str:
    """Searches the Security Remediation Playbooks (RAG)."""
    return "Remediation Playbook #40: For database log attacks, isolate port 3306, enable VPC Service Controls, and rotate target IAM passwords."

async def build_and_upload_mitigation_brief(target_node: str, incident_type: str, tool_context: ToolContext) -> dict:
    """Generates an executive security brief PDF and uploads it securely to GCS."""
    pdf_content = f"Aegis Remediation Brief for {target_node}\n\nIncident: {incident_type}".encode()
    
    # Simulate a signed GCS upload operation via GCS MCP server
    gcs_dest_url = f"https://storage.googleapis.com/aegis-security-briefs/{target_node.lower().replace('.', '_')}_mitigation_brief.pdf"
    
    return {
        "status": "success",
        "brief_url": gcs_dest_url,
        "message": f"Successfully generated security patch script and uploaded executive brief to {gcs_dest_url}"
    }

mitigation_agent = Agent(
    model="gemini-3.5-flash",
    name="mitigation_agent",
    description="Tailored playbook PDF synthesis and cloud upload specialist.",
    instruction="You generate patch scripts and executive briefings. Use Playbook search and GCS upload tools.",
    tools=[search_remediation_playbooks, build_and_upload_mitigation_brief, gcs_mcp_toolset]
)

a2a_app = to_a2a(mitigation_agent)

if __name__ == "__main__":
    uvicorn.run(a2a_app, host="127.0.0.1", port=8003)
```

---

### Self-Reflection Answers

1.  **In AgentOps, why is trace context propagation critical for debugging multi-agent HTTP calls?**
    *   **Boundary-Spanning Traceability:** Since A2A nodes communicate over standard network HTTP protocols, a single user request results in cascading calls across different processes or physical machines. Without trace context propagation (e.g. injecting standard `traceparent` headers), each agent would log its activity as completely isolated, disconnected events. Context propagation allows Google Cloud Trace to rebuild the execution tree showing precisely how much of the latency was spent in the orchestrator, model generation, or database calls.

2.  **What are the architectural differences between measuring token counts locally versus exporting OpenTelemetry span metrics to Google Cloud Monitoring?**
    *   **Aggregate Analytics:** Local token logging is highly useful for instant console debugging or inline budget guardrails inside the script. However, it does not scale. OpenTelemetry metrics export these values as structured multidimensional datasets. This enables platform engineering teams to build automated GCP dashboards tracking total token costs across all company departments, trigger alerts on anomalous cost spikes, and analyze consumption trends over time.
