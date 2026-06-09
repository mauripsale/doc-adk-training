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
3.  Use `uv add` to install the modern ADK and dotenv:
    ```bash
    uv add "google-adk>=2.1.0" python-dotenv
    ```
    Notice how `uv` automatically creates a virtual environment (`.venv`) and locks the dependencies in `uv.lock`.

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
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.apps import App
from google.adk.runners import InMemoryRunner

async def main():
    load_dotenv()
    
    print("🔍 Testing ADK 2.0 Environment...")

    try:
        # 1. Define a simple Node (Agent)
        agent = Agent(
            name="verify_agent",
            model="gemini-3.5-flash",
            instruction="Respond with: 'ADK 2.0 is Ready!'"
        )

        # 2. Create the App
        app = App(name="verify_app", root_agent=agent)

        # 3. Initialize the Runner
        runner = InMemoryRunner(app=app)

        # 4. Execute using the new run_debug helper
        print("🚀 Connecting to LLM...")
        events = await runner.run_debug("Hello!", user_id="test_user")
        
        # Verify the response
        ready = False
        for event in events:
            if event.is_final_response():
                print(f"✅ Agent Response: {event.content.parts[0].text}")
                ready = True
        
        if ready:
            print("\n🎉 SETUP COMPLETE! You are running ADK 2.0.")
        else:
            print("\n❌ Failed to get a final response from the agent.")

    except ImportError as e:
        print(f"❌ Version Error: {e}")
        print("Ensure you installed google-adk>=2.1.0")
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

### 💡 Troubleshooting: Model Not Found (404)

If you see an error like `Publisher Model ... gemini-3.5-flash was not found`, it usually means the specific model is not yet available in your chosen Google Cloud region (e.g., `us-central1`).

**The Fix:**
1.  Open your `.env` file.
2.  Change `GOOGLE_CLOUD_LOCATION` to a different supported region, such as `us-east4`, `us-west1`, or `europe-west9`.
3.  Run the verification script again.

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
