---
sidebar_position: 23
title: "Module 23: Handling Files with Artifacts"
pagination_label: "Module 23: Handling Files with Artifacts — 📖 Theory & Overview"
---

# Module 23: Handling Files with Artifacts

![Agent Artifacts & Versioned File Storage (Light)](img/hero-light.webp#gh-light-mode-only)
![Agent Artifacts & Versioned File Storage (Dark)](img/hero-dark.webp#gh-dark-mode-only)

## Theory

### Why Artifacts Matter

Agents often need to create and persist files (reports, data, images) that live beyond a single conversation. Simple state is not enough for this; you need a proper file management system. The ADK provides this through **Artifacts**.

Artifacts provide structured file storage with powerful features that are critical for production agents:

*   💾 **Persistence**: Files survive across agent sessions.
*   📝 **Versioning**: Every time a file is saved, a new version is created automatically, providing a complete history.
*   🔍 **Discoverability**: Agents can list and search for all available artifacts.
*   📊 **Audit Trail**: The version history allows you to track who created what and when.
*   🔐 **Credentials**: A related system provides secure storage for secrets like API keys.

### The Artifact System

An **artifact** is a versioned file stored by the agent system. Each `save` operation creates a new, immutable version, and all previous versions are retained.

![Artifact Versioning Lifecycle & Storage Pipeline (Light)](img/artifact-versioning-lifecycle-light.webp#gh-light-mode-only)
![Artifact Versioning Lifecycle & Storage Pipeline (Dark)](img/artifact-versioning-lifecycle-dark.webp#gh-dark-mode-only)
*Figure: Artifact versioning lifecycle and immutable storage pipeline across session boundaries.*

**Important:** Artifact versions are **0-indexed**. The first save of a file creates version 0.

### Configuring Artifact Storage

Before using artifacts, you must configure an `artifact_service` in your `Runner`.

*   **`InMemoryArtifactService`**: Stores artifacts in volatile RAM (lost on process exit). Ideal for fast unit tests and `InMemoryRunner`.
*   **`FileArtifactService`**: Stores versioned artifacts on the local filesystem (`file://<path>`). **Used automatically by `uv run adk web`** (`<agent>/.adk/artifacts/`) unless `--no_use_local_storage` is passed!
*   **`GcsArtifactService`**: The cloud production solution (`gs://<bucket>`). Stores versioned artifacts durably in a Google Cloud Storage bucket across multi-replica deployments.

```python
# Local volatile testing
from google.adk.artifacts import InMemoryArtifactService, FileArtifactService, GcsArtifactService
from google.adk.runners import Runner
artifact_service = InMemoryArtifactService()

# Local filesystem persistence
local_artifact_service = FileArtifactService(root_dir="./local_artifacts")

# Production Google Cloud Storage
gcs_artifact_service = GcsArtifactService(bucket_name="your-gcs-bucket")

# Attach to Runner
runner = Runner(
    app_name="doc_app",
    agent=root_agent,
    session_service=session_service,
    artifact_service=gcs_artifact_service,
)
```

### How Agents and Tools Interact with Artifacts

The primary way to work with artifacts is from within an **asynchronous custom tool** using the `ToolContext`. All artifact operations are `async` and must be `await`ed.

*   **`await tool_context.save_artifact(filename, artifact)`**: Saves a `types.Part` object as a new version of a file and returns the new version number.
*   **`await tool_context.load_artifact(filename, version=None)`**: Loads the content of an artifact. If `version` is omitted, it loads the latest version.
*   **`await tool_context.list_artifacts()`**: Returns a list of all artifact filenames available in the current session.

### Handling Binary Data (Images, PDFs, Audio)

One of the main reasons to use Artifacts instead of simple state is to handle binary data. While text uses `types.Part.from_text()`, binary files use `types.Part.from_bytes()`.

You must always specify the **MIME type** (e.g., `image/png`, `application/pdf`) so the system knows how to handle the file.

```python
# Saving an image inside an async tool
image_data = b'\x89PNG\r\n...'  # Raw bytes
part = types.Part.from_bytes(data=image_data, mime_type='image/png')
await tool_context.save_artifact('chart.png', part)
```

### Artifact Scopes: Session vs. User

By default, artifacts are scoped to the **current session**. When the session ends, they are no longer accessible to the agent (though they may still exist in storage).

To make an artifact **persistent for a specific user across multiple sessions**, prefix the filename with `user:`.

*   `"report.txt"` -> Visible only in the current conversation.
*   `"user:preferences.json"` -> Visible to this user in *any* conversation they start.

### Credential Management

Never store sensitive API keys or OAuth tokens in `session.state` (`user:` or `app:`) or unencrypted artifacts. Instead, ADK provides a dedicated credential subsystem for runtime secrets and user-delegated OAuth tokens:

*   **`await tool_context.save_credential(auth_config)`**
*   **`await tool_context.load_credential(auth_config)`**

This subsystem pairs an `AuthConfig` object with a `CredentialService` (or Google Cloud Secret Manager for service-level keys) so sensitive tokens stay isolated from conversation logs, trace exports, and cross-user state tables.

> **Going Further:** this module's lab doesn't exercise Credential Management hands-on — setting up a real OAuth flow is more infrastructure than a single lab warrants. If you want to try it, wire up `save_credential`/`load_credential` around a real third-party OAuth provider and confirm a tool can use the stored token on a later call, in a later session.

<KnowledgeCheck
  id="m23-artifact-versioning-and-scopes"
  question="In Google ADK, what version number is assigned the first time you call await tool_context.save_artifact('user:report.pdf', part), and how is that file scoped?"
  options={[
    "Version 0, accessible across all future sessions belonging to the same user",
    "Version 1, restricted strictly to the current turn and deleted afterward",
    "Version 0, shared globally across every user of the application",
    "Version 1, stored directly inside the session.state JSON dictionary"
  ]}
  correctIndex={0}
  hint="Check both the indexing rule for artifact versions and the effect of the 'user:' filename prefix."
  explanation="ADK artifact versions are 0-indexed (the initial save creates version 0), and prefixing an artifact filename with 'user:' binds it to the user across multiple sessions rather than isolating it to a single session."
/>

### Key Takeaways
- The ADK's **Artifacts** system provides persistent, versioned file storage for agents.
- **Binary Support:** Unlike simple text memory, Artifacts handle images, PDFs, and audio using `types.Part.from_bytes()`.
- **Scoping:** Use the `user:` prefix (e.g., `user:settings.json`) to persist files across multiple sessions for the same user.
- **Versioning and Auditability:** Automatic 0-indexed versioning provides an immutable audit trail, allowing you to trace changes and inspect prior file revisions.
- **Pluggable Storage Backends:** `adk web` uses `FileArtifactService` (`.adk/artifacts/`) locally by default; unit tests use `InMemoryArtifactService`, and cloud deployments use `GcsArtifactService`.
- Tools interact with artifacts asynchronously using `ToolContext` (`save_artifact`, `load_artifact`, `list_artifacts`).
- **Asynchronous Operations:** All interactions with the Artifact Service are asynchronous (`async`/`await`) so file and cloud storage I/O never blocks the Python event loop.