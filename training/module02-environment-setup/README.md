---
sidebar_position: 2
title: "Module 2: Setting Up Your Development Environment (ADK 2.0)"
---

# Module 2: Setting Up Your Development Environment

## Theory

### The Importance of a Clean Environment

Before diving into building agents, it's crucial to set up a proper development environment. A well-structured environment ensures that your project's dependencies are isolated, preventing conflicts with other Python projects on your system. It makes your project self-contained and easily reproducible by others.

### Python 3.10+ and ADK 2.0 Requirements

The ADK uses modern Python features like advanced type hints and improved asynchronous handling. 

*   **Python Requirement:** Strictly **3.10 or higher**.
*   **ADK Requirement:** This course is built for **google.adk >= 2.1.0**, which introduces the **Workflow Graph Runtime**. Older versions (1.x) are not compatible with the advanced orchestration patterns taught in this course.

### Enter `uv`: The Modern Standard

Enterprise agent development has moved to **`uv`**.

`uv` is an extremely fast Python package and project manager written in Rust. It replaces `pip`, `venv`, and other tools with a single, unified interface that is orders of magnitude faster.

**Key Benefits of `uv`:**

*   **Speed:** It resolves dependencies and installs packages in a fraction of the time.
*   **Deterministic Builds:** It automatically manages a `uv.lock` file ensuring that every developer gets the *exact* same package versions.
*   **Python Version Management:** `uv` can automatically download and use the correct Python version if you specify it during initialization (e.g., `uv init --python 3.10`).

### Authentication: Connecting to Google Services

To use the ADK, your agent needs to communicate with Google's services. There are two primary ways to authenticate.

#### Option A: API Key (Recommended for Beginners)

The quickest way to get started is by using an API key from **Google AI Studio**.

1.  **Get an API Key:** Visit [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  **Set an Environment Variable:** Provide this key through an environment variable named `GOOGLE_API_KEY`, typically stored in a `.env` file.

#### Option B: Google Cloud Authentication (Enterprise)

For production, use **Application Default Credentials (ADC)** via the **Google Cloud CLI (gcloud)**.

```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

The ADK automatically detects these credentials.

### Troubleshooting Common Errors

#### 1. 🛑 `404: Model 'gemini-3.5-flash' not found`
This error usually occurs when the model has not yet been deployed to your specific Google Cloud location.

**The Fix:**
Change your `GOOGLE_CLOUD_LOCATION` (or `LOCATION` in `.env`) to one of the following high-availability regions:
*   `us-central1`
*   `us-east4`
*   `europe-west9`

#### 2. 🛑 `PermissionDenied: 403`
Your user or service account does not have the "Agent Platform User" role.
**The Fix:** Go to IAM in the Cloud Console and grant your account the `roles/aiplatform.user` role.

#### 3. 🛑 `ModuleNotFoundError: No module named 'google'`
This happens if you are not running the command inside the virtual environment.
**The Fix:** Always prefix your commands with `uv run` (e.g., `uv run adk web .`).

### Key Takeaways
- **Python 3.10+** and **google.adk >= 2.1.0** are strictly required.
- **`uv`** is the recommended tool for managing Python projects and environments.
- Use a **`.env`** file to manage your API key or project settings securely.