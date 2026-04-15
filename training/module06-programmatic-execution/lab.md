---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 6: Programmatic Execution: Apps and Runners

## Goal

In this lab, you will move beyond the CLI and trigger your **"Support Analyzer"** agent from a Python script. You will learn how to wrap your agent in an `App` container and use an `InMemoryRunner` to handle multiple independent user sessions.

This will teach you the canonical way to execute an agent as part of a larger Python application (like a web server or a bot).

### Step 1: Prepare the Project

1.  **Navigate to your `adk-training/support_analyzer` directory:**
    ```shell
    cd /path/to/your/adk-training/support_analyzer
    ```

2.  **Create the execution script:**
    In the same directory as your `agent.py`, create a new Python file named `main.py`. This is where you will write the code to run your agent.

### Python Skeleton (`main.py`)
Complete the `main.py` script by following the conceptual comments below. Refer to the "Theory" section if you forget the class names or method signatures.

```python
import asyncio
import logging
from dotenv import load_dotenv

# Optional: Suppress noisy ADK/httpx logs for cleaner terminal output
logging.getLogger("google.adk").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# TODO: Step 1 - Bring in your "Intelligence" (the Agent) 
# and your "Infrastructure" components (App and InMemoryRunner).
# Remember: Agent is in agent.py, Apps/Runners are in google.adk.

load_dotenv()

# TODO: Step 2 - Build the "Office Building" (The App instance).
# Create an App container named "support_app" and move your Agent inside it.
app = ...

# TODO: Step 3 - Start the "Management System" (The Runner instance).
# Instantiate the single Runner that will manage all your user sessions.
# For local dev, the InMemory version is the easiest way to start.
runner = ...

async def main():
    print("--- User A (Alice) ---")
    # TODO: Step 4 - Process a message for Alice (Billing issue: "I was overcharged $50").
    # Use the convenient debug method to execute the message.
    # IMPORTANT: You must identify this session as "Alice".
    events_a = ...
    
    # TODO: Step 5 - Inspect the output.
    # The debug method returns a list of Events. 
    # Loop through them to find the one that marks the "final response" 
    # and print the content text to the console.
    # Hint: use `event.is_final_response()` and `event.content.parts[0].text`

    print("\n--- User B (Bob) ---")
    # TODO: Step 6 - Process a message for Bob (Technical issue: "My wifi is slow").
    # Use the SAME runner instance, but a DIFFERENT user_id to ensure 
    # their conversations don't leak into each other.
    ...

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 3: Run the Script

Once you have completed the script, you can execute it directly from your terminal.

1.  **Ensure your virtual environment is active.**

2.  **Run the script from your `support_analyzer` directory:**
    ```shell
    python main.py
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

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMDYtcHJvZ3JhbW1hdGljLWV4ZWN1dGlvbi9sYWItc29sdXRpb24=`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module06-programmatic-execution/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
