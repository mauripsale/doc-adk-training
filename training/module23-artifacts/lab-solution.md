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
    
    part = types.Part.from_text(extracted_content)
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
    
    part = types.Part.from_text(summary_content)
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
    part = types.Part.from_bytes(dummy_png_bytes, mime_type="image/png")
    
    version = await tool_context.save_artifact(
        filename=f"{document_name}_chart.png", artifact=part
    )
    return f"Chart generated and saved as version {version}."

async def create_report(document_name: str, tool_context: ToolContext) -> str:
    """Creates a final report by compiling all artifacts for a document."""
    print(f"Creating final report for '{document_name}'...")
    all_artifacts = await tool_context.list_artifacts()
    
    # Filter for artifacts related to the specific document.
    doc_artifacts_names = [name for name in all_artifacts if name.startswith(document_name)]
    
    report = f"# Final Report for: {document_name}\n\n"
    for name in doc_artifacts_names:
        artifact = await tool_context.load_artifact(name)
        if artifact:
            # Check if it is text or binary
            if artifact.text:
                report += f"## Artifact: {name}\n\n```text\n{artifact.text[:500]}...\n```\n\n"
            else:
                 # It's binary (like our chart), so we just mention it
                report += f"## Artifact: {name}\n\n*[Binary File Attached: {name} - Type: {artifact.mime_type}]*\n\n"

    part = types.Part.from_text(report)
    version = await tool_context.save_artifact(
        filename=f"{document_name}_FINAL_REPORT.md", artifact=part
    )
    return f"Final report for '{document_name}' created and saved as version {version}."

# ============================================================================ 
# AGENT DEFINITION
# ============================================================================ 

root_agent = Agent(
    model='gemini-2.5-flash',
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

1.  **Why is the versioning feature of the Artifacts system important for audibility and debugging in a production environment?**
    *   **Answer:** Versioning is crucial because it provides an immutable history of every file generated or modified by the agent. For audibility, you can trace exactly what data was used or produced at any point in time. For debugging, if an agent produces an incorrect report, you can easily go back to previous versions of intermediate artifacts (like the extracted text or summary) to pinpoint where the error was introduced. This is invaluable for understanding and rectifying complex agentic workflows.

2.  **All the tool functions in this lab are `async`. Why is this a requirement for functions that interact with the Artifact Service?**
    *   **Answer:** Interacting with file storage (especially cloud services like GCS) involves I/O operations that can be slow. If these operations were synchronous (`def` instead of `async def`), they would block the main Python thread, making the agent unresponsive and unable to process other requests or continue its own internal reasoning until the file operation completed. `async` functions, used with `await`, ensure that these I/O-bound tasks run concurrently, keeping the agent efficient and responsive.

3.  **The lab uses an `InMemoryArtifactService`. What changes would you need to make to the `Runner` configuration to use the persistent `GcsArtifactService` in a production deployment?**
    *   **Answer:** You would modify the `Runner` initialization in your main application entry point (e.g., `main.py`). Instead of `InMemoryArtifactService`, you would use `GcsArtifactService` and provide it with a Google Cloud Storage bucket name:

        ```python
        from google.adk.artifacts import GcsArtifactService
        from google.adk.runner import Runner

        # ... root_agent definition ...

        gcs_artifact_service = GcsArtifactService(bucket_name="your-production-bucket-name")

        runner = Runner(
            agent=root_agent,
            artifact_service=gcs_artifact_service,
            # ... other services ...
        )
        ```
        You would also need to ensure your environment has the necessary Google Cloud authentication configured (e.g., via `GOOGLE_APPLICATION_CREDENTIALS` or a service account).
