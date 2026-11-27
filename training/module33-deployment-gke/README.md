---
sidebar_position: 33
title: "Module 33: Deployment to Google Kubernetes Engine (GKE)"
pagination_label: "Module 33: Deployment to GKE — 📖 Theory & Overview"
---

# Module 33: Deployment to Google Kubernetes Engine (GKE)

## Theory

![Enterprise Container Orchestration on GKE (Light)](img/hero-light.webp#gh-light-mode-only)
![Enterprise Container Orchestration on GKE (Dark)](img/hero-dark.webp#gh-dark-mode-only)
*Figure: Enterprise agent container orchestration on Google Kubernetes Engine (GKE) with private VPC networking and multi-pod replica management.*

### When You Need Full Cluster Control

In Module 32, you deployed an agent to Google Cloud Run — a serverless container platform that scales down to zero and abstracts away cluster management. For stateless or bursty HTTP agents, Cloud Run or Vertex AI Agent Runtime are ideal starting points.

However, enterprise platform teams choose **Google Kubernetes Engine (GKE)** when workloads demand deeper infrastructure control:
*   **Custom Compute & Accelerators:** Running co-located GPU/TPU inference sidecars, custom compute classes, or memory-intensive pods alongside your ADK agent.
*   **Private Zero-Trust Networking:** Enforcing Kubernetes `NetworkPolicy` rules, service meshes, internal VPC-only LoadBalancers for pod-to-pod A2A traffic, and custom Cloud NAT egress gateways.
*   **Sidecar Architectures:** Pairing agent containers with dedicated proxy sidecars (such as the Cloud SQL Auth Proxy for persistent session state or OpenTelemetry collectors).
*   **Unified Platform Standardization:** Operating agents inside an organization's existing Kubernetes GitOps, Prometheus, and fleet governance ecosystem.

### Cloud Run vs. GKE Autopilot: Architectural Trade-Offs

**Google Kubernetes Engine (GKE) Autopilot** manages the Kubernetes control plane, node provisioning, and security hardening while preserving the full Kubernetes API (`Deployment`, `Service`, `HorizontalPodAutoscaler`, `PodDisruptionBudget`, and Workload Identity).

| Criteria | Google Cloud Run | GKE Autopilot (`--deployment-target gke`) |
| :--- | :--- | :--- |
| **Abstraction Level** | High (Serverless container revisions) | Medium (Managed Kubernetes cluster & pods) |
| **Scaling Mechanism** | Revision concurrency + instance auto-scaling (including scale-to-zero) | Declarative `HorizontalPodAutoscaler` (HPA), VPA, and node auto-provisioning |
| **Sizing Configuration** | Imperative `agents-cli deploy` flags (`--cpu`, `--memory`, `--concurrency`) or Terraform | **Declarative Terraform only** (`deployment/terraform/`); CLI sizing flags are rejected |
| **Networking** | Public HTTPS URL with IAM auth (`--no-allow-unauthenticated`) or VPC egress | Private VPC + Cloud NAT + **Internal LoadBalancer** by default (`kubectl port-forward` for dev) |
| **Persistent Sessions** | Cloud SQL via Unix socket volume mount or Agent Platform Sessions | Cloud SQL via **Auth Proxy sidecar container** in the pod or Agent Platform Sessions |
| **Rollback Mechanism** | Cloud Run revision traffic shifting (`gcloud run services update-traffic`) | Kubernetes rollout history (`kubectl rollout undo deployment/...`) or GitOps |

---

### Part 1: The Enterprise Golden Path — GKE Autopilot with `agents-cli`

![GKE Enterprise Agent Cluster Topology (Light)](img/gke-cluster-topology-light.webp#gh-light-mode-only)
![GKE Enterprise Agent Cluster Topology (Dark)](img/gke-cluster-topology-dark.webp#gh-dark-mode-only)
*Figure: Multi-tier GKE cluster topology showing load balancer ingress, replica Agent Pods governed by HPA and PDB, private VPC services, and Workload Identity.*

Hand-writing VPC subnets, Cloud NAT routers, Artifact Registry repositories, IAM bindings, and multi-object Kubernetes manifests from scratch is error-prone. **`agents-cli`** (`google-agents-cli`) codifies Google Cloud's production GKE Autopilot golden path into a repeatable scaffold-and-deploy workflow.

Whether you create a new GKE project or upgrade an existing prototype (`support-ops-agent`) in place, `agents-cli` generates the complete container and Terraform stack automatically:

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export DEPLOY_REGION="us-central1"

# Option A: Create a new GKE-targeted ADK project with GitHub Actions CI/CD
agents-cli scaffold create support-ops-gke \
  --agent adk \
  --deployment-target gke \
  --cicd-runner github_actions \
  --region "$DEPLOY_REGION" \
  --agent-guidance-filename GEMINI.md

# Option B: Upgrade an existing prototype directory in place
# agents-cli scaffold enhance . --deployment-target gke --cicd-runner github_actions
```

#### What `agents-cli` Automates Under `deployment/terraform/`

When you select `--deployment-target gke`, `agents-cli` generates two Terraform layouts — `deployment/terraform/single-project/` (for single-project environments and `agents-cli deploy`) and `deployment/terraform/cicd/` (for staging/production CI/CD pipelines):

1.  **GKE Autopilot & Private Networking (`service.tf`):** Provisions a dedicated VPC, subnet, Cloud Router + Cloud NAT (so private Autopilot nodes can reach Vertex AI endpoints without public node IPs), Artifact Registry, and a GKE Autopilot cluster.
2.  **Keyless Workload Identity (`iam.tf` & `kubernetes_service_account_v1`):** Creates a least-privilege GCP runtime service account (`app_sa`) and binds it to the Kubernetes ServiceAccount via `roles/iam.workloadIdentityUser`. Pods authenticate to Vertex AI, Cloud Trace, and Secret Manager automatically — zero service account JSON keys are ever created or mounted.
3.  **Declarative Kubernetes Workloads & Autoscaling (`service.tf`):**
    *   **`kubernetes_deployment_v1`:** Runs your single-stage `uv`-built `Dockerfile` (`uvicorn app.fast_api_app:app` on port `8080`, exposing both `/run_sse` and `/a2a/app`), configured with startup, readiness, and liveness probes, resource requests/limits, and an optional Cloud SQL Auth Proxy sidecar when `--session-type cloud_sql` is used.
    *   **`kubernetes_horizontal_pod_autoscaler_v2` (HPA):** Automatically scales pod replicas (default `2` to `10` replicas at `70%` CPU utilization).
    *   **`kubernetes_pod_disruption_budget_v1` (PDB):** Enforces `minAvailable: 1` so GKE node maintenance never takes all agent pods offline simultaneously.
    *   **`kubernetes_service_v1`:** Exposes port `8080` via an **Internal LoadBalancer** (`cloud.google.com/load-balancer-type: "Internal"`) by default for private intra-VPC and A2A traffic. During development, you tunnel from your laptop with `kubectl port-forward` and test directly via `agents-cli run --url ... --mode a2a` or `--mode adk`.

> **Critical `agents-cli` Rule for GKE Sizing:** Unlike Cloud Run and Agent Runtime — where you can pass `--cpu`, `--memory`, `--concurrency`, `--min-instances`, `--max-instances`, or `--service-name` directly on `agents-cli deploy` — **those sizing and naming flags are rejected on GKE**. Why? Because on GKE, pod resource requests/limits, service names, and `HorizontalPodAutoscaler` bounds are owned **declaratively in `deployment/terraform/single-project/service.tf` (and `cicd/service.tf`)**. Rejecting imperative CLI sizing flags prevents ad-hoc deployments from drifting out of sync with Terraform and HPA rules.

When deploying `gemini-3.8-flash` to a regional GKE cluster (such as `DEPLOY_REGION=us-central1`), pass `GOOGLE_GENAI_USE_ENTERPRISE=1` and `GOOGLE_CLOUD_LOCATION=global` via `--env-vars` so the container routes model inference to the global Vertex AI endpoint:

```bash
agents-cli deploy \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --region "$DEPLOY_REGION" \
  --env-vars "GOOGLE_GENAI_USE_ENTERPRISE=1,GOOGLE_CLOUD_LOCATION=global" \
  --no-confirm-project
```

---

### Part 2: Under the Hood — Raw Kubernetes Primitives (`Dockerfile`, `deployment.yaml` & `kubectl`)

While `agents-cli` automates cluster creation, Terraform state, and FastAPI/A2A packaging, understanding the raw Kubernetes primitives underneath makes you far more effective when debugging pod rollouts or customizing cluster topologies.

When deploying an ADK agent manually without `agents-cli`, five core steps occur beneath the surface:
1.  **Containerize with Headless `adk api_server`:** Package your agent subdirectory inside `/app/<agent_name>/` (containing `__init__.py` and `agent.py`) and run `adk api_server /app --host 0.0.0.0 --port 8080` — never `adk web`, which exposes debug traces and UI overhead in production.
2.  **Build & Push to Artifact Registry:** Submit the container build via Cloud Build (`gcloud builds submit`) to a regional Docker repository (`${DEPLOY_REGION}-docker.pkg.dev/...`).
3.  **Provision GKE Autopilot:** Create a cluster (`gcloud container clusters create-auto`) and fetch `kubeconfig` credentials (`get-credentials`).
4.  **Author Kubernetes Manifests (`deployment.yaml`):**
    *   A **`Deployment`** defines *execution*: which container image to pull, how many pod replicas to run, and container environment variables (`GOOGLE_GENAI_USE_ENTERPRISE="1"`, `GOOGLE_CLOUD_LOCATION="global"`).
    *   A **`Service`** defines *network access*: a stable IP address and load balancer routing traffic to ephemeral pod IPs selected by label (`app: support-agent`).
5.  **Apply & Operate with `kubectl`:** Apply manifests via `kubectl apply -f`, inspect logs via `kubectl logs`, and recover from bad image pushes instantaneously via `kubectl rollout undo deployment/<name>`.

<KnowledgeCheck
  id="m33-gke-api-server-routing"
  question="When containerizing an ADK agent named 'support_agent' for GKE using 'adk api_server /app --port 8080', how must the agent files be structured inside '/app' so that HTTP requests to '/apps/support_agent/...' succeed instead of returning 404 Not Found?"
  options={[
    "Place 'agent.py' directly at the filesystem root '/' and omit '__init__.py'",
    "Place the agent package inside a subdirectory '/app/support_agent/' (containing '__init__.py' and 'agent.py') and pass the parent directory '/app' to 'adk api_server'",
    "Rename the Kubernetes Service to 'support_agent_service' with underscores",
    "Run 'adk web' instead of 'adk api_server' in production"
  ]}
  correctIndex={1}
  hint="Recall how 'adk api_server <AGENTS_DIR>' discovers application names from subdirectories."
  explanation="When passed '/app', 'adk api_server' registers each valid agent subdirectory inside '/app' by its folder name. Copying your package to '/app/support_agent/' (with '__init__.py' and 'agent.py') mounts the agent under '/apps/support_agent/...', whereas copying files flat into '/app' mounts the app as '/apps/app/...' and causes '/apps/support_agent/...' requests to 404."
/>

### Key Takeaways
- **`agents-cli` Golden Path (`--deployment-target gke`):** `agents-cli scaffold create` / `enhance` automates private VPC + Cloud NAT networking, GKE Autopilot cluster provisioning, Artifact Registry, keyless **Workload Identity (`app_sa`)**, **HorizontalPodAutoscaler (HPA)**, and **PodDisruptionBudget (PDB)** via `deployment/terraform/`.
- **Declarative GKE Sizing Rule:** Runtime sizing flags (`--cpu`, `--memory`, `--concurrency`, `--min-instances`, `--max-instances`) on `agents-cli deploy` are **rejected for GKE** because pod resource requests/limits and HPA scaling live declaratively in `deployment/terraform/`.
- **Dual-Protocol Verification:** Every `agents-cli` Python container serves `uvicorn app.fast_api_app:app` on port `8080`, allowing you to test live GKE pods over both **A2A** (`--mode a2a`) and **ADK SSE** (`--mode adk --app-name app`) via `agents-cli run --url`.
- **`Deployment` vs. `Service` Objects:** Under the hood, a Kubernetes **`Deployment`** manages pod execution, replicas, and rolling updates (`kubectl rollout undo`), while a **`Service`** provides a stable network endpoint routing traffic across ephemeral pod IPs.
- **`adk api_server` vs. `adk web` in Production:** Always serve headless API containers (`uvicorn app.fast_api_app:app` in `agents-cli` or `adk api_server` in raw Dockerfiles) rather than `adk web`, which exposes internal instructions, tool schemas, and reasoning traces.
