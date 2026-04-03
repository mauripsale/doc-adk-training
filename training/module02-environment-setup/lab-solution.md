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

### Check Python Version
```bash
python --version
# OR (on some systems)
python3 --version
```
**Requirement:** You must see `Python 3.10.x` or higher. If you have an older version, please upgrade Python before continuing.

### Check pip
```bash
pip --version
# OR
pip3 --version
```
**Requirement:** `pip` must be installed to manage Python packages.

## Step 2: Create the Project Structure

1.  **Create Directory:**
    ```bash
    mkdir adk_training
    cd adk_training
    ```

2.  **Create Virtual Environment:**
    Using a virtual environment is mandatory to avoid conflicts.
    ```bash
    # macOS/Linux
    python3 -m venv venv
    
    # Windows
    python -m venv venv
    ```

3.  **Activate Virtual Environment:**
    ```bash
    # macOS/Linux
    source venv/bin/activate
    
    # Windows
    .\venv\Scripts\activate
    ```
    **Verification:** Your terminal prompt should now show `(venv)`.

## Step 3: Install Packages

Install the Google ADK and the dotenv library:

```bash
pip install google-adk python-dotenv
```

## Step 4: Configure Authentication

Create a file named `.env` in the `adk-training` folder.

**Option A: Google AI Studio (API Key)**
```text
GOOGLE_API_KEY="AIzaSy..."
```

**Option B: Vertex AI (Service Account/ADC)**
```text
GOOGLE_GENAI_USE_VERTEXAI="1"
GOOGLE_CLOUD_PROJECT="your-project-id"
GOOGLE_CLOUD_LOCATION="us-central1"
```
*Note: If using Vertex AI, ensure you have run `gcloud auth application-default login`.*

## Step 5: Run Verification

Create `verify_setup.py` and run it:

```bash
python verify_setup.py
```

**Expected Output:**
`✅ Google ADK is installed correctly.`
`✅ Authentication successful: Connected to the LLM service via ADK agent.`

---

## Self-Reflection Answers

*   **Why is Python 3.10+ required?**
    The ADK uses modern Python features like advanced type hints and improved asynchronous handling that are only available in version 3.10 and later.
*   **Why use a virtual environment?**
    It isolates your project. If you have another project that needs an older version of a library, the virtual environment prevents them from breaking each other.
*   **Why use an IDE instead of a simple text editor?**
    IDEs like VS Code provide syntax highlighting, error detection, and debugging tools that are essential when building complex AI agents.