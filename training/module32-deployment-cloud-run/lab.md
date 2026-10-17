---
sidebar_position: 2
title: "Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 32: Deploying the Customer Support Agent Challenge

## Goal

In this lab, you will build a multi-agent customer support system (a `billing_agent` and a `tech_support_agent` behind a router, config-defined in YAML) and deploy it to Google Cloud Run. This will make your agent accessible via a public URL, transforming it from a local project into a shareable, cloud-hosted service. You'll reuse this same system in later modules to compare deployment targets.

### Prerequisites

*   A Google Cloud Project with billing enabled.
*   You have completed Module 2 and have the Google Cloud CLI installed and authenticated (`gcloud auth login` and `gcloud auth application-default login`).
*   You have been granted the `Owner` or `Editor` IAM role in your GCP project, which is necessary for the deployment command to enable APIs and set permissions.
*   **Required APIs:** Ensure the following APIs are enabled in your project:
    *   Cloud Run API
    *   Cloud Build API
    *   Artifact Registry API
    *   Vertex AI API
*   **Set GCP Project:** Before starting, ensure your `gcloud` CLI is configured to the correct project:
    ```shell
    gcloud config set project YOUR_PROJECT_ID
    ```

### Step 1: Prepare Your Project for Deployment

The `uv run adk deploy cloud_run` command is a powerful tool that automates most of the deployment process. Let's prepare our project and then use the command.

<Setup/>

1.  **Navigate to your training directory:**

    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Create a new project for this lab:**
    We'll build a fresh multi-agent customer support system for this lab.

    ```shell
    # Create the main project directory
    mkdir customer_support_cloud
    cd customer_support_cloud

    # Create the agent subdirectory
    uv run adk create --type=config support_agent
    cd support_agent
    ```

3.  **Re-create the agent files:**
    Inside the `support_agent` directory, create the following three YAML files.

    *   **`billing_agent.yaml`:**
        ```yaml
        name: billing_agent
        model: gemini-3.5-flash
        description: "Handles questions about billing, invoices, and payments."
        instruction: "You are a billing support agent. Politely answer questions about billing and payment issues."
        ```

    *   **`tech_support_agent.yaml`:**
        ```yaml
        name: tech_support_agent
        model: gemini-3.5-flash
        description: "Handles technical support questions and troubleshooting."
        instruction: "You are a technical support agent. Help users troubleshoot technical issues and provide clear solutions."
        ```

    *   **`root_agent.yaml`:**
        ```yaml
        name: router_agent
        model: gemini-3.5-flash
        description: "The main customer support router."
        instruction: |
          You are the customer support router.
          Your job is to understand the user's request and delegate it to the correct specialist agent.
          - If the user has a question about billing, delegate to the `billing_agent`.
          - If the user has a technical problem, delegate to the `tech_support_agent`.
        sub_agents:
          - config_path: billing_agent.yaml
          - config_path: tech_support_agent.yaml
        ```

4.  **Configure the `.env` file for Vertex AI:**
    Cloud Run deployments work best with Agent Platform. Open the `.env` file and configure it for your project.
    ```
    GOOGLE_GENAI_USE_VERTEXAI=1
    GOOGLE_CLOUD_PROJECT=<your_gcp_project>
    GOOGLE_CLOUD_LOCATION=us-central1
    ```
    Replace `<your_gcp_project>` with your actual Google Cloud Project ID.

### Step 2: Deploy the Agent to Cloud Run

Now for the main event. We will use a single command to package, containerize, and deploy our agent.

1.  **Navigate back to the project root:**
    Make sure you are in the `customer_support_cloud` directory (the parent of `support_agent`).

    ```shell
    cd ..
    ```

2.  **Run the deployment command:**

    Execute the following command, replacing `YOUR_PROJECT_ID` with your Google Cloud Project ID.

    ```shell
    uv run adk deploy cloud_run \
      --project=YOUR_PROJECT_ID \
      --region=us-central1 \
      --with_ui \
      support_agent/
    ```
    **Command Breakdown:**
    *   `uv run adk deploy cloud_run`: The main command.
    *   `--project=YOUR_PROJECT_ID`: Specifies which Google Cloud project to deploy to.
    *   `--region=us-central1`: Specifies the geographical region for the deployment.
    *   `--with_ui`: This crucial flag tells the command to include the ADK Developer UI in the deployment, so we can interact with it in a browser.
    *   `support_agent/`: The path to the directory containing our agent's configuration.

3.  **Follow the Prompts:**
    *   The command may ask you to enable certain APIs if they are not already enabled. Type `y` and press Enter to approve.
    *   It will eventually ask: `Allow unauthenticated invocations to [service-name] (y/N)?`. For this lab, type `y` and press Enter. This makes your deployed agent publicly accessible.

The deployment process will take several minutes as it builds and uploads the container. Once complete, it will print the **Service URL**.

### Step 3: Test Your Deployed Agent

1.  **Open the Service URL:**
    Copy the URL from the terminal output and paste it into your web browser.

2.  **Interact with the Agent:**
    You should see the familiar ADK Dev UI, but this time it's being served from the cloud, not your local machine!
    *   Test the routing logic:
        *   **User:** "I have a question about my invoice." (Should be handled by the billing agent).
        *   **User:** "My app keeps crashing." (Should be handled by the tech support agent).

    Your multi-agent system is now live on the internet.

### Lab Summary

Congratulations! You have successfully deployed a multi-agent system to a scalable, serverless environment. This is the final step in taking an agent from a local prototype to a real-world application.

You have learned to:
*   Prepare a multi-agent project for deployment.
*   Use the `uv run adk deploy cloud_run` command to automate the containerization and deployment process.
*   Include the Dev UI in a deployment using the `--with_ui` flag.
*   Access and test your agent running live on a public URL.

In the next module, you will learn about an alternative deployment target, Google Kubernetes Engine (GKE), for when you need more control over your agent's infrastructure.

### Self-Reflection Questions
- The `uv run adk deploy cloud_run` command automates many steps. What are these steps, and what would you have to do manually if this command didn't exist?
- We deployed with the `--with_ui` flag. In a real production scenario where your agent is being called by another application (not a human in a browser), why would you omit this flag?
- Cloud Run can scale down to zero instances. What are the cost and performance implications of this feature for an agent that receives infrequent traffic?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="32">

# Lab 32 Solution: Deploying the Customer Support Agent

## Goal

This lab is a procedural tutorial. The primary "solution" is a successfully deployed agent and a public URL.

### Expected Output

After running the `uv run adk deploy cloud_run` command and waiting for the build and deployment process to complete, you should see output in your terminal that looks similar to this:

```
...
✓ Deploying new service... Done.
  ✓ Creating new revision...
  ✓ Routing traffic...
  ✓ Setting IAM Policy...
Done.
Service [customer_support_cloud] revision [customer_support_cloud-00001-...] has been deployed and is serving 100 percent of traffic.
Service URL: https://customer_support_cloud-xxxxxxxxxx-uc.a.run.app
```

The most important part is the **Service URL**.

### Expected Behavior

1.  When you open the **Service URL** in your browser, you should see the ADK Developer UI, identical to the one you have been using locally.

2.  When you interact with the agent, it should correctly route your requests to the appropriate sub-agent:
    *   **You:** "I have a question about my invoice."
    *   **Agent (billing_agent):** "I can help with that. What is your question about your invoice?"
    *   **You:** "My app is not loading."
    *   **Agent (tech_support_agent):** "I understand you're having trouble with the app. Can you tell me what error message you are seeing?"

### Troubleshooting Common Errors

*   **`PERMISSION_DENIED` on `iam.googleapis.com`:**
    *   **Problem:** Your user account does not have permission to set IAM policies, which is required to make the Cloud Run service public.
    *   **Solution:** Ensure your Google Cloud user account has the `Owner` or `Editor` role in the project.

*   **`PERMISSION_DENIED` on `cloudbuild.googleapis.com` or `artifactregistry.googleapis.com`:**
    *   **Problem:** The Cloud Build service account, which builds the container, doesn't have permission to push to Artifact Registry or deploy to Cloud Run. The `uv run adk deploy` command attempts to set these permissions automatically, but may fail if your user account lacks sufficient privileges.
    *   **Solution:** Manually grant the `Cloud Build Service Account` the `Artifact Registry Writer` and `Cloud Run Admin` roles in the IAM section of the Google Cloud Console.

*   **Deployment fails with a generic error:**
    *   **Solution:** Go to the Google Cloud Console, navigate to "Cloud Build", and look at the build history. Find the failed build and inspect its logs. The logs will provide a detailed error message explaining why the container build failed (e.g., a typo in `requirements.txt`, a syntax error in a Python file, etc.).

### Self-Reflection Answers

1.  **The `uv run adk deploy cloud_run` command automates many steps. What are these steps, and what would you have to do manually if this command didn't exist?**
    *   **Answer:** The `uv run adk deploy cloud_run` command automates the entire process of taking your agent from local code to a deployed Cloud Run service. Manually, this would involve:
        1.  **Containerization:** Writing a `Dockerfile` to package your agent code and its dependencies into a Docker image.
        2.  **Image Build:** Running `docker build` (or `gcloud builds submit`) to create the container image.
        3.  **Image Push:** Pushing the container image to a container registry (like Google Artifact Registry or Docker Hub) using `docker push` or `gcloud artifacts docker push`.
        4.  **Service Creation/Update:** Creating or updating a Cloud Run service, specifying the container image, environment variables, region, and IAM permissions, typically using `gcloud run deploy`.
        The `uv run adk deploy` command abstracts away all these complex, multi-step cloud infrastructure commands.

2.  **We deployed with the `--with_ui` flag. In a real production scenario where your agent is being called by another application (not a human in a browser), why would you omit this flag?**
    *   **Answer:** In a headless production scenario, the `--with_ui` flag should be omitted for two main reasons:
        1.  **Security:** The ADK Dev UI exposes internal agent details like the full instruction, tool definitions, and detailed execution traces. Exposing this information publicly can be a security risk, potentially revealing sensitive business logic or internal workings that should not be accessible to external applications or unauthorized users.
        2.  **Efficiency/Cost:** The UI adds unnecessary overhead to the container image size and consumes additional memory and CPU resources when running. Omitting it results in a smaller, faster, and more cost-effective deployment, as the agent only needs to serve its API endpoint without the additional burden of rendering a UI.

3.  **Cloud Run can scale down to zero instances. What are the cost and performance implications of this feature for an agent that receives infrequent traffic?**
    *   **Answer:**
        *   **Cost Implications:** Scaling to zero is highly cost-effective for agents with infrequent traffic because you are **not billed for idle time**. When no requests are being processed, Cloud Run gracefully shuts down all instances, and you only pay for the compute resources consumed *during active request processing*. This makes it very economical for agents that are used sporadically.
        *   **Performance Implications:** The trade-off for scaling to zero is **"cold start" latency**. The very first request to a service that has scaled down to zero instances will experience a higher latency as Cloud Run needs to provision and initialize a new container instance. This can take several seconds. Subsequent requests to the active instance(s) will be fast, but if traffic remains low and instances scale down again, the cold start penalty will recur.

</SolutionVault>
