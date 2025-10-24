# Module 3: Your First Agent: The "Echo" Agent

## Lab 3: Build and Run the "Echo" Agent

### Goal

In this lab, you will build and run your first AI agent using the ADK. You will create a simple "Echo" agent that takes any text you provide and repeats it back to you. This will teach you the fundamental workflow of creating, configuring, and running an agent using the ADK's config-based approach.

### Prerequisites

*   You have successfully completed the setup in Module 2.
*   Your virtual environment from the previous lab is active. (You should see `(.venv)` in your terminal prompt).
*   You have authenticated with the gcloud CLI.

### Step 1: Create the Agent Project

We will use the `adk` command-line tool to create the file structure for our new agent.

1.  **Navigate to your training directory:**

    Make sure you are in the `adk-training` directory you created in the previous module.

    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Create the agent project:**

    Run the following command to create a new agent named `echo-agent`.

    ```shell
    adk create --type=config echo-agent
    ```

    This command creates a new directory named `echo-agent/` with two files inside: `root_agent.yaml` and `.env`.

### Step 2: Configure the Agent

Now, let's tell the agent how to behave and provide it with the necessary credentials.

1.  **Navigate into the agent directory:**

    ```shell
    cd echo-agent
    ```

2.  **Set up your API key:**

    Open the `.env` file in a text editor. This file is used to store secret information like API keys so you don't have to put them directly in your agent's configuration.

    *   **If you are using a Google AI Studio API Key:**
        Uncomment the `GOOGLE_API_KEY` line and paste your key. The file should look like this:
        ```
        GOOGLE_GENAI_USE_VERTEXAI=0
        GOOGLE_API_KEY=<your-google-gemini-api-key>
        ```
    *   **If you are using Google Cloud Vertex AI:**
        Uncomment the `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` lines and fill in your project details. The file should look like this:
        ```
        GOOGLE_GENAI_USE_VERTEXAI=1
        GOOGLE_CLOUD_PROJECT=<your_gcp_project>
        GOOGLE_CLOUD_LOCATION=us-central1
        ```

3.  **Define the agent's behavior:**

    Open the `root_agent.yaml` file. This is where you define your agent's identity and instructions.

    Replace the entire contents of the file with the following YAML configuration:

    ```yaml
    # yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
    name: echo_agent
    model: gemini-2.5-flash
    description: An agent that repeats the user's input.
    instruction: You are an echo agent. Your only job is to repeat the user's input back to them exactly as they wrote it. Do not add any extra words or explanations.
    ```

    This configuration tells the agent its name, which LLM to use (`gemini-2.5-flash`), and a very specific instruction: to only repeat the user's input.

### Step 3: Run the Agent

With the configuration complete, you can now bring your agent to life.

1.  **Start the ADK web server:**

    While inside the `echo-agent` directory, run the following command:

    ```shell
    adk web
    ```

    You should see output in your terminal indicating that a server has started, usually on `http://127.0.0.1:8080`.

2.  **Interact with your agent:**

    *   Open the URL (`http://127.0.0.1:8080`) in your web browser.
    *   You will see the ADK Developer UI.
    *   In the chat interface, type a message like "Hello, world!" and press Enter.
    *   The agent should respond with the exact same message: "Hello, world!".
    *   Try a few more messages to see it in action.

### Lab Summary

Fantastic! You have successfully built and interacted with your first AI agent. You have learned the core development loop:

1.  **Create:** Use `adk create` to scaffold a new agent project.
2.  **Configure:** Edit the `.env` file with credentials and the `root_agent.yaml` file with the agent's logic.
3.  **Run:** Use `adk web` to start the agent and interact with it through the Dev UI.

In the next module, you will take a closer look at the `LlmAgent` configuration to understand how to craft more sophisticated instructions.
