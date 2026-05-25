---
sidebar_position: 2
title: "Module 2: Setting Up Your Development Environment"
---

# Module 2: Setting Up Your Development Environment

## Theory

### The Importance of a Clean Environment

Before diving into building agents, it's crucial to set up a proper development environment. A well-structured environment ensures that your project's dependencies are isolated, preventing conflicts with other Python projects on your system. It makes your project self-contained and easily reproducible by others.

The standard and recommended way to achieve this in Python is by using a **virtual environment** and a modern package manager.

### Python 3.10+ Requirement

The ADK uses modern Python features like advanced type hints and improved asynchronous handling. Therefore, **it requires Python version 3.10 or higher**. Using older versions (like 3.9) will result in warnings, missing features, and potential crashes.

### Enter `uv`: The Modern Standard

While older tutorials might teach you to use `python -m venv` and `pip`, enterprise agent development has largely moved to **`uv`**.

`uv` is an extremely fast Python package and project manager written in Rust. It replaces `pip`, `venv`, and other tools with a single, unified interface that is orders of magnitude faster.

**Key Benefits of `uv`:**

*   **Speed:** It resolves dependencies and installs packages in a fraction of the time of traditional tools.
*   **Deterministic Builds:** It automatically manages a `uv.lock` file (similar to `package-lock.json` in Node.js) ensuring that every developer on your team gets the *exact* same package versions, preventing "it works on my machine" bugs.
*   **Automatic Environments:** When you use commands like `uv run`, it automatically detects or creates the virtual environment for you. You rarely need to manually "activate" environments anymore.
*   **Python Version Management:** Crucially for our 3.10+ requirement, `uv` can automatically download and use the correct Python version if you specify it during initialization (e.g., `uv init --python 3.10`), even if you don't have it installed globally!

In this course, we will use `uv` as the foundation of our enterprise-ready scaffolding.

### Authentication: Connecting to Google Services

To use the ADK, your agent needs to communicate with Google's services to access the Gemini Large Language Models. There are two primary ways to authenticate.

#### Option A: API Key (Recommended for Beginners)

The quickest way to get started is by using an API key from **Google AI Studio**.

1.  **Get an API Key:** Visit [Google AI Studio](https://aistudio.google.com/app/apikey) and create a new API key.
2.  **Set an Environment Variable:** You will then provide this key to your application through an environment variable named `GOOGLE_API_KEY`. This is typically done by creating a `.env` file in your project directory.

This method is simple, fast, and doesn't require a full Google Cloud project, making it ideal for learning and prototyping.

#### Option B: Google Cloud Authentication (Advanced)

For production applications or for users who are already deeply integrated with Google Cloud, the standard authentication method is to use **Application Default Credentials (ADC)**.

The **Google Cloud CLI (gcloud)** is the primary tool for handling this. By running a simple command (`gcloud auth application-default login`), you grant your local development environment the necessary permissions to access Google Cloud APIs (like the Vertex AI API) on your behalf.

When you run your ADK agent, the underlying Google client libraries automatically find and use these credentials, so you don't have to manage API keys directly in your code. This method is more secure and robust for production environments.

In the following lab, you will put these concepts into practice by initializing a project with `uv`, installing the ADK, and setting up your chosen authentication method.

### Key Takeaways
- **Python 3.10 or higher** is strictly required for modern ADK features.
- A **virtual environment** is essential for isolating project dependencies and ensuring reproducibility.
- **`uv`** is the modern, enterprise-standard tool for managing Python projects, replacing `pip` and `venv`.
- You can authenticate with Google services using either a simple **API Key** from Google AI Studio or through **Google Cloud Authentication** with the `gcloud` CLI.
- Using a `.env` file to manage your API key or project settings is a standard and secure practice.