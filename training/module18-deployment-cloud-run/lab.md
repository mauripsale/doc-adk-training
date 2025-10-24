# Module 18: Deployment to Cloud Run

## Lab 18: Deploying the Customer Support Agent

### Goal

In this lab, you will take the multi-agent customer support system you built in Module 11 and deploy it to Google Cloud Run. This will make your agent accessible via a public URL, transforming it from a local project into a shareable, cloud-hosted service.

### Prerequisites

*   A Google Cloud Project with billing enabled.
*   You have completed Module 2 and have the Google Cloud CLI installed and authenticated (`gcloud auth login` and `gcloud auth application-default login`).
*   You have been granted the `Owner` or `Editor` IAM role in your GCP project, which is necessary for the deployment command to enable APIs and set permissions.

### Step 1: Prepare Your Project for Deployment

The `adk deploy cloud_run` command is a powerful tool that automates most of the deployment process. Let's prepare our project and then use the command.

1.  **Navigate to your training directory:**

    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Create a new project for this lab:**
    We'll use the multi-agent customer support system from Module 11. Let's create a fresh copy to ensure it's set up correctly.

    ```shell
    # Create the main project directory
    mkdir customer-support-cloud
    cd customer-support-cloud

    # Create the agent subdirectory
    adk create --type=config support_agent
    cd support_agent
    ```

3.  **Re-create the agent files:**
    Inside the `support_agent` directory, create the three YAML files from Module 11.

    *   **`billing_agent.yaml`:**
        ```yaml
        name: billing_agent
        model: gemini-1.5-flash
        description: "Handles questions about billing, invoices, and payments."
        instruction: "You are a billing support agent. Politely answer questions about billing and payment issues."
        ```

    *   **`tech_support_agent.yaml`:**
        ```yaml
        name: tech_support_agent
        model: gemini-1.5-flash
        description: "Handles technical support questions and troubleshooting."
        instruction: "You are a technical support agent. Help users troubleshoot technical issues and provide clear solutions."
        ```

    *   **`root_agent.yaml`:**
        ```yaml
        name: router_agent
        model: gemini-1.5-flash
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
    Cloud Run deployments work best with Vertex AI. Open the `.env` file and configure it for your project.
    ```
    GOOGLE_GENAI_USE_VERTEXAI=1
    GOOGLE_CLOUD_PROJECT=<your_gcp_project>
    GOOGLE_CLOUD_LOCATION=us-central1
    ```
    Replace `<your_gcp_project>` with your actual Google Cloud Project ID.

### Step 2: Deploy the Agent to Cloud Run

Now for the main event. We will use a single command to package, containerize, and deploy our agent.

1.  **Navigate back to the project root:**
    Make sure you are in the `customer-support-cloud` directory (the parent of `support_agent`).

    ```shell
    cd ..
    ```

2.  **Run the deployment command:**

    Execute the following command, replacing `YOUR_PROJECT_ID` with your Google Cloud Project ID.

    ```shell
    adk deploy cloud_run \
      --project=YOUR_PROJECT_ID \
      --region=us-central1 \
      --with_ui \
      support_agent/
    ```
    **Command Breakdown:**
    *   `adk deploy cloud_run`: The main command.
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
*   Use the `adk deploy cloud_run` command to automate the containerization and deployment process.
*   Include the Dev UI in a deployment using the `--with_ui` flag.
*   Access and test your agent running live on a public URL.

In the next module, you will learn about an alternative deployment target, Google Kubernetes Engine (GKE), for when you need more control over your agent's infrastructure.
