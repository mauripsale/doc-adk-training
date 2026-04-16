---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 2: Environment Setup Challenge

## Prerequisites
Before you begin, ensure you have the following tools ready:
*   **Code Editor (IDE):** You need a good environment to write your code. We recommend:
    *   [VS Code](https://code.visualstudio.com/) (Local)
    *   [Project IDX](https://idx.dev/) (Cloud-based)
    *   [Google Cloud Shell Editor](https://shell.cloud.google.com/) (Cloud-based)
*   **uv:** You must install the `uv` package manager. If you don't have it, install it via your terminal:
    *   macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
    *   Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Goal
Your task is to prepare your local machine for enterprise agent development using modern tools. Try to complete the steps below using your existing knowledge. If you get stuck, the `lab-solution.md` file provides a detailed, step-by-step walkthrough.

## Lab Tasks

### Step 0: Ensure Python 3.10+ (Crucial)
Before you start, you must ensure you are using a modern version of Python. The ADK **requires Python 3.10 or higher**. Using older versions (like 3.9) will result in numerous warnings and potential crashes.

Fortunately, `uv` makes this easy. Even if your system doesn't have Python 3.10, you can tell `uv` to install and use it for your project.

### Step 1: Create the Project Structure with `uv`
1.  Use `uv` to initialize a new Python project named `adk-training`. Use the `--python 3.10` flag to guarantee you meet the ADK's requirements:
    ```bash
    uv init adk-training --python 3.10
    ```
2.  Navigate into the `adk-training` directory.
3.  Use `uv add` to install the `google-adk` and `python-dotenv` packages. Notice how `uv` automatically creates a virtual environment (`.venv`) for you and locks the dependencies in `uv.lock`.

### Step 2: Configure Authentication

Create a file named `.env` in your `adk-training` directory. This file will securely store your authentication credentials. Choose **one** of the two options below.

**Option A: Use a Google AI Studio API Key (Recommended for Beginners)**
1.  Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Add the following line to your `.env` file:
    ```
    GOOGLE_API_KEY="YOUR_API_KEY"
    ```

**Option B: Use Vertex AI (Advanced)**
1.  Authenticate with the gcloud CLI: `gcloud auth application-default login`
2.  Add the following lines to your `.env` file, replacing the placeholder values with your Google Cloud project details:
    ```
    GOOGLE_GENAI_USE_VERTEXAI="1"
    GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    GOOGLE_CLOUD_LOCATION="us-central1"
    ```

### Step 3: Verification Script

Create a file named `verify_setup.py` and add the following content:

```python
# verify_setup.py
import asyncio
import os
import logging
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Suppress noisy ADK logs
logging.getLogger("google.adk").setLevel(logging.WARNING)

async def main():
    # Load environment variables from the .env file
    load_dotenv()

    try:
        print("✅ Google ADK is installed correctly.")
        print("Attempting to connect to the LLM service via an ADK agent...")

        # Define a simple ADK agent
        agent = LlmAgent(
            name="verify_agent",
            model="gemini-2.5-flash",
            instruction="You are a helpful assistant. Respond with a short confirmation."
        )

        # Use the ADK Runner to execute the agent
        runner = Runner(
            app_name="agents", # This must match the ADK's inferred app name
            agent=agent,
            session_service=InMemorySessionService()
        )
        session = await runner.session_service.create_session(
            app_name="agents", user_id="test_user"
        )
        message = types.Content(parts=[types.Part(text="hello")])

        # Stream the response from the agent
        final_response_text = "Agent did not produce a final response."
        async for event in runner.run_async(user_id="test_user", session_id=session.id, new_message=message):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response_text = event.content.parts[0].text
                elif event.actions and event.actions.escalate:
                    final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                break

        if final_response_text != "Agent did not produce a final response.":
            print("✅ Authentication successful: Connected to the LLM service via ADK agent.")
            print(f"ADK agent response: {final_response_text}")
        else:
            print("❌ Authentication failed: Could not connect to the LLM service via ADK agent.")

    except ImportError:
        print("❌ Installation error: The 'google-adk' package could not be found.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 4: Run the Verification

Execute the script using `uv run`. This command ensures that your script runs within the virtual environment that `uv` created, without you needing to manually activate it!

```bash
uv run python verify_setup.py
```

> **Note:** You might see a `UserWarning` regarding an `[EXPERIMENTAL]` feature (like `PLUGGABLE_AUTH`). You can safely ignore this; it is just the ADK informing you of its internal development state and does not affect your lab.

## Self-Reflection Questions
*   Why is `uv` considered a major upgrade over traditional tools like `pip` and `venv`?
*   What is the purpose of the `uv.lock` file generated in your project directory?
*   What are the security implications of storing API keys in a `.env` file versus hardcoding them in your script?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMDItZW52aXJvbm1lbnQtc2V0dXAvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module02-environment-setup/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
