---
sidebar_position: 35
title: "Module 35: Deploying to Agent Runtime"
---

# Module 35: Deploying to Agent Runtime


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

The Agents CLI streamlines the path to production into a few simple commands:

1.  **Scaffold (`uvx google-agents-cli scaffold enhance`):** This is a one-time command that analyzes your existing ADK agent and adds the necessary deployment files to it. This includes Terraform configurations for infrastructure and Cloud Build YAML files for the CI/CD pipeline.

2.  **Deploy (`uvx google-agents-cli deploy`):** This command is the main entry point for deployment. It performs two key stages:
    *   **Provision:** It runs a Cloud Build pipeline that uses Terraform to create all the necessary cloud infrastructure for your agent (Artifact Registry, Agent Runtime service, service accounts, etc.).
    *   **Upload & Execute:** It packages your agent code, uploads it to Agent Runtime, and starts the agent.

### Key Takeaways
- **Google Cloud's Agent Runtime** is a fully managed service in the Gemini Enterprise Agent Platform for deploying, scaling, and securing ADK agents.
- The **Accelerated Deployment** method, using the **Agents CLI**, is the recommended best practice for new projects, providing a pre-configured CI/CD pipeline and Infrastructure as Code.
- The **Standard Deployment** method involves writing a custom Python script with the Vertex AI SDK, which is useful for understanding the underlying mechanics.
- The Accelerated workflow follows a simple process: **Scaffold** (adds deployment files to your project) and **Deploy** (provisions infrastructure and uploads your code).
- **Agent Runtime and Complex Clients:** The architecture of Agent Runtime (a managed, scalable backend) simplifies the development of complex clients (like web or mobile apps). It handles concurrency and horizontal scaling automatically, provides a stable API for clients written in any language to connect to, and cleanly separates the UI/session management logic on the client from the heavy lifting of agent orchestration and AI logic on the backend.
- **Advantages of Accelerated Deployment:** The Accelerated Deployment method is superior for production as it automates the creation of infrastructure as code (IaC) with Terraform and establishes a simple, repeatable deployment process. This provides a reproducible, auditable, and consistent deployment, incorporating best practices from the start, whereas the Standard Deployment is manual and better suited for learning the underlying SDK mechanics.
