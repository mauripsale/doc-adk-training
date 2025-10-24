# Module 21: Programmatic Execution

## Theory

### Beyond the ADK CLI

The `adk web`, `adk run`, and `adk api_server` commands are incredibly convenient wrappers that handle a lot of boilerplate setup for you. They automatically discover your agents, set up a session service, and manage the application lifecycle. This is ideal for rapid development and standard deployments.

However, there are many scenarios where you need more control. You might want to:
*   Integrate an ADK agent into a larger, existing application (e.g., a Flask or Django web server).
*   Use a custom implementation for the session service (e.g., storing session data in a Redis or a different SQL database).
*   Have fine-grained control over the execution loop, perhaps to add custom logging, metrics, or pre-processing logic before the agent runs.

For these cases, you need to move beyond the CLI and interact directly with the core components of the ADK runtime. This is known as **programmatic execution**.

### The Core Runtime Components

At the heart of the ADK's runtime are two fundamental classes: the `SessionService` and the `Runner`.

#### 1. **The `SessionService`**
The `SessionService` is the **memory management** layer of your application. Its job is to create, retrieve, update, and persist conversation sessions.

*   **`create_session(...)`:** Creates a new, empty session for a given user.
*   **`get_session(...)`:** Retrieves an existing session.
*   **`append_event(...)`:** This is the most important method. It adds a new event (like a user message or a tool response) to a session's history and, crucially, **updates the session's state**.

The ADK provides a simple, default implementation called `InMemorySessionService`, which is what `adk web` uses. It's fast and easy for local development, but as its name implies, it loses all data when the application restarts. For production, you would use or create a persistent implementation.

#### 2. **The `Runner`**
The `Runner` is the **execution engine**. It's the component that actually "runs" the agent. It orchestrates the entire process of taking a user's message, passing it to the agent, handling the back-and-forth with the LLM and tools, and generating the final stream of events.

When you initialize a `Runner`, you need to provide it with two key things:
*   The `root_agent` of your application.
*   An instance of a `SessionService` to handle the memory.

The primary method of the `Runner` is `run_async(...)`. You give it the user's ID, the session ID, and the new message, and it returns an asynchronous generator that yields the `Event` objects as they are produced by the agent's execution.

### The Programmatic Execution Flow

When you run an agent programmatically, you are essentially recreating the logic that the `adk` commands handle for you. The flow looks like this:

1.  **Initialization:**
    *   Import your `root_agent`.
    *   Instantiate a `SessionService` (e.g., `InMemorySessionService`).
    *   Instantiate a `Runner`, passing it your agent and the session service.

2.  **Execution Loop (for each user request):**
    *   Get the user's ID, session ID, and message content.
    *   Use the `SessionService` to either `create_session` (for a new conversation) or `get_session` (for an existing one).
    *   Call the `runner.run_async(...)` method with the session details and the new message.
    *   Iterate through the events yielded by the runner to process the agent's response (e.g., print the final text, handle tool calls).

By taking control of this flow, you gain the ultimate flexibility to integrate the power of the ADK into any application architecture you can imagine. In the lab, you will write a Python script that implements this exact flow.
