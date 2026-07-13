---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 40: Cymbal Enterprise Intervention Multi-Agent System Challenge

## Goal
In this advanced capstone lab, you will build a sophisticated, distributed customer intervention system for Cymbal Meet. You will create three cooperative agents communicating via the Agent-to-Agent (A2A) protocol, utilizing MCP servers, Model Armor, Vertex AI Search (RAG), and Cloud Storage.

---

### Exercise 1: Implement the Data Agent (A2A Server)
The **Data Agent** must expose a natural language interface to BigQuery and sanitize output emails using Model Armor.

1.  **Skeleton for `data_agent/agent.py`:**
    Complete the `TODO` placeholders in the agent script below to load the BigQuery MCP server and sanitize output text.

```python
import os
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.mcp import McpToolset
from dotenv import load_dotenv
import uvicorn

load_dotenv()

# TODO 1: Load the BigQuery MCP Server configurations
# For this challenge, initialize an McpToolset pointing to the hosted BigQuery MCP server.
mcp_toolset = McpToolset(
    mcp_server_url=os.getenv("BIGQUERY_MCP_SERVER_URL", "http://localhost:5001")
)

# TODO 2: Define a post-process response callback to sanitize data via Model Armor
def mask_email_addresses(text: str) -> str:
    """
    Scans the response for email addresses and masks them.
    E.g. 'john.doe@cymbal.com' -> 'j***@cymbal.com'
    """
    import re
    email_regex = r"([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
    
    def mask_match(match):
        local_part = match.group(1)
        domain = match.group(2)
        if len(local_part) <= 1:
            return f"*@{domain}"
        return f"{local_part[0]}***@{domain}"

    return re.sub(email_regex, mask_match, text)

# TODO 3: Construct the Data Agent using gemini-3.5-flash
data_agent = Agent(
    model="gemini-3.5-flash",
    name="data_agent",
    instruction="""
        You are a Cymbal customer data specialist.
        You can execute read-only queries on BigQuery customer engagement tables.
        Always describe the table metadata and fetch representative rows if unsure about schemas.
    """,
    tools=[mcp_toolset]
)

# TODO 4: Add the output sanitization hook to the agent's output lifecycle
@data_agent.after_response
def sanitize_output(event):
    if event.is_final_response():
        # Sanitize sensitive data in-place
        event.content.parts[0].text = mask_email_addresses(event.content.parts[0].text)

a2a_app = to_a2a(data_agent)

if __name__ == "__main__":
    uvicorn.run(a2a_app, host="0.0.0.0", port=8001)
```

---

### Exercise 2: Implement the Improve Engagement Agent (Orchestrator)
The **Orchestrator** coordinates the Data Agent and the Intervention Agent to run complete intervention flows.

1.  **Skeleton for `orchestrator_agent/agent.py`:**
    Complete the `TODO` placeholders to consume remote A2A services as tools.

```python
from google.adk.agents import Agent, RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from dotenv import load_dotenv

load_dotenv()

# TODO 1: Define Remote A2A Agents
data_agent_service = RemoteA2aAgent(
    name="data_agent",
    agent_card=f"http://localhost:8001/a2a/data_agent{AGENT_CARD_WELL_KNOWN_PATH}"
)

intervention_agent_service = RemoteA2aAgent(
    name="intervention_agent",
    agent_card=f"http://localhost:8003/a2a/intervention_agent{AGENT_CARD_WELL_KNOWN_PATH}"
)

# TODO 2: Create the main user-facing Orchestrator Agent
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

### Exercise 3: Implement the Intervention Agent (A2A Server)
The **Intervention Agent** receives an issue profile, queries Vertex AI Search (RAG) for CS playbook docs, generates a PDF action plan, and uploads it to Cloud Storage.

1.  **Skeleton for `intervention_agent/agent.py`:**

```python
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import ToolContext
from google.adk.mcp import McpToolset
import os
import uvicorn

# TODO 1: Initialize the GCS Storage MCP server to fetch signed URLs
gcs_mcp_toolset = McpToolset(
    mcp_server_url=os.getenv("GCS_MCP_SERVER_URL", "http://localhost:5002")
)

# TODO 2: Write a tool to search Playbook reference documents
def search_cs_playbooks(query: str) -> str:
    """Searches the Customer Success Playbooks (RAG)."""
    # Simulate a semantic search return
    return "Playbook standard #14: For device performance dropouts, provide room telemetry instructions and offer hardware replacement discount."

# TODO 3: Write a tool to render and upload the action plan PDF
async def build_and_upload_plan(customer_name: str, problem_description: str, tool_context: ToolContext) -> dict:
    """Generates a PDF action plan and uploads it to GCS via MCP."""
    # Mocking PDF generation bytes
    pdf_content = f"Cymbal Meet Action Plan for {customer_name}\n\nProblem: {problem_description}".encode()
    
    # Use the GCS MCP server to get a signed URL and upload
    # For this challenge, we mock the signed GCS upload URL response
    gcs_dest_url = f"https://storage.googleapis.com/cymbal-interventions/{customer_name.lower().replace(' ', '_')}_plan.pdf"
    
    return {
        "status": "success",
        "action_plan_url": gcs_dest_url,
        "message": f"Successfully generated and uploaded intervention plan to {gcs_dest_url}"
    }

# TODO 4: Construct the Intervention Agent
intervention_agent = Agent(
    model="gemini-3.5-flash",
    name="intervention_agent",
    instruction="You generate customer outreach action plans. Use Playbook search and upload tools.",
    tools=[search_cs_playbooks, build_and_upload_plan, gcs_mcp_toolset]
)

a2a_app = to_a2a(intervention_agent)

if __name__ == "__main__":
    uvicorn.run(a2a_app, host="0.0.0.0", port=8003)
```

---

### Self-Reflection Questions
- Why are A2A microservices superior to monolithic architectures for large multi-agent setups?
- What are the compliance and privacy implications of sanitizing outputs using Model Armor before returning from remote data-fetching agents?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlNDAtYWR2YW5jZWQtY2Fwc3RvbmUtY3ltYmFsLWludGVydmVudGlvbi9sYWItc29sdXRpb24=`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module40-advanced-capstone-cymbal-intervention/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
