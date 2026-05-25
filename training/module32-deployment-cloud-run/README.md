---
sidebar_position: 32
title: "Module 32: Deployment to Cloud Run"
---

# Module 32: Deployment to Cloud Run

## Theory

### From Localhost to the World

So far, you have been running your agents on your local machine using commands like `adk web`. This is perfect for development and testing. However, to make your agent accessible to users or to integrate it with other applications, you need to **deploy** it to a publicly accessible, scalable, and reliable environment.

This is the final step in the agent development lifecycle: moving from a local prototype to a production-ready service.

### What is Deployment?

Deployment is the process of taking your agent's code, packaging it up with all its dependencies, and running it on a server. For modern applications, this is almost always done using **containers**.

A container (like a Docker container) is a lightweight, standalone, executable package that includes everything needed to run a piece of software: the code, a runtime (like Python), system tools, and libraries. Containerizing your application ensures that it runs the same way regardless of where it's deployed.

### Introducing Google Cloud Run

Google Cloud Run is a **fully managed, serverless platform** designed to run containers. "Serverless" doesn't mean there are no servers; it means you don't have to manage them. You simply provide your container, and Cloud Run handles everything else:

*   **Provisioning:** It automatically provides the necessary computing resources.
*   **Scaling:** It automatically scales the number of running containers up or down based on incoming traffic. It can even scale down to zero when there are no requests, which can be very cost-effective.
*   **Load Balancing:** It distributes incoming requests across your running containers.
*   **Security:** It provides a secure environment with managed SSL certificates for your service's public URL.

Cloud Run is an ideal platform for deploying ADK agents because it's simple to use, scales automatically, and you only pay for the computing resources you actually use.

### The Deployment Process with `adk deploy cloud_run`

While you can manually build a container, push it to a registry, and configure a Cloud Run service, the ADK provides a powerful command-line tool that automates this entire process for you: `adk deploy cloud_run`.

When you run this command, it performs a series of steps behind the scenes:

1.  **Packages Your Code:** It gathers your agent's code, your `requirements.txt` file, and any other necessary files.
2.  **Builds a Container Image:** It uses Google Cloud Build to create a container image based on a standard Python environment. This step is like running `docker build`.
3.  **Pushes the Image:** It pushes the newly created container image to Google Artifact Registry, a private repository for your project's containers.
4.  **Creates a Cloud Run Service:** It creates a new Cloud Run service (or updates an existing one).
5.  **Deploys the Image:** It configures the service to run the container image it just pushed.
6.  **Configures the Environment:** It passes necessary environment variables (like your Google Cloud Project ID) to the running container so the ADK can function correctly.

The result is a publicly accessible HTTPS endpoint for your agent, all from a single command. This streamlined process allows you to focus on building your agent's logic, not on the complexities of cloud infrastructure.

In the lab for this module, you will use the `adk deploy cloud_run` command to deploy the multi-agent customer support system you built in Module 15.

### Key Takeaways
- **Deployment** is the process of packaging an agent into a **container** and running it on a production server.
- **Google Cloud Run** is a fully managed, serverless platform that is ideal for deploying ADK agents due to its simplicity, automatic scaling (including to zero), and pay-per-use cost model.
- The `adk deploy cloud_run` command automates the entire deployment workflow, including containerization, pushing to a registry, and configuring the Cloud Run service.
- This streamlined command allows you to deploy a production-ready, publicly accessible agent with a single command.
- **Scale-to-Zero Implications:** Cloud Run's ability to scale to zero instances is highly cost-effective for agents with infrequent traffic, as you are not billed for idle time. However, this comes with a performance trade-off: the first request to a scaled-down service will experience a "cold start," resulting in higher latency as a new container instance is provisioned. Subsequent requests will be fast until the instance scales down again.
- **Omitting `--with_ui` in Production:** In a headless production scenario where the agent is consumed by another application via its API, the `--with_ui` flag should be omitted. This is for two main reasons: **security** (the Dev UI exposes internal agent details like the full instruction and tool trajectory that should not be public) and **efficiency** (the UI adds unnecessary overhead to the container size and resource consumption).
- **Automation of `adk deploy`:** The `adk deploy cloud_run` command automates a multi-step process that would otherwise be manual and complex: packaging the code, building a container image (like `docker build`), pushing the image to a registry (like Artifact Registry), and creating/updating the Cloud Run service with the correct permissions and configuration. Without this command, each of these steps would need to be performed manually using `gcloud` or `docker` commands.