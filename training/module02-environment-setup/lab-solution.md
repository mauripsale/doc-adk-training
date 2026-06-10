---
sidebar_position: 3
id: lab-solution
title: "Lab Solution"
---

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
**Requirement:** You must see the `uv` version printed. If not, follow the installation instructions in the lab challenge. `uv` handles Python installation automatically, so you no longer need to worry about checking your Python version manually!

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

---

## Self-Reflection Answers

*   **Why is `uv` considered a major upgrade over traditional tools like `pip` and `venv`?**
    `uv` is written in Rust, making it extremely fast. It unifies project management, virtual environments, and dependency locking into a single tool, eliminating the need to juggle `pip`, `venv`, and `requirements.txt` manually. It even handles downloading the correct Python version for you.
*   **What is the purpose of the `uv.lock` file generated in your project directory?**
    The `uv.lock` file records the exact version of every dependency (and sub-dependency) installed. If you share your project, `uv sync` reads this file to recreate an identical environment, preventing "it works on my machine" bugs.
*   **What are the security implications of storing API keys in a `.env` file versus hardcoding them in your script?**
    Hardcoding keys makes them visible to anyone viewing your source code, and they will likely be committed to version control (like GitHub) by accident. A `.env` file is meant to be ignored by git (`.gitignore`), keeping your secrets local and safe.