---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 33: Deployment to GKE — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 33: Deploying Enterprise Agents to GKE Autopilot Challenge

## Goal

In this two-part lab, you will master deploying ADK 2.0 agents to **Google Kubernetes Engine (GKE) Autopilot** from both the enterprise platform engineering perspective and the low-level Kubernetes perspective:

*   **Part 1 — Accelerated GKE Autopilot Deployment with `agents-cli` (Primary Golden Path):** Scaffold `support-ops-gke` with `--deployment-target gke`, load the canonical Part 6 stateful `support_ops_agent`, inspect the generated Terraform modules (GKE Autopilot, Workload Identity `app_sa`, and `HorizontalPodAutoscaler`), deploy with `agents-cli deploy`, test the live endpoint over **both A2A and ADK SSE** via `agents-cli run`, and practice Kubernetes rollbacks.
*   **Part 2 — Under the Hood: Manual `Dockerfile`, `deployment.yaml` & `kubectl` Deep Dive:** Build a raw container image running `adk api_server /app` and author Kubernetes `Deployment` and `Service` manifests manually to understand exactly what `agents-cli` orchestrates behind the scenes.

### Prerequisites

*   A Google Cloud Project with billing enabled.
*   Google Cloud CLI (`gcloud`) installed and authenticated (`gcloud auth login` and `gcloud auth application-default login`).
*   `kubectl` installed (`gcloud components install kubectl`) and `terraform` installed (`>= 1.5`).
*   `uv` and `google-agents-cli` installed (`uv tool install google-agents-cli`).

<Setup/>

### Prepare Your Cloud Environment

Export your project ID and `DEPLOY_REGION=us-central1` for regional GKE and Artifact Registry infrastructure, and enable the required Google Cloud APIs. Throughout both parts of this lab, we separate the cluster's regional location (`us-central1`) from the model inference endpoint (`GOOGLE_CLOUD_LOCATION=global`) required by `gemini-3.8-flash`.

```shell
export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
export DEPLOY_REGION=us-central1

gcloud config set project "$GOOGLE_CLOUD_PROJECT"

gcloud services enable \
    aiplatform.googleapis.com \
    container.googleapis.com \
    compute.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    iam.googleapis.com \
    secretmanager.googleapis.com
```

---

## Part 1: Accelerated GKE Autopilot Deployment with `agents-cli` (Recommended)

### Step 1.1: Scaffold `support-ops-gke` with the Stateful `support_ops_agent`

1.  **Scaffold a GKE-targeted ADK project and load the canonical Part 6 agent:**
    Run `agents-cli scaffold create` with `--deployment-target gke` (remember: do **not** `mkdir support-ops-gke` beforehand — `agents-cli` creates the directory), download the stateful `support_ops_agent` (`lookup_ticket`, `check_sla_policy`, `escalate_ticket`, and `App(root_agent=root_agent, name="app")`), and install dependencies:
    ```shell
    export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
    export DEPLOY_REGION=us-central1
    agents-cli scaffold create support-ops-gke \
      --agent adk \
      --deployment-target gke \
      --cicd-runner github_actions \
      --region "$DEPLOY_REGION" \
      --agent-guidance-filename GEMINI.md
    curl -fsSL https://mauripsale.github.io/doc-adk-training/samples/part6/agent.py -o support-ops-gke/app/agent.py
    cd support-ops-gke
    agents-cli install
    ```
    *(Tip: If you already have an existing `support-ops-agent` prototype directory from an earlier Part 6 module and want to add GKE support in place, run `agents-cli scaffold enhance . --deployment-target gke --cicd-runner github_actions` from inside that project directory.)*

2.  **Verify `app/agent.py` Alignment with `agents-cli-manifest.yaml`:**
    Open `app/agent.py` and confirm three essential contracts:
    *   `MODEL = "gemini-3.8-flash"`
    *   `root_agent = Agent(name="support_ops_agent", ...)`
    *   `app = App(root_agent=root_agent, name="app")` matching `agent_directory: "app"` in `agents-cli-manifest.yaml`.

### Step 1.2: Inspect the Generated GKE Autopilot Terraform & Workload Identity

Before deploying, inspect the infrastructure-as-code files that `agents-cli` generated under `deployment/terraform/`:

```shell
ls -la deployment/terraform/single-project/
```

Examine two key files in `deployment/terraform/single-project/`:
*   **`iam.tf` (Workload Identity):** Inspect how `app_sa` (the runtime GCP Service Account) is granted Vertex AI / telemetry permissions and bound to the Kubernetes ServiceAccount via `roles/iam.workloadIdentityUser`. Pods authenticate as `app_sa` with zero exported JSON keys.
*   **`service.tf` (Cluster, Pod Sizing, HPA & Internal LB):** Locate the private VPC/Cloud NAT resources, GKE Autopilot cluster, `kubernetes_deployment_v1`, `kubernetes_horizontal_pod_autoscaler_v2` (2–10 replicas at 70% CPU), `kubernetes_pod_disruption_budget_v1` (`minAvailable: 1`), and `kubernetes_service_v1` (annotated as an internal LoadBalancer on port `8080`).

> **Why GKE Rejects CLI Sizing Flags:** Try checking `agents-cli deploy --help`. Passing `--cpu`, `--memory`, or `--concurrency` to `agents-cli deploy` on a GKE project fails intentionally — pod resource requests/limits and HorizontalPodAutoscaler rules are managed declaratively in `deployment/terraform/single-project/service.tf` (and `deployment/terraform/cicd/service.tf`) so imperative CLI deploys never conflict with HPA or Terraform state.

### Step 1.3: Deploy to GKE Autopilot via `agents-cli`

Preview the deployment plan first with `--dry-run`, then run `agents-cli deploy` (note that provisioning a new GKE Autopilot cluster on the first run takes roughly 8–12 minutes):

```shell
# Preview what agents-cli will build and apply
agents-cli deploy \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --region "$DEPLOY_REGION" \
  --env-vars "GOOGLE_GENAI_USE_ENTERPRISE=1,GOOGLE_CLOUD_LOCATION=global" \
  --no-confirm-project \
  --dry-run

# Execute the build, push, and GKE Autopilot deployment
agents-cli deploy \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --region "$DEPLOY_REGION" \
  --env-vars "GOOGLE_GENAI_USE_ENTERPRISE=1,GOOGLE_CLOUD_LOCATION=global" \
  --no-confirm-project
```

### Step 1.4: Test the Live GKE Endpoint Over A2A and ADK SSE

By default, `agents-cli` configures the GKE `Service` as an **Internal LoadBalancer** inside your private VPC so pod-to-pod A2A traffic is never exposed to the public internet. Forward port `8080` from the GKE service to your laptop (or point `GKE_SERVICE_URL` at your ingress endpoint), then verify **both** protocols with `agents-cli run`:

```shell
# Fetch cluster credentials if not already configured in kubeconfig, then port-forward
kubectl get svc -A
kubectl port-forward svc/support-ops-gke 8080:8080 -n support-ops-gke &
PF_PID=$!
sleep 2

export GKE_SERVICE_URL="http://127.0.0.1:8080"

# 1. Test over the built-in Agent-to-Agent (A2A) JSON-RPC protocol
agents-cli run "Investigate ticket TCK-1042 and escalate if P1." --url "$GKE_SERVICE_URL" --mode a2a

# 2. Test over the native ADK SSE streaming surface (/run_sse)
agents-cli run "Check SLA for enterprise tier." --url "$GKE_SERVICE_URL" --mode adk --app-name app

# Stop the background port-forward when finished
kill "$PF_PID"
```

Observe how the same GKE pod seamlessly serves A2A requests (discovering the agent card automatically and executing `lookup_ticket` → `check_sla_policy` → `escalate_ticket` for P1 ticket `TCK-1042`) as well as native ADK `/run_sse` sessions!

### Step 1.5: Operational Inspection & Rollback Commands

In production, platform engineers inspect active deployments with `agents-cli` and recover instantaneously from faulty container releases using Kubernetes' native ReplicaSet history:

```shell
# List deployments discovered in the project/region
agents-cli deploy --list --project "$GOOGLE_CLOUD_PROJECT" --region "$DEPLOY_REGION"

# Inspect pod status and Deployment revision history
kubectl get pods -n support-ops-gke
kubectl rollout history deployment/support-ops-gke -n support-ops-gke

# Roll back immediately to the previous healthy ReplicaSet revision (and monitor completion)
kubectl rollout undo deployment/support-ops-gke -n support-ops-gke
kubectl rollout status deployment/support-ops-gke -n support-ops-gke
```

Return to your parent workspace directory before starting Part 2:

```shell
cd ..
```

---

## Part 2: Under the Hood — Manual `Dockerfile`, `deployment.yaml` & `kubectl` Deep Dive

Now that you have experienced the automated `agents-cli` golden path, let's peel back the curtain and manually assemble a raw `Dockerfile` (`adk api_server`) and `deployment.yaml` (`Deployment` + `Service`) for the multi-agent Customer Support router from Module 32.

### Step 2.1: Create the Multi-Agent Customer Support Package

1.  **Create the `gke_support_agent/support_agent` directory structure:**
    Placing the Python package inside `support_agent/` ensures that when `adk api_server /app` starts in the container, it discovers the `support_agent` folder name and mounts routes at `/apps/support_agent/...`:
    ```shell
    mkdir -p gke_support_agent/support_agent
    cd gke_support_agent
    ```

2.  **Create `support_agent/__init__.py`:**
    ```python
    from . import agent
    ```

3.  **Complete the Challenge Skeleton in `support_agent/agent.py`:**
    Fill in the three `# TODO` blocks below using `gemini-3.8-flash` to define `billing_agent`, `tech_support_agent`, and the delegating `root_agent`:
    ```python
    from google.adk.agents import Agent

    # TODO: 1. Define `billing_agent` (name="billing_agent", model="gemini-3.8-flash")
    # to politely handle questions about billing, invoices, and payments.
    billing_agent = None

    # TODO: 2. Define `tech_support_agent` (name="tech_support_agent", model="gemini-3.8-flash")
    # to troubleshoot technical issues and provide clear solutions.
    tech_support_agent = None

    # TODO: 3. Define `root_agent` (name="router_agent", model="gemini-3.8-flash")
    # that delegates billing questions to `billing_agent` and technical problems
    # to `tech_support_agent` via `sub_agents=[billing_agent, tech_support_agent]`.
    root_agent = None
    ```

### Step 2.2: Containerize the Agent Manually

1.  **Create `requirements.txt`:**
    ```shell
    echo "google-adk" > requirements.txt
    ```

2.  **Create `Dockerfile` in `gke_support_agent/`:**
    Notice how `support_agent/` is copied into `/app/support_agent/` while `/app` is passed as `AGENTS_DIR` to `adk api_server`. Copying files flat into `/app` would mount routes at `/apps/app/...` instead of `/apps/support_agent/...`!
    ```dockerfile
    FROM python:3.11-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY support_agent/ /app/support_agent/
    EXPOSE 8080
    CMD ["adk", "api_server", "/app", "--host", "0.0.0.0", "--port", "8080"]
    ```

### Step 2.3: Build and Push the Image to Artifact Registry

```shell
gcloud artifacts repositories create adk-images \
    --repository-format=docker \
    --location="$DEPLOY_REGION"

gcloud builds submit \
    --tag "${DEPLOY_REGION}-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/adk-images/support-agent:v1"
```

### Step 2.4: Create `deployment.yaml` and Apply with `kubectl`

1.  **Create or connect to a GKE Autopilot cluster:**
    *(If your Autopilot cluster from Part 1 is still active, you can deploy into a separate namespace on it, or create a standalone `adk-cluster` as shown below.)*
    ```shell
    gcloud container clusters create-auto adk-cluster \
        --location="$DEPLOY_REGION"

    gcloud container clusters get-credentials adk-cluster \
        --location="$DEPLOY_REGION"
    ```

2.  **Author `deployment.yaml`:**
    Notice how `GOOGLE_GENAI_USE_ENTERPRISE="1"` and `GOOGLE_CLOUD_LOCATION="global"` route `gemini-3.8-flash` calls to the global Vertex AI endpoint, and Kubernetes `metadata.name` values use hyphens (`support-agent-deployment`) to satisfy RFC 1123 naming rules:
    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: support-agent-deployment
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: support-agent
      template:
        metadata:
          labels:
            app: support-agent
        spec:
          containers:
          - name: support-agent
            image: ${DEPLOY_REGION}-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/adk-images/support-agent:v1
            ports:
            - containerPort: 8080
            env:
              - name: GOOGLE_GENAI_USE_ENTERPRISE
                value: "1"
              - name: GOOGLE_CLOUD_PROJECT
                value: "${GOOGLE_CLOUD_PROJECT}"
              - name: GOOGLE_CLOUD_LOCATION
                value: "global"
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: support-agent-service
    spec:
      type: LoadBalancer
      selector:
        app: support-agent
      ports:
      - protocol: TCP
        port: 80
        targetPort: 8080
    ```

3.  **Substitute environment variables and apply to the cluster:**
    ```shell
    envsubst < deployment.yaml | kubectl apply -f -
    ```

### Step 2.5: Verify Your Raw Kubernetes Deployment

1.  **Wait for the LoadBalancer `EXTERNAL-IP`:**
    ```shell
    kubectl get service support-agent-service --watch
    ```
    Once assigned, press `Ctrl+C` and store the IP:
    ```shell
    export EXTERNAL_IP=$(kubectl get service support-agent-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    ```

2.  **Test Session Creation & SSE Routing via `curl`:**
    ```shell
    # 1. Create session s1 for user u1 on support_agent
    curl -X POST "http://${EXTERNAL_IP}/apps/support_agent/users/u1/sessions/s1" \
      -H "Content-Type: application/json" \
      -d '{}'

    # 2. Send a billing inquiry via SSE streaming (delegates to billing_agent)
    curl -X POST "http://${EXTERNAL_IP}/run_sse" \
      -H "Content-Type: application/json" \
      -d '{
        "app_name": "support_agent",
        "user_id": "u1",
        "session_id": "s1",
        "new_message": {
          "role": "user",
          "parts": [{"text": "I have a question about my invoice."}]
        }
      }'
    ```
    Send a follow-up request with `"My app keeps crashing."` to confirm delegation to `tech_support_agent`.

---

### Cleanup (Important!)

GKE Autopilot clusters and LoadBalancers incur ongoing charges if left running. Tear down both environments when finished:

```shell
# 1. Tear down Part 1 Terraform-managed GKE infrastructure (if deployed)
cd ../support-ops-gke/deployment/terraform/single-project
terraform destroy -auto-approve
cd ../../../..

# 2. Delete Part 2 manual GKE cluster and Artifact Registry repository
gcloud container clusters delete adk-cluster \
    --location="$DEPLOY_REGION" \
    --async

gcloud artifacts repositories delete adk-images \
    --location="$DEPLOY_REGION" \
    --async

# 3. Remove local lab directories
rm -rf support-ops-gke gke_support_agent
```

### Self-Reflection Questions
- Why does `agents-cli deploy` reject `--cpu`, `--memory`, and `--concurrency` flags when `--deployment-target gke` is configured, whereas Cloud Run and Agent Runtime accept them?
- How does GKE Workload Identity (`app_sa` in `iam.tf`) eliminate the security risks of static service account JSON keys?
- In Part 2's `deployment.yaml`, what is the distinct role of the `Deployment` object versus the `Service` object, and why is `adk api_server` used in the `Dockerfile` instead of `adk web`?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="33">

# Lab 33 Solution: Deploying Enterprise Agents to GKE Autopilot

## Goal

This solution provides the complete runnable Python code for **Part 1** (`support-ops-gke/app/agent.py` deployed via `agents-cli --deployment-target gke`) and **Part 2** (`gke_support_agent/support_agent/` deployed manually via `Dockerfile` + `deployment.yaml` + `kubectl`), along with expected outputs and troubleshooting guidance.

### Part 1 Solution: `support-ops-gke/app/agent.py` (`agents-cli` Golden Path)

```python
"""
Enterprise Support Operations Agent — Canonical Part 6 End-to-End Agent (`agents-cli`).
Built with Google ADK 2.0 (`gemini-3.8-flash`), stateful tools, and built-in A2A serving.
"""

from typing import Any, Dict

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.tool_context import ToolContext
from google.genai import types

MODEL = "gemini-3.8-flash"

TICKET_DB: Dict[str, Dict[str, Any]] = {
    "TCK-1042": {
        "customer": "Acme Cloud Robotics",
        "tier": "enterprise",
        "severity": "P1",
        "status": "open",
        "summary": "Production payment webhook returning HTTP 503 timeouts in eu-west1.",
    },
    "TCK-2088": {
        "customer": "Northwind Retail",
        "tier": "standard",
        "severity": "P3",
        "status": "investigating",
        "summary": "CSV invoice export omits localized tax column.",
    },
}

SLA_POLICIES: Dict[str, Dict[str, str]] = {
    "enterprise": {
        "P1_response": "15 minutes",
        "P2_response": "1 hour",
        "P3_response": "4 hours",
        "dedicated_oncall": "Yes (24/7 SRE pager)",
    },
    "standard": {
        "P1_response": "2 hours",
        "P2_response": "8 hours",
        "P3_response": "24 business hours",
        "dedicated_oncall": "No (business-hours queue)",
    },
}


def initialize_support_state(callback_context: CallbackContext) -> None:
    """Initializes default session and user state keys before the first turn."""
    if "user:customer_tier" not in callback_context.state:
        callback_context.state["user:customer_tier"] = "standard"
    if "escalated_tickets" not in callback_context.state:
        callback_context.state["escalated_tickets"] = []


def lookup_ticket(ticket_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Looks up an enterprise support ticket by ID and syncs customer tier into state.

    Args:
        ticket_id: Ticket identifier such as 'TCK-1042' or 'TCK-2088'.
    """
    norm_id = ticket_id.strip().upper()
    record = TICKET_DB.get(norm_id)
    if not record:
        return {
            "status": "not_found",
            "ticket_id": norm_id,
            "available_sample_tickets": sorted(TICKET_DB.keys()),
            "message": f"Ticket '{norm_id}' was not found.",
        }

    tool_context.state["user:customer_tier"] = record["tier"]
    tool_context.state["active_ticket_id"] = norm_id
    return {"status": "found", "ticket_id": norm_id, **record}


def check_sla_policy(tier: str) -> Dict[str, Any]:
    """Returns response-time SLA targets for a customer tier ('enterprise' or 'standard').

    Args:
        tier: Customer support tier ('enterprise' or 'standard').
    """
    norm_tier = tier.strip().lower()
    policy = SLA_POLICIES.get(norm_tier)
    if not policy:
        return {
            "status": "error",
            "message": f"Unknown tier '{tier}'. Valid tiers: enterprise, standard.",
        }
    return {"status": "success", "tier": norm_tier, "sla_targets": policy}


def escalate_ticket(
    ticket_id: str,
    reason: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Escalates a high-severity support ticket to the incident engineering queue.

    Args:
        ticket_id: Ticket identifier to escalate (e.g., 'TCK-1042').
        reason: Concise technical justification for the escalation.
    """
    norm_id = ticket_id.strip().upper()
    if norm_id not in TICKET_DB:
        return {"status": "error", "message": f"Cannot escalate unknown ticket '{norm_id}'."}

    escalated = list(tool_context.state.get("escalated_tickets", []))
    if norm_id not in escalated:
        escalated.append(norm_id)
    tool_context.state["escalated_tickets"] = escalated

    tier = tool_context.state.get("user:customer_tier", TICKET_DB[norm_id]["tier"])
    queue = "24/7 P1 SRE Oncall" if tier == "enterprise" else "Tier-2 Engineering Queue"
    return {
        "status": "escalated",
        "ticket_id": norm_id,
        "assigned_queue": queue,
        "reason": reason.strip(),
        "session_escalated_tickets": escalated,
    }


# Keep name="support_ops_agent" in sync with root_agent_name in agents-cli-manifest.yaml
root_agent = Agent(
    name="support_ops_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    before_agent_callback=initialize_support_state,
    instruction=(
        "You are the Support Operations Agent (active customer tier: {user:customer_tier?}).\n"
        "Follow this exact operational workflow:\n"
        "1. When given a ticket ID, ALWAYS call `lookup_ticket` first.\n"
        "2. Call `check_sla_policy` for the ticket's customer tier so your answer cites exact SLA response times.\n"
        "3. If a ticket has P1 severity OR the user requests escalation, call `escalate_ticket` with a concise technical reason.\n"
        "4. Summarize the ticket status, applicable SLA target, and any escalation queue clearly."
    ),
    tools=[lookup_ticket, check_sla_policy, escalate_ticket],
)

# CRITICAL for agents-cli: App `name` MUST match `agent_directory: "app"` in agents-cli-manifest.yaml
app = App(
    root_agent=root_agent,
    name="app",
)
```

---

### Part 2 Solution: Raw Manual GKE Package (`gke_support_agent/`)

#### `support_agent/__init__.py`

```python
from . import agent
```

#### `support_agent/agent.py`

```python
from google.adk.agents import Agent

billing_agent = Agent(
    name="billing_agent",
    model="gemini-3.8-flash",
    description="Handles questions about billing, invoices, and payments.",
    instruction="You are a billing support agent. Politely answer questions about billing and payment issues.",
)

tech_support_agent = Agent(
    name="tech_support_agent",
    model="gemini-3.8-flash",
    description="Handles technical support questions and troubleshooting.",
    instruction="You are a technical support agent. Help users troubleshoot technical issues and provide clear solutions.",
)

root_agent = Agent(
    name="router_agent",
    model="gemini-3.8-flash",
    description="The main customer support router.",
    instruction="""
You are the customer support router.
Your job is to understand the user's request and delegate it to the correct specialist agent.
- If the user has a question about billing, delegate to the `billing_agent`.
- If the user has a technical problem, delegate to the `tech_support_agent`.
""",
    sub_agents=[billing_agent, tech_support_agent],
)
```

#### `Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY support_agent/ /app/support_agent/
EXPOSE 8080
CMD ["adk", "api_server", "/app", "--host", "0.0.0.0", "--port", "8080"]
```

### Expected Outputs

#### Part 1: `agents-cli run` Against Live GKE Service
*   **A2A Mode (`--mode a2a`):** Resolves the agent card from `/a2a/app`, invokes `lookup_ticket("TCK-1042")`, `check_sla_policy("enterprise")`, and `escalate_ticket("TCK-1042", ...)`, and reports the `15 minutes` P1 SLA target and `24/7 P1 SRE Oncall` escalation queue.
*   **ADK SSE Mode (`--mode adk --app-name app`):** Creates an ADK session under `/apps/app/...`, streams SSE events from `/run_sse`, and returns the `enterprise` SLA policy targets (`15 minutes` P1, `1 hour` P2, `4 hours` P3).

#### Part 2: `kubectl apply` & `kubectl get service --watch`
```
deployment.apps/support-agent-deployment created
service/support-agent-service created
```
```
NAME                    TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)        AGE
support-agent-service   LoadBalancer   10.44.192.123   34.123.45.67    80:30123/TCP   2m30s
```

### Troubleshooting Common GKE Errors

*   **Passing `--cpu` / `--memory` / `--concurrency` on `agents-cli deploy` fails:**
    *   **Cause:** `agents-cli` rejects imperative container sizing flags for GKE targets.
    *   **Solution:** Edit pod resource requests/limits and `kubernetes_horizontal_pod_autoscaler_v2` settings declaratively in `deployment/terraform/single-project/service.tf` (and `cicd/service.tf`).
*   **`kubectl apply` fails with `metadata.name: Invalid value ... RFC 1123 label`:**
    *   **Cause:** Kubernetes resource names cannot contain underscores (`_`), even when your Python package (`support_agent`) uses underscores.
    *   **Solution:** Always use hyphens (`support-agent-deployment`, `support-agent-service`) in Kubernetes `metadata.name` fields.
*   **`CrashLoopBackOff` or `404 NOT_FOUND` on `gemini-3.8-flash`:**
    *   **Cause:** Missing `GOOGLE_GENAI_USE_ENTERPRISE=1` or `GOOGLE_CLOUD_LOCATION=global` in the pod environment, or mismatched `AGENTS_DIR` inside `Dockerfile`.
    *   **Solution:** Inspect pod logs with `kubectl logs deployment/<deployment-name>` and ensure `GOOGLE_GENAI_USE_ENTERPRISE="1"` and `GOOGLE_CLOUD_LOCATION="global"` are set.

### Self-Reflection Answers

1.  **Why does `agents-cli deploy` reject `--cpu`, `--memory`, and `--concurrency` flags when `--deployment-target gke` is configured, whereas Cloud Run and Agent Runtime accept them?**
    *   **Answer:** On GKE, pod resource requests/limits and replica scaling (`HorizontalPodAutoscaler` + `PodDisruptionBudget`) are governed declaratively by Kubernetes resources inside `deployment/terraform/`. Allowing ad-hoc CLI sizing flags during image deployment would create configuration drift between live Kubernetes cluster state and Terraform IaC, and could conflict with HPA target utilization metrics.
2.  **How does GKE Workload Identity (`app_sa` in `iam.tf`) eliminate the security risks of static service account JSON keys?**
    *   **Answer:** Workload Identity binds a Kubernetes `ServiceAccount` directly to a GCP IAM Service Account (`app_sa`) using `roles/iam.workloadIdentityUser`. GKE's metadata server automatically issues short-lived, auto-rotating OAuth credentials to pods running under that Kubernetes `ServiceAccount`, completely eliminating downloadable JSON key files that could be leaked or committed to Git.
3.  **In Part 2's `deployment.yaml`, what is the distinct role of the `Deployment` object versus the `Service` object, and why is `adk api_server` used in the `Dockerfile` instead of `adk web`?**
    *   **Answer:** The `Deployment` manages pod execution, desired replica counts, self-healing, and rolling updates/rollbacks, whereas the `Service` provides a stable IP and load balancer across ephemeral pod IPs. `adk api_server` exposes a lean, headless REST/SSE API suitable for production backends, whereas `adk web` bundles the developer debug UI — exposing internal agent prompts, tool definitions, and execution traces while consuming extra memory and CPU.

</SolutionVault>
