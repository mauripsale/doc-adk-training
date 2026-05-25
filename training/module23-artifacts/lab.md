---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 23: Building a Document Processing Pipeline Challenge

## Goal

In this lab, you will build a **Document Processor** agent that uses a multi-step pipeline to process a file, saving the output of each step as a versioned artifact. This will teach you how to build complex, auditable file management workflows.

### The Pipeline

1.  **Extract Text:** Takes a source document name and saves its cleaned text as an artifact.
2.  **Summarize:** Reads the extracted text artifact and saves a summary as a new artifact.
3.  **Generate Chart (New!):** Creates a visual representation (simulated binary image) of the document stats.
4.  **Report:** Reads all previously generated artifacts and compiles them into a final report artifact.

### Step 1: Create the Agent Project

1.  **Create the agent project:**
    ```shell
    adk create doc_processor
    ```
    When prompted, choose the **Programmatic (Python script)** option.

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

1.  **Set up your `.env` file** with your API key or Vertex AI project.
2.  **Navigate to the parent directory** (`cd ..`) and start the Dev UI:
    ```shell
    adk web doc_processor
    ```
    *   **Note on Persistence:** For this lab, the default `InMemoryArtifactService` is used, meaning artifacts will be lost if the `adk web` server is restarted. For persistent storage, a `GcsArtifactService` would be configured in the `Runner`.
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

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMjMtYXJ0aWZhY3RzL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module23-artifacts/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
