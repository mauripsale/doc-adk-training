---
sidebar_position: 40
title: "Module 40: Advanced Capstone - Aegis Incident Response & AgentOps"
---

# Module 40: Advanced Capstone - Aegis Incident Response & AgentOps

## Theory & Architecture

### 1. The Scenario: Enterprise Security Operations & Threat Remediation
In a modern enterprise security operations center (SOC), analysts are overwhelmed by the sheer volume of system audit logs, security alerts, and vulnerability notices. Sifting through BigQuery access logs, cross-referencing system vulnerabilities with the NIST/CVE database, and drafting actionable mitigation playbooks is slow, manual, and prone to human error.

### 2. The Solution: Aegis Incident Response System (AIRS)
To solve this, you will implement an advanced, distributed multi-agent system called **Aegis Incident Response System (AIRS)**. This is a secure, automated threat hunting and patching coordinator built with **ADK 2.0**, using a real Model Context Protocol (MCP) server and the Agent-to-Agent (A2A) protocol.

**A note on scope:** this capstone runs entirely on your local machine — no GCP project or billing required. Model Armor, Vertex AI Search (RAG), the GCS upload, and the AgentOps telemetry export are represented with **simplified, simulated implementations**, clearly marked as such in the code. What's real and fully functional is the part this capstone is actually testing: three independent ADK agents cooperating correctly over A2A, backed by a real MCP server and real AgentOps callback hooks. The diagram below shows the target production architecture this design is modeled on; see "Going Further" at the end for how to wire the simulated pieces up to the real services.

```mermaid
graph TD
    User([SOC Analyst - Gemini Enterprise UI]) <--> Orchestrator[Aegis Orchestrator Agent<br/>Agent Runtime]
    
    subgraph Services [Google Cloud Infrastructure]
        ModelArmor[Model Armor Service]
        BigQueryData[(BigQuery Audit Logs)]
        GCSBucket[(GCS Security Briefs Bucket)]
        GCSReference[(GCS CIS Playbooks)]
        Logging[Cloud Logging]
        Trace[Cloud Trace]
    end

    subgraph Agent1 [1. Threat Intelligence Agent - Cloud Run]
        Orchestrator <-->|A2A| ThreatIntelAgent[Threat Intel Agent]
        ThreatIntelAgent <--> BQMCP[BigQuery MCP Server]
        BQMCP <--> BigQueryData
        ThreatIntelAgent <--> ModelArmor
    end

    subgraph Agent3 [3. Mitigation & Patching Agent - Cloud Run]
        Orchestrator <-->|A2A| MitigationAgent[Mitigation & Patching Agent]
        MitigationAgent <--> RAG[Vertex AI Search RAG]
        RAG <--> GCSReference
        MitigationAgent <--> GCS_MCP[GCS MCP Server]
        GCS_MCP <--> GCSBucket
    end

    ThreatIntelAgent -.->|AgentOps OpenTelemetry| Logging
    Orchestrator -.->|AgentOps OpenTelemetry| Logging
    MitigationAgent -.->|AgentOps OpenTelemetry| Logging
    ThreatIntelAgent -.->|AgentOps OpenTelemetry| Trace
    Orchestrator -.->|AgentOps OpenTelemetry| Trace
    MitigationAgent -.->|AgentOps OpenTelemetry| Trace
```

---

## The Three Cooperative Agents & AgentOps

### 1. Threat Intelligence Agent (A2A Server, runs locally)
Acts as an automated log investigator and threat hunter.
*   **MCP Log Hunting:** Connects to a real local **MCP server** — a lightweight stand-in for a hosted BigQuery MCP server — to query simulated security audit logs, login attempts, and injection attempts. You built a server just like it in Module 28.
*   **Data Masking (simulated Model Armor):** Prior to outputting threat details, it masks sensitive internal IP addresses using a local regex, standing in for a call to the real **Model Armor** API.
*   **AgentOps Metrics (real hooks, simulated export):**
    *   Real `before_model_callback`/`after_model_callback` hooks measure model-call latency.
    *   The hooks print what a real system would export to Cloud Logging and Cloud Trace — the hook mechanism is real ADK, the export destination is simulated.

### 2. Aegis Orchestrator Agent (Orchestrator, runs locally)
The central dispatch system for SOC analysts.
*   **Coordination:** It acts as an A2A client that calls the Threat Intelligence and Mitigation agents as remote sub-agents.
*   **Command Scope:** Understands commands like:
    *   *"Detect any brute-force attacks on our billing databases and generate patching plans."*
    *   *"Remediate recent SQL injection risks in the mid-market segment logs."*
*   **Reliability:** Uses `RemoteA2aAgent(..., use_legacy=False)` to opt into ADK's reliability-fixed A2A executor (see Module 21), avoiding known streaming-mode message-duplication bugs.

### 3. Mitigation & Patching Agent (A2A Server, runs locally)
Compiles security advisories and automated patch scripts.
*   **Playbook Search (simulated RAG):** A tool function stands in for a Vertex AI Search (RAG) query over CIS Controls, NIST playbooks, and company-approved remediation standards.
*   **Briefing & Simulated GCS Upload:** Generates an executive security advisory and returns a simulated signed GCS URL, standing in for a real PDF render + Cloud Storage upload.

---

## AgentOps Deep-Dive: System Observability in Production

Implementing multi-agent systems in production requires robust **AgentOps** practices to track system performance, debug failures, and monitor costs:

1.  **Distributed Trace Propagation:**
    A2A agents communicate over HTTP. To see a unified timeline of a request, a production system propagates trace contexts across agent boundaries using standard W3C Trace Context headers. This links the user chat span to every downstream tool call and remote agent hop in a single trace tree. (This lab doesn't wire up real trace export — see "Going Further" below.)
2.  **Telemetry Hooks:**
    ADK 2.0's real hook mechanism is `before_model_callback` and `after_model_callback`, passed as constructor arguments to `Agent(...)` (the same pattern you used in Module 26). This lab uses them to measure and print:
    *   **LLM Latency:** Time taken by the model to generate responses.
    *   **AgentOps events:** A line simulating what a real export to Cloud Logging/Cloud Trace would send.

    A production system would keep the exact same callback signatures and replace the `print()` calls with real OpenTelemetry SDK calls.

### Going Further: Wiring Up the Real Services

Every simulated piece in this lab is a drop-in replacement point:
*   **Model Armor:** replace `mask_security_secrets`'s regex with a call to the real Model Armor API — the function signature doesn't need to change.
*   **Vertex AI Search (RAG):** replace `search_remediation_playbooks`'s fixed string with a real Vertex AI Search query, or an MCP server wrapping one, following the same `McpToolset` pattern already used for BigQuery.
*   **GCS Upload:** replace the simulated URL in `build_and_upload_mitigation_brief` with a real PDF render and a Cloud Storage upload (directly, or via another local MCP server built the same way as `bigquery_mock_server.py`).
*   **Real observability:** replace the `print()` calls in the AgentOps hooks with real OpenTelemetry spans and metrics, exported to Cloud Trace and Cloud Logging — Module 25 covers this pattern in depth.
*   **Real deployment:** once the pieces above are real, deploy the three agents the same way you learned in Modules 32-35 (Cloud Run for the two A2A servers, Agent Runtime for the orchestrator).
*   **Agent Skills for the playbooks:** `search_remediation_playbooks` is currently a plain function returning a fixed string. Module 39.5's Skills pattern (`SkillToolset` + `load_skill_from_dir`) is arguably a better fit than a hand-written RAG query for this: bundle each CIS/NIST playbook as its own Skill, with the remediation steps living in the Skill's `references/` folder, loaded via Progressive Disclosure only when the Mitigation Agent actually needs that specific playbook instead of always in context.
