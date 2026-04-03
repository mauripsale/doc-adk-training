---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 32 Solution: Deploying the Customer Support Agent

## Goal

This lab is a procedural tutorial. The primary "solution" is a successfully deployed agent and a public URL.

### Expected Output

After running the `adk deploy cloud_run` command and waiting for the build and deployment process to complete, you should see output in your terminal that looks similar to this:

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
    *   **Problem:** The Cloud Build service account, which builds the container, doesn't have permission to push to Artifact Registry or deploy to Cloud Run. The `adk deploy` command attempts to set these permissions automatically, but may fail if your user account lacks sufficient privileges.
    *   **Solution:** Manually grant the `Cloud Build Service Account` the `Artifact Registry Writer` and `Cloud Run Admin` roles in the IAM section of the Google Cloud Console.

*   **Deployment fails with a generic error:**
    *   **Solution:** Go to the Google Cloud Console, navigate to "Cloud Build", and look at the build history. Find the failed build and inspect its logs. The logs will provide a detailed error message explaining why the container build failed (e.g., a typo in `requirements.txt`, a syntax error in a Python file, etc.).

### Self-Reflection Answers

1.  **The `adk deploy cloud_run` command automates many steps. What are these steps, and what would you have to do manually if this command didn't exist?**
    *   **Answer:** The `adk deploy cloud_run` command automates the entire process of taking your agent from local code to a deployed Cloud Run service. Manually, this would involve:
        1.  **Containerization:** Writing a `Dockerfile` to package your agent code and its dependencies into a Docker image.
        2.  **Image Build:** Running `docker build` (or `gcloud builds submit`) to create the container image.
        3.  **Image Push:** Pushing the container image to a container registry (like Google Artifact Registry or Docker Hub) using `docker push` or `gcloud artifacts docker push`.
        4.  **Service Creation/Update:** Creating or updating a Cloud Run service, specifying the container image, environment variables, region, and IAM permissions, typically using `gcloud run deploy`.
        The `adk deploy` command abstracts away all these complex, multi-step cloud infrastructure commands.

2.  **We deployed with the `--with_ui` flag. In a real production scenario where your agent is being called by another application (not a human in a browser), why would you omit this flag?**
    *   **Answer:** In a headless production scenario, the `--with_ui` flag should be omitted for two main reasons:
        1.  **Security:** The ADK Dev UI exposes internal agent details like the full instruction, tool definitions, and detailed execution traces. Exposing this information publicly can be a security risk, potentially revealing sensitive business logic or internal workings that should not be accessible to external applications or unauthorized users.
        2.  **Efficiency/Cost:** The UI adds unnecessary overhead to the container image size and consumes additional memory and CPU resources when running. Omitting it results in a smaller, faster, and more cost-effective deployment, as the agent only needs to serve its API endpoint without the additional burden of rendering a UI.

3.  **Cloud Run can scale down to zero instances. What are the cost and performance implications of this feature for an agent that receives infrequent traffic?**
    *   **Answer:**
        *   **Cost Implications:** Scaling to zero is highly cost-effective for agents with infrequent traffic because you are **not billed for idle time**. When no requests are being processed, Cloud Run gracefully shuts down all instances, and you only pay for the compute resources consumed *during active request processing*. This makes it very economical for agents that are used sporadically.
        *   **Performance Implications:** The trade-off for scaling to zero is **"cold start" latency**. The very first request to a service that has scaled down to zero instances will experience a higher latency as Cloud Run needs to provision and initialize a new container instance. This can take several seconds. Subsequent requests to the active instance(s) will be fast, but if traffic remains low and instances scale down again, the cold start penalty will recur.
