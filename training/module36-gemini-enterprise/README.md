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

Once your ADK agent is deployed to Cloud Run or Agent Runtime, you register and publish it into the Gemini Enterprise catalog using the official CLI command:

```bash
# Register an ADK agent into Gemini Enterprise
uvx google-agents-cli publish gemini \
  --agent-name "support-analyzer-prod" \
  --endpoint "https://support-analyzer-xyz-uc.a.run.app" \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --region "us-central1"
```

#### Dual Publishing Modes: ADK Direct vs. A2A Protocol

| Feature | ADK Direct Mode | A2A (Agent-to-Agent) Mode |
| :--- | :--- | :--- |
| **Protocol** | Native ADK session & invocation endpoint | Standardized OpenAPI / Agent-to-Agent JSON RPC |
| **Best For** | Internal Gemini Enterprise copilot chat integration | Cross-organization federation & multi-agent routing |
| **Authentication** | Google Cloud IAM / OAuth2 Bearer Tokens | OAuth2 / mTLS / API Key gateway tokens |
| **CLI Flag** | `--mode adk` (Default) | `--mode a2a --schema ./agent_card.json` |

<KnowledgeCheck
  id="m36-gemini-enterprise-publish"
  question="Which CLI command is used to publish and register a deployed ADK agent into the enterprise Gemini Agent Catalog?"
  options={[
    "uvx google-agents-cli publish gemini",
    "gcloud agents publish --all",
    "uv run adk share --public",
    "kubectl apply -f gemini-catalog.yaml"
  ]}
  correctIndex={0}
  hint="Look for the unified publishing command in the Google Agents CLI."
  explanation="'uvx google-agents-cli publish gemini' registers your deployed agent service with the Gemini Enterprise Agent Registry, making it discoverable and invocable across the enterprise."
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