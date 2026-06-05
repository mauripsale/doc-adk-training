---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 3 Solution: Build and Run the "Echo" Agent

## Goal

### Overview

Build your first AI agent with the Google Agent Development Kit (ADK). In this lab, you'll create a "Parrot" agent. Its only purpose is to take any text you provide and repeat it back to you exactly, without answering questions or adding any commentary.

### Expected Behavior
*   **User:** "What time is it?" -> **Agent:** "What time is it?"
*   **User:** "Help me with my homework." -> **Agent:** "Help me with my homework."

### Prerequisites

*   You have successfully completed the setup in Module 2.
*   Your virtual environment is active.
*   You have authenticated with the gcloud CLI.
*   A Google API key from [Google AI Studio](https://aistudio.google.com/app/apikey) or a configured Google Cloud project.

### Core Concepts

*   **Agent:** An AI assistant powered by a Large Language Model (LLM). It's a blueprint defining the agent's purpose (instructions), its model (e.g., Gemini), and its capabilities.
*   **`adk` CLI:** A command-line tool for creating and managing ADK projects.
*   **Dev UI:** An interactive web interface for testing and debugging your agents.

### Step 1: Create the Agent Project

We will use the `adk` command-line tool to create the file structure for our new agent.

1.  **Navigate to your training directory:**
    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Create the agent project:**
    Run the following command to create a new agent named `echo_agent`. This defaults to the Python-based approach.
    ```shell
    adk create echo_agent
    ```
    This command creates a new directory named `echo_agent/` with an `agent.py` file and a `.env` file inside.

### Step 2: Configure the Agent

Now, let's tell the agent how to behave and provide it with the necessary credentials.

1.  **Set up your API key:**
    Open the `.env` file. This file stores secret information like API keys.

    *   **For Google AI Studio API Key:**
        You can get a free API key from the [Google AI Studio](https://aistudio.google.com/app/apikey).
        ```
        GOOGLE_API_KEY=<your-google-gemini-api-key>
        ```
    *   **For Google Cloud Vertex AI:**
        ```
        GOOGLE_GENAI_USE_VERTEXAI=1
        GOOGLE_CLOUD_PROJECT=<your_gcp_project>
        GOOGLE_CLOUD_LOCATION=us-central1
        ```

2.  **Define the agent's behavior (Python method):**
    Open `agent.py` and replace its contents with this:

    ```python
    from google.adk.agents import LlmAgent

    # IMPORTANT: The ADK requires this main agent variable
    # to be named exactly `root_agent`.
    root_agent = LlmAgent(
        name="echo_agent",
        model="gemini-3.5-flash",
        description="A parrot agent that only repeats user input.",
        instruction="You are a parrot. Your ONLY job is to repeat the user's input back to them exactly as they wrote it. DO NOT answer questions. DO NOT provide help. DO NOT add extra words. If the user asks a question, repeat the question back to them."
    )
    ```

### Alternative: Defining the Agent in YAML

Instead of Python, you can define your agent in a YAML file. This is simpler for basic agents but less flexible.

1.  **Create the agent with the `--type=config` flag:**
    ```shell
    adk create --type=config echo_agent
    ```
    This creates a `root_agent.yaml` file instead of `agent.py`.

2.  **Define the agent's behavior in `root_agent.yaml`:**
    Open `root_agent.yaml` and replace its contents with this:

    ```yaml
    # The first line is an optional schema definition that provides
    # auto-completion and validation in compatible code editors.
    # yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
    name: echo_agent
    model: gemini-3.5-flash
    description: An agent that repeats the user's input.
    instruction: You are an echo agent. Your only job is to repeat the user's input back to them exactly as they wrote it. Do not add any extra words or explanations.
    ```
    > **Note:** If both `agent.py` and `root_agent.yaml` exist, the ADK will use the `root_agent.yaml` file.

### Step 3: Run the Agent

1.  **Start the ADK web server:**
    From the parent `adk-training` directory, run:
    ```shell
    adk web
    ```
    You should see output indicating a server has started on `http://127.0.0.1:8080`.

2.  **Interact with your agent:**
    *   Open the URL in your web browser.
    *   In the chat interface, type "Hello, world!".
    *   The agent should respond with the exact same message: "Hello, world!".

### Understanding What's Happening

When you send a message:
1.  **Runner** receives your input and retrieves (or creates) your **Session**.
2.  **App** provides the **Agent** node to the runner.
3.  **ADK** packages your message with the agent's instructions and session history.
4.  **Gemini LLM** generates a response.
5.  **Runner** saves the response to the session state and returns it to you.

**Use the Trace tab** in the Dev UI to see this flow in detail!

### Key Takeaways

✅ **`adk create`** is the starting point for all agents.
✅ Agent behavior is defined by its **`instruction`**.
✅ **`.env`** keeps your API keys safe and out of code.
✅ You can define agents in **Python** (flexible) or **YAML** (simple).
✅ **`adk web`** is your primary tool for testing and debugging.

### Common Issues & Solutions

*   **Problem**: "Agent not found" or errors on startup.
    *   **Solution**: Make sure you are running `adk web` from the *parent directory* of `echo_agent`.
*   **Problem**: "Authentication error".
    *   **Solution**: Double-check that your `.env` file is correctly configured with your API key or GCP project.
*   **Problem**: If using `agent.py`, "root_agent not found".
    *   **Solution**: Ensure your agent variable is named **exactly** `root_agent`.

### Lab Summary

Fantastic! You have successfully built and interacted with your first AI agent. You have learned the core development loop: Create, Configure, and Run.

In the next modules, you will learn how to give your agents more sophisticated instructions and powerful new capabilities.

### Self-Reflection Answers
- **Advantages of Python over YAML:** Python allows you to add dynamic logic, load complex tools, use advanced environment variable integration, and define custom agents by inheriting from `BaseAgent`. YAML is excellent for rapid prototyping and strictly instruction-based agents without complex orchestration.
- **Importance of `.env` files:** It protects sensitive credentials (API keys) from being accidentally committed to version control systems like GitHub. It also makes it easier to swap credentials across different environments (dev, staging, production) without changing the source code.
- **Using the "Events" tab:** The Events tab provides a detailed trace of the interaction between the ADK and the LLM. It shows the raw system instructions, the chat history, and any tool calls or errors. This is invaluable for debugging more complex agents to see exactly why a model might be behaving unexpectedly or failing to call a tool.
