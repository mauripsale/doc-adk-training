---
sidebar_position: 35
title: "Module 35: Deploying to Agent Runtime"
pagination_label: "Module 35: Deploying to Agent Runtime — 📖 Theory & Overview"
---

# Module 35: Deploying to Agent Runtime

![Deploying to Agent Runtime Banner (Light)](img/hero-light.webp#gh-light-mode-only)
![Deploying to Agent Runtime Banner (Dark)](img/hero-dark.webp#gh-dark-mode-only)

## Theory

### From Local Development to Production-Grade Deployment

Deploying an agent involves packaging its code and running it on a scalable, reliable, and managed platform. **Google Cloud's Agent Runtime** is a fully managed service in the Gemini Enterprise Agent Platform designed for this, handling server management, scaling, and security.

### Two Paths to Deployment

1.  **Accelerated Deployment (Recommended Best Practice):**
    *   **Method:** Use the **Agents CLI** (`uvx google-agents-cli`). This tool applies a production-ready template to your existing ADK project, adding all the necessary files for deployment. (This replaces the older Agent Starter Pack, now in maintenance mode.)
    *   **Key Features:** It includes pre-built CI/CD pipelines using Cloud Build, Infrastructure as Code (IaC) with Terraform, and a unified CLI for a seamless deployment process.
    *   **Best For:** All new projects. It establishes best practices for security, reliability, and maintainability from the start.

2.  **Standard Deployment (Manual):**
    *   **Method:** Write a custom Python script using the Vertex AI SDK to package and deploy your agent.
    *   **Best For:** Learning the underlying mechanics of deployment, modifying an existing deployment, or for projects where the starter pack's structure is not a good fit.

This module's lab will guide you through both methods.

### The Accelerated Deployment Workflow

![Agent Runtime Architecture & Authorization Lifecycle (Light)](img/agent-runtime-auth-lifecycle-light.webp#gh-light-mode-only)
![Agent Runtime Architecture & Authorization Lifecycle (Dark)](img/agent-runtime-auth-lifecycle-dark.webp#gh-dark-mode-only)
*Figure: Managed execution, OAuth2 authentication, and deployment lifecycle in Vertex AI Agent Runtime.*

The Agents CLI streamlines the path to production into two core commands:

1.  **Scaffold (`uvx google-agents-cli scaffold enhance . --adk -d agent_runtime --agent-directory support_agent`):** Analyzes an existing plain ADK directory (passing `--adk` as a shortcut for `--base-template adk` when no `agents-cli-manifest.yaml` exists yet) and adds production deployment files in place—including a `Dockerfile`, FastAPI/A2A entrypoint, Terraform configurations (`deployment/terraform/`), and CI/CD pipelines.

2.  **Deploy (`uvx google-agents-cli deploy`):** Packages your project, builds the container image on Agent Runtime in your infrastructure region (e.g., `--region us-central1` while passing `--env-vars "GOOGLE_CLOUD_LOCATION=global"` for `gemini-3.8-flash` Vertex AI inference), and starts or updates the managed `ReasoningEngine` resource:
    *   **Non-blocking rollouts:** Because Agent Runtime container builds take 5–10 minutes, pass `--no-wait` to start the rollout asynchronously and `--status` to poll progress until completion.
    *   **Downstream metadata (`deployment_metadata.json`):** Upon completion, `agents-cli deploy` writes `deployment_metadata.json` (recording `remote_agent_runtime_id`, `deployment_target`, `is_a2a`, and `agent_directory`), which feeds directly into Module 36's zero-flag `uvx google-agents-cli publish gemini` registration!

<KnowledgeCheck
  id="m35-agent-runtime-accelerated-deployment"
  question="When enhancing an existing plain ADK directory (without an existing manifest) for Vertex AI Agent Runtime using google-agents-cli, which command generates the Dockerfile, Terraform IaC, and CI/CD pipeline assets?"
  options={[
    "uvx google-agents-cli scaffold enhance . --adk -d agent_runtime --agent-directory support_agent",
    "uv run adk build --docker-only",
    "gcloud compute instances create-with-container",
    "terraform init -backend=agent-platform"
  ]}
  correctIndex={0}
  hint="Think about the CLI subcommand that applies the ADK base template ('--adk') and Agent Runtime target ('-d agent_runtime') to an existing directory."
  explanation="Running 'uvx google-agents-cli scaffold enhance . --adk -d agent_runtime --agent-directory <dir>' applies the ADK base template to an existing folder in place, adding the Dockerfile, FastAPI/A2A adapter, Terraform IaC, and CI/CD workflows without overwriting your agent code."
/>

### Key Takeaways
- **Google Cloud's Agent Runtime** is a fully managed service in the Gemini Enterprise Agent Platform for deploying, scaling, and securing ADK agents.
- The **Accelerated Deployment** method, using the **Agents CLI**, is the recommended best practice for new projects, providing a pre-configured CI/CD pipeline and Infrastructure as Code.
- The **Standard Deployment** method involves writing a custom Python script with the Vertex AI SDK, which is useful for understanding the underlying mechanics.
- The Accelerated workflow follows a simple process: **Scaffold** (adds deployment files to your project) and **Deploy** (provisions infrastructure and uploads your code).
- **Agent Runtime and Complex Clients:** The architecture of Agent Runtime (a managed, scalable backend) simplifies the development of complex clients (like web or mobile apps). It handles concurrency and horizontal scaling automatically, provides a stable API for clients written in any language to connect to, and cleanly separates the UI/session management logic on the client from the heavy lifting of agent orchestration and AI logic on the backend.
- **Advantages of Accelerated Deployment:** The Accelerated Deployment method is superior for production as it automates the creation of infrastructure as code (IaC) with Terraform and establishes a simple, repeatable deployment process. This provides a reproducible, auditable, and consistent deployment, incorporating best practices from the start, whereas the Standard Deployment is manual and better suited for learning the underlying SDK mechanics.
