---
sidebar_position: 22
title: "Module 22: State and Memory - Persistent Agent Context"
pagination_label: "Module 22: State & Memory Management — 📖 Theory & Overview"
---

# Module 22: State and Memory - Persistent Agent Context

![Persistent Agent State & Memory Architecture (Light)](img/hero-light.webp#gh-light-mode-only)
![Persistent Agent State & Memory Architecture (Dark)](img/hero-dark.webp#gh-dark-mode-only)

## Theory

### Giving Agents Memory: Sessions vs. Long-Term Memory

Welcome to **Part 4: Production Readiness**. In Part 3, you learned how to orchestrate multiple specialized agents into teams and workflows. To make those systems truly production-ready, an agent cannot treat every turn like a stranger walking in for the first time—it needs **context continuity**.

Google ADK separates conversational continuity into two distinct, complementary subsystems:

| Dimension | `Session` (`SessionService`) | Long-Term `Memory` (`MemoryService`) |
| :--- | :--- | :--- |
| **Mental Model** | **The Active Workbench** (current conversation thread & scratchpad) | **The Searchable Archive** (filing cabinet of past knowledge) |
| **Data Stored** | Ordered `events` ledger + structured key-value `state` | Distilled facts, semantic memories, or indexed past transcripts |
| **How Data Is Read** | Automatically loaded on every turn by `(app_name, user_id, session_id)` | Queried via `search_memory(app_name=..., user_id=..., query=...)` |
| **Primary Use Case** | Multi-turn dialogue history, active workflow progress, user preferences | Recalling unstructured insights discussed weeks ago across threads |
| **Built-in Backends** | `InMemorySessionService`, `DatabaseSessionService`, `VertexAiSessionService` *(+ CLI `SqliteSessionService`)* | `InMemoryMemoryService`, `SqliteMemoryService`, `VertexAiMemoryBankService`, `VertexAiRagMemoryService` |

---

### Anatomy of an ADK `Session`

Every conversation in ADK is represented by a `google.adk.sessions.Session` Pydantic model and uniquely addressed by a **3-part composite coordinate**:

```text
(app_name, user_id, session_id)
```

When a `Runner` loads or creates a `Session`, it populates six core attributes:

```python
from google.adk.sessions import Session

# Conceptual inspection of a live Session instance:
# session.id               -> str: Unique thread ID (e.g., "session_math_1")
# session.app_name         -> str: Application namespace (e.g., "personal_tutor")
# session.user_id          -> str: Caller identity (e.g., "student_42")
# session.state            -> dict[str, Any]: Merged key-value state dictionary
# session.events           -> list[Event]: Chronological append-only turn ledger
# session.last_update_time -> float: Unix timestamp of the most recent event
```

Understanding the 3-part coordinate `(app_name, user_id, session_id)` makes **State Scoping** intuitive—each prefix simply binds a key to a broader or narrower slice of that coordinate!

---

### Session State (`session.state`) & Scoped Prefixes

`session.state` is a structured key-value dictionary used to personalize behavior, track multi-step workflow progress, and pass structured outputs between agents. ADK routes keys to different persistence scopes based on their prefix:

| Prefix | Bound Coordinate | Persistence | Example Use Case |
| :--- | :--- | :--- | :--- |
| *(None)* | `(app_name, user_id, session_id)` | Current session only | `state['current_topic'] = 'asyncio'` — Active lesson progress |
| `user:` | `(app_name, user_id)` | Shared across **all sessions** for that user | `state['user:language'] = 'es'` — Persistent user preferences |
| `app:` | `(app_name)` | Shared across **all users and sessions** | `state['app:course_version'] = '2.1'` — Global configuration |
| `temp:` | Current `invocation_id` only | **Never persisted** to storage | `state['temp:quiz_percentage'] = 92.5` — Single-turn scratch math |

> **Note (`temp:` State Visibility):** Although `temp:` keys are stripped before storage commit and never survive into the next user turn, they remain visible inside the live `Event` stream and the Dev UI **Trace View** during the current turn—making `temp:` ideal for passing transient calculations between tools or nodes within a single invocation without polluting persistent state.

> **Security & Multi-Tenant Hygiene:**
> * **Never store secrets, API keys, or OAuth tokens in `session.state`** (even under `temp:`): persistent scopes are written as JSON in database tables, and `temp:` deltas are emitted in live event traces. Store credentials in Secret Manager, environment variables, or ADK `AuthCredential` stores.
> * **Mind `app:` blast radius & `user:` retention:** `app:` keys are merged into **every user's** session—never write user- or tenant-specific data into `app:*`. Conversely, `delete_session()` removes session events while preserving `user:*` profile keys, so handle GDPR erasure requests explicitly on user state.

![Session State Scoped Persistence Pipeline (Light)](img/session-state-pipeline-light.webp#gh-light-mode-only)
![Session State Scoped Persistence Pipeline (Dark)](img/session-state-pipeline-dark.webp#gh-dark-mode-only)
*Figure: Scoped session state lifecycle and persistence pipeline from ephemeral turn scratchpad to durable storage tables.*

---

### How Event-Sourced State Mutation Works (`EventActions.state_delta`)

A critical architectural rule in ADK is that **state is event-sourced**. Calling `await session_service.get_session(...)` returns a **detached snapshot** of the session. Mutating `session.state["key"] = "value"` directly on that snapshot in external Python code will **not** persist to the database!

Instead, every durable state change is recorded as a `state_delta` inside `EventActions` and committed atomically through `session_service.append_event(session, event)`:

```mermaid
sequenceDiagram
    participant T as Tool / Callback / Agent
    participant R as ADK Runner
    participant S as SessionService
    participant DB as Storage Tables (App / User / Session)

    T->>R: tool_context.state["user:language"] = "es"
    T->>R: tool_context.state["temp:raw_score"] = 9
    R->>S: append_event(session, Event(actions=EventActions(state_delta=...)))
    Note over S: Strip temp:* keys before persistence
    S->>DB: Upsert user:language into User State Table
    S->>DB: Append Event to Session Ledger
```

#### The 4 Safe Ways to Write State

1. **Inside a Function Tool (`ToolContext`):**
   ```python
   def set_language(lang: str, tool_context: ToolContext) -> dict:
       tool_context.state["user:language"] = lang.strip().lower()[:10]
       return {"status": "saved"}
   ```
2. **Inside a Lifecycle Callback (`CallbackContext`):**
   ```python
   def track_turn(callback_context: CallbackContext):
       callback_context.state["turn_count"] = callback_context.state.get("turn_count", 0) + 1
   ```
3. **Automatically via Agent `output_key`:**
   ```python
   summarizer = Agent(
       name="summarizer",
       model="gemini-3.8-flash",
       instruction="Summarize the lesson in 2 bullet points.",
       output_key="last_lesson_summary",  # Emits state_delta={"last_lesson_summary": ...}
   )
   ```
4. **Seeding Initial State (`create_session`) or External System Updates (`append_event`):**
   ```python
   from google.adk.events import Event, EventActions

   # A. Seed initial state when creating a session:
   session = await session_service.create_session(
       app_name="personal_tutor",
       user_id="student_42",
       session_id="session_1",
       state={"app:course_version": "2.1"},
   )

   # B. Commit an out-of-band system state update on an existing session:
   await session_service.append_event(
       session,
       Event(
           author="system",
           invocation_id="sys_sync_1",
           actions=EventActions(state_delta={"user:tier": "pro"}),
       ),
   )
   ```

---

### Accessing State in Instructions: `{key}` vs. `{key?}`

ADK automatically interpolates session state values into an agent's `instruction` string right before calling the model:

* **`{current_topic}` (Required Key):** Replaces the placeholder with `session.state["current_topic"]`. If the key is missing from `state`, ADK raises a `KeyError`—helpful in deterministic multi-agent pipelines (Modules 17–18) to catch broken upstream handoffs early.
* **`{app:course_version?}` (Optional Key — trailing `?`):** Replaces the placeholder with the value if present, or cleanly substitutes an empty string `""` if the key has not been initialized yet. *(Tip: when interpolating user-supplied state like `{user:language?}`, validate/allowlist values inside your tool first so untrusted text cannot inject instructions.)*

```python
from google.adk.agents import Agent

tutor = Agent(
    name="personal_tutor",
    model="gemini-3.8-flash",
    instruction=(
        "You are a helpful tutor (Catalog {app:course_version?}). "
        "Adapt explanations to the user's preferred language: {user:language?}."
    ),
)
```

---

### `SessionService` Lifecycle & Storage Backends

Every ADK `Runner` delegates session persistence to an implementation of `BaseSessionService`, exposing four asynchronous keyword-only CRUD operations:

```python
# 1. Create a new session (with optional custom session_id and initial state)
session = await session_service.create_session(
    app_name="tutor_app",
    user_id="student_42",
    session_id="session_1",
    state={"app:course_version": "2.1"},
)

# 2. Retrieve an existing session snapshot (returns None if not found)
loaded = await session_service.get_session(
    app_name="tutor_app",
    user_id="student_42",
    session_id="session_1",
)

# 3. List all sessions for a user (or across the entire app if user_id is omitted)
response = await session_service.list_sessions(
    app_name="tutor_app",
    user_id="student_42",
)
print([s.id for s in response.sessions])

# 4. Delete a session (removes session-scoped events/state; preserves user: & app: state!)
await session_service.delete_session(
    app_name="tutor_app",
    user_id="student_42",
    session_id="session_1",
)
```

#### Choosing the Right `SessionService` Backend

| Backend | Import / Extra | Concurrency & Best Fit |
| :--- | :--- | :--- |
| **`InMemorySessionService`** | `google.adk.sessions` (core) | **Volatile RAM.** Lost when the Python process exits. Best for fast unit tests and `InMemoryRunner`. |
| **`SqliteSessionService`** | `google.adk.sessions.sqlite_session_service` (core `aiosqlite`) | **Local CLI SQLite** (`sqlite:///`). Lightweight JSON schema used internally by `adk web`'s default `.adk/session.db`. Single-process local dev only. |
| **`DatabaseSessionService`** | `google.adk.sessions` (`google-adk[db]`) | **SQLAlchemy 2.0 Async Relational Store.** Use `sqlite+aiosqlite:///` for **single-instance local/CI testing**, and `postgresql+asyncpg://` (Cloud SQL / AlloyDB) or Cloud Spanner for **multi-worker production** with row-level `SELECT ... FOR UPDATE` locking. |
| **`VertexAiSessionService`** | `google.adk.sessions` + Vertex AI | **Fully Managed Cloud Service** (`agentengine://...`). Serverless horizontal scaling on Cloud Run / GKE / Agent Engine with zero database ops. |
| **Custom `BaseSessionService`** | Subclass `BaseSessionService` | **NoSQL / Custom Stores** (such as the Cloud Firestore provider you built in Module 13.5). |

#### Programmatic Example with `DatabaseSessionService`

Always manage `DatabaseSessionService` with `async with` in standalone scripts (or close it during FastAPI app lifespan shutdown). Under the hood, `aiosqlite` and `asyncpg` maintain background worker threads/socket pools—disposing the engine cleanly ensures `asyncio.run(...)` exits immediately without hanging:

```python
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService

# Single-instance local dev: "sqlite+aiosqlite:///./tutor_sessions.db"
# Multi-replica Cloud Run / GKE: "postgresql+asyncpg://user:pass@host:5432/dbname"
async with DatabaseSessionService(
    db_url="sqlite+aiosqlite:///./tutor_sessions.db"
) as session_service:
    runner = Runner(
        app_name="tutor_app",
        agent=root_agent,
        session_service=session_service,
    )
    # Any user: or app: state written during runner.run_async() is now persisted on disk!
```

> **Important — How `uv run adk web` Persists Sessions & CLI Flags:**
> In ADK 2.0+, `adk web` (intended strictly for local development on `127.0.0.1`) enables `--use_local_storage` by default, writing sessions to `<agent_folder>/.adk/session.db` via `SqliteSessionService`! You can switch backends from the CLI *(note: `--session_service_uri` cannot be combined with `--[no_]use_local_storage`)*:
> * **Default local `.adk/` SQLite:** `uv run adk web`
> * **Pure ephemeral RAM (reset on restart):** `uv run adk web --no_use_local_storage` *(or `--session_service_uri="memory://"`)*
> * **SQLite (`SqliteSessionService` schema):** `uv run adk web --session_service_uri="sqlite:///./local_dev.db"`
> * **SQLAlchemy (`DatabaseSessionService`, requires `google-adk[db]` + async driver):** `uv run adk web --session_service_uri="sqlite+aiosqlite:///./tutor_sessions.db"` or `"postgresql+asyncpg://user:pass@host:5432/dbname"`

---

### Managing Long Sessions: Rewind, Caching & Compaction

#### 1. Session Rewind (`runner.rewind_async`)

ADK supports **rewinding** an active session to a point prior to a specific `invocation_id`—useful when a user cancels an action or wants to retry a quiz from an earlier turn:

* **Restored:** Session-scoped state keys (keys created after the rewind point are reset to `None`) and session artifacts.
* **Preserved (NOT rewound):** Persistent `user:` and `app:` state, plus external side effects (such as emails already sent).

```python
await runner.rewind_async(
    user_id="student_42",
    session_id="session_1",
    rewind_before_invocation_id=target_invocation_id,
)
```

#### 2. Context Caching (`ContextCacheConfig`)

When agents include large static system instructions or reference manuals, resending those tokens on every turn increases latency and cost. `ContextCacheConfig` caches immutable prompt prefixes on Gemini:

```python
from google.adk.apps.app import App
from google.adk.agents.context_cache_config import ContextCacheConfig

app = App(
    name="enterprise_analyst",
    root_agent=root_agent,
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,     # Cache only if system context exceeds 2,048 tokens
        ttl_seconds=1800,    # Cache Time-To-Live in seconds (30 minutes)
        cache_intervals=10,  # Refresh cache every N invocations
    ),
)
```

#### 3. Context Compaction (`EventsCompactionConfig`)

In long multi-turn tutoring or support sessions, raw `session.events` history grows continuously. **Context Compaction** applies sliding-window LLM summarization over older events while keeping recent turns intact:

```python
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models import LLMRegistry

app = App(
    name="long_running_assistant",
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=20,  # Trigger summarization every 20 invocations
        overlap_size=3,          # Keep the 3 most recent turns uncompressed
        summarizer=LlmEventSummarizer(llm=LLMRegistry.new_llm("gemini-3.8-flash")),
    ),
)
```

---

### Long-Term Recall with `MemoryService`

While `user:` state is ideal for **structured key-value attributes** (language, tier, completed topic IDs), `MemoryService` is designed for **unstructured cross-session recall**—answering open-ended questions like *"What struggle did I have when we studied recursion last month?"*.

* **`InMemoryMemoryService` / `SqliteMemoryService`:** Lightweight keyword-based recall over ingested sessions for local prototyping and CLI testing.
* **`VertexAiMemoryBankService`:** Managed Google Cloud service that uses LLM-powered **Memory Extraction & Consolidation** to turn raw chat logs into semantic user memories.

**Standard 3-Step Workflow:**

```python
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.tools import load_memory

memory_service = InMemoryMemoryService()

# 1. Ingest a completed Session into long-term memory
completed_session = await session_service.get_session(
    app_name="tutor_app", user_id="student_42", session_id="session_1"
)
await memory_service.add_session_to_memory(completed_session)

# 2. Query memories programmatically across past sessions
results = await memory_service.search_memory(
    app_name="tutor_app",
    user_id="student_42",
    query="recursion base cases",
)

# 3. Wire memory_service into Runner and equip your Agent with load_memory
tutor_with_recall = Agent(
    name="tutor_with_recall",
    model="gemini-3.8-flash",
    instruction="Use load_memory whenever the student asks about past lessons.",
    tools=[load_memory],
)
runner = Runner(
    app_name="tutor_app",
    agent=tutor_with_recall,
    session_service=session_service,
    memory_service=memory_service,
)
```

---

### Interactive Knowledge Checks

<KnowledgeCheck
  id="m22-state-scoping-prefixes"
  question="In ADK 2.0 State Management, which state prefix ensures a stored value is shared across all future sessions belonging to the same user rather than being restricted to a single session or turn?"
  options={[
    "user: (e.g., tool_context.state['user:language'] = 'es')",
    "temp: (e.g., tool_context.state['temp:quiz_score'] = 95)",
    "global: (e.g., tool_context.state['global:setting'] = True)",
    "app: (e.g., tool_context.state['app:course_version'] = '2.1')"
  ]}
  correctIndex={0}
  hint="Review how the 4 state prefixes map onto the (app_name, user_id, session_id) coordinate."
  explanation="Keys prefixed with 'user:' are bound to (app_name, user_id) and automatically merged into every session created for that user. Unprefixed keys stay isolated to a single session_id, 'app:' is shared across all users, and 'temp:' is discarded at the end of the turn."
/>

<KnowledgeCheck
  id="m22-event-sourced-session-mutation"
  question="Why does mutating session.state['topic'] = 'SQL' directly on a Session object returned by session_service.get_session() fail to persist in DatabaseSessionService?"
  options={[
    "Because ADK state dictionaries become immutable once create_session() finishes running in Python.",
    "Because get_session() returns a detached snapshot; durable writes flow through EventActions(state_delta=...) via tool_context.state, callback_context.state, output_key, or append_event().",
    "Because SQLAlchemy async engines only permit storing numeric integer values inside session state.",
    "Because unprefixed state keys are stripped before storage commit identically to temp: scratchpad keys."
  ]}
  correctIndex={1}
  hint="Recall the Event-Sourced State Mutation diagram: how does SessionService know which keys changed?"
  explanation="ADK uses event-sourced state persistence. Modifying tool_context.state or callback_context.state (or setting output_key) packages an Event with EventActions(state_delta={...}) that SessionService.append_event() commits atomically to the backing database."
/>

### Key Takeaways
- **Composite Session Identity:** Every `Session` is uniquely addressed by `(app_name, user_id, session_id)` and holds an append-only `events` list plus a merged `state` dictionary.
- **Four State Scopes:** Unprefixed keys stay in one `session_id`; `user:` spans all sessions for a `user_id`; `app:` spans all users of an `app_name`; `temp:` vanishes when the current turn ends.
- **Event-Sourced Writes:** Always mutate state via `tool_context.state`, `callback_context.state`, `output_key`, `create_session(..., state=...)`, or `append_event()` so changes persist through `EventActions.state_delta`.
- **Dynamic Instructions:** Use `{key}` for required state interpolation and `{key?}` for optional keys that may not be initialized yet.
- **Pluggable `SessionService` Backends:** `adk web` persists locally to `.adk/` SQLite by default; production deployments use `DatabaseSessionService` (`postgresql+asyncpg://`) or `VertexAiSessionService`.
- **Session vs. Memory:** Use `Session` (`SessionService`) for active thread history and structured state, and `MemoryService` (`add_session_to_memory` / `search_memory`) for searchable cross-session recall.
