"""
Module Rubrics Definitions for Google ADK Training (From Zero to Hero)
"""

from typing import Dict, Optional
from scripts.rubrics import ModuleRubric

RUBRICS: Dict[str, ModuleRubric] = {
    "01": ModuleRubric(
        module_id="01",
        title="Introduction to AI Agents & ADK Architecture",
        theory_ref="Module 01 Theory -> 'AI Agents vs Workflows'",
        has_code=False,
    ),
    "02": ModuleRubric(
        module_id="02",
        title="Setting Up Your Development Environment",
        theory_ref="Module 02 Theory -> 'Modern uv Development'",
        has_code=False,
    ),
    "03": ModuleRubric(
        module_id="03",
        title="Your First Agent: Echo and Simple Instructions",
        required_imports=["google.adk", "Agent"],
        required_symbols=["agent"],
        expected_models=["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-2.5-flash"],
        theory_ref="Module 03 Theory -> 'Creating Your First Agent'",
        hints={
            "missing_agent": "Ensure you define an Agent object with `name` and `instruction`.",
            "wrong_model": "Use the standard course model 'gemini-3.8-flash'."
        }
    ),
    "04": ModuleRubric(
        module_id="04",
        title="Agent Configuration & Personas Deep Dive",
        required_imports=["google.adk", "Agent"],
        required_symbols=["agent"],
        expected_models=["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-2.5-flash"],
        theory_ref="Module 04 Theory -> 'Designing Robust System Instructions'",
    ),
    "04_5": ModuleRubric(
        module_id="04_5",
        title="Multi-Model Agents with LiteLLM Integration",
        required_imports=["google.adk", "Agent"],
        theory_ref="Module 04.5 Theory -> 'Multi-Model Fallbacks with LiteLLM'",
    ),
    "05": ModuleRubric(
        module_id="05",
        title="Running Agents: CLI & Interactive Playground",
        theory_ref="Module 05 Theory -> 'Interactive adk run and adk web'",
        has_code=False,
    ),
    "06": ModuleRubric(
        module_id="06",
        title="Programmatic Execution: App, Runners, and Events",
        required_imports=["google.adk", "App", "InMemoryRunner"],
        required_symbols=["app", "runner"],
        theory_ref="Module 06 Theory -> 'ADK 2.0 Execution Lifecycle: App & Runner'",
        hints={
            "deprecated_candidates": "Do not use `.candidates`. ADK 2.0 uses direct `.content` on responses."
        }
    ),
    "07": ModuleRubric(
        module_id="07",
        title="Multimodal Understanding: Text, Images, and Documents",
        required_imports=["google.adk", "Agent", "App"],
        theory_ref="Module 07 Theory -> 'Multimodal Inputs in ADK 2.0'",
    ),
    "08": ModuleRubric(
        module_id="08",
        title="Introduction to Tools: Deterministic Capability",
        required_imports=["google.adk", "Agent"],
        theory_ref="Module 08 Theory -> 'Function Tools and Schema Generation'",
    ),
    "09": ModuleRubric(
        module_id="09",
        title="Custom Python Function Tools",
        required_imports=["google.adk", "Agent"],
        theory_ref="Module 09 Theory -> 'Type Annotations and Docstrings in Tools'",
    ),
    "10": ModuleRubric(
        module_id="10",
        title="Advanced Function Tools: Pydantic Validation & Context",
        required_imports=["google.adk", "Agent"],
        theory_ref="Module 10 Theory -> 'Structured Outputs & Pydantic Tools'",
    ),
    "11": ModuleRubric(
        module_id="11",
        title="OpenAPI Tools: Connecting REST Endpoints",
        required_imports=["google.adk"],
        theory_ref="Module 11 Theory -> 'OpenAPI Tool Specifications'",
    ),
    "12": ModuleRubric(
        module_id="12",
        title="Built-in Grounding Tools: Google Search & Vertex AI",
        required_imports=["google.adk"],
        theory_ref="Module 12 Theory -> 'Grounded Agents with Search'",
    ),
    "13": ModuleRubric(
        module_id="13",
        title="Tool Context & Dynamic Invocation Metadata",
        required_imports=["google.adk"],
        theory_ref="Module 13 Theory -> 'Accessing Context in Tool Invocations'",
    ),
    "13_5": ModuleRubric(
        module_id="13_5",
        title="State Persistence with Google Cloud Firestore",
        required_imports=["google.adk"],
        theory_ref="Module 13.5 Theory -> 'Persistent Session Services'",
    ),
    "14": ModuleRubric(
        module_id="14",
        title="Third-Party Ecosystem Tools (LangChain & Community)",
        required_imports=["google.adk"],
        theory_ref="Module 14 Theory -> 'Integrating Ecosystem Tools'",
    ),
    "15": ModuleRubric(
        module_id="15",
        title="Introduction to Multi-Agent Systems (MAS)",
        required_imports=["google.adk", "Agent"],
        theory_ref="Module 15 Theory -> 'Multi-Agent Topologies & Delegation'",
    ),
    "16": ModuleRubric(
        module_id="16",
        title="Static Sequential Orchestration Pipelines",
        required_imports=["google.adk", "Agent"],
        theory_ref="Module 16 Theory -> 'Chaining Agents Sequentially'",
    ),
    "17": ModuleRubric(
        module_id="17",
        title="Structured Intent Routing & Dispatchers",
        required_imports=["google.adk", "Agent"],
        theory_ref="Module 17 Theory -> 'Intent Classification & Dynamic Routing'",
    ),
    "18": ModuleRubric(
        module_id="18",
        title="Dynamic Multi-Agent Orchestration & Resumability",
        required_imports=["google.adk", "Agent"],
        theory_ref="Module 18 Theory -> 'Dynamic Sub-Agent Orchestration'",
    ),
    "19": ModuleRubric(
        module_id="19",
        title="Collaborative Teams & Autonomous Sub-Agents",
        required_imports=["google.adk", "Agent"],
        theory_ref="Module 19 Theory -> 'Peer-to-Peer Agent Collaboration'",
    ),
    "20": ModuleRubric(
        module_id="20",
        title="Cyclic Workflows: Evaluator-Optimizer & Reflection Loops",
        required_imports=["google.adk", "Agent"],
        theory_ref="Module 20 Theory -> 'Iterative Reflection & Optimization'",
    ),
    "21": ModuleRubric(
        module_id="21",
        title="Distributed Agent Graphs with Agent-to-Agent (A2A)",
        required_imports=["google.adk"],
        theory_ref="Module 21 Theory -> 'A2A Protocol & Distributed Agents'",
    ),
    "21_5": ModuleRubric(
        module_id="21_5",
        title="Multi-Agent Systems Knowledge Milestone",
        theory_ref="Module 21.5 Milestone Review",
        has_code=False,
    ),
    "22": ModuleRubric(
        module_id="22",
        title="State Management, Memory, and Session Context",
        required_imports=["google.adk"],
        theory_ref="Module 22 Theory -> 'State Scopes: Session, User, and App'",
    ),
    "23": ModuleRubric(
        module_id="23",
        title="Artifacts Management & Rich Document Outputs",
        required_imports=["google.adk"],
        theory_ref="Module 23 Theory -> 'Generating and Managing Artifacts'",
    ),
    "24": ModuleRubric(
        module_id="24",
        title="Evaluation: LLM-as-Judge & Trajectory Scoring",
        required_imports=[],
        theory_ref="Module 24 Theory -> 'Automated Evaluation Flywheel'",
    ),
    "25": ModuleRubric(
        module_id="25",
        title="Observability: Tracing, Logging, and AgentOps",
        required_imports=["google.adk"],
        theory_ref="Module 25 Theory -> 'Distributed Tracing & Telemetry'",
    ),
    "25_5": ModuleRubric(
        module_id="25_5",
        title="Responsible AI & Safety Guardrail Plugins",
        required_imports=["google.adk"],
        theory_ref="Module 25.5 Theory -> 'Input/Output Content Moderation'",
    ),
    "26": ModuleRubric(
        module_id="26",
        title="Agent Callbacks & Interceptors",
        required_imports=["google.adk"],
        theory_ref="Module 26 Theory -> 'Lifecycle Interceptors & Hook Points'",
    ),
    "27": ModuleRubric(
        module_id="27",
        title="Introduction to Model Context Protocol (MCP)",
        required_imports=["google.adk"],
        theory_ref="Module 27 Theory -> 'MCP Client Integration'",
    ),
    "28": ModuleRubric(
        module_id="28",
        title="Building Custom MCP Tool Servers",
        required_imports=["google.adk"],
        theory_ref="Module 28 Theory -> 'Authoring MCP Tools & Resource Endpoints'",
    ),
    "29": ModuleRubric(
        module_id="29",
        title="UI Integration: Webhooks & Client Interfaces",
        theory_ref="Module 29 Theory -> 'Connecting Frontends to Agent Endpoints'",
        has_code=False,
    ),
    "30": ModuleRubric(
        module_id="30",
        title="Custom Real-Time Streaming Clients",
        required_imports=["google.adk"],
        theory_ref="Module 30 Theory -> 'SSE & Bidirectional Token Streaming'",
    ),
    "31": ModuleRubric(
        module_id="31",
        title="Production Deployment Strategies",
        theory_ref="Module 31 Theory -> 'Serverless vs Containerized Workloads'",
        has_code=False,
    ),
    "32": ModuleRubric(
        module_id="32",
        title="Deploying Agents to Google Cloud Run",
        theory_ref="Module 32 Theory -> 'Containerizing ADK Services for Cloud Run'",
        has_code=False,
    ),
    "33": ModuleRubric(
        module_id="33",
        title="Enterprise Deployment on Google Kubernetes Engine (GKE)",
        theory_ref="Module 33 Theory -> 'Kubernetes Deployment Topology'",
        has_code=False,
    ),
    "34": ModuleRubric(
        module_id="34",
        title="Deploying MCP Servers to Cloud Run",
        required_imports=["google.adk"],
        theory_ref="Module 34 Theory -> 'Production MCP Architecture'",
    ),
    "35": ModuleRubric(
        module_id="35",
        title="Vertex AI Agent Runtime & Managed Infrastructure",
        required_imports=["google.adk"],
        theory_ref="Module 35 Theory -> 'Managed Vertex AI Agent Engine'",
    ),
    "36": ModuleRubric(
        module_id="36",
        title="Gemini Enterprise Agent Gateway & Workflows",
        theory_ref="Module 36 Theory -> 'Enterprise Tool Federation & Discovery'",
        has_code=False,
    ),
    "37": ModuleRubric(
        module_id="37",
        title="Capstone Project: Autonomous Shopping Agent",
        required_imports=["google.adk"],
        theory_ref="Module 37 Theory -> 'End-to-End Multimodal E-Commerce Agent'",
    ),
    "38": ModuleRubric(
        module_id="38",
        title="Production Best Practices & Reliability Matrix",
        required_imports=["google.adk"],
        theory_ref="Module 38 Theory -> 'Enterprise Reliability Defense Matrix'",
    ),
    "39": ModuleRubric(
        module_id="39",
        title="Modular Agent Plugins & Interceptors",
        required_imports=["google.adk"],
        theory_ref="Module 39 Theory -> 'Plugin Architecture & LifeCycle Hooks'",
    ),
    "39_5": ModuleRubric(
        module_id="39_5",
        title="Autonomous Agent Skills & Dynamic Capabilities",
        required_imports=["google.adk"],
        theory_ref="Module 39.5 Theory -> 'On-Demand SKILL.md Resolution'",
    ),
    "40": ModuleRubric(
        module_id="40",
        title="Final Capstone: Aegis Autonomous Incident Response System",
        required_imports=["google.adk"],
        theory_ref="Module 40 Theory -> 'Autonomous SecOps Threat Remediation'",
    ),
}


def get_rubric_for_module(identifier: str) -> Optional[ModuleRubric]:
    """
    Finds rubric by module number or directory name.
    """
    clean_id = identifier.strip().lower()
    
    # 1. Direct key match (e.g. "03", "39_5")
    if clean_id in RUBRICS:
        return RUBRICS[clean_id]
        
    # 2. Number normalization (e.g. "3" -> "03")
    if clean_id.isdigit():
        padded = f"{int(clean_id):02d}"
        if padded in RUBRICS:
            return RUBRICS[padded]
            
    # 3. Directory prefix match (e.g. "module03-first-agent-echo" -> "03")
    for key, rubric in RUBRICS.items():
        if f"module{key}" in clean_id or f"module{key.replace('_', '.')}" in clean_id:
            return rubric
        if clean_id in rubric.title.lower():
            return rubric
            
    return None
