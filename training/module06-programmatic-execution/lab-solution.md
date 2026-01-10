---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 6 Solution: Programmatic Execution with the ADK Runner

## Goal

In this lab, you learned how to run an ADK agent programmatically from within a Python script, using the standard `Runner`. You imported and ran the **Haiku Poet agent** you built in Module 4.

This demonstrated the canonical way to execute an agent as part of a larger Python application, without using the `adk` command-line tools.

### Step 1: Prepare the Project

1.  **Navigate to your `adk-training` directory:**
    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Create the dedicated directory and script:**
    ```shell
    mkdir run_haiku_agent
    cd run_haiku_agent
    # Create run_haiku_agent.py inside this folder
    ```

### Step 2: Complete the `run_haiku_agent.py` Script

Here is the complete `run_haiku_agent.py` script:

```python
import asyncio
import sys
import os

# Add the parent directory to sys.path so we can import our agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import the root_agent from your haiku_poet_agent directory.
from haiku_poet_agent.agent import root_agent as haiku_agent

async def main():
    # Create a Session Service.
    session_service = InMemorySessionService()

    # Initialize the Runner, passing in the session service.
    runner = Runner(
        app_name="haiku_poet_agent",
        agent=haiku_agent,
        session_service=session_service
    )

    # Create a new session for your agent.
    session = await session_service.create_session(
        app_name="haiku_poet_agent",
        user_id="user123",
    )
    
    # Package your query.
    query_string = "A quiet morning with a cup of coffee."
    new_message = types.Content(
        parts=[types.Part(text=query_string)],
        role="user",
    )

    # Run the agent.
    # We pass the user_id and session_id (which the runner uses to fetch the session from the service)
    async for event in runner.run_async(
        user_id="user123", 
        session_id=session.id, 
        new_message=new_message
    ):
        # Print the text from the final agent response.
        if event.is_final_response():
            if event.content and event.content.parts:
                print(event.content.parts[0].text)

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 3: Run the Script

1.  **Ensure your virtual environment is active.**

2.  **Run the script from your `run_haiku_agent` directory:**
    ```shell
    python run_haiku_agent.py
    ```

### Step 4: Observe the Output

If your script is correct, you will see the haiku response printed directly to your console.

### Lab Summary

You have successfully run an agent programmatically using the standard `Runner`. This is the foundation for integrating your agent into any larger Python application.

### Self-Reflection Answers

1.  **Why is it important to decouple the `Runner` from the `SessionService`? What advantage does this give you in a production environment?**
    *   **Answer:** Decoupling `Runner` from `SessionService` promotes a modular architecture, making the `Runner` stateless and reusable across different session management strategies. In a production environment, this allows you to easily swap `InMemorySessionService` for persistent alternatives like `FirestoreSessionService` or custom implementations without modifying the core `Runner` logic. This flexibility is crucial for scaling, handling failures, and integrating with diverse backend systems where session state needs to be reliably stored and retrieved.

2.  **The `runner.run_async` method returns a stream of events. Why is this streaming approach useful in a real-world application compared to a function that just returns the final string?**
    *   **Answer:** The streaming approach of `runner.run_async` is highly beneficial in real-world applications for several reasons:
        *   **Real-time Feedback:** It allows for immediate partial responses (e.g., streaming LLM output word-by-word), improving the user experience by reducing perceived latency.
        *   **Progress Indicators:** Developers can use intermediate events (like tool calls or agent thoughts) to display progress indicators or provide more context to the user about what the agent is doing.
        *   **Handling Long-Running Tasks:** For agents performing complex or long-running tasks, streaming prevents the client from blocking indefinitely, allowing it to process information incrementally.

3.  **How would you modify this script to have a continuous conversation with the agent instead of just sending one message? (Hint: Think about loops and reusing the session object).**
    *   **Answer:** To have a continuous conversation, you would wrap the query and `runner.run_async` call within an asynchronous loop. Before each iteration, you would take new user input, and then reuse the same `session.id` to maintain context.

        ```python
        # ... (imports and main setup)
            while True:
                user_input = input("\n[User]: ")
                if user_input.lower() == "exit":
                    break

                new_message = types.Content(
                    parts=[types.Part(text=user_input)],
                    role="user",
                )

                print("[Agent]: ", end="")
                async for event in runner.run_async(
                    user_id="user123", 
                    session_id=session.id, 
                    new_message=new_message
                ):
                    if event.is_final_response():
                        if event.content and event.content.parts:
                            print(event.content.parts[0].text)
        ```
