# Module 5: Running and Interacting with Agents

## Theory

### Bringing Your Agent to Life

Creating an agent configuration is the first step, but to test and use your agent, you need to run it. The ADK provides a powerful and flexible command-line interface (CLI) that offers several ways to run your agent, each suited for different stages of the development lifecycle.

Understanding these different execution modes is key to efficiently developing, debugging, and eventually deploying your agents.

### 1. Interactive Development: `adk web`

The `adk web` command is your primary tool during development. It starts a local web server that hosts the **ADK Developer UI**.

**Key Features:**

*   **Chat Interface:** Provides a user-friendly chat window to interact with your agent in real-time.
*   **Trace View:** This is the most powerful feature. It gives you a detailed, step-by-step visualization of your agent's execution flow. You can see the exact prompts sent to the LLM, which tools were called with which arguments, the data returned by the tools, and any changes to the agent's internal state. This is invaluable for debugging.
*   **Session Management:** The UI allows you to manage different conversation sessions, so you can test how your agent behaves over multiple interactions.
*   **No Code Changes Needed:** You can test and iterate on your `root_agent.yaml` configuration without restarting the server. Simply save your changes, and the UI will use the updated configuration for the next conversation.

The Dev UI is the best way to get immediate feedback and deep insight into your agent's reasoning process.

### 2. Headless Interaction: `adk run`

The `adk run` command allows you to interact with your agent directly from your terminal, without a graphical user interface.

**Key Features:**

*   **Command-Line Chat:** It drops you into a simple, text-based chat session with your agent.
*   **Quick Testing:** It's a fast way to test a specific input or a simple conversation without the overhead of launching a web browser.
*   **Scripting and Automation:** Because it runs in the terminal, `adk run` can be used in automated testing scripts. You can pipe input to it and check the output to verify the agent's behavior.

This mode is ideal for quick checks and for integrating agent tests into a continuous integration (CI) pipeline.

### 3. Deployment and Integration: `adk api_server`

The `adk api_server` command runs your agent as a standalone HTTP server, exposing its functionality through a RESTful API.

**Key Features:**

*   **API Endpoints:** It creates standard API endpoints (e.g., `/run_sse`, `/list-apps`) that allow other applications to communicate with your agent programmatically.
*   **Decoupled Architecture:** This is how you would typically run your agent in a production or staging environment. Your user-facing application (e.g., a web app, a mobile app) would make HTTP requests to this agent server.
*   **Scalability:** Running the agent as an API server allows it to be containerized (e.g., with Docker) and deployed to scalable infrastructure like Cloud Run or Google Kubernetes Engine.

This mode is essential for moving your agent from a local development tool to a component that can be integrated into a larger system.

In the lab for this module, you will get hands-on experience with all three of these commands, giving you a complete toolkit for running and interacting with your agents.
