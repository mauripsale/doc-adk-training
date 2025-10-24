# Module 16: Real-time Interaction with Streaming

## Lab 16: Running a Basic Streaming Agent

### Goal

In this lab, you will set up and run a basic bidirectional streaming agent. While a full implementation of a custom voice application is beyond the scope of this introductory lab, you will learn how to enable streaming mode in the ADK and interact with a pre-configured agent using the Dev UI's audio features. This will give you a firsthand experience of the low-latency, interruptible nature of streaming conversations.

**Note:** This feature is currently experimental and best supported in Python.

### Prerequisites

*   A working microphone connected to your computer.
*   Your browser must have permission to access your microphone. You will likely be prompted for this when you first try to use the audio feature.

### Step 1: Create the Streaming Agent Project

1.  **Navigate to your training directory:**

    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Create the agent project:**

    ```shell
    adk create --type=config streaming-agent
    ```

3.  **Navigate into the new directory:**

    ```shell
    cd streaming-agent
    ```

### Step 2: Configure the Agent for Streaming

We will create a simple conversational agent. The key change is enabling the streaming mode in the configuration.

1.  **Set up your environment variables:**

    Open the `.env` file. Streaming requires a **Vertex AI** setup. Configure the file as follows:
    ```
    GOOGLE_GENAI_USE_VERTEXAI=1
    GOOGLE_CLOUD_PROJECT=<your_gcp_project>
    GOOGLE_CLOUD_LOCATION=us-central1
    ```

2.  **Update the `root_agent.yaml` file:**

    Replace the contents of `root_agent.yaml` with the following:

    ```yaml
    # yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
    name: streaming_conversational_agent
    model: gemini-1.5-flash
    description: A conversational agent that can chat in real-time.
    instruction: |
      You are a friendly and talkative assistant.
      Keep your answers concise and conversational.
      Your goal is to have a natural, flowing conversation with the user.
    
    # This is the key to enabling bidi-streaming mode.
    streaming: True
    ```
    The only new line here is `streaming: True`. This tells the ADK to initialize the agent and its underlying model in a mode that supports bidirectional streaming.

### Step 3: Test the Streaming Interaction

1.  **Start the web server:**

    From the `streaming-agent` directory, run `adk web`.

    ```shell
    adk web
    ```

2.  **Interact with the agent using your voice:**
    *   Open the Dev UI in your browser.
    *   You will see a microphone icon in the chat input box.
    *   **Click and hold the microphone icon.** Your browser will likely ask for permission to use your microphone. Click "Allow".
    *   While holding the icon, start speaking. For example, say: "Hello, can you tell me a fun fact about space?"
    *   Release the microphone icon when you are done speaking.
    *   **Observe the response:** The agent should start speaking its response back to you almost immediately. You will hear the audio output through your speakers.

3.  **Test Interruptibility:**
    *   This is the most important part of the experiment.
    *   Start a new conversation. Click and hold the microphone and ask a question that will have a longer answer, like: "Can you give me a brief summary of the plot of the first Star Wars movie?"
    *   As soon as the agent starts speaking its response, **click and hold the microphone icon again and start speaking over it.** For example, say: "Actually, stop. Tell me about The Empire Strikes Back instead."
    *   **Observe the agent's behavior:** The agent should immediately stop its current response and listen to your new request. It will then answer your second question.

### Lab Summary

Congratulations! You have experienced the power of bidirectional streaming. While you didn't build a custom voice front-end, you have learned the fundamental concepts and witnessed the key benefits.

You have learned to:
*   Enable bidirectional streaming for an ADK agent by setting `streaming: True` in its configuration.
*   Use the ADK Dev UI's built-in audio features to have a voice conversation with an agent.
*   Experience the low-latency and interruptible nature of a streaming-enabled agent.

This opens the door to building a new generation of AI applications that feel more natural and responsive than ever before. In the next module, you will learn how to systematically evaluate your agents to ensure they are performing correctly and meeting quality standards.
