# Module 6: Introduction to Tools

## Lab 6: Creating a "Researcher" Agent with Google Search

### Goal

In this lab, you will build a new agent that can answer questions about current events and topics beyond the LLM's training data. You will achieve this by giving the agent its first "superpower": the ability to search the web using the built-in `google_search` tool.

### Step 1: Create the Researcher Agent Project

1.  **Navigate to your training directory:**

    Open your terminal and make sure you are in the `adk-training` directory.

    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Create the agent project:**

    Use the `adk create` command to create a new agent named `researcher-agent`.

    ```shell
    adk create --type=config researcher-agent
    ```

3.  **Navigate into the new directory:**

    ```shell
    cd researcher-agent
    ```

### Step 2: Configure the Agent to Use Google Search

To use the `google_search` tool, you need to enable the **Vertex AI API** in your Google Cloud project, as this is the service that provides the grounding functionality.

1.  **Enable the Vertex AI API:**

    *   Go to the [Vertex AI API page](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com) in the Google Cloud Console.
    *   Make sure your current project is selected.
    *   Click the **"Enable"** button if it's not already enabled.

2.  **Set up your environment variables:**

    Open the `.env` file. For the search tool to work, you **must** configure your agent to use Vertex AI.

    Update the `.env` file to look like this, filling in your project ID and desired location:
    ```
    GOOGLE_GENAI_USE_VERTEXAI=1
    GOOGLE_CLOUD_PROJECT=<your_gcp_project>
    GOOGLE_CLOUD_LOCATION=us-central1
    ```
    *   **Important:** The `google_search` tool does not work with a simple Google AI Studio API key; it requires a full Google Cloud project setup.

3.  **Define the agent's behavior and add the tool:**

    Open the `root_agent.yaml` file and replace its contents with the following:

    ```yaml
    # yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
    name: researcher_agent
    model: gemini-1.5-flash
    description: An agent that can research current events using Google Search.
    instruction: |
      You are a helpful research assistant.
      Your job is to answer the user's questions accurately.
      If the question is about a recent event, a specific person, or anything that might require up-to-date information, you MUST use the `google_search` tool.
      Do not rely on your own knowledge for topics that could have changed since your training.
    tools:
      - name: google_search
    ```

    **Analysis of the Configuration:**
    *   **`instruction`:** We've explicitly told the agent *when* and *why* it should use the `google_search` tool. This is a crucial step. Just giving an agent a tool is not enough; you must guide it on how to use it.
    *   **`tools`:** We've added a `tools` section. The line `- name: google_search` tells the ADK to attach the powerful, pre-built Google Search capability to our agent.

### Step 3: Test Your New Agent

1.  **Start the web server:**

    From inside the `researcher-agent` directory, run `adk web`.

    ```shell
    adk web
    ```

2.  **Interact with the Researcher Agent:**
    *   Open the Dev UI in your browser.
    *   Ask a question that the LLM wouldn't know from its training data:
        *   "Who won the last Super Bowl?"
        *   "What are the latest headlines about space exploration?"
        *   "What is the weather like in London today?"
    *   **Examine the Trace View:** Click on the "Trace" tab. You will now see a new step in the execution flow: `execute_tool`. Expand it to see that the `google_search` tool was called. You can see the search query the agent decided to use and the search results that were returned to the agent. This confirms the agent is using its new tool correctly.

### Lab Summary

Congratulations! You have successfully given an agent a powerful new capability. You have learned how to:

*   Enable the necessary Google Cloud APIs for advanced features.
*   Configure an agent to use a built-in tool like `google_search`.
*   Write instructions that guide the agent on when to use its tools.
*   Verify that a tool was used by inspecting the Trace View in the Dev UI.

In the next module, you will move beyond built-in tools and learn how to create your own custom tools from scratch.
