---
sidebar_position: 2
title: "Challenge Lab"
---

import { ChainSetup } from '../_chain-setup-snippet.mdx';

# Lab 6: Programmatic Execution: Apps and Runners

## Goal

In this lab, you will move beyond the CLI and trigger your **"Support Analyzer"** agent from a Python script. You will learn how to wrap your agent in an `App` container and use an `InMemoryRunner` to handle multiple independent user sessions.

This will teach you the canonical way to execute an agent as part of a larger Python application (like a web server or a bot).

### Step 1: Prepare the Project

<ChainSetup module={4} project="support_analyzer" />

1.  **Navigate to your `adk-training/support_analyzer` directory:**
    ```shell
    cd /path/to/your/adk-training/support_analyzer
    ```

2.  **Create the execution script:**
    In the same directory as your `agent.py`, create a new Python file named `main.py`. This is where you will write the code to run your agent.

### Python Skeleton (`main.py`)
Complete the `main.py` script by following the comments.

```python
import asyncio
import logging
from dotenv import load_dotenv

# --- Step 1: ADK Imports ---
# TODO: Import App from google.adk.apps
# TODO: Import InMemoryRunner from google.adk.runners
# TODO: Import root_agent from agent.py
from ... import ...

# Optional: Suppress noisy ADK/httpx logs
logging.getLogger("google.adk").setLevel(logging.WARNING)

load_dotenv()

# --- Step 2: Infrastructure Setup ---
# TODO: 1. Create the App instance named "support_app".
app = ...

# TODO: 2. Create the Runner instance using the app.
runner = ...

async def main():
    print("--- User A (Alice) ---")
    # --- Step 3: Run for Alice ---
    # TODO: Use the runner's debug method to send Alice's billing issue: 
    # "I was overcharged $50". Don't forget the user_id!
    events_a = ...
    
    # --- Step 4: Process Events ---
    # TODO: Loop through events_a and find the final response.
    # Hint: use event.is_final_response()
    for event in events_a:
        ...

    print("\n--- User B (Bob) ---")
    # --- Step 5: Run for Bob ---
    # TODO: Use the SAME runner instance to send Bob's technical issue:
    # "My wifi is slow". Use a different user_id.
    ...

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 3: Run the Script

Once you have completed the script, you can execute it using `uv run`.

1.  **Run the script from your `support_analyzer` directory:**
    ```shell
    uv run python main.py
    ```

### Step 4: Observe the Output

If your script is correct, you will see two distinct interactions printed to your console—one for Alice's billing issue and one for Bob's technical issue. Observe how the same Runner managed both interactions correctly using their `user_id`.

### Lab Summary

You have successfully run an agent programmatically using the modern **App and Runner** architecture. This is the foundation for integrating your agent into any larger Python application.

You have learned to:
*   Wrap an agent in an **`App`** to manage infrastructure concerns.
*   Instantiate an **`InMemoryRunner`** for easy local development.
*   Use **`run_debug()`** to quickly execute agents and see their output.
*   Use **`user_id`** to ensure that different users' conversations are isolated from one another.

### Self-Reflection Questions
- Why is the `App` class considered "infrastructure" while the `Agent` is considered "intelligence"?
- What would happen if you didn't provide a `user_id` to the runner (or provided the same one for both Alice and Bob)?
- In a production web server (like FastAPI), where would you put the code to instantiate the `Runner`? Would you put it inside the request handler function or as a global variable? Why?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="06">

# Lab 6 Solution: Programmatic Execution: Apps and Runners

## Goal

In this lab, you learned how to run an ADK agent programmatically from within a Python script using the modern `App` and `Runner` architecture. You wrapped the **Support Analyzer** agent (from Module 4) in an `App` and executed it for two different users to demonstrate session isolation.

### `support_analyzer/main.py`

Here is the complete `main.py` script:

```python
import asyncio
from dotenv import load_dotenv
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from agent import root_agent

load_dotenv()

# 1. Create the App container.
# This separates infrastructure (App) from intelligence (Agent).
# In ADK 2.0, root_agent is passed as a named argument.
app = App(name="support_app", root_agent=root_agent)

# 2. Initialize the Runner.
# We pass the 'app' instance to the Runner.
runner = InMemoryRunner(app=app)

async def main():
    print("--- User A (Alice) ---")
    # 3. Run for Alice (Billing Issue)
    # run_debug automatically prints the agent response to the terminal.
    events_a = await runner.run_debug("I was overcharged $50.", user_id="Alice")
    
    # Optional: If you need to access the text in code, iterate through events:
    for event in events_a:
        if event.is_final_response():
            print(f"DEBUG: Alice's JSON: {event.content.parts[0].text}")

    print("
--- User B (Bob) ---")
    # 4. Run for Bob (Technical Issue)
    # Even with the same Runner, Bob's state is separate from Alice's.
    await runner.run_debug("My wifi is not working.", user_id="Bob")

if __name__ == "__main__":
    asyncio.run(main())
```

### Key Components Explained

1.  **`App`**: This is the container for your agent. In a production app, this is where you would register global plugins (like for logging or monitoring) or configure context caching. It represents the "Building" the agent lives in.
2.  **`InMemoryRunner`**: This is the engine that executes the code. It's "In-Memory" because it stores all the conversation history (sessions) in the computer's RAM. If you restart the script, the history is lost. For production, you would use a `Runner` connected to a database.
3.  **`user_id`**: This is the most important parameter for multi-user apps. By passing `"Alice"` or `"Bob"`, the Runner knows which specific "drawer" of memory to open.
4.  **`run_debug()`**: A high-level helper that simplifies execution by handling the async event stream and automatically printing responses. It returns a **list of `Event` objects**.

### Self-Reflection Answers

1.  **Why is the `App` class considered "infrastructure" while the `Agent` is considered "intelligence"?**
    *   **Answer:** The `Agent` contains the prompt, the model choice, and the logical rules (the "Employee"). The `App` contains the operational settings like which database to use, which plugins are active, and the name of the overall service (the "Office"). This separation allows you to use the same Agent logic in different Apps.

2.  **What would happen if you didn't provide a `user_id` to the runner (or provided the same one for both Alice and Bob)?**
    *   **Answer:** If you use the same `user_id` (or leave it as the default), the Runner will treat both messages as part of the **same conversation**. Alice's billing problem and Bob's technical problem would be mixed together in the chat history, likely confusing the LLM.

3.  **In a production web server (like FastAPI), where would you put the code to instantiate the `Runner`?**
    *   **Answer:** You should instantiate the `Runner` as a **global variable** (or a singleton) at the start of your application. You should **not** create a new Runner inside every request handler, as that would be inefficient and you would lose the benefit of internal session management.

### Lab Summary

You have now moved from testing agents in a UI to controlling them with code. This is the first step toward building real-world, scalable agentic applications.

</SolutionVault>
