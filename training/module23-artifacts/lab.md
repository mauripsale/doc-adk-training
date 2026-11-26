---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 23: Handling Files with Artifacts — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 23: Building a Document Processing Pipeline Challenge

## Goal

In this lab, you will build a **Document Processor** agent (`doc_processor`) that reads a **real source document** (either from a local `doc_processor/sample_docs/` folder or uploaded directly inside the `adk web` chat) and processes it through a 4-stage pipeline, saving the output of every stage as an immutable, versioned ADK **Artifact**.

### The Pipeline

1.  **Extract & Clean Text (`extract_text`):** Sanitizes the document name, reads the real `.txt` source file (from `doc_processor/sample_docs/` or a chat file attachment), normalizes messy whitespace/blank lines, and saves `{clean_name}_extracted.txt` as an artifact.
2.  **Summarize (`summarize_document`):** Loads `{clean_name}_extracted.txt` from the Artifact Service, extracts real word counts, headline context, and financial/operational metrics from the text, and saves `{clean_name}_summary.txt`.
3.  **Generate Chart (`generate_chart`):** Verifies `{clean_name}_extracted.txt` exists, computes real character/word/numeric-figure statistics from the extracted text, and saves a binary PNG (`image/png`) artifact as `{clean_name}_chart.png`.
4.  **Compile Audit Report (`create_report`):** Queries `list_artifacts()`, verifies the exact expected artifacts exist in presentation order (`_summary.txt` → `_chart.png` → `_extracted.txt`), and compiles them into `{clean_name}_FINAL_REPORT.md`.

---

### Step 1: Create the Agent Project & Sample Input File

<Setup/>

1.  **Scaffold the agent package** from your `adk-training` workspace directory *(stay inside `adk-training` for all subsequent commands!)*:

    ```shell
    uv run adk create doc_processor
    ```
    Select any default model/backend prompt during creation—you will set `gemini-3.8-flash` explicitly in `doc_processor/agent.py` below.

2.  **Provide the real sample input file (`Annual_Report_2025.txt`) — choose Option A or Option B:**

    Notice that the sample corporate report intentionally contains **extra horizontal spaces and multiple blank lines** alongside FY 2025 financial figures so you can see `extract_text` clean real data!

    *   **Option A — Local `doc_processor/sample_docs/` Folder (Recommended for testing edits & `version 0` → `version 1`):**
        Run this 1-liner from `adk-training` to create `doc_processor/sample_docs/Annual_Report_2025.txt`:
        ```shell
        mkdir -p doc_processor/sample_docs && curl -fsSL https://mauripsale.github.io/doc-adk-training/samples/module23/Annual_Report_2025.txt -o doc_processor/sample_docs/Annual_Report_2025.txt
        ```
        *(On Windows / manual IDE setup, you can also <a href="/doc-adk-training/samples/module23/Annual_Report_2025.txt" download="Annual_Report_2025.txt"><strong>📥 Download Annual_Report_2025.txt</strong></a> and place it inside `doc_processor/sample_docs/`, or expand the raw contents below to copy-paste.)*

    *   **Option B — Direct File Upload in `adk web` Chat (Zero terminal file setup):**
        Click <a href="/doc-adk-training/samples/module23/Annual_Report_2025.txt" download="Annual_Report_2025.txt"><strong>📥 Download Annual_Report_2025.txt</strong></a> to save the file anywhere on your computer (or pick any `.txt` file of your own). In Step 3, you will attach it directly inside the `adk web` chat bar via **More options (`+`) → Upload local file**!

<details>
<summary>📄 View raw <code>Annual_Report_2025.txt</code> contents (optional manual copy-paste)</summary>

```text
ACME CLOUD ROBOTICS INC.   —   ANNUAL EXECUTIVE REPORT (FY 2025)
====================================================================


1. EXECUTIVE SUMMARY
Acme Cloud Robotics closed   fiscal year 2025   with record enterprise adoption
across North America and EMEA.   Autonomous warehouse orchestration   drove the
majority of net-new multi-year contracts.



2. KEY FINANCIAL & OPERATIONAL METRICS
- Total Revenue:    $48.6M   (+34% YoY growth vs. FY 2024)
- Annual Recurring Revenue (ARR):   $52.1M
- Net Dollar Retention (NDR):    118%
- Gross Margin:   74.2%    (up 310 bps YoY)
- Global Headcount:   215 full-time employees across 4 engineering hubs



3. STRATEGIC HIGHLIGHTS & FY 2026 OUTLOOK
In Q3 2025,   Acme launched   the Aegis Fleet Controller 2.0 powered by Google ADK,
reducing customer incident resolution latency by   62%.
For FY 2026, management targets   $68.0M in ARR   and expansion into APAC logistics.
```

</details>

---

### Step 2: Implement the Real-File Artifact Pipeline

**Exercise:** Open `doc_processor/agent.py`. The starter skeleton below already includes safe input helpers (`_sanitize_doc_name`, `_load_raw_source`, and `_clean_text`) so both `sample_docs/` files and `adk web` chat uploads work seamlessly. Complete the `# TODO:` sections inside the four `async` tools using `tool_context` (`save_artifact`, `load_artifact`, `list_artifacts`) and `types.Part`!

```python
# In doc_processor/agent.py (Starter Code)

from pathlib import Path
import re

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

_BASE_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd() / "doc_processor"
SAMPLE_DOCS_DIR = _BASE_DIR / "sample_docs"


def _sanitize_doc_name(document_name: str) -> str:
    """Strips optional .txt/.md suffix and enforces safe alphanumeric document names."""
    raw = document_name.strip()
    for ext in (".txt", ".md"):
        if raw.lower().endswith(ext):
            raw = raw[: -len(ext)].strip()
            break
    if not raw or ".." in raw or not re.match(r"^[A-Za-z0-9_\- ]+$", raw):
        raise ValueError(
            f"Invalid document name '{document_name}'. Provide a plain document name without path separators."
        )
    return raw


def _load_raw_source(clean_name: str, tool_context: ToolContext) -> tuple[str | None, str]:
    """Reads raw text from a matching chat-uploaded text file or from sample_docs/{clean_name}.txt."""
    inline_text_parts = []
    user_content = getattr(tool_context, "user_content", None)
    if user_content and getattr(user_content, "parts", None):
        for p in user_content.parts:
            blob = getattr(p, "inline_data", None)
            if blob and blob.data:
                mime = (getattr(blob, "mime_type", None) or "text/plain").lower()
                if mime.startswith("text/") or mime in ("application/json", "application/octet-stream"):
                    inline_text_parts.append(blob)

    # 1. Exact filename match on chat-uploaded text attachment
    for blob in inline_text_parts:
        disp = (getattr(blob, "display_name", None) or "").strip()
        if disp and Path(disp).stem.lower() == clean_name.lower():
            return blob.data.decode("utf-8", errors="replace"), f"uploaded file '{disp}'"

    # 2. Local sample_docs/{clean_name}.txt on disk
    source_file = SAMPLE_DOCS_DIR / f"{clean_name}.txt"
    if source_file.is_file():
        return source_file.read_text(encoding="utf-8", errors="replace"), f"sample_docs/{clean_name}.txt"

    # 3. Single chat-uploaded text file fallback when user asks to "process this uploaded document"
    if len(inline_text_parts) == 1:
        disp = (getattr(inline_text_parts[0], "display_name", None) or clean_name).strip()
        return inline_text_parts[0].data.decode("utf-8", errors="replace"), f"uploaded file '{disp}'"

    available = (
        sorted(p.name for p in SAMPLE_DOCS_DIR.glob("*.txt"))
        if SAMPLE_DOCS_DIR.is_dir()
        else []
    )
    available_msg = ", ".join(available) if available else "none (create doc_processor/sample_docs/ first)"
    return (
        None,
        f"Error: Source document '{clean_name}.txt' was not found in 'doc_processor/sample_docs/' "
        f"(and no matching text file was attached in chat). Available sample_docs files: {available_msg}.",
    )


def _clean_text(raw_text: str) -> str:
    """Normalizes extra spaces and collapses redundant blank lines while keeping paragraphs."""
    normalized_lines = [re.sub(r"[ \t]+", " ", line).strip() for line in raw_text.splitlines()]
    joined = "\n".join(normalized_lines).strip()
    return re.sub(r"\n{3,}", "\n\n", joined)


# ============================================================================
# ARTIFACT-HANDLING TOOLS
# ============================================================================

async def extract_text(document_name: str, tool_context: ToolContext) -> str:
    """Reads, cleans, and saves source text from sample_docs/ or chat upload as an artifact."""
    try:
        clean_name = _sanitize_doc_name(document_name)
    except ValueError as err:
        return f"Error: {err}"

    raw_text, source_info = _load_raw_source(clean_name, tool_context)
    if raw_text is None:
        return source_info  # Returns helpful error listing available sample_docs files

    cleaned_content = _clean_text(raw_text)
    if not cleaned_content:
        return f"Error: Source document from {source_info} is empty after whitespace normalization."

    # TODO: 1. Wrap `cleaned_content` in `types.Part.from_text(text=...)`.
    # TODO: 2. Save it via `await tool_context.save_artifact(...)` as f"{clean_name}_extracted.txt".
    # TODO: 3. Return a confirmation message including `source_info` and the saved `version`.
    return "Extraction complete."


async def summarize_document(document_name: str, tool_context: ToolContext) -> str:
    """Generates a data-driven summary from the extracted text artifact."""
    try:
        clean_name = _sanitize_doc_name(document_name)
    except ValueError as err:
        return f"Error: {err}"

    # TODO: 1. Load f"{clean_name}_extracted.txt" via `await tool_context.load_artifact(...)`.
    #          If missing (or `.text` is empty), return a clear error telling the caller to run `extract_text` first.
    # TODO: 2. Inspect `source_artifact.text` to compute real stats (e.g. word/line counts and lines
    #          containing '$', '%', 'Revenue', 'ARR', or 'Margin') and build a multi-line `summary_content` string.
    # TODO: 3. Wrap `summary_content` in `types.Part.from_text(...)` and save it as f"{clean_name}_summary.txt".
    # TODO: 4. Return a confirmation message with the new `version`.
    return "Summarization complete."


async def generate_chart(document_name: str, tool_context: ToolContext) -> str:
    """Verifies extracted data, computes document stats, and saves a binary PNG chart artifact."""
    try:
        clean_name = _sanitize_doc_name(document_name)
    except ValueError as err:
        return f"Error: {err}"

    # TODO: 1. Load f"{clean_name}_extracted.txt" first to verify extraction ran (return an error if missing)
    #          and compute real stats from `source_artifact.text` (e.g., word count and character count).

    # 1x1 valid PNG binary payload (avoids external plotting libraries while exercising binary MIME storage)
    dummy_png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
        b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    # TODO: 2. Wrap `dummy_png_bytes` using `types.Part.from_bytes(..., mime_type="image/png")`.
    # TODO: 3. Save the binary artifact as f"{clean_name}_chart.png" and return a message including
    #          both the calculated text statistics and the saved `version`.
    return "Chart generated."


async def create_report(document_name: str, tool_context: ToolContext) -> str:
    """Compiles expected document artifacts in deterministic order into a final Markdown report."""
    try:
        clean_name = _sanitize_doc_name(document_name)
    except ValueError as err:
        return f"Error: {err}"

    # TODO: 1. Call `await tool_context.list_artifacts()` and verify all 3 expected filenames exist
    #          in order: [f"{clean_name}_summary.txt", f"{clean_name}_chart.png", f"{clean_name}_extracted.txt"]
    #          (avoid broad `startswith` checks that could collide with other similarly named files!).
    # TODO: 2. Loop over the ordered names, `await tool_context.load_artifact(name)`, and append:
    #          - `artifact.text` inside a fenced block if it is text, OR
    #          - a binary metadata line (`artifact.inline_data.mime_type` and byte size) if it is binary.
    # TODO: 3. Save the compiled Markdown string as f"{clean_name}_FINAL_REPORT.md" and return its `version`.
    return "Report complete."


# ============================================================================
# AGENT DEFINITION
# ============================================================================

# TODO: Configure `root_agent` with Clear Instructions:
# - Run the 4 tools in strict order: extract_text -> summarize_document -> generate_chart -> create_report.
# - Stop immediately and report available files if `extract_text` returns an `Error:`.
# - Register all 4 async tools wrapped in `FunctionTool(...)`.
root_agent = Agent(
    model="gemini-3.8-flash",
    name="document_processor",
    instruction="""
    # Your instruction here...
    """,
    tools=[
        # Your tools here...
    ],
)
```

---

### Step 3: Run and Test the Real-File Pipeline

1.  **Verify your credentials** in `doc_processor/.env` (or in your workspace `.env`).
2.  **From your `adk-training` workspace directory, start the Dev UI:**
    ```shell
    uv run adk web
    ```
    *   **Note on Local vs. Cloud Persistence:** `doc_processor` reads input `.txt` files from `doc_processor/sample_docs/` (or from chat file attachments) and saves versioned output artifacts locally inside `doc_processor/.adk/artifacts/` via `FileArtifactService` (`--use_local_storage` default). Pass `--no_use_local_storage` for volatile RAM testing, or `--artifact_service_uri="gs://your-bucket"` (`GcsArtifactService`) in multi-replica cloud deployments.

3.  **Select `doc_processor` in the top-left agent dropdown and walk through these 3 verification scenarios:**

    *   **3.1 Happy Path — Real Extraction, Metrics Summary & Audit Report (`version 0`):**
        *   *If you chose Option A (`sample_docs/`):* send:
            ```text
            Process the document named 'Annual_Report_2025'.
            ```
        *   *If you chose Option B (Chat Upload):* click **More options (`+`) → Upload local file** in the bottom chat bar, attach `Annual_Report_2025.txt`, and send:
            ```text
            Process 'Annual_Report_2025'.
            ```
        *   Open the **Artifacts** tab/panel in `adk web`: inspect `Annual_Report_2025_extracted.txt`, `Annual_Report_2025_summary.txt`, `Annual_Report_2025_chart.png`, and `Annual_Report_2025_FINAL_REPORT.md` (`version 0`). Confirm that the extra spaces were cleaned and that the real `$48.6M` / `$52.1M ARR` metrics from the file appear inside the summary and final report!

    *   **3.2 Auditability & Versioning (`version 0` → `version 1`):**
        *   Open `doc_processor/sample_docs/Annual_Report_2025.txt` in your editor (or edit your local copy if using Option B), change `Total Revenue: $48.6M` to `Total Revenue: $51.2M (Audited)`, and save the file.
        *   Send the prompt again in the **same session** *(Option B users: re-attach your updated `Annual_Report_2025.txt` via **More options (`+`) → Upload local file** along with the prompt)*:
            ```text
            Process the document named 'Annual_Report_2025' again with the updated figures.
            ```
        *   Notice that every artifact advances to **`version 1`** while **`version 0`** remains preserved in the Artifact history for side-by-side audit comparison! *(Bonus: create a second file like `doc_processor/sample_docs/Q1_Notes.txt` and process it too!)*

    *   **3.3 Guided Missing-File Error Handling:**
        *   Test what happens when a requested file does not exist:
            ```text
            Process 'Missing_File'.
            ```
        *   Verify that `extract_text` stops cleanly without crashing, lists the valid files available inside `doc_processor/sample_docs/` (such as `Annual_Report_2025.txt`, or `none` if you only used Option B chat uploads), and prevents downstream tools from running on empty data.

### Having Trouble?

If you get stuck, unlock the **Reference Solution Vault** at the bottom of this page after completing the quick comprehension checks.

### Lab Summary

You have built an end-to-end, auditable document processing agent backed by real file input and ADK Artifacts:
*   Sanitized user-supplied document names against path traversal and loaded real `.txt` inputs from `doc_processor/sample_docs/` or `adk web` chat attachments (`tool_context.user_content`).
*   Saved cleaned text and data-driven metric summaries with `await tool_context.save_artifact()` and `types.Part.from_text()`.
*   Saved binary PNG artifacts with `types.Part.from_bytes(..., mime_type="image/png")` and compiled expected artifacts in deterministic order without prefix collisions.
*   Verified immutable `0`-indexed artifact versioning (`version 0` → `version 1`) when re-processing modified source files.

### Self-Reflection Questions
- Why is the versioning feature of the Artifacts system important for auditability and debugging when source files are revised over time?
- All the tool functions in this lab are `async`. Why is this a requirement for functions that interact with the Artifact Service?
- Locally, `uv run adk web` uses `FileArtifactService` (`.adk/artifacts/`). How do you configure `GcsArtifactService` for multi-replica cloud production?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="23">

## Lab 23 Solution: Building a Document Processing Pipeline

## Goal

This file contains the complete implementation for `doc_processor/agent.py`, reading real source documents (either from `doc_processor/sample_docs/` or attached directly via `adk web` chat upload) and processing them through a 4-stage versioned ADK Artifact pipeline.

### `doc_processor/agent.py`

```python
"""
Document Processor with Real File Input & Versioned Artifact Management.
Processes documents from sample_docs/ (or chat uploads) through four auditable stages.
"""

from pathlib import Path
import re

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

_BASE_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd() / "doc_processor"
SAMPLE_DOCS_DIR = _BASE_DIR / "sample_docs"


def _sanitize_doc_name(document_name: str) -> str:
    """Strips optional .txt/.md suffix and enforces safe alphanumeric document names."""
    raw = document_name.strip()
    for ext in (".txt", ".md"):
        if raw.lower().endswith(ext):
            raw = raw[: -len(ext)].strip()
            break
    if not raw or ".." in raw or not re.match(r"^[A-Za-z0-9_\- ]+$", raw):
        raise ValueError(
            f"Invalid document name '{document_name}'. Provide a plain document name without path separators."
        )
    return raw


def _load_raw_source(clean_name: str, tool_context: ToolContext) -> tuple[str | None, str]:
    """Reads raw text from a matching chat-uploaded text file or from sample_docs/{clean_name}.txt."""
    inline_text_parts = []
    user_content = getattr(tool_context, "user_content", None)
    if user_content and getattr(user_content, "parts", None):
        for p in user_content.parts:
            blob = getattr(p, "inline_data", None)
            if blob and blob.data:
                mime = (getattr(blob, "mime_type", None) or "text/plain").lower()
                if mime.startswith("text/") or mime in ("application/json", "application/octet-stream"):
                    inline_text_parts.append(blob)

    # 1. Exact filename match on chat-uploaded text attachment
    for blob in inline_text_parts:
        disp = (getattr(blob, "display_name", None) or "").strip()
        if disp and Path(disp).stem.lower() == clean_name.lower():
            return blob.data.decode("utf-8", errors="replace"), f"uploaded file '{disp}'"

    # 2. Local sample_docs/{clean_name}.txt on disk
    source_file = SAMPLE_DOCS_DIR / f"{clean_name}.txt"
    if source_file.is_file():
        return source_file.read_text(encoding="utf-8", errors="replace"), f"sample_docs/{clean_name}.txt"

    # 3. Single chat-uploaded text file fallback when user asks to "process this uploaded document"
    if len(inline_text_parts) == 1:
        disp = (getattr(inline_text_parts[0], "display_name", None) or clean_name).strip()
        return inline_text_parts[0].data.decode("utf-8", errors="replace"), f"uploaded file '{disp}'"

    available = (
        sorted(p.name for p in SAMPLE_DOCS_DIR.glob("*.txt"))
        if SAMPLE_DOCS_DIR.is_dir()
        else []
    )
    available_msg = ", ".join(available) if available else "none (create doc_processor/sample_docs/ first)"
    return (
        None,
        f"Error: Source document '{clean_name}.txt' was not found in 'doc_processor/sample_docs/' "
        f"(and no matching text file was attached in chat). Available sample_docs files: {available_msg}.",
    )


def _clean_text(raw_text: str) -> str:
    """Normalizes extra spaces and collapses redundant blank lines while keeping paragraphs."""
    normalized_lines = [re.sub(r"[ \t]+", " ", line).strip() for line in raw_text.splitlines()]
    joined = "\n".join(normalized_lines).strip()
    return re.sub(r"\n{3,}", "\n\n", joined)


# ============================================================================
# ARTIFACT-HANDLING TOOLS
# ============================================================================

async def extract_text(document_name: str, tool_context: ToolContext) -> str:
    """Reads, cleans, and saves source text from sample_docs/ or chat upload as an artifact."""
    try:
        clean_name = _sanitize_doc_name(document_name)
    except ValueError as err:
        return f"Error: {err}"

    raw_text, source_info = _load_raw_source(clean_name, tool_context)
    if raw_text is None:
        return source_info

    cleaned_content = _clean_text(raw_text)
    if not cleaned_content:
        return f"Error: Source document from {source_info} is empty after whitespace normalization."

    part = types.Part.from_text(text=cleaned_content)
    version = await tool_context.save_artifact(
        filename=f"{clean_name}_extracted.txt",
        artifact=part,
    )
    return (
        f"Extracted and cleaned {len(cleaned_content)} characters from {source_info}; "
        f"saved '{clean_name}_extracted.txt' as version {version}."
    )


async def summarize_document(document_name: str, tool_context: ToolContext) -> str:
    """Generates a data-driven summary from the extracted text artifact."""
    try:
        clean_name = _sanitize_doc_name(document_name)
    except ValueError as err:
        return f"Error: {err}"

    source_artifact = await tool_context.load_artifact(f"{clean_name}_extracted.txt")
    if source_artifact is None or not source_artifact.text:
        return (
            f"Error: Could not find non-empty '{clean_name}_extracted.txt'. "
            "Please run 'extract_text' first with a valid document."
        )

    text = source_artifact.text
    non_empty_lines = [ln for ln in text.splitlines() if ln.strip() and not set(ln.strip()) <= {"=", "-"}]
    words = text.split()
    metric_lines = [
        ln.lstrip("- ").strip()
        for ln in non_empty_lines
        if any(tok in ln for tok in ("$", "%", "Revenue", "ARR", "Retention", "Margin", "Headcount"))
    ]
    headline = non_empty_lines[0] if non_empty_lines else clean_name
    lead_sentence = non_empty_lines[2] if len(non_empty_lines) > 2 else headline

    summary_lines = [
        f"Executive Summary — {headline}",
        f"- Source Stats: {len(non_empty_lines)} content lines, {len(words)} words",
        f"- Overview: {lead_sentence}",
    ]
    if metric_lines:
        summary_lines.append("- Extracted Key Metrics:")
        for metric in metric_lines[:5]:
            summary_lines.append(f"  * {metric}")

    summary_content = "\n".join(summary_lines)
    part = types.Part.from_text(text=summary_content)
    version = await tool_context.save_artifact(
        filename=f"{clean_name}_summary.txt",
        artifact=part,
    )
    return (
        f"Summary for '{clean_name}' ({len(words)} words analyzed, {len(metric_lines)} metrics extracted) "
        f"saved as version {version}."
    )


async def generate_chart(document_name: str, tool_context: ToolContext) -> str:
    """Verifies extracted data, computes document stats, and saves a binary PNG chart artifact."""
    try:
        clean_name = _sanitize_doc_name(document_name)
    except ValueError as err:
        return f"Error: {err}"

    source_artifact = await tool_context.load_artifact(f"{clean_name}_extracted.txt")
    if source_artifact is None or not source_artifact.text:
        return (
            f"Error: Cannot generate chart because '{clean_name}_extracted.txt' is missing. "
            "Run 'extract_text' first."
        )

    text = source_artifact.text
    word_count = len(text.split())
    char_count = len(text)
    numeric_tokens = re.findall(r"\$?\d+(?:\.\d+)?[%MKB]?", text)

    # 1x1 valid PNG binary payload (avoids external plotting dependencies while exercising binary MIME storage)
    dummy_png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
        b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    part = types.Part.from_bytes(data=dummy_png_bytes, mime_type="image/png")
    version = await tool_context.save_artifact(
        filename=f"{clean_name}_chart.png",
        artifact=part,
    )
    return (
        f"Chart '{clean_name}_chart.png' generated from extracted stats "
        f"({word_count} words, {char_count} chars, {len(numeric_tokens)} numeric figures) "
        f"and saved as version {version}."
    )


async def create_report(document_name: str, tool_context: ToolContext) -> str:
    """Compiles expected document artifacts in deterministic order into a final Markdown report."""
    try:
        clean_name = _sanitize_doc_name(document_name)
    except ValueError as err:
        return f"Error: {err}"

    existing = set(await tool_context.list_artifacts())
    expected_order = [
        f"{clean_name}_summary.txt",
        f"{clean_name}_chart.png",
        f"{clean_name}_extracted.txt",
    ]
    missing = [name for name in expected_order if name not in existing]
    if missing:
        return (
            f"Error: Missing prerequisite artifacts for '{clean_name}': {', '.join(missing)}. "
            "Run 'extract_text', 'summarize_document', and 'generate_chart' first."
        )

    report = f"# Final Audit Report: {clean_name}\n\n"
    for name in expected_order:
        artifact = await tool_context.load_artifact(name)
        if artifact is None:
            continue
        if artifact.text is not None:
            safe_text = artifact.text.replace("```", "'''")
            report += f"## Artifact: `{name}`\n\n```text\n{safe_text}\n```\n\n"
        elif artifact.inline_data:
            byte_len = len(artifact.inline_data.data or b"")
            report += (
                f"## Artifact: `{name}`\n\n"
                f"*[Binary Image Attached: `{name}` — MIME: `{artifact.inline_data.mime_type}`, "
                f"Size: {byte_len} bytes]*\n\n"
            )

    final_report_name = f"{clean_name}_FINAL_REPORT.md"
    part = types.Part.from_text(text=report)
    version = await tool_context.save_artifact(
        filename=final_report_name,
        artifact=part,
    )
    return f"Final report '{final_report_name}' compiled from {len(expected_order)} artifacts and saved as version {version}."


# ============================================================================
# AGENT DEFINITION
# ============================================================================

root_agent = Agent(
    model="gemini-3.8-flash",
    name="document_processor",
    instruction="""
You are a document processing pipeline agent. Your job is to process a source document
from `sample_docs/` (or from a file attached directly in chat) through four ordered stages:

1. Call `extract_text` first. If `extract_text` returns an `Error:`, stop immediately,
   report the exact error and available files to the user, and do NOT call downstream tools.
   (If the user attached a file in chat without typing its name, pass the attached filename.)
2. Call `summarize_document` to summarize the cleaned text artifact.
3. Call `generate_chart` to compute document statistics and store the PNG chart artifact.
4. Call `create_report` to compile the summary, chart metadata, and cleaned text into the final report.

Summarize the artifact versions created at the end of a successful run.
""",
    tools=[
        FunctionTool(extract_text),
        FunctionTool(summarize_document),
        FunctionTool(generate_chart),
        FunctionTool(create_report),
    ],
)
```

### Self-Reflection Answers

1.  **Why is the versioning feature of the Artifacts system important for auditability and debugging in a production environment?**
    *   **Answer:** Versioning is crucial because it provides an immutable history of every file generated or modified by the agent. When you edited `Annual_Report_2025.txt` and re-ran the pipeline, ADK preserved `version 0` alongside `version 1`. For auditability, you can prove exactly which source snapshot produced a given executive report; for debugging, you can compare intermediate artifacts across versions to pinpoint regressions.

2.  **All the tool functions in this lab are `async`. Why is this a requirement for functions that interact with the Artifact Service?**
    *   **Answer:** Interacting with file storage (especially cloud object stores like Google Cloud Storage) involves network I/O operations that can take tens or hundreds of milliseconds. Using `async def` with `await` ensures I/O-bound tasks never block the Python event loop, keeping the agent server responsive under concurrent requests.

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

</SolutionVault>
