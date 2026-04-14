---
sidebar_position: 3
title: "Lab Solution"
---

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
app = App(name="support_app", root_agent=root_agent)

# 2. Initialize the Runner.
# We use InMemoryRunner which automatically sets up session management.
runner = InMemoryRunner(app=app)

async def main():
    print("--- User A (Alice) ---")
    # 3. Run for Alice (Billing Issue)
    # The runner uses the user_id to isolate this conversation.
    # run_debug automatically prints the agent response to the terminal.
    events_a = await runner.run_debug("I was overcharged $50.", user_id="Alice")
    
    # Optional: If you need to access the text in code, iterate through events:
    for event in events_a:
        if event.is_final_response():
            print(f"DEBUG: Alice's JSON: {event.content.parts[0].text}")

    print("\n--- User B (Bob) ---")
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
