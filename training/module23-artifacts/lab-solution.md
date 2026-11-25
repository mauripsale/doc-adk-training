---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 23 Solution: Building a Document Processing Pipeline

## Goal

This file contains the complete, simplified code for the `agent.py` script in the Document Processing Pipeline lab.

### `doc_processor/agent.py`

```python
"""
Document Processor with Artifact Management
Processes documents through multiple stages with versioning and audit trails.
"""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

# ============================================================================ 
# ARTIFACT-HANDLING TOOLS
# ============================================================================ 

async def extract_text(document_name: str, tool_context: ToolContext) -> str:
    """Extracts and cleans text from a document, saving it as an artifact."""
    print(f"Extracting text from '{document_name}'...")
    # In a real scenario, this would involve file reading and cleaning.
    extracted_content = f"EXTRACTED AND CLEANED TEXT FROM DOCUMENT: {document_name}"
    
    part = types.Part.from_text(text=extracted_content)
    version = await tool_context.save_artifact(
        filename=f"{document_name}_extracted.txt", artifact=part
    )
    return f"Text extracted from '{document_name}' and saved as version {version}."

async def summarize_document(document_name: str, tool_context: ToolContext) -> str:
    """Generates a summary of a document from its extracted text artifact."""
    print(f"Summarizing '{document_name}'...")
    # Load the artifact from the previous step.
    source_artifact = await tool_context.load_artifact(f"{document_name}_extracted.txt")
    if not source_artifact:
        return "Error: Could not find the extracted text. Please run the 'extract_text' step first."

    # In a real scenario, this would involve an LLM call for summarization.
    summary_content = f"This is a concise summary of the document '{document_name}'."
    
    part = types.Part.from_text(text=summary_content)
    version = await tool_context.save_artifact(
        filename=f"{document_name}_summary.txt", artifact=part
    )
    return f"Summary for '{document_name}' created and saved as version {version}."

async def generate_chart(document_name: str, tool_context: ToolContext) -> str:
    """Generates a dummy visualization chart for the document stats."""
    print(f"Generating chart for '{document_name}'...")
    
    # 1x1 transparent pixel PNG bytes
    dummy_png_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    
    # IMPORTANT: Use .from_bytes for binary data and specify the MIME type!
    part = types.Part.from_bytes(data=dummy_png_bytes, mime_type="image/png")
    
    version = await tool_context.save_artifact(
        filename=f"{document_name}_chart.png", artifact=part
    )
    return f"Chart generated and saved as version {version}."

async def create_report(document_name: str, tool_context: ToolContext) -> str:
    """Creates a final report by compiling all artifacts for a document."""
    print(f"Creating final report for '{document_name}'...")
    all_artifacts = await tool_context.list_artifacts()
    
    # Filter for source/intermediate artifacts (excluding any prior FINAL_REPORT)
    final_report_name = f"{document_name}_FINAL_REPORT.md"
    doc_artifacts_names = [
        name for name in all_artifacts
        if name.startswith(document_name) and name != final_report_name
    ]
    
    report = f"# Final Report for: {document_name}\n\n"
    for name in doc_artifacts_names:
        artifact = await tool_context.load_artifact(name)
        if artifact:
            # Check if it is text or binary
            if artifact.text:
                report += f"## Artifact: {name}\n\n```text\n{artifact.text[:500]}...\n```\n\n"
            elif artifact.inline_data:
                report += f"## Artifact: {name}\n\n*[Binary File Attached: {name} - Type: {artifact.inline_data.mime_type}]*\n\n"

    part = types.Part.from_text(text=report)
    version = await tool_context.save_artifact(
        filename=final_report_name, artifact=part
    )
    return f"Final report for '{document_name}' created and saved as version {version}."

# ============================================================================ 
# AGENT DEFINITION
# ============================================================================ 

root_agent = Agent(
    model='gemini-3.8-flash',
    name='document_processor',
    instruction="""
You are a document processing pipeline agent. Your job is to take a document name
and process it through a series of steps by calling the appropriate tools in the
correct order.

Workflow:
1.  When the user wants to process a document, first call `extract_text`.
2.  After extraction, call `summarize_document`.
3.  Then, call `generate_chart` to create visual stats.
4.  Finally, call `create_report` to compile all the results.
    """,
    tools=[
        FunctionTool(extract_text),
        FunctionTool(summarize_document),
        FunctionTool(generate_chart),
        FunctionTool(create_report),
    ]
)
```

### Self-Reflection Answers

1.  **Why is the versioning feature of the Artifacts system important for auditability and debugging in a production environment?**
    *   **Answer:** Versioning is crucial because it provides an immutable history of every file generated or modified by the agent. For auditability, you can trace exactly what data was used or produced at any point in time. For debugging, if an agent produces an incorrect report, you can inspect previous versions of intermediate artifacts (like the extracted text or summary) to pinpoint where the error was introduced.

2.  **All the tool functions in this lab are `async`. Why is this a requirement for functions that interact with the Artifact Service?**
    *   **Answer:** Interacting with file storage (especially cloud services like GCS) involves I/O operations that can take tens or hundreds of milliseconds. Using `async def` with `await` ensures I/O-bound tasks never block the Python event loop, keeping the agent server responsive under concurrent requests.

3.  **Locally, `uv run adk web` uses `FileArtifactService` (`.adk/artifacts/`). How do you configure `GcsArtifactService` for multi-replica cloud production?**
    *   **Answer:** Either pass `--artifact_service_uri="gs://your-production-bucket-name"` to `adk api_server` / `adk web`, or pass `GcsArtifactService` directly into `Runner`:

        ```python
        from google.adk.agents import Agent
        from google.adk.artifacts import GcsArtifactService
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService

        root_agent = Agent(name="document_processor", model="gemini-3.8-flash")
        gcs_artifact_service = GcsArtifactService(bucket_name="your-production-bucket-name")
        runner = Runner(
            app_name="doc_app",
            agent=root_agent,
            session_service=InMemorySessionService(),
            artifact_service=gcs_artifact_service,
        )
        ```
        Ensure your runtime environment has Google Cloud Application Default Credentials (or a Cloud Run / GKE Workload Identity service account) with Storage Object permissions on the bucket.
