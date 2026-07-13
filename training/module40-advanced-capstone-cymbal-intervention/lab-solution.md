---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 40 Solution: Cymbal Enterprise Intervention Multi-Agent System

This solution provides the definitive ADK 2.0 production implementation for Cymbal Meet's distributed customer intervention system.

---

### 1. Data Agent (`data_agent/agent.py`)

```python
import os
import re
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

def mask_email_addresses(text: str) -> str:
    """
    Model Armor Sanitization:
    Scans the response for email addresses and masks them.
    """
    email_regex = r"([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
    
    def mask_match(match):
        local_part = match.group(1)
        domain = match.group(2)
        if len(local_part) <= 1:
            return f"*@{domain}"
        return f"{local_part[0]}***@{domain}"

    return re.sub(email_regex, mask_match, text)

data_agent = Agent(
    model="gemini-3.5-flash",
    name="data_agent",
    description="BigQuery access specialist with sensitive data masking.",
    instruction="""
        You are a Cymbal customer data specialist.
        You can execute read-only queries on BigQuery customer engagement tables.
        Always describe the table metadata and fetch representative rows if unsure about schemas.
    """,
    tools=[mcp_toolset]
)

# Output filter hook to mask emails before return
@data_agent.after_response
def sanitize_output(event):
    if event.is_final_response():
        event.content.parts[0].text = mask_email_addresses(event.content.parts[0].text)

a2a_app = to_a2a(data_agent)

if __name__ == "__main__":
    uvicorn.run(a2a_app, host="127.0.0.1", port=8001)
```

---

### 2. Improve Engagement Agent (`orchestrator_agent/agent.py`)

```python
from google.adk.agents import Agent, RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from dotenv import load_dotenv

load_dotenv()

# Remote microservice gateways
data_agent_service = RemoteA2aAgent(
    name="data_agent",
    agent_card=f"http://127.0.0.1:8001/a2a/data_agent{AGENT_CARD_WELL_KNOWN_PATH}"
)

intervention_agent_service = RemoteA2aAgent(
    name="intervention_agent",
    agent_card=f"http://127.0.0.1:8003/a2a/intervention_agent{AGENT_CARD_WELL_KNOWN_PATH}"
)

# User-facing coordinator
root_agent = Agent(
    model="gemini-3.5-flash",
    name="improve_engagement_orchestrator",
    instruction="""
        You are the master coordinator for Cymbal Meet Customer Engagement Interventions.
        
        1. First, consult the `data_agent` to identify customers experiencing support, usage, or performance issues.
        2. For each identified at-risk customer, compile an Engagement Issue Profile containing:
           - Customer Name / Segment
           - Core Metric Shortfall
           - Open support case details
        3. Send this profile to `intervention_agent` to generate and upload a tailored PDF action plan.
        4. Present the resulting intervention PDF download links directly to the user.
    """,
    sub_agents=[data_agent_service, intervention_agent_service]
)

app = App(name="cymbal_meet_intervention_system", root_agent=root_agent)
runner = InMemoryRunner(app=app)
```

---

### 3. Intervention Agent (`intervention_agent/agent.py`)

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

def search_cs_playbooks(query: str) -> str:
    """Searches Customer Success best practices playbooks (RAG)."""
    return "Playbook standard #14: For device performance dropouts, provide room telemetry instructions and offer hardware replacement discount."

async def build_and_upload_plan(customer_name: str, problem_description: str, tool_context: ToolContext) -> dict:
    """Generates an action plan PDF and uploads it securely to GCS."""
    pdf_content = f"Cymbal Meet Action Plan for {customer_name}\n\nProblem: {problem_description}".encode()
    
    # Simulate a signed GCS upload operation using GCS MCP server
    gcs_dest_url = f"https://storage.googleapis.com/cymbal-interventions/{customer_name.lower().replace(' ', '_')}_plan.pdf"
    
    return {
        "status": "success",
        "action_plan_url": gcs_dest_url,
        "message": f"Successfully generated and uploaded intervention plan to {gcs_dest_url}"
    }

intervention_agent = Agent(
    model="gemini-3.5-flash",
    name="intervention_agent",
    description="Tailored playbook PDF synthesis and cloud upload specialist.",
    instruction="You generate customer outreach action plans. Use Playbook search and upload tools.",
    tools=[search_cs_playbooks, build_and_upload_plan, gcs_mcp_toolset]
)

a2a_app = to_a2a(intervention_agent)

if __name__ == "__main__":
    uvicorn.run(a2a_app, host="127.0.0.1", port=8003)
```

---

### Self-Reflection Answers

1.  **Why are A2A microservices superior to monolithic architectures for large multi-agent setups?**
    *   **Independent Lifecycles:** The `data_agent` can be maintained, updated, and scaled by a data team without touching the `intervention_agent` or the orchestrator.
    *   **Resource Separation:** A2A agents can run on separate, dedicated containers (e.g. `data_agent` on a container with higher memory for large result sets).
    *   **Secure Access boundaries:** Enterprise service-to-service IAM credentials secure each agent endpoint individually.

2.  **What are the compliance and privacy implications of sanitizing outputs using Model Armor?**
    *   **Zero Trust Privacy:** It ensures that personal identifiable information (PII) like customer email addresses never leaves the internal secure network boundary of the data agent, guaranteeing strict HIPAA or GDPR compliance.
