# Module 20: Observability: Logging and Cloud Trace

## Lab 20: Observing a Deployed Agent

### Goal

In this final lab, you will learn how to enable and inspect the two pillars of observability—logging and tracing—for a deployed ADK agent. You will redeploy the customer support agent from Module 18 with observability features enabled and then use the Google Cloud Console to view its logs and traces.

### Prerequisites

*   You have successfully completed Module 18 and have a Google Cloud project set up.
*   You have the `customer-support-cloud` project directory ready.

### Step 1: Redeploy the Agent with Observability Enabled

The ADK CLI makes it incredibly simple to enable logging and tracing for a Cloud Run deployment.

1.  **Navigate to your project directory:**

    ```shell
    cd /path/to/your/adk-training/customer-support-cloud
    ```

2.  **Run the deploy command with new flags:**
    We will use the same `adk deploy cloud_run` command as before, but with two additional flags: `--log_level` and `--trace_to_cloud`.

    ```shell
    adk deploy cloud_run \
      --project=YOUR_PROJECT_ID \
      --region=us-central1 \
      --with_ui \
      --log_level=DEBUG \
      --trace_to_cloud \
      support_agent/
    ```
    **New Flags Explained:**
    *   `--log_level=DEBUG`: This tells the ADK to configure the logging level to `DEBUG`. This is very verbose and perfect for debugging, but you would typically use `INFO` in a real production environment.
    *   `--trace_to_cloud`: This is the magic flag that enables distributed tracing. It tells the ADK to automatically instrument your agent and send trace data to Google Cloud Trace.

3.  **Follow the prompts** to approve API enablement and allow unauthenticated access, just as you did in Module 18. Wait for the deployment to complete and for the command to output the new **Service URL**.

### Step 2: Generate Logs and Traces

Now that the agent is deployed, we need to interact with it to generate some observability data.

1.  **Open the Service URL** in your browser.
2.  **Interact with the agent:** Have a conversation with your customer support agent. Make sure to trigger the routing logic.
    *   **User:** "I have a question about my bill."
    *   **User:** "My internet is not working."

### Step 3: Inspect the Logs in Cloud Logging

1.  **Navigate to the Logs Explorer:**
    *   Open the [Google Cloud Console](https://console.cloud.google.com/).
    *   In the navigation menu (hamburger icon), scroll down to the "Logging" section and click on "Logs Explorer".

2.  **Query the Logs:**
    *   In the Logs Explorer, you need to filter for the logs from your Cloud Run service.
    *   Click on the "Resource" filter dropdown. Select "Cloud Run Revision" and then choose your service (it will likely be named `adk-default-service-name` or similar).
    *   You will now see a stream of logs from your agent. Because you set the log level to `DEBUG`, you will see a lot of detail.
    *   Look for log messages that show the agent's reasoning, such as the full LLM prompt, the tool calls being made (`transfer_to_agent`), and the final response.

### Step 4: Inspect the Traces in Cloud Trace

1.  **Navigate to the Trace Explorer:**
    *   In the Google Cloud Console navigation menu, scroll down to the "Trace" section and click on "Trace explorer".

2.  **Find Your Traces:**
    *   The Trace explorer will show a scatter plot of recent traces. You should see several recent dots corresponding to the requests you just made.
    *   Click on one of the dots to open the detailed trace view.

3.  **Analyze the Waterfall Diagram:**
    *   You will see a waterfall diagram that looks very similar to the "Trace" view in the local Dev UI.
    *   You can see the total duration of the request and a breakdown of the time spent in each part of the process.
    *   Click on the spans to see more details. You will see a span for the main `agent_run`, and nested within it, spans for the `call_llm` and the `execute_tool` (which in this case is the `transfer_to_agent` function call).
    *   This view is incredibly powerful for diagnosing performance bottlenecks in a production environment.

### Course and Lab Summary

**Congratulations! You have completed the Google ADK Developer Training Course!**

In this final lab, you have learned how to bridge the gap between local development and production monitoring. You now know how to:
*   Enable detailed logging for a deployed agent using the `--log_level` flag.
*   Enable distributed tracing for a deployed agent using the `--trace_to_cloud` flag.
*   Use the Google Cloud Logging Explorer to search and analyze your agent's logs.
*   Use the Google Cloud Trace Explorer to visualize the execution flow and diagnose performance issues.

You have journeyed from the fundamental concepts of AI agents all the way to deploying and observing a multi-agent system in the cloud. You are now equipped with the knowledge and skills to build, test, and run your own powerful and reliable AI agents with the Google ADK.
