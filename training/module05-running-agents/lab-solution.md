---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 5 Solution: Exploring Different Execution Modes

## Goal

In this lab, you will learn how to run and interact with your "Haiku Poet" agent using the three primary execution modes provided by the ADK CLI: `adk web`, `adk run`, and `adk api_server`.

## Prerequisites

*   You have successfully completed Module 4.
*   You have the `haiku_poet_agent` configured in your `adk-training` directory.
*   Your virtual environment is active.

## Part 1: Interactive Development with `adk web`

This is the mode you've used so far. Let's explore its features more deeply.

1.  **Navigate to your project directory:**
    Make sure you are in your main `adk-training` directory.
    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Start the web UI:**
    Run the command from the parent directory. When run from the parent, the ADK will discover all agents in the subdirectories.
    ```shell
    adk web
    ```

3.  **Explore the Dev UI:**
    *   Open the UI in your browser (`http://127.0.0.1:8080`).
    *   Select `haiku_poet_agent` from the dropdown menu if it's not already selected.
    *   Have a short conversation with your poet agent.
    *   **Trace View:** On the right side of the screen, click on the "Trace" tab. You will see a waterfall diagram. Click on the `LlmAgent` step to expand it. Here you can see the full prompt sent to the Gemini model, including your detailed instruction and the user's message. This view is critical for debugging why an agent behaves a certain way.
    *   **State View:** Click the "State" tab. This view shows the agent's short-term memory for the current conversation. We will explore this more in later modules.

## Part 2: Headless Interaction with `adk run`

Now, let's chat with the agent directly in the terminal.

1.  **Stop the web server:**
    Go back to your terminal where `adk web` is running and press `Ctrl+C` to stop it.

2.  **Start the command-line runner:**
    Again, run this from the parent `adk-training` directory.
    ```shell
    adk run haiku_poet_agent
    ```

3.  **Chat with the agent:**
    *   You will see a prompt like `[user]:`.
    *   Type a message, for example: `I'm learning about AI agents.`
    *   The agent will respond directly in the terminal with a haiku.
    *   You can have a continuous conversation.
    *   To exit, press `Ctrl+C`.

## Part 3: Running as a Service with `adk api_server`

Finally, let's run the agent as a background service. This mode is the foundation for production deployments where your agent acts as a backend API for other applications.

1.  **Start the API server:**
    From the `adk-training` directory, run:
    ```shell
    adk api_server
    ```
    The server will start and listen for HTTP requests on `http://127.0.0.1:8000`.

2.  **Interact with the API (Step A: The Intentional Failure):**
    *   Open a **new, separate terminal window**.
    *   Try to send a message to the agent immediately using `curl`:
        ```bash
        curl -X POST http://127.0.0.1:8000/run_sse \
             -H "Content-Type: application/json" \
             -d '{
                   "app_name": "haiku_poet_agent",
                   "user_id": "test_user",
                   "session_id": "missing_session",
                   "new_message": {"role": "user", "parts": [{"text": "Hello"}]}
                 }'
        ```
    *   **The Result:** You will receive an error: `{"detail":"Session not found"}`.
    *   **The Explanation:** Unlike `adk web` or `adk run`, which handle session creation for you behind the scenes, the `api_server` is a raw interface. It requires an existing session to store the conversation state. If you try to talk to a session ID that hasn't been created yet, it will fail.

3.  **Create the Session (Step B: The Fix):**
    *   Before sending a message, you must explicitly create the session resource. Run this command:
        ```bash
        curl -X POST http://127.0.0.1:8000/apps/haiku_poet_agent/users/test_user/sessions/test_session
        ```
    *   **The Result:** You should receive `{"status": "ok"}`. This tells the server to allocate memory (or database space) for a conversation named `test_session`.

4.  **Send the Message (Step C: Success):**
    *   Now, run the message command again, ensuring the `session_id` matches the one you just created (`test_session`):
        ```bash
        curl -X POST http://127.0.0.1:8000/run_sse \
             -H "Content-Type: application/json" \
             -d '{
                   "app_name": "haiku_poet_agent",
                   "user_id": "test_user",
                   "session_id": "test_session",
                   "new_message": {"role": "user", "parts": [{"text": "A beautiful sunset"}]}
                 }'
        ```
    *   **The Result:** You will see a stream of JSON objects. Look for the events where `event.name == 'agent:response'` to find your haiku!

5.  **Stop the API server:**
    Go back to the first terminal and press `Ctrl+C`.

### Self-Reflection Answers

1.  **In what scenarios would the detailed "Trace View" in `adk web` be more useful than the simple chat interface of `adk run`?**
    *   **Answer:** The "Trace View" in `adk web` is invaluable for debugging complex agent behaviors. It allows developers to see the exact sequence of events, including LLM calls, tool executions, and state changes. This is crucial when an agent isn't behaving as expected, as it provides a granular understanding of its internal reasoning process. In contrast, `adk run` is better for quick, high-level testing of an agent's output.

2.  **The `curl` command in the `adk api_server` section is a simple example of a programmatic client. What kind of real-world applications could you build that would interact with your agent's API in this way?**
    *   **Answer:** Programmatic interaction with `adk api_server` enables a wide range of real-world applications, such as:
        *   **Chatbots/Virtual Assistants:** Integrating the agent into a custom web or mobile application.
        *   **Automated Workflows:** Triggering agent actions from other systems (e.g., a CRM, an email client).
        *   **Backend Services:** Using the agent as a component within a larger microservice architecture.
        *   **Data Processing:** Feeding structured data to the agent for analysis or transformation.

3.  **Why is it necessary to run the `adk api_server` and the `curl` command in two separate terminal windows? What does this separation represent in a real-world application architecture?**
    *   **Answer:** Running `adk api_server` and `curl` in separate terminal windows is necessary because `adk api_server` starts a long-running process that occupies the terminal. The `curl` command then acts as a client, sending requests to this running server. This separation represents a fundamental architectural pattern: **client-server architecture**. In a real-world application, the `adk api_server` would be deployed as a backend service (e.g., on Cloud Run), and the `curl` command would be analogous to a separate client application (e.g., a web frontend, a mobile app, or another backend service) making API calls to that deployed service.

### Lab Summary

You have now mastered the three ways to run an ADK agent:

*   `adk web`: For interactive development and deep debugging with the Trace View.
*   `adk run <agent_name>`: For quick tests and automated scripting in the terminal.
*   `adk api_server`: For running your agent as a service to be integrated with other applications.

This completes the foundational part of the course. You are now ready to start extending your agent's capabilities with tools.

