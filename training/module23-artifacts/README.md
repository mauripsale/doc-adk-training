---
sidebar_position: 23
title: "Module 23: Handling Files with Artifacts"
---

# Module 23: Handling Files with Artifacts

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

**Artifact Structure:**
```text
+--------------------------------------------------+
|                 ARTIFACT SERVICE                 |
+--------------------------------------------------+
|                                                  |
|  +------------------+     +--------------------+ |
|  |   Filename       |     |  Version History   | |
|  |  "report.txt"    |---->|   v0, v1, v2, ...  | |
|  +------------------+     +--------------------+ |
|           |                        |             |
|           v                        v             |
|  +------------------+     +--------------------+ |
|  |   Content        |     |      Metadata      | |
|  |  (types.Part)    |     | (Author, Timestamp)| |
|  +------------------+     +--------------------+ |
+--------------------------------------------------+
```
**Important:** Artifact versions are **0-indexed**. The first save of a file creates version 0.

### Configuring Artifact Storage

Before using artifacts, you must configure an `artifact_service` in your `Runner`.

*   **`InMemoryArtifactService`**: The default for local development. It stores files in memory and they are lost when the application restarts.
*   **`GcsArtifactService`**: The production-ready solution. It stores artifacts securely and persistently in a Google Cloud Storage bucket.

```python
# For local dev
from google.adk.artifacts import InMemoryArtifactService
artifact_service = InMemoryArtifactService()

# For production
from google.adk.artifacts import GcsArtifactService
artifact_service = GcsArtifactService(bucket_name='your-gcs-bucket')

# Add to runner
runner = Runner(
    agent=root_agent,
    artifact_service=artifact_service
    # Other services (session, memory) can also be configured here
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
# Saving an image
image_data = b'\x89PNG\r\n...' # Raw bytes
part = types.Part.from_bytes(image_data, mime_type='image/png')
await context.save_artifact('chart.png', part)
```

### Artifact Scopes: Session vs. User

By default, artifacts are scoped to the **current session**. When the session ends, they are no longer accessible to the agent (though they may still exist in storage).

To make an artifact **persistent for a specific user across multiple sessions**, prefix the filename with `user:`.

*   `"report.txt"` -> Visible only in the current conversation.
*   `"user:preferences.json"` -> Visible to this user in *any* conversation they start.

### Credential Management

While you can store simple secrets in the session state, the ADK provides a more secure, dedicated system for sensitive data like API keys and OAuth tokens.

*   **`await context.save_credential(auth_config)`**
*   **`await context.load_credential(auth_config)`**

This system uses a more complex `AuthConfig` object and is designed for production scenarios requiring robust security. For many use cases, storing simple API keys in the `user:` or `app:` state is a sufficient and simpler alternative.

> **Going Further:** this module's lab doesn't exercise Credential Management hands-on — setting up a real OAuth flow is more infrastructure than a single lab warrants. If you want to try it, wire up `save_credential`/`load_credential` around a real third-party OAuth provider and confirm a tool can use the stored token on a later call, in a later session.

### Key Takeaways
- The ADK's **Artifacts** system provides persistent, versioned file storage for agents.
- **Binary Support:** Unlike simple text memory, Artifacts handle images, PDFs, and audio using `types.Part.from_bytes()`.
- **Scoping:** Use the `user:` prefix (e.g., `user:settings.json`) to persist files across multiple sessions for the same user.
- **Versioning and Auditability:** The automatic versioning of artifacts is crucial for production environments. It provides a complete audit trail, allowing you to trace changes, debug errors by reverting to previous states, and ensure compliance by having a verifiable history of all generated files.
- You must configure an `artifact_service` in your `Runner`, using `InMemoryArtifactService` for development and `GcsArtifactService` for production.
- Tools interact with artifacts asynchronously using the `ToolContext`, with methods like `save_artifact`, `load_artifact`, and `list_artifacts`.
- **Asynchronous Operations:** All interactions with the Artifact Service (e.g., `save_artifact`, `load_artifact`) are asynchronous (`async`). This is because file I/O operations, especially with cloud storage services like GCS, can be time-consuming. Using `async` ensures that the main Python thread remains non-blocking, allowing the agent to handle other tasks or requests concurrently while waiting for file operations to complete.