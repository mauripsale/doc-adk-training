---
sidebar_position: 1
title: "Module 6: Programmatic Execution: Apps and Runners"
---

# Module 6: Programmatic Execution: Apps and Runners

## Theory

Until now, you've used the ADK CLI (`adk web`, `adk run`) to interact with your agents. While great for testing, real-world applications (like a Discord bot or a web backend) need to trigger agents programmatically from within Python code.

To do this, you need to understand the relationship between three core objects: the **Agent**, the **App**, and the **Runner**.

### The "Three Pillars" of ADK Architecture

Think of building an agentic application like setting up a smart office:

#### 1. The Agent: The Intelligence
The `Agent` (or `root_agent`) is the employee. It has instructions, a model, and (soon) tools. It's the "thinking" part of your application.
*   **Role:** Reasoning and task execution.
*   **Scope:** Specific to the agent's logic.

#### 2. The App: The Infrastructure
The `App` is the office building. It's a top-level container that holds the `root_agent` and manages global operational concerns.
*   **Role:** Configuration and lifecycle management.
*   **Key Responsibilities:** Managing global plugins, context caching, and resumability configurations. It separates operational infrastructure from the agent's logic.

#### 3. The Runner: The Motor
The `Runner` is the management system that actually makes things happen. It receives a message from a user and "runs" it through the App.
*   **Role:** Orchestration and session management.
*   **The Singleton Pattern:** In most applications, you create **one Runner instance** for your entire application. This single Runner is designed to handle multiple users and multiple sessions simultaneously.

### How the Runner Handles Multiple Users

A common point of confusion is: *"Do I need a new Runner for every user?"* **No.**

When you tell the Runner to execute a message, you must provide two unique identifiers:
1.  **`user_id`**: Identifies who is talking.
2.  **`session_id`**: Identifies the specific conversation thread.

```python
# The Runner uses these IDs to fetch the correct memory/state automatically
async for event in runner.run_async(
    user_id="alice_123", 
    session_id="chat_session_001", 
    new_message=message
):
    # Process events...
```

The Runner uses these IDs to look up the correct conversation history from its `SessionService`. This ensures that Alice's conversation never leaks into Bob's conversation, even though they are both being processed by the same Runner.

### Minimal Programmatic Setup

To run an agent from Python, your `main.py` typically follows this flow:

```python
import asyncio
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from agent import root_agent # Your agent from Module 04

# 1. Wrap the agent in an App
app = App(name="my_support_app", root_agent=root_agent)

# 2. Instantiate a Runner for that App
# InMemoryRunner is great for development as it handles 
# session storage in local memory.
runner = InMemoryRunner(app=app)

async def main():
    # 3. Execute!
    # Tip: run_debug() is a helper for simple testing in v1.18+
    # it wraps the complex async loop and returns a list of Event objects.
    events = await runner.run_debug("I have a billing problem.")
    for event in events:
        if event.is_final_response():
            print(f"Agent Response: {event.content.parts[0].text}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Key Takeaways
- **Agent**: Defines the persona and logic.
- **App**: A container for the agent and global configurations (Plugins, Caching).
- **Runner**: The execution engine. You typically use one Runner to serve many users.
- **Isolation**: The ADK ensures session isolation using `user_id` and `session_id`.
- **`run_debug()`**: A convenient method for quick programmatic testing without manually handling async event streams.
