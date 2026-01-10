---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 6: Programmatic Execution with the ADK Runner

## Goal

In this lab, you will learn how to run an ADK agent programmatically from within a Python script, using the standard `Runner`. Instead of creating a new agent, you will import and run the **Haiku Poet agent** you built in Module 4.

This will teach you the canonical way to execute an agent as part of a larger Python application, without using the `adk` command-line tools.

### Step 1: Prepare the Project

1.  **Navigate to your `adk-training` directory:**
    This is the root directory containing all your agents.
    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Create a dedicated directory for your script:**
    To keep your project clean, create a folder for this programmatic execution task.
    ```shell
    mkdir run_haiku_agent
    cd run_haiku_agent
    ```

3.  **Create the execution script:**
    Inside the `run_haiku_agent/` directory, create a new Python file named `run_haiku_agent.py`. This is where you will write the code to run your agent.

### Step 2: Complete the `run_haiku_agent.py` Script

You will now complete the script to programmatically run your `haiku_poet_agent`. Open `run_haiku_agent.py` and follow the `# TODO` comments.

```python
import asyncio
import sys
import os

# Add the parent directory to sys.path so we can import our agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import Session, InMemorySessionService
from google.genai import types

# TODO: Step 1 - Import your agent
# The ADK makes any agent in a subdirectory available as a Python module.
# Import the `root_agent` from your `haiku_poet_agent` directory.
# Example: from haiku_poet_agent import agent as haiku_agent_module

async def main():
    # TODO: Step 2 - Create a Session Service.
    # For this lab, we'll use a simple in-memory session store.
    # Instantiate `InMemorySessionService`.

    # TODO: Step 3 - Initialize the Runner.
    # Create an instance of the `Runner` class, passing the session_service you just created.

    # TODO: Step 4 - Create a new session for your agent.
    # Use the session_service's `create_session` method.
    # You need to provide the `app_name` (the folder name of your agent: "haiku_poet_agent") and a `user_id`.
    
    # TODO: Step 5 - Package your query.
    # Create a query string, for example: "A quiet morning with a cup of coffee."
    # Package this into a `types.Content` object.

    # TODO: Step 6 - Run the agent.
    # Call the `runner.run_async()` method. You will need to pass the
    # session object you created and the new message.

    # TODO: Step 7 - Print the final response.
    # The `run_async` method returns a stream of events. Loop through them
    # and print the `text` from the `Part` of the final agent response.
    # The final event will have `event.name == 'agent:response'`.

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 3: Run the Script

Once you have completed the script, you can execute it directly from your terminal.

1.  **Ensure your virtual environment is active.**

2.  **Run the script from your `run_haiku_agent` directory:**
    ```shell
    python run_haiku_agent.py
    ```

### Step 4: Observe the Output

If your script is correct, you will see the haiku response printed directly to your console. For the example query, it might look something like this:

```
Steam gently does rise,
The world outside is quiet,
Warm mug in my hands.
```

### Having Trouble?

If you get stuck, you can find the complete code in the `lab-solution.md` file.

### Lab Summary

You have successfully run an agent programmatically using the standard `Runner`. This is the foundation for integrating your agent into any larger Python application.

You have learned to:
*   Import an agent from a neighboring directory as a Python module.
*   Instantiate an `InMemorySessionService` to manage session state.
*   Instantiate the `Runner` and provide it with the necessary services.
*   Create a `Session` programmatically for a specific agent app.
*   Use `runner.run_async` to execute the agent and process the event stream to get the final response.

### Self-Reflection Questions
- Why is it important to decouple the `Runner` from the `SessionService`? What advantage does this give you in a production environment?
- The `runner.run_async` method returns a stream of events. Why is this streaming approach useful in a real-world application compared to a function that just returns the final string?
- How would you modify this script to have a continuous conversation with the agent instead of just sending one message? (Hint: Think about loops and reusing the session object).

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMDYtcHJvZ3JhbW1hdGljLWV4ZWN1dGlvbi9sYWItc29sdXRpb24=`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module06-programmatic-execution/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
