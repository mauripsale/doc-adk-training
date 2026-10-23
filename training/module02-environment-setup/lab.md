---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 02: Setting Up Your Environment (ADK 2.0) — 🧪 Challenge Lab"
---

# Lab 2: Environment Setup Challenge

## Prerequisites
Before you begin, ensure you have the following tools ready:
*   **Code Editor (IDE):** You need a good environment to write your code. We recommend:
    *   [VS Code](https://code.visualstudio.com/) (Local)
    *   [Project IDX](https://idx.dev/) (Cloud-based)
    *   [Google Cloud Shell Editor](https://shell.cloud.google.com/) (Cloud-based)
*   **Environment Choice (Pick one - see README for full step-by-step guides):**
    *   **Option A — 1-Click Cloud Workspace (Zero Setup):**
        *   [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/mauripsale/doc-adk-training?quickstart=1)
        *   [![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https://github.com/mauripsale/doc-adk-training.git)
    *   **Option B — VS Code Dev Containers (Local Docker):** Open the repo in VS Code with Docker Desktop running and click **"Reopen in Container"**.
    *   **Option C — Standard Local Setup (`uv` on Host OS):** Install `uv` via terminal:
        *   macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
        *   Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Goal
Your task is to prepare your environment for enterprise agent development using modern tools. Try to complete the steps below using your existing knowledge. If you get stuck, the `lab-solution.md` file provides a detailed, step-by-step walkthrough.

## Lab Tasks

### Step 0: Ensure Python 3.10+ (Crucial)
Before you start, you must ensure you are using a modern version of Python. The ADK **requires Python 3.10 or higher**. Using older versions (like 3.9) will result in numerous warnings and potential crashes.

Fortunately, `uv` makes this easy. Even if your system doesn't have Python 3.10, you can tell `uv` to install and use it for your project. (If you are using Codespaces or DevContainer, Python 3.11 is already the active default).

### Step 1: Create the Project Structure with `uv`
1.  Use `uv` to initialize a new Python project named `adk-training`. Use the `--python 3.10` flag to guarantee you meet the ADK's requirements:
    ```bash
    uv init adk-training --python 3.10
    ```
    *(Note: Run this in your terminal — whether on your local host or inside the DevContainer/Codespaces terminal)*.
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

**Option B: Use Agent Platform (Advanced)**
1.  Authenticate with the gcloud CLI: `gcloud auth application-default login`
2.  Add the following lines to your `.env` file, replacing the placeholder values with your Google Cloud project details:
    ```
    GOOGLE_GENAI_USE_VERTEXAI="1"
    GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    GOOGLE_CLOUD_LOCATION="us-central1"
    ```

> **Note on `adk create` and `.env` variables:** Later modules use `uv run adk create <name>` to scaffold a project. That command is an **interactive wizard** — it will prompt you for choices like the model, backend, GCP project, and region, so don't be surprised when it asks questions instead of just running silently. Also, the `.env` file it auto-generates may show `GOOGLE_GENAI_USE_ENTERPRISE=1` instead of the `GOOGLE_GENAI_USE_VERTEXAI=1` used in this lab's examples. Both variables are real and fully supported — they are functionally equivalent ways of telling the ADK to use Vertex AI/Agent Platform. If you see `GOOGLE_GENAI_USE_ENTERPRISE=1` in a generated `.env` file, that's fine; there's no need to "fix" it to match the `GOOGLE_GENAI_USE_VERTEXAI=1` shown elsewhere in the docs.

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
4.  If switching regions doesn't resolve it, the model may simply not be enabled/allowlisted for your specific GCP project at all. Check the Vertex AI Model Garden in your project, or contact your project admin to confirm access.

> **Note:** You might see a `UserWarning` regarding an `[EXPERIMENTAL]` feature (like `PLUGGABLE_AUTH`). You can safely ignore this; it is just the ADK informing you of its internal development state and does not affect your lab.

## Self-Reflection Questions
*   Why is `uv` considered a major upgrade over traditional tools like `pip` and `venv`?
*   What is the purpose of the `uv.lock` file generated in your project directory?
*   What are the security implications of storing API keys in a `.env` file versus hardcoding them in your script?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="02">

# Lab Solution: Environment Setup

This guide walks you through verifying and troubleshooting your environment setup.

## Step 1: Verify Prerequisites

First, ensure you have the right tools installed.

### IDE (Code Editor)
Make sure you have an IDE installed and open.
*   **VS Code:** Recommended for local development.
*   **Project IDX:** Excellent cloud-based alternative.
*   **Cloud Shell Editor:** Built into Google Cloud.

### Check uv
```bash
uv --version
```
**Requirement:** You must see the `uv` version printed. If not, follow the installation instructions in the lab challenge. `uv` handles Python installation automatically, so you no longer need to worry about checking your Python version manually! *(Note: If you are using the DevContainer / GitHub Codespaces environment, `uv` and Python 3.11 are already pre-installed and available).*


## Step 2: Create the Project Structure

Using `uv` makes project initialization incredibly fast and simple.

1.  **Initialize Project with Python 3.10+:**
    ```bash
    uv init adk-training --python 3.10
    ```
    This creates the directory, sets up a `pyproject.toml` file, and prepares the structure. **Crucially, the `--python 3.10` flag tells `uv` to use Python 3.10. If you don't have it installed on your machine, `uv` will download it for you automatically!**

2.  **Navigate into the directory:**
    ```bash
    cd adk-training
    ```

## Step 3: Install Packages

Use `uv` to add your dependencies. We explicitly require version 2.1.0 or higher for the Graph Runtime.

```bash
uv add "google-adk>=2.1.0" python-dotenv
```

## Step 4: Configure Authentication

Create a file named `.env` in the `adk-training` folder.

**Option A: Google AI Studio (API Key)**
```text
GOOGLE_API_KEY="AIzaSy..."
```

**Option B: Agent Platform (Service Account/ADC)**
```text
GOOGLE_GENAI_USE_VERTEXAI="1"
GOOGLE_CLOUD_PROJECT="your-project-id"
GOOGLE_CLOUD_LOCATION="us-central1"
```
*Note: If using Agent Platform, ensure you have run `gcloud auth application-default login`.*

> **Note on `adk create` and `.env` variables:** Later modules use `uv run adk create <name>` to scaffold a project. That command is an **interactive wizard** — it will prompt you for choices like the model, backend, GCP project, and region, so don't be surprised when it asks questions instead of just running silently. Also, the `.env` file it auto-generates may show `GOOGLE_GENAI_USE_ENTERPRISE=1` instead of the `GOOGLE_GENAI_USE_VERTEXAI=1` used above. Both variables are real and fully supported — they are functionally equivalent ways of telling the ADK to use Vertex AI/Agent Platform. If you see `GOOGLE_GENAI_USE_ENTERPRISE=1` in a generated `.env` file, that's fine; there's no need to "fix" it to match the `GOOGLE_GENAI_USE_VERTEXAI=1` shown elsewhere in the docs.

## Step 5: Run Verification

Create `verify_setup.py` (using the modern `Agent` and `App` patterns) and run it using `uv run`. `uv run` ensures the script is executed using the exact Python version (3.10) and dependencies stored in your virtual environment.

```bash
uv run python verify_setup.py
```

**Expected Output:**
`🔍 Testing ADK 2.0 Environment...`
`🚀 Connecting to LLM...`
`✅ Agent Response: ADK 2.0 is Ready!`
`🎉 SETUP COMPLETE! You are running ADK 2.0.`

### 💡 Troubleshooting: Model Not Found (404)

If you see a `404 NOT_FOUND` error for `gemini-3.5-flash`, it is likely a region availability issue.

**The Fix:**
1.  Open your `.env` file.
2.  Update `GOOGLE_CLOUD_LOCATION` to a region where the model is available (e.g., `us-east4`, `us-west1`, or `europe-west9`).
3.  Run the verification script again.
4.  If switching regions doesn't resolve it, the model may simply not be enabled/allowlisted for your specific GCP project at all. Check the Vertex AI Model Garden in your project, or contact your project admin to confirm access.

---

## Self-Reflection Answers

*   **Why is `uv` considered a major upgrade over traditional tools like `pip` and `venv`?**
    `uv` is written in Rust, making it extremely fast. It unifies project management, virtual environments, and dependency locking into a single tool, eliminating the need to juggle `pip`, `venv`, and `requirements.txt` manually. It even handles downloading the correct Python version for you.
*   **What is the purpose of the `uv.lock` file generated in your project directory?**
    The `uv.lock` file records the exact version of every dependency (and sub-dependency) installed. If you share your project, `uv sync` reads this file to recreate an identical environment, preventing "it works on my machine" bugs.
*   **What are the security implications of storing API keys in a `.env` file versus hardcoding them in your script?**
    Hardcoding keys makes them visible to anyone viewing your source code, and they will likely be committed to version control (like GitHub) by accident. A `.env` file is meant to be ignored by git (`.gitignore`), keeping your secrets local and safe.

</SolutionVault>
