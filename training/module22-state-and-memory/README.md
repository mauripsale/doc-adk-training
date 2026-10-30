---
sidebar_position: 22
title: "Module 22: State and Memory - Persistent Agent Context"
pagination_label: "Module 22: State & Memory Management — 📖 Theory & Overview"
---

# Module 22: State and Memory - Persistent Agent Context

![Persistent Agent State & Memory Architecture (Light)](img/hero-light.webp#gh-light-mode-only)
![Persistent Agent State & Memory Architecture (Dark)](img/hero-dark.webp#gh-dark-mode-only)

## Theory

### Giving Agents Memory

Welcome to **Part 4: Production Readiness**. You've spent Part 3 learning to orchestrate multiple agents into real systems -- now it's time to make those systems production-ready, starting with the most basic requirement of all: an agent that actually remembers things.

A key feature that elevates a simple chatbot to a capable assistant is **memory**. The ADK provides a robust system for managing two different kinds of memory: short-term **State** and long-term **Memory**.

### Session State (`session.state`)

The agent's **scratchpad**—a key-value dictionary for conversation-level data. It is used to:
*   **Personalize Interaction:** Remember user preferences (e.g., 'user:theme': 'dark').
*   **Track Task Progress:** Keep tabs on steps in a process (e.g., 'booking_step': 'confirm').
*   **Accumulate Information:** Build lists (e.g., 'cart': ['book', 'pen']).

**State Scoping with Prefixes**:

| Prefix  | Scope                   | Persistence              | Example Use Case                                             |
| ------- | ----------------------- | ------------------------ | ------------------------------------------------------------ |
| None    | Current session         | SessionService dependent | `state['current_topic'] = 'python'` - Task progress          |
| `user:` | All sessions for user   | Persistent               | `state['user:preferred_language'] = 'en'` - User preferences |
| `app:`  | All users/sessions      | Persistent               | `state['app:course_catalog'] = [...]` - Global settings      |
| `temp:` | Current invocation only | **Never persisted**      | `state['temp:quiz_score'] = 85` - Temporary calculations     |

> **Note on `temp:` State Visibility:** Although `temp:` state is never persisted beyond the current invocation, it is fully visible within the Event Stream and the Dev UI's Trace View during the agent's execution. This makes it a valuable tool for debugging intermediate calculations or temporary data flow within a single turn.

![Session State Scoped Persistence Pipeline (Light)](img/session-state-pipeline-light.webp#gh-light-mode-only)
![Session State Scoped Persistence Pipeline (Dark)](img/session-state-pipeline-dark.webp#gh-dark-mode-only)
*Figure: Scoped session state lifecycle and persistence pipeline from ephemeral turn scratchpad to long-term storage backend.*

### Accessing State in Instructions

You can directly inject session state values into your agent's instructions using `{key}` templating. This makes your prompts dynamic and context-aware.

```python
agent = Agent(
    name="StoryGenerator",
    instruction="Write a story about a cat with the theme: {current_topic}."
)
```
If `state['current_topic']` is "space exploration", the LLM sees: "...theme: space exploration."

### Updating State Correctly

**⚠️ Important:** The safest way to modify state is through the `Context` object provided to your tools or callbacks.

*   **In Tools:** `tool_context.state['key'] = 'value'`
*   **In Callbacks:** `callback_context.state['key'] = 'value'`

Avoid modifying the `session.state` directly on a Session object retrieved via `session_service.get_session()` outside of a managed flow, as this bypasses the event system and may lead to data loss or race conditions.

### Session Rewind

The ADK supports **rewinding** a session to a previous point. This is useful for undoing mistakes, handling user cancellations, or exploring alternative conversation branches during interactive debugging.

*   **How it works:** You specify an `invocation_id` to rewind *before*. The system restores the session-level state dictionary and artifacts to that exact moment.
*   **What is restored:** Session-level state and session artifacts.
*   **What is NOT restored:** Persistent scopes like `app:` or `user:` state, and external side-effects (like external database rows already modified).

```python
from google.adk.runners import InMemoryRunner

runner = InMemoryRunner(agent=root_agent, app_name="my_app")

# Rewind session state and artifacts to before a specific turn
await runner.rewind_async(
    user_id="user_123",
    session_id=session.id,
    rewind_before_invocation_id=target_invocation_id,
)
```

### Context Caching (`ContextCacheConfig`)

In applications where agents use extensive system instructions, large few-shot prompt libraries, or fixed reference documents, sending those tokens on every turn increases latency and costs. 

ADK 2.0 provides **Context Caching** configured directly at the `App` or `Agent` level:

```python
from google.adk.apps.app import App
from google.adk.agents.context_cache_config import ContextCacheConfig

app = App(
    name="enterprise_analyst",
    root_agent=root_agent,
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,     # Cache only if system context exceeds 2,048 tokens
        ttl_seconds=1800,    # Cache Time-To-Live in seconds (e.g. 30 minutes)
        cache_intervals=10,  # Refresh cache every N invocations
    ),
)
```
*Result:* Gemini caches the immutable token prefix in memory on Google Cloud, reducing time-to-first-token (TTFT) and input token costs by up to 80%.

### Context Compaction (`EventsCompactionConfig`)

For long-running, multi-turn customer support or coding workflows, conversation history eventually exceeds model context limits or slows down response times. 

**Context Compaction** automatically applies sliding-window LLM summarization over older events:

```python
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models import Gemini

app = App(
    name="long_running_assistant",
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=20,  # Trigger summarization every 20 events
        overlap_size=3,          # Keep last 3 events uncompressed for seamless continuity
        summarizer=LlmEventSummarizer(llm=Gemini(model="gemini-3.8-flash")),
    ),
)
```

### Memory Service

The Memory Service provides **long-term, searchable memory** for your agent, like an archive of past conversations across sessions.

**Implementations**:

1.  **`InMemoryMemoryService`**: A simple, non-persistent keyword search for development and testing. Stores full conversation history.
2.  **`VertexAiMemoryBankService`**: A production-grade service managed by Google Cloud. It uses semantic search and "Memory Extraction" to consolidate meaningful information rather than just storing raw logs.

**Workflow**:

1.  **Ingest:** After a meaningful conversation, call `memory_service.add_session_to_memory(session)`.
2.  **Recall:** In a future session, use a tool to call `memory_service.search_memory(query)`.
3.  **Act:** The agent uses the retrieved context to answer questions like "What did we discuss last week?".

<KnowledgeCheck
  id="m22-state-scoping-prefixes"
  question="In ADK 2.0 State Management, which state prefix ensures a stored value is isolated to the current user across all their sessions rather than being restricted to a single ephemeral turn?"
  options={[
    "user: (e.g. session.state['user:preference'])",
    "temp: (e.g. session.state['temp:query'])",
    "global: (e.g. session.state['global:setting'])",
    "app: (e.g. session.state['app:config'])"
  ]}
  correctIndex={0}
  hint="Review the state scoping prefixes: session vs user vs app vs temp."
  explanation="In ADK 2.0, state keys prefixed with 'user:' persist across distinct sessions for the identified user, whereas standard unprefixed keys belong to the active session, and 'temp:' keys are discarded after the turn."
/>

### Key Takeaways
- **Session State** manages short-term context with scoped prefixes (`user:`, `app:`, `temp:`).
- **Inject State** directly into instructions using `{key}` syntax for dynamic behavior.
- **Update State** via `tool_context` or `callback_context` to ensure safety and persistence.
- **Session Rewind** (`runner.rewind_async`) allows reverting a conversation to a previous turn.
- **Context Caching** (`ContextCacheConfig`) cuts cost and latency on large static prompts.
- **Context Compaction** (`EventsCompactionConfig`) compresses long histories via sliding-window summarization.
- **Memory Service** provides cross-session long-term recall (`VertexAiMemoryBankService`).