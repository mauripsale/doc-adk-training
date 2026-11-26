---
sidebar_position: 36
title: "Module 36: Gemini Enterprise (formerly AgentSpace)"
pagination_label: "Module 36: Gemini Enterprise Publishing — 📖 Theory & Overview"
---

# Module 36: Gemini Enterprise (formerly AgentSpace)

![Gemini Enterprise Agent Ecosystem Banner (Light)](img/hero-light.webp#gh-light-mode-only)
![Gemini Enterprise Agent Ecosystem Banner (Dark)](img/hero-dark.webp#gh-dark-mode-only)

## Theory

### From Development to Enterprise Operations

While the ADK is a powerful framework for **building** agents, **Gemini Enterprise** (formerly known as Google AgentSpace) is Google Cloud's platform for **deploying, managing, and governing** those agents at an enterprise scale.

Think of the relationship like this:
*   **ADK = Development**: The tools you use to write, test, and debug your agent's logic locally.
*   **Gemini Enterprise = Operations**: The cloud platform where you run your finished agents in a secure, scalable, and managed environment.

### What is Gemini Enterprise?

Gemini Enterprise is a fully managed platform that provides the infrastructure and tooling needed for enterprise-grade agentic systems. Its key features include:

*   **Managed Hosting:** Deploy your ADK-built agents to a serverless environment where Google handles all the scaling, security, and infrastructure management.
*   **Agent Governance:** Provides centralized control over all agents in your organization, including role-based access control (RBAC), audit logging, and compliance enforcement (e.g., for HIPAA or FedRAMP).
*   **Data Connectors:** Offers pre-built, secure connectors to popular enterprise data sources like Google Drive, SharePoint, Salesforce, and BigQuery. This allows your agents to be grounded in your company's private data.
*   **Agent Gallery:** A central, internal marketplace where you can publish your agents for others in your organization to discover, share, and use.
*   **Pre-built Google Agents:** Comes with a library of powerful, production-ready agents built by Google, such as the "Deep Research Agent" and "Idea Generation Agent," which your own agents can collaborate with.
*   **Agent Designer:** A no-code, web-based interface that allows non-developers to build and configure their own simple agents.

### The Deployment Workflow

The typical workflow is to build and test your agent locally using the ADK, and then deploy it to Gemini Enterprise for production use.

![Gemini Enterprise Integration Hub & Deployment Lifecycle (Light)](img/gemini-enterprise-hub-light.webp#gh-light-mode-only)
![Gemini Enterprise Integration Hub & Deployment Lifecycle (Dark)](img/gemini-enterprise-hub-dark.webp#gh-dark-mode-only)
*Figure: Enterprise data grounding, RBAC governance, and agent extension architecture in Gemini Enterprise.*

By providing a clear separation between development (ADK) and operations (Gemini Enterprise), this model allows developers to focus on building great agent logic, while platform administrators can focus on ensuring security, compliance, and efficient operation at scale.

### Publishing Agents with `agents-cli publish gemini`

Once a text-based agent is deployed (live/bidi voice agents are not supported by the Gemini app) and a Gemini Enterprise app exists in your Google Cloud project (list existing apps anytime with `uvx google-agents-cli publish gemini --list`), register it into the Gemini Agent Gallery using `uvx google-agents-cli publish gemini`. Registration is **idempotent**—re-running updates the existing entry in place.

#### Mode 1: ADK Registration (Agent Runtime — Default on Agent Runtime)

For ADK agents deployed to **Agent Runtime**, Gemini invokes your reasoning engine natively via `:streamQuery` (`streaming_agent_run_with_events`), supporting end-to-end Google Cloud authentication and OAuth 2.0 user consent (`--authorization-id`):

```bash
# Zero-flag auto-detection when deployment_metadata.json is present (written by Module 35's `agents-cli deploy`)
uvx google-agents-cli publish gemini \
  --gemini-app-id "projects/$PROJECT_NUMBER/locations/global/collections/default_collection/engines/$GEMINI_ENGINE_ID"

# Explicit programmatic flags (ideal for CI/CD pipelines)
uvx google-agents-cli publish gemini \
  --gemini-app-id "projects/$PROJECT_NUMBER/locations/global/collections/default_collection/engines/$GEMINI_ENGINE_ID" \
  --registration-type adk \
  --agent-runtime-id "projects/$PROJECT_NUMBER/locations/us-central1/reasoningEngines/$REASONING_ENGINE_ID" \
  --display-name "Customer Support Router" \
  --description "Routes customer billing and technical support inquiries to specialist ADK agents."

# Interactive guided wizard (prompts for Gemini app, metadata auto-detection, and display name)
uvx google-agents-cli publish gemini --interactive
```

#### Mode 2: A2A Registration (Cloud Run & GKE)

On **Cloud Run** and **GKE** (which do not expose a native `ReasoningEngine` resource), or for any non-ADK framework, **A2A (Agent-to-Agent)** is the default and required registration mode. Pass the live Agent Card URL (`https://<service-url>/a2a/<agent>/.well-known/agent-card.json` for Python ADK apps, or `https://<service-url>/.well-known/agent-card.json` for Go / root-mounted servers). On Cloud Run, ensure `roles/run.servicesInvoker` is granted to the Discovery Engine service agent (`service-<PROJECT_NUMBER>@gcp-sa-discoveryengine.iam.gserviceaccount.com`):

```bash
uvx google-agents-cli publish gemini \
  --gemini-app-id "projects/$PROJECT_NUMBER/locations/global/collections/default_collection/engines/$GEMINI_ENGINE_ID" \
  --registration-type a2a \
  --agent-card-url "https://customer-support-xyz-uc.a.run.app/a2a/support_agent/.well-known/agent-card.json" \
  --display-name "Customer Support Router (Cloud Run)" \
  --description "Serverless customer support router registered over the A2A protocol."
```

#### Registration Mode Comparison

| Feature | Mode 1: ADK Registration | Mode 2: A2A Registration |
| :--- | :--- | :--- |
| **Target Runtime** | **Agent Runtime** (ADK projects only; default when `deployment_metadata.json` is present) | **Cloud Run**, **GKE**, or any non-ADK framework |
| **Invocation Protocol** | Native ReasoningEngine `:streamQuery` | Standardized Agent-to-Agent (A2A) JSON-RPC via live Agent Card |
| **Authentication & OAuth** | End-to-end IAM + managed OAuth user consent (`--authorization-id`) | IAM (`roles/run.servicesInvoker` for Discovery Engine SA) / A2A auth |
| **Core CLI Flags** | `--registration-type adk --agent-runtime-id <full_resource_name>` (or auto-detected from `deployment_metadata.json`) | `--registration-type a2a --agent-card-url https://<service-url>/a2a/<agent>/.well-known/agent-card.json` |

### Fleet Governance with Google Cloud Agent Registry

Separate from an individual Gemini app's Agent Gallery, **Google Cloud Agent Registry** provides a fleet-wide catalog of **agents and MCP servers** across your organization (managed with `roles/agentregistry.editor`). Agents deployed to Agent Runtime via `agents-cli deploy` are **auto-registered** in Agent Registry; external MCP servers (such as Module 34's Cloud Run MCP server) can be cataloged explicitly by uploading their `tools/list` specification:

```bash
# List and inspect fleet-registered agents across your project
gcloud beta agent-registry agents list \
  --project="$GOOGLE_CLOUD_PROJECT" \
  --location="us-central1"

# Register an external Cloud Run MCP server in the enterprise fleet catalog
gcloud beta agent-registry services create mcp-cart-server \
  --project="$GOOGLE_CLOUD_PROJECT" \
  --location="us-central1" \
  --mcp-server-spec-type=tool-spec \
  --mcp-server-spec-content=toolspec.json \
  --interfaces="url=https://mcp-cart-server-xyz-uc.a.run.app/mcp,protocolBinding=jsonrpc"
```

<KnowledgeCheck
  id="m36-gemini-enterprise-publish"
  question="You deployed a Python ADK agent to Cloud Run (with A2A enabled) and want to register it with an existing Gemini Enterprise app. Which command and flags are valid in 'google-agents-cli'?"
  options={[
    "uvx google-agents-cli publish gemini --gemini-app-id <app_resource> --registration-type a2a --agent-card-url https://<service-url>/a2a/<agent>/.well-known/agent-card.json",
    "uvx google-agents-cli publish gemini --gemini-app-id <app_resource> --registration-type adk --agent-runtime-id https://<service-url>",
    "gcloud agents publish --all --project <project_id>",
    "uv run adk share --public --gemini-app-id <app_resource>"
  ]}
  correctIndex={0}
  hint="Cloud Run has no ReasoningEngine resource, so 'publish gemini' fetches the live A2A Agent Card URL via '--registration-type a2a' and '--agent-card-url'."
  explanation="On Cloud Run and GKE, 'uvx google-agents-cli publish gemini' registers agents over the A2A protocol using '--gemini-app-id', '--registration-type a2a', and '--agent-card-url' pointing to the live '/a2a/<agent>/.well-known/agent-card.json' (or '/.well-known/agent-card.json') endpoint—whereas Agent Runtime ADK agents use '--registration-type adk' and '--agent-runtime-id' (or auto-detection from 'deployment_metadata.json')."
/>

### Key Takeaways
- **Gemini Enterprise** is Google Cloud's managed platform for **operating** agents at an enterprise scale, while the **ADK** is the framework for **building** them.
- It provides critical enterprise features like managed hosting, centralized governance (RBAC, audit logging), and compliance.
- **Data Connectors** allow agents to be securely grounded in private enterprise data sources like Salesforce and SharePoint.
- The **Agent Gallery** serves as an internal marketplace for discovering and sharing agents within an organization.
- Gemini Enterprise also includes **pre-built Google agents** and a no-code **Agent Designer** for non-developers.
- **Advantages of an Agent Gallery:** A centralized "Agent Gallery" is invaluable for large enterprises as it solves key problems: **Discovery** (prevents duplication of effort by allowing teams to find existing agents), **Sharing** (provides a formal and secure way to publish agents across the organization), and **Adoption** (promotes the use of automation and fosters a culture of innovation by making agents easily accessible and reusable).
- **Benefits and Risks of Agent Designer (No-Code):** The "Agent Designer" empowers non-developers to quickly build simple agents, fostering innovation and freeing up AI engineers for more complex tasks. However, it carries risks: non-developers might not implement proper guardrails (M26) or constraints (M4), leading to unreliable agents, increased costs from inefficient LLM calls, and governance challenges (e.g., shadow IT). Robust monitoring and governance by Gemini Enterprise are crucial to manage these risks.
- **Grounding and Hallucination Mitigation:** Grounding an agent in private, secure enterprise data sources (via Data Connectors) is the most effective method to mitigate hallucination and ensure accuracy. This approach leverages **Retrieval Augmented Generation (RAG)**, forcing the LLM to base its responses on retrieved, up-to-date, and approved company information rather than its static pre-trained knowledge. This drastically reduces the risk of the agent fabricating information and ensures responses are relevant and secure.

This completes **Part 6: Deployment & Enterprise** — you now know how to choose a deployment platform, ship to it, and govern what runs on it. In Part 7, you'll put everything from the entire course together in two capstone-scale projects.