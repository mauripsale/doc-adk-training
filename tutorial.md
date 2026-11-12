# Welcome to Google ADK 2.0 Training (From Zero to Hero)

Welcome to the enterprise-grade **Google Agent Development Kit (ADK 2.0)** hands-on training curriculum.

This interactive walkthrough ensures your cloud environment and project boundaries are securely configured before executing agent workflows.

---

## Step 1: Select Your Google Cloud Project

Before creating agents or provisioning cloud resources, select a dedicated **training/sandbox Google Cloud project**.

<walkthrough-project-setup billing="true"></walkthrough-project-setup>

### Confirm Active Project Configuration
Run the following command in the terminal to set your active project:

```bash
gcloud config set project <walkthrough-project-id/>
```

Verify your active identity and project isolation:

```bash
gcloud auth list
echo "Active Project: $(gcloud config get-value project)"
```

---

## Step 2: Enable Required Google Cloud APIs

Ensure the necessary APIs for Vertex AI, Cloud Run, and Artifact Registry are enabled:

<walkthrough-enable-apis apis="aiplatform.googleapis.com,run.googleapis.com,cloudbuild.googleapis.com,artifactregistry.googleapis.com"></walkthrough-enable-apis>

---

## Step 3: Initialize Development Environment

Initialize the Python virtual environment and install course dependencies using `uv`:

```bash
# 1. Ensure uv package manager is available
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# 2. Create Python 3.11 virtual environment
uv venv .venv --python 3.11

# 3. Install course dependencies
uv pip install --python .venv/bin/python -r requirements-dev.txt

# 4. Activate virtual environment
source .venv/bin/activate
```

---

## Step 4: Configure API Credentials

Set up your Gemini API credentials by initializing your `.env` file:

```bash
cp .env.example .env
```

Open the `.env` file and insert your API key:
* For Google AI Studio: set `GEMINI_API_KEY=your_key_here`
* For Vertex AI on Google Cloud: set `GOOGLE_GENAI_USE_VERTEXAI=True` and `GOOGLE_CLOUD_PROJECT=<walkthrough-project-id/>`

---

## Step 5: Test the Lab Grader

Verify your environment by running the automated lab validator:

```bash
# Test grader CLI
python3 scripts/grade_lab.py --all
```

---

## Step 6: Start Learning!

You are now fully configured and isolated in your selected Google Cloud project!

* 📂 Explore training modules: `training/module01-intro-to-ai-agents` to `training/module40-advanced-capstone-aegis-incident-response`
* 📖 View documentation: `doc/`
* 🧪 Run local labs: `cd training/<module-name> && python3 lab.py`
