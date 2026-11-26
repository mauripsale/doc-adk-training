---
sidebar_position: 32
title: "Module 32: Deployment to Cloud Run"
pagination_label: "Module 32: Deployment to Cloud Run — 📖 Theory & Overview"
---

# Module 32: Deployment to Cloud Run

## Theory

![Serverless Agent Deployment to Cloud Run (Light)](img/hero-light.webp#gh-light-mode-only)
![Serverless Agent Deployment to Cloud Run (Dark)](img/hero-dark.webp#gh-dark-mode-only)
*Figure: Deploying production-grade serverless agent microservices to Google Cloud Run with instant scaling and secure HTTPS endpoints.*

### From Localhost to the World

So far, you have been running your agents on your local machine using commands like `uv run adk web`. This is perfect for development and testing. However, to make your agent accessible to users or to integrate it with other applications, you need to **deploy** it to a publicly accessible, scalable, and reliable environment.

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

### The Deployment Process with `uv run adk deploy cloud_run`

![Automated Cloud Run Deployment Pipeline (Light)](img/cloud-run-deployment-pipeline-light.webp#gh-light-mode-only)
![Automated Cloud Run Deployment Pipeline (Dark)](img/cloud-run-deployment-pipeline-dark.webp#gh-dark-mode-only)
*Figure: Automated 4-stage deployment pipeline: Code Packaging, Cloud Build container compilation, Artifact Registry storage, and Cloud Run service rollout.*

While you can manually build a container, push it to a registry, and configure a Cloud Run service, the ADK provides a powerful command-line tool that automates this entire process for you: `uv run adk deploy cloud_run`.

When you run this command, it performs a series of steps behind the scenes:

1.  **Packages Your Code:** It gathers your agent's code, your `requirements.txt` file, and any other necessary files.
2.  **Builds a Container Image:** It uses Google Cloud Build to create a container image based on a standard Python environment. This step is like running `docker build`.
3.  **Pushes the Image:** It pushes the newly created container image to Google Artifact Registry, a private repository for your project's containers.
4.  **Creates a Cloud Run Service:** It creates a new Cloud Run service (or updates an existing one).
5.  **Deploys the Image:** It configures the service to run the container image it just pushed.
6.  **Configures the Environment:** It passes necessary environment variables (like your Google Cloud Project ID) to the running container so the ADK can function correctly.

The result is a publicly accessible HTTPS endpoint for your agent, all from a single command. This streamlined process allows you to focus on building your agent's logic, not on the complexities of cloud infrastructure.

In the lab for this module, you will use the `uv run adk deploy cloud_run` command to deploy the multi-agent customer support system you'll build in this lab.

### Separating Infrastructure Region from Vertex AI Model Location

When deploying containers to Google Cloud, always separate two distinct location concepts:

*   **`DEPLOY_REGION` (e.g., `us-central1`):** The regional control plane where Cloud Run services, Artifact Registry repositories, and Cloud Build jobs are provisioned.
*   **`GOOGLE_CLOUD_LOCATION=global`:** The Vertex AI inference endpoint passed **into the container** as an environment variable, together with `GOOGLE_GENAI_USE_ENTERPRISE=1` (ADK 2.0's canonical Vertex AI / Agent Platform flag for the `google-genai` SDK) and `GOOGLE_CLOUD_PROJECT`. Because `gemini-3.8-flash` is served via the `global` Vertex AI endpoint, injecting `GOOGLE_CLOUD_LOCATION=global` prevents runtime `404 NOT_FOUND` model region errors inside deployed containers.

For example, when deploying with `adk deploy cloud_run` or directly with `gcloud run deploy`:

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export DEPLOY_REGION="us-central1"

# Option A: Automated ADK CLI deployment
uv run adk deploy cloud_run \
  --project="$GOOGLE_CLOUD_PROJECT" \
  --region="$DEPLOY_REGION" \
  --env GOOGLE_CLOUD_LOCATION=global \
  support_agent/

# Option B: Explicit gcloud run deploy from a pre-built image or source
gcloud run deploy customer-support \
  --source . \
  --project="$GOOGLE_CLOUD_PROJECT" \
  --region="$DEPLOY_REGION" \
  --set-env-vars="GOOGLE_GENAI_USE_ENTERPRISE=1,GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=global"
```

### Production GitOps & Infrastructure Scaffolding with `agents-cli`

For enterprise teams requiring reproducible Infrastructure-as-Code (IaC) and CI/CD pipelines, the **Google Agents CLI (`google-agents-cli`)** complements `adk deploy` by scaffolding production-grade deployment assets into your repository:

```bash
# 1. Enhance an existing plain ADK directory with Cloud Run deployment assets
uvx google-agents-cli scaffold enhance . --adk -d cloud_run --agent-directory support_agent

# 2. Deploy directly using the managed CLI workflow
uvx google-agents-cli deploy \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --region "$DEPLOY_REGION" \
  --env-vars "GOOGLE_CLOUD_LOCATION=global" \
  --no-confirm-project
```

#### What `agents-cli scaffold enhance . --adk -d cloud_run` Generates:
- **`Dockerfile`**: Single-stage Python container build using `uv` that serves `uvicorn app.fast_api_app:app` on port `8080` (exposing both the ADK HTTP surface and the `/a2a/{app_name}/.well-known/agent-card.json` endpoint).
- **`deployment/terraform/`**: Modular Terraform IaC (`single-project/` and `cicd/` configurations) provisioning the Cloud Run v2 service, Artifact Registry repository, optional Cloud SQL session storage, and least-privilege `app_sa` / `cicd_runner_sa` IAM bindings.
- **CI/CD & Load Tests**: Automated Cloud Build or GitHub Actions deployment pipelines plus `tests/load_test/` suites for tuning concurrency and memory limits.

<KnowledgeCheck
  id="m32-cloud-run-region-and-ui"
  question="When deploying a 'gemini-3.8-flash' ADK agent to Cloud Run in 'us-central1' using 'uv run adk deploy cloud_run', why should you pass '--env GOOGLE_CLOUD_LOCATION=global' alongside '--region=us-central1'?"
  options={[
    "Cloud Run services can only be created in a region literally named 'global'",
    "Without '--env GOOGLE_CLOUD_LOCATION=global', the deployer defaults GOOGLE_CLOUD_LOCATION to the Cloud Run '--region' ('us-central1'), causing Vertex AI calls to 'gemini-3.8-flash' to fail with 404 model region errors",
    "It disables HTTPS/TLS encryption so the container starts faster",
    "It automatically converts the Cloud Run service into a GKE cluster"
  ]}
  correctIndex={1}
  hint="Consider the difference between where the Cloud Run container infrastructure runs ('DEPLOY_REGION') and where 'gemini-3.8-flash' is hosted on Vertex AI."
  explanation="Cloud Run infrastructure requires a concrete GCP region such as 'us-central1' ('--region'), whereas 'gemini-3.8-flash' on Vertex AI is served on the 'global' endpoint. Passing '--env GOOGLE_CLOUD_LOCATION=global' overrides the container's runtime model location so inference calls succeed."
/>

### Key Takeaways
- **Deployment** is the process of packaging an agent into a **container** and running it on a production server.
- **Google Cloud Run** is a fully managed, serverless platform that is ideal for deploying ADK agents due to its simplicity, automatic scaling (including to zero), and pay-per-use cost model.
- The `uv run adk deploy cloud_run` command automates the entire deployment workflow, including containerization, pushing to a registry, and configuring the Cloud Run service.
- This streamlined command allows you to deploy a production-ready, publicly accessible agent with a single command.
- **Scale-to-Zero Implications:** Cloud Run's ability to scale to zero instances is highly cost-effective for agents with infrequent traffic, as you are not billed for idle time. However, this comes with a performance trade-off: the first request to a scaled-down service will experience a "cold start," resulting in higher latency as a new container instance is provisioned. Subsequent requests will be fast until the instance scales down again.
- **Omitting `--with_ui` in Production:** In a headless production scenario where the agent is consumed by another application via its API, the `--with_ui` flag should be omitted. This is for two main reasons: **security** (the Dev UI exposes internal agent details like the full instruction and tool trajectory that should not be public) and **efficiency** (the UI adds unnecessary overhead to the container size and resource consumption).
- **Automation of `uv run adk deploy`:** The `uv run adk deploy cloud_run` command automates a multi-step process that would otherwise be manual and complex: packaging the code, building a container image (like `docker build`), pushing the image to a registry (like Artifact Registry), and creating/updating the Cloud Run service with the correct permissions and configuration. Without this command, each of these steps would need to be performed manually using `gcloud` or `docker` commands.