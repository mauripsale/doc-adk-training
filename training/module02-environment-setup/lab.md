# Module 2: Setting Up Your Development Environment

## Lab 2: Installation and Configuration

### Goal

This lab will walk you through the essential steps of setting up a clean, isolated Python environment, installing the Google ADK, and authenticating with Google Cloud. By the end, your machine will be fully prepared to start building agents.

### Prerequisites

*   **Python 3.8 or higher:** To check if you have Python installed, open your terminal (or Command Prompt on Windows) and run `python3 --version` (or `python --version`). If it's not installed, download it from the [official Python website](https://www.python.org/downloads/).
*   **Google Cloud Account:** You will need a Google Cloud account to access the Gemini API. If you don't have one, you can sign up for a free trial.

### Step 1: Create a Project Directory

First, let's create a dedicated folder for all the projects you'll be working on during this course.

```shell
mkdir adk-training
cd adk-training
```

### Step 2: Set Up a Python Virtual Environment

We will use `venv` to create an isolated environment for our project.

1.  **Create the virtual environment:**

    Run the following command inside your `adk-training` directory. This creates a sub-directory named `.venv` which will contain the isolated Python environment.

    ```shell
    python3 -m venv .venv
    ```

2.  **Activate the virtual environment:**

    You must activate the environment to start using it. The command differs based on your operating system.

    *   **macOS / Linux (bash/zsh):**
        ```shell
        source .venv/bin/activate
        ```
    *   **Windows (Command Prompt):**
        ```shell
        .venv\Scripts\activate.bat
        ```
    *   **Windows (PowerShell):**
        ```shell
        .venv\Scripts\Activate.ps1
        ```

    After activation, you should see `(.venv)` at the beginning of your terminal prompt, indicating that the virtual environment is active.

### Step 3: Install the Google ADK

With your virtual environment active, you can now safely install the ADK.

1.  **Install the package using `pip`:**

    ```shell
    pip install google-adk
    ```
    `pip` is the Python package installer, and this command downloads and installs the latest version of the ADK and its required dependencies into your `.venv`.

2.  **(Optional) Verify the installation:**

    To confirm that the ADK was installed correctly, run:

    ```shell
    pip show google-adk
    ```
    This will display information about the package, including its version. You can also run `adk --version` to check the command-line tool.

### Step 4: Authenticate with Google Cloud

Finally, let's authorize your local environment to use Google Cloud services.

1.  **Install the Google Cloud CLI:**

    If you don't have it installed, follow the official instructions to [install the Google Cloud CLI](https://cloud.google.com/sdk/docs/install).

2.  **Log in and create Application Default Credentials:**

    Run the following command in your terminal:

    ```shell
    gcloud auth application-default login
    ```

    This command will open a web browser and prompt you to log in with your Google account. After you approve the permissions, the gcloud CLI will store authentication credentials on your local machine. The ADK will automatically find and use these credentials to make secure API calls.

### Lab Summary

Congratulations! You have successfully:

*   Created and activated an isolated Python virtual environment.
*   Installed the Google ADK package.
*   Authenticated your machine with Google Cloud.

Your development environment is now ready. In the next module, you will use this setup to create and run your very first AI agent.
