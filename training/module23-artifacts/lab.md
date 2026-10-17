---
sidebar_position: 2
title: "Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 23: Building a Document Processing Pipeline Challenge

## Goal

In this lab, you will build a **Document Processor** agent that uses a multi-step pipeline to process a file, saving the output of each step as a versioned artifact. This will teach you how to build complex, auditable file management workflows.

### The Pipeline

1.  **Extract Text:** Takes a source document name and saves its cleaned text as an artifact.
2.  **Summarize:** Reads the extracted text artifact and saves a summary as a new artifact.
3.  **Generate Chart (New!):** Creates a visual representation (simulated binary image) of the document stats.
4.  **Report:** Reads all previously generated artifacts and compiles them into a final report artifact.

### Step 1: Create the Agent Project

<Setup/>

1.  **Create the agent project:**
    ```shell
    uv run adk create doc_processor
    ```
    This prompts for a model choice (any option is fine, you'll set the real model in `agent.py` below) and, if needed, a backend -- there's no separate "type" prompt, `agent.py`/Code is already the default.

2.  **Navigate into the new directory:**
    ```shell
    cd doc_processor
    ```

### Step 2: Implement the Artifact Pipeline

**Exercise:** Open `agent.py`. A skeleton with the tool function signatures is provided. Your task is to implement the logic for each tool using the `tool_context` to save and load artifacts. Remember that all artifact operations are `async` and must be `await`ed.

```python
# In agent.py (Starter Code)

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

# ============================================================================ 
# ARTIFACT-HANDLING TOOLS
# ============================================================================ 

async def extract_text(document_name: str, tool_context: ToolContext) -> str:
    """Extracts and cleans text from a document, saving it as an artifact."""
    extracted_content = f"EXTRACTED AND CLEANED TEXT FROM DOCUMENT: {document_name}"
    
    # TODO: 1. Create a types.Part from the `extracted_content`.
    # TODO: 2. Save the part as an artifact named f"{document_name}_extracted.txt".
    # TODO: 3. Return a confirmation message including the new version number.
    return "Extraction complete."

async def summarize_document(document_name: str, tool_context: ToolContext) -> str:
    """Generates a summary of a document from its extracted text artifact."""
    # TODO: 1. Load the latest version of the f"{document_name}_extracted.txt" artifact.
    # TODO: 2. If the artifact is not found, return a helpful error message.
    
    summary_content = f"This is a concise summary of the document '{document_name}'."
    
    # TODO: 3. Create a types.Part from the `summary_content`.
    # TODO: 4. Save the summary as a new artifact named f"{document_name}_summary.txt".
    # TODO: 5. Return a confirmation message.
    return "Summarization complete."

async def generate_chart(document_name: str, tool_context: ToolContext) -> str:
    """Generates a dummy visualization chart for the document stats."""
    # Simulating a binary PNG image (1x1 pixel)
    # In a real app, you would use a library like matplotlib to generate bytes.
    dummy_png_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    
    # TODO: 1. Create a types.Part using `types.Part.from_bytes()`.
    # IMPORTANT: You MUST specify `mime_type="image/png"`.
    
    # TODO: 2. Save the artifact as f"{document_name}_chart.png".
    return "Chart generated."

async def create_report(document_name: str, tool_context: ToolContext) -> str:
    """Creates a final report by compiling all artifacts for a document."""
    # TODO: 1. List all available artifacts using the tool_context.
    # TODO: 2. Filter the list to get only the names of artifacts for the current document.
    
    report = f"# Final Report for: {document_name}\n\n"
    # TODO: 3. Loop through your filtered list of artifact names. In the loop,
    # load each artifact.
    # - If it's text, append it to the `report`.
    # - If it's an image (mime_type starts with 'image/'), append a reference like "[Attached Image: {name}]".
    
    # TODO: 4. Save the final `report` string as an artifact named
    # f"{document_name}_FINAL_REPORT.md".
    # TODO: 5. Return a confirmation message.
    return "Report complete."

# ============================================================================ 
# AGENT DEFINITION
# ============================================================================ 

# TODO: Define the `root_agent`. Give it an instruction that tells it to run the
# pipeline in the correct order (extract -> summarize -> chart -> report) and 
# register the four async tools.
root_agent = Agent(
    model='gemini-3.5-flash',
    name='document_processor',
    instruction="""
    # Your instruction here...
    """,
    tools=[
        # Your tools here...
    ]
)
```

### Step 3: Run and Test the Pipeline

1.  **Set up your `.env` file** with your API key or Agent Platform project.
2.  **Navigate to the parent directory** (`cd ..`) and start the Dev UI:
    ```shell
    uv run adk web doc_processor
    ```
    *   **Note on Persistence:** For this lab, the default `InMemoryArtifactService` is used, meaning artifacts will be lost if the `uv run adk web` server is restarted. For persistent storage, a `GcsArtifactService` would be configured in the `Runner`.
3.  **Interact with the agent:**
    *   Select "document_processor" and send a prompt like: "Process the document named 'Annual_Report_2025'."
4.  **Analyze the Trace and Artifacts:**
    *   In the **Trace** view, observe the chain of tool calls.
    *   In the **Chat** view, click the blue "Artifacts" button to see the list of files your agent created. Click on each one to view its content.

### Having Trouble?

If you get stuck, you can find the complete, working code in the `lab-solution.md` file.

### Lab Summary

You have successfully built a multi-step document processing agent that uses artifacts for state management and auditability. You have learned to:
*   Write `async` tools that can save and load artifacts.
*   Use `await tool_context.save_artifact()` to create versioned files.
*   Use `await tool_context.load_artifact()` to read previously created files.
*   Chain tools together to create a pipeline where the output of one step is the input to the next.

### Self-Reflection Questions
- Why is the versioning feature of the Artifacts system important for audibility and debugging in a production environment?
- All the tool functions in this lab are `async`. Why is this a requirement for functions that interact with the Artifact Service?
- The lab uses an `InMemoryArtifactService`. What changes would you need to make to the `Runner` configuration to use the persistent `GcsArtifactService` in a production deployment?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="23">

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
                report += f"## Artifact: {name}\n\n*[Binary File Attached: {name} - Type: {artifact.inline_data.mime_type}]*\n\n"

    part = types.Part.from_text(text=report)
    version = await tool_context.save_artifact(
        filename=f"{document_name}_FINAL_REPORT.md", artifact=part
    )
    return f"Final report for '{document_name}' created and saved as version {version}."

# ============================================================================ 
# AGENT DEFINITION
# ============================================================================ 

root_agent = Agent(
    model='gemini-3.5-flash',
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
        from google.adk.runners import Runner

        # ... root_agent definition ...

        gcs_artifact_service = GcsArtifactService(bucket_name="your-production-bucket-name")

        runner = Runner(
            agent=root_agent,
            artifact_service=gcs_artifact_service,
            # ... other services ...
        )
        ```
        You would also need to ensure your environment has the necessary Google Cloud authentication configured (e.g., via `GOOGLE_APPLICATION_CREDENTIALS` or a service account).

</SolutionVault>
