# SPEC: ADK 2.0+ Advanced Features & Enterprise Optimization Deepening

## 1. Objective & Scope
The objective is to enrich the current 41-module curriculum with recently introduced / high-value ADK 2.0+ framework features without altering module numbering or visual asset bindings.

The updates target three core areas:
1. **Module 10 (`training/module10-advanced-function-tools/README.md`)**: Human-in-the-Loop & Tool Confirmation (`FunctionTool(require_confirmation=True | callable)`).
2. **Module 22 (`training/module22-state-and-memory/README.md`)**:
   - Explicit code and execution pattern for **Session Rewind** (`runner.rewind_async`).
   - **Context Caching** (`ContextCacheConfig`) for token & latency optimization.
   - **Context Compaction** (`EventsCompactionConfig`, `LlmEventSummarizer`) for sliding-window multi-turn summarization.
3. **Module 39 (`training/module39-plugins/README.md`)**:
   - Expansion of Built-in Framework Plugins: `BigQueryAgentAnalyticsPlugin`, `GlobalInstructionPlugin`, `ContextFilterPlugin`, alongside `ReflectAndRetryToolPlugin`.

---

## 2. Technical Contracts & API Specifications

### 2.1 Module 10: Tool Confirmation Specification
```python
from google.adk.tools import FunctionTool

# Static approval requirement
sensitive_tool = FunctionTool(delete_database, require_confirmation=True)

# Dynamic conditional approval predicate
def needs_approval(amount: float, **kwargs) -> bool:
    return amount > 1000.0

transfer_tool = FunctionTool(transfer_funds, require_confirmation=needs_approval)
```

### 2.2 Module 22: Context Optimization & Time-Travel Specification
```python
# Context Caching
from google.adk.apps.app import App
from google.adk.agents.context_cache_config import ContextCacheConfig

app = App(
    name="legal_app",
    root_agent=root_agent,
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,
        ttl_seconds=1800,
        cache_intervals=10,
    ),
)

# Context Compaction
from google.adk.apps.app import EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models import Gemini

app = App(
    name="chat_app",
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=20,
        overlap_size=3,
        summarizer=LlmEventSummarizer(llm=Gemini(model="gemini-3.5-flash")),
    ),
)

# Session Rewind
from google.adk.runners import InMemoryRunner

runner = InMemoryRunner(agent=root_agent, app_name="my_app")
await runner.rewind_async(
    user_id=user_id,
    session_id=session.id,
    rewind_before_invocation_id=invocation_id,
)
```

### 2.3 Module 39: Standard Built-in Plugins Specification
```python
from google.adk.plugins import (
    ReflectAndRetryToolPlugin,
    BigQueryAgentAnalyticsPlugin,
    GlobalInstructionPlugin,
    ContextFilterPlugin,
)

app = App(
    name="enterprise_app",
    root_agent=root_agent,
    plugins=[
        ReflectAndRetryToolPlugin(max_retries=3),
        BigQueryAgentAnalyticsPlugin(project_id="my-gcp-proj", dataset_id="agent_telemetry"),
        GlobalInstructionPlugin(global_instruction="Always adhere to GDPR and SOC2 compliance."),
    ],
)
```

---

## 3. Verification & Testing Strategy
1. **Docusaurus Build Verification**:
   - Command: `npm --prefix doc run build`
   - Verify zero build errors, zero broken markdown tags, zero missing imports or broken links.
2. **Pedagogical Consistency**:
   - Ensure all model mentions adhere strictly to user memory rule: `gemini-3.5-flash`.
   - Maintain image links (`#gh-light-mode-only` / `#gh-dark-mode-only`) and existing visual headers.

---

## 4. Boundaries & Constraints
- ZERO modification to module directory names or numbering.
- ZERO modification to existing visual assets.
- Clean git commits on `feat-adk2-advanced-features`.
