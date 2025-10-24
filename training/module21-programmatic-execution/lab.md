# Module 21: Programmatic Execution

## Lab 21: Running an Agent with a Python Script

### Goal

In this lab, you will learn how to run an ADK agent programmatically using a Python script, without relying on the `adk` command-line tool. You will create a `main.py` file that initializes the `Runner` and `SessionService` to run the "Echo" agent you built in Module 3.

### Step 1: Prepare the Agent Project

We will use the simple, config-based "Echo" agent for this lab.

1.  **Navigate to your training directory:**

    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Copy the Echo Agent project:**
    Let's make a fresh copy to work with.

    ```shell
    cp -r module03-first-agent-echo/echo-agent/ programmatic-echo-agent/
    cd programmatic-echo-agent/
    ```
    *Note: We are copying the inner `echo-agent` directory.*

3.  **Ensure the agent is defined in Python:**
    The `Runner` needs a Python object to work with. We'll convert the YAML agent to a Python definition.
    *   Delete the `root_agent.yaml` file.
    *   Create a new file named `agent.py` and add the following code:
        ```python
        from google.adk.agents import LlmAgent

        root_agent = LlmAgent(
            name="echo_agent",
            model="gemini-1.5-flash",
            description="An agent that repeats the user's input.",
            instruction="You are an echo agent. Your only job is to repeat the user's input back to them exactly as they wrote it. Do not add any extra words or explanations."
        )
        ```

### Step 2: Create the Main Execution Script

This script will be the entry point for our application. It will set up and run the ADK components.

1.  **Create a `main.py` file:**
    In the `programmatic-echo-agent` directory, create a file named `main.py`.

2.  **Add the following code to `main.py`:**

    ```python
    import asyncio
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai.types import Content, Part

    # 1. Import your agent from the agent.py file
    from agent import root_agent

    # --- Configuration ---
    APP_NAME = "programmatic_echo_app"
    USER_ID = "test_user_123"
    SESSION_ID = "session_abc_789"

    async def main():
        """
        This function sets up the ADK runtime and runs the agent.
        """
        print("-- Initializing ADK Runtime --")
        
        # 2. Instantiate the SessionService
        # For this lab, we use the simple in-memory service.
        session_service = InMemorySessionService()

        # 3. Instantiate the Runner
        # Provide the root agent and the session service.
        runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

        # 4. Create a session for our conversation
        # This is equivalent to starting a new chat in the Dev UI.
        await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )
        print(f"Session '{SESSION_ID}' created for user '{USER_ID}'.")

        # --- Main Interaction Loop ---
        print("\n--- Starting Interaction (type 'quit' to exit) ---")
        while True:
            # 5. Get user input from the command line
            user_input = input("[User]: ")
            if user_input.lower() == 'quit':
                break

            # 6. Prepare the user's message in the ADK format
            user_message = Content(role="user", parts=[Part.from_text(user_input)])

            # 7. Run the agent
            # The runner.run_async method returns an async generator that yields events.
            final_response = ""
            async for event in runner.run_async(
                user_id=USER_ID, session_id=SESSION_ID, new_message=user_message
            ):
                # 8. Process the events to find the final response
                if event.is_final_response() and event.content:
                    final_response = event.content.parts[0].text.strip()
            
            print(f"[Agent]: {final_response}")

        print("\n--- Interaction ended ---")


    if __name__ == "__main__":
        # Use asyncio.run() to execute our async main function.
        asyncio.run(main())

    ```

### Step 3: Run the Script

1.  **Ensure your environment is set up:**
    *   Make sure your virtual environment is active.
    *   Make sure your `.env` file is correctly configured with your API key or Vertex AI project.

2.  **Run the Python script:**
    Instead of using `adk run`, you will now directly execute your `main.py` script.

    ```shell
    python main.py
    ```

3.  **Interact with the agent:**
    *   You will see the "Initializing..." and "Session created..." messages.
    *   The script will then wait for your input at the `[User]:` prompt.
    *   Type a message, like "Hello from my custom script!", and press Enter.
    *   The agent should respond with the same message.
    *   You can continue the conversation. Type `quit` to exit the program.

### Lab Summary

You have successfully taken full control of the ADK runtime! You've built a standalone Python application that can run an ADK agent without relying on the `adk` command-line wrappers.

You have learned to:
*   Import a defined `root_agent` into an application script.
*   Instantiate a `SessionService` to manage conversation memory.
*   Instantiate the `Runner` to act as the execution engine.
*   Create a `Session` programmatically.
*   Call the `runner.run_async` method to execute the agent.
*   Process the stream of `Event` objects returned by the runner to get the final response.

This programmatic approach is the foundation for integrating ADK agents into any larger application, giving you the ultimate flexibility and control.
