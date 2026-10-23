---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 08: Introduction to Tools — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 8: Creating a "Researcher" Agent with Google Search Challenge

## Goal
Your task is to build and configure a new agent that can search the web to answer questions about current events.

## Lab Tasks

<Setup/>

1.  **Create a new agent** named `researcher_agent` using the `uv run adk create` command, specifying the Python type.
2.  **Enable the Vertex AI API** in your Google Cloud project.
3.  **Configure the `.env` file** inside the `researcher_agent` directory to use Vertex AI, providing your project ID and a location.
4.  **Modify the `agent.py` file** (Python approach):

    ```python
    # In agent.py
    from google.adk import Agent
    from google.adk.tools import google_search

    # TODO: Define the root_agent node
    # - name: "researcher_agent"
    # - model: "gemini-3.5-flash"
    # - instruction: Tell it to use search for current events.
    # - tools: Add the google_search tool.
    root_agent = Agent(...)
    ```

5.  **Run the agent** from your main `adk-training` directory using the `uv run adk web` command (without specifying the agent name).
6.  **Test the agent** by asking it a question about a recent event (e.g., "Who won the last major sports championship?").
7.  **Verify** that the `google_search` tool was used by inspecting the **"Trace"** view in the Dev UI.

## Self-Reflection Questions
- Why is it important to explicitly instruct the agent *when* to use the `google_search` tool? What might happen if you just gave it the tool with no instructions?
- The `google_search` tool requires an Agent Platform configuration. Why do you think this is a requirement, as opposed to using a simple Google AI Studio API key?
- How does giving an agent access to real-time information fundamentally change the kinds of problems it can solve compared to an agent that only relies on its internal knowledge?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="08">

# Lab 8 Solution: Creating a "Researcher" Agent with Google Search

## Goal

This file contains the complete, step-by-step guide to creating the "Researcher" agent.

### Goal

You will build a new agent that can answer questions about current events and topics beyond the LLM's training data by giving it the ability to search the web using the built-in `google_search` tool.

### Prerequisites
*   **Note on Costs:** Enabling the Vertex AI API and using the `google_search` tool may incur small costs on your Google Cloud bill. Please be aware of the pricing for these services.

### Step 1: Create the Researcher Agent Project

1.  **Navigate to your training directory:**

    Open your terminal and make sure you are in the `adk-training` directory.

    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Create the agent project (Python approach):**

    Use the `uv run adk create` command to create a new Python agent named `researcher_agent`.

    ```shell
    uv run adk create --type=code researcher_agent
    ```

    **Alternative (YAML approach):**

    ```shell
    uv run adk create --type=config researcher_agent
    ```

### Step 2: Configure the Agent to Use Google Search

To use the `google_search` tool, you need to enable the **Vertex AI API** in your Google Cloud project, as this is the service that provides the grounding functionality.

1.  **Enable the Vertex AI API:**

    *   Go to the [Vertex AI API page](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com) in the Google Cloud Console.
    *   Make sure your current project is selected.
    *   Click the **"Enable"** button if it's not already enabled.

2.  **Set up your environment variables:**

    Navigate into the `researcher_agent` directory and open the `.env` file. For the search tool to work, you **must** configure your agent to use Agent Platform.

    Update the `.env` file to look like this, filling in your project ID and desired location:
    ```
    GOOGLE_GENAI_USE_VERTEXAI=1
    GOOGLE_CLOUD_PROJECT=<your_gcp_project>
    GOOGLE_CLOUD_LOCATION=us-central1
    ```
    *   **Important:** The `google_search` tool does not work with a simple Google AI Studio API key; it requires a full Google Cloud project setup.

3.  **Define the agent's behavior and add the tool (Python approach):**

    Open the `agent.py` file inside `researcher_agent` and replace its contents with the following:

    ```python
    from google.adk import Agent
    from google.adk.tools import google_search

    root_agent = Agent(
        name="researcher_agent",
        model="gemini-3.5-flash",
        description="An agent that can research current events using Google Search.",
        instruction=(
            "You are a helpful research assistant. "
            "Your job is to answer the user's questions accurately. "
            "If the question is about a recent event, a specific person, or anything that might require up-to-date information, you MUST use the `google_search` tool. "
            "Do not rely on your own knowledge for topics that could have changed since your training."
        ),
        tools=[
            google_search
        ],
    )
    ```

    **Alternative (YAML approach):**

    Open the `root_agent.yaml` file and replace its contents with the following:

    ```yaml
    # yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
    name: researcher_agent
    model: gemini-3.5-flash
    description: An agent that can research current events using Google Search.
    instruction: |
      You are a helpful research assistant.
      Your job is to answer the user's questions accurately.
      If the question is about a recent event, a specific person, or anything that might require up-to-date information, you MUST use the `google_search` tool.
      Do not rely on your own knowledge for topics that could have changed since your training.
    tools:
      - name: google_search
    ```

### Step 3: Test Your New Agent

1.  **Navigate back to the parent directory:**
    ```shell
    cd ..
    ```

2.  **Start the web server:**

    From the `adk-training` directory, run `uv run adk web`.

    ```shell
    uv run adk web
    ```

3.  **Interact with the Researcher Agent:**
    *   Open the Dev UI in your browser.
    *   Select `researcher_agent` from the dropdown menu.
    *   Ask a question that the LLM wouldn't know from its training data:
        *   "Who won the last Super Bowl?"
        *   "What are the latest headlines about space exploration?"
    *   **Examine the Trace View:** Click on the "Trace" tab. Unlike a custom function tool, `google_search` is a **server-side grounding tool** — Gemini itself performs the search, so you won't see a separate `execute_tool` span for it. Instead, expand the `call_llm` (`generate_content`) span: its response payload includes `groundingMetadata` (with `web_search_queries` and grounding chunks/citations), which is your evidence that the model actually invoked Google Search while producing its answer. You can also confirm it from the final response itself, since grounded answers typically include inline citations or links back to source pages.

### Lab Summary

You have successfully given an agent a powerful new capability. You have learned how to:

*   Enable the necessary Google Cloud APIs for advanced features.
*   Configure an agent to use a built-in tool like `google_search` (using both Python and YAML approaches).
*   Write instructions that guide the agent on when to use its tools.
*   Verify that a tool was used by inspecting the Trace View in the Dev UI.

</SolutionVault>
