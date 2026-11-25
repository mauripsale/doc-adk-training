---
title: "Challenge Lab"
pagination_label: "Module 22: State & Memory Management — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Module 22: State and Memory - Building a Personal Tutor Agent

## Lab 22: Building a Personal Learning Tutor

### Goal

In this lab, you will put ADK's session architecture into practice by building a **Personal Learning Tutor** that leverages all four state scopes (`user:`, `app:`, unprefixed session state, and `temp:`), inspecting live `state_delta` events in `adk web`, and programmatically persisting multi-session state to a local SQLite database with `DatabaseSessionService` alongside `InMemoryMemoryService`.

### The Use Case

You will build and verify a tutor system that:
* Stores a student's preferences (`language`, `difficulty_level`) and completed study history in **`user:`** state so they survive across every new session.
* Tracks the active lesson topic in unprefixed **session** state so each conversation thread stays independent.
* Uses **`temp:`** state for single-turn quiz grading math that is discarded immediately after the turn.
* Dynamically injects global catalog metadata from **`app:`** state into the system prompt via `{app:course_version?}`.
* Persists multiple sessions onto disk using **`DatabaseSessionService`** (`sqlite+aiosqlite`) and archives completed sessions into **`InMemoryMemoryService`**.

---

### Step 1: Create the Project Structure

<Setup/>

From your `adk-training` workspace directory, scaffold the `personal_tutor` agent package *(stay inside `adk-training` for all subsequent commands!)*:

```shell
uv run adk create personal_tutor
```
Select any default model/backend prompt during creation—you will configure `gemini-3.8-flash` explicitly in `personal_tutor/agent.py` next.

---

### Step 2: Implement the State-Management Tools (`personal_tutor/agent.py`)

**Exercise:** Open `personal_tutor/agent.py`, replace its contents with the starter skeleton below, and complete every `# TODO:` using `tool_context.state` and the appropriate scoping prefixes (`user:`, `temp:`, or unprefixed session keys) from the **Theory** tab.

```python
# personal_tutor/agent.py (Starter Code)

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext

load_dotenv(Path(__file__).with_name(".env"), override=True)

ALLOWED_DIFFICULTIES = {"beginner", "intermediate", "advanced"}

# ============================================================================
# TOOLS: State Management & Memory Operations
# ============================================================================


def set_user_preferences(
    language: str,
    difficulty_level: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """
    Set user learning preferences (stored persistently across all sessions).

    Args:
        language: Preferred language code or name (en, es, fr, it, etc.)
        difficulty_level: beginner, intermediate, or advanced
    """
    # TODO: Normalize/validate inputs (e.g., fallback to 'beginner' if difficulty_level
    # is not in ALLOWED_DIFFICULTIES) and save 'user:language' and 'user:difficulty_level'
    # in tool_context.state so they persist across all sessions for this user.
    pass

    return {
        "status": "success",
        "message": f"Preferences saved: {language}, {difficulty_level} level",
    }


def record_topic_completion(
    topic: str,
    quiz_score: int,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """
    Record that the user completed a topic (stored persistently across sessions).

    Args:
        topic: Topic name (e.g., "Python Basics", "Data Structures")
        quiz_score: Score out of 100
    """
    # TODO: Read 'user:topics_covered' (list) and 'user:quiz_scores' (dict) from state,
    # append/update them with the new topic and quiz_score, and write them back to state.
    # Tip: Wrap retrieved values in list(...) and dict(...) before mutating!
    topics = []  # Placeholder

    return {
        "status": "success",
        "topics_count": len(topics),
        "message": f"Recorded: {topic} with score {quiz_score}/100",
    }


def get_user_progress(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Get the user's learning progress summary across all sessions.
    """
    # TODO: Read 'user:language', 'user:difficulty_level', 'user:topics_covered',
    # and 'user:quiz_scores' from tool_context.state and compute the average score.
    language = "en"
    difficulty = "beginner"
    topics = []
    scores = {}
    avg_score = 0.0

    return {
        "status": "success",
        "language": language,
        "difficulty_level": difficulty,
        "topics_completed": len(topics),
        "topics": topics,
        "average_quiz_score": round(avg_score, 1),
        "all_scores": scores,
    }


def start_learning_session(
    topic: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """
    Start a new learning session for a topic.

    Uses unprefixed session state to track the active topic in this session only.
    """
    # TODO: Store 'current_topic' and an ISO-8601 'session_start_time'
    # (datetime.now(timezone.utc).isoformat()) in session-scoped state (no prefix).
    # TODO: Read the user's persistent difficulty level (defaulting to 'beginner').
    difficulty = "beginner"

    return {
        "status": "success",
        "topic": topic,
        "difficulty_level": difficulty,
        "message": f"Started learning session: {topic} at {difficulty} level",
    }


def calculate_quiz_grade(
    correct_answers: int,
    total_questions: int,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """
    Calculate a quiz grade using temporary invocation-scoped state (temp:).
    """
    # TODO: Guard against total_questions <= 0, compute percentage, store 'temp:raw_score'
    # and 'temp:quiz_percentage' in temporary state, and assign a letter grade
    # ('A' >= 90, 'B' >= 80, 'C' >= 70, 'D' >= 60, else 'F').
    percentage = 0.0
    grade = "F"

    return {
        "status": "success",
        "score": f"{correct_answers}/{total_questions}",
        "percentage": round(percentage, 1),
        "grade": grade,
        "message": f"Quiz grade: {grade} ({percentage:.1f}%)",
    }


def search_past_lessons(
    query: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """
    Search past learning history for relevant completed topics.
    """
    # TODO: Read 'user:topics_covered' from state and filter topics matching query.lower().
    return {
        "status": "success",
        "found": False,
        "message": f'No past sessions found for "{query}"',
    }


# ============================================================================
# AGENT DEFINITION
# ============================================================================

# TODO: Instantiate root_agent with model="gemini-3.8-flash", all 6 tools,
# output_key="last_tutor_response", and an instruction that includes {app:course_version?}
# so global app state is dynamically interpolated when present!
root_agent = None
```

---

### Step 3: Inspect Live Sessions & Scoped State in `adk web`

1. Verify your credentials in `personal_tutor/.env`.
2. From your `adk-training` workspace directory, launch the Dev UI:
   ```shell
   uv run adk web
   ```
3. Select **`personal_tutor`** from the agent dropdown and test the 4 state scopes:
   * In the chat input bar, click the **Actions (`+`)** button → **Update state**, enter `{"app:course_version": "2.1"}`, and send: *"Set my preferred language to Italian at intermediate level, and start a session on Python Decorators."*
   * Open the **State** tab in the left panel to inspect the live merged dictionary, and check the **Events / Trace** view to see `EventActions(state_delta=...)` emitted by your tools!
   * Click **+ New Session** in the top bar and ask: *"What is my progress and what topic are we studying right now?"* Notice how `user:language` (`Italian`) and `app:course_version` (`2.1`) carried over into the new `session_id`, while `current_topic` started clean!
   * **Local Storage Under the Hood:** Stop (`Ctrl+C`) and restart `uv run adk web`. Because ADK 2.0+ enables `--use_local_storage` by default (`personal_tutor/.adk/session.db`), your sessions and `user:`/`app:` state survive server restarts! Try `uv run adk web --no_use_local_storage` whenever you want volatile RAM-only testing instead.

---

### Step 4: Programmatic SQLite Persistence (`DatabaseSessionService`) & `MemoryService`

Now let's build a standalone Python script that wires `Runner` to both `DatabaseSessionService` (`sqlite+aiosqlite`) and `InMemoryMemoryService`, proving multi-session scoping on disk plus cross-session recall.

1. From your `adk-training` workspace directory, install the ADK SQLAlchemy database extra *(or `uv pip install "google-adk[db]"` if running inside a non-`pyproject.toml` container)*:
   ```shell
   uv add "google-adk[db]"
   ```
2. Create `personal_tutor/test_session_persistence.py` using the starter skeleton below and complete the `# TODO:` steps:

```python
# personal_tutor/test_session_persistence.py (Starter Code)

import asyncio
from pathlib import Path

from dotenv import load_dotenv
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

from agent import root_agent

load_dotenv(Path(__file__).with_name(".env"), override=True)


async def test_sqlite_sessions():
    db_file = Path(__file__).resolve().with_name("tutor_sessions.db")
    if db_file.exists():
        db_file.unlink()

    db_url = f"sqlite+aiosqlite:///{db_file.as_posix()}"
    app_name = "personal_tutor_app"
    user_id = "student_42"
    memory_service = InMemoryMemoryService()

    # TODO 1: Open DatabaseSessionService(db_url=db_url) using `async with ... as session_service:`
    # and instantiate a `Runner` bound to app_name, root_agent, session_service, and memory_service.

    # TODO 2: Create "session_1" via `await session_service.create_session(...)`
    # seeded with state={"app:course_version": "2.1", "current_topic": "Onboarding"}.

    # TODO 3: Run one user turn on "session_1" via `runner.run_async(...)` asking the tutor
    # to set language="Spanish", difficulty="intermediate", and start a session on "Python Asyncio".
    # Then reload "session_1" via `get_session(...)`, archive it with
    # `await memory_service.add_session_to_memory(s1_loaded)`, and query `memory_service.search_memory(...)`!

    # TODO 4: Create a brand-new "session_2" for the SAME user_id ("student_42")
    # and print `session_2.state` to verify that `app:*` and `user:*` persisted across sessions
    # while unprefixed session keys (`current_topic`, `last_tutor_response`) started clean!

    # TODO 5: Call `await session_service.list_sessions(app_name=app_name, user_id=user_id)`
    # and print the list of stored session IDs from SQLite.
    pass


if __name__ == "__main__":
    asyncio.run(test_sqlite_sessions())
```

3. Run your persistence verification script from `adk-training`:
   ```shell
   uv run python personal_tutor/test_session_persistence.py
   ```
   Confirm in the terminal output that `MemoryService` recalls `Asyncio`, `session_2.state` inherits `app:course_version` and your `user:*` preferences from `tutor_sessions.db`, and `list_sessions()` reports `['session_1', 'session_2']`!

---

### Step 5 (Bonus Challenge): Context Compaction & Session Rewind

For fast finishers: in long-running tutoring threads, you can configure automatic sliding-window summarization (`EventsCompactionConfig`) and roll back an accidental turn (`runner.rewind_async`).

**Exercise:** Create `personal_tutor/test_memory_advanced.py` and complete the `# TODO:` markers:

```python
# personal_tutor/test_memory_advanced.py (Bonus Starter Code)

import asyncio
from pathlib import Path

from dotenv import load_dotenv
from google.adk.apps.app import App
from google.adk.runners import InMemoryRunner
from google.genai import types

from agent import root_agent

# TODO 1: Import EventsCompactionConfig (from google.adk.apps.app),
# LlmEventSummarizer (from google.adk.apps.llm_event_summarizer),
# and LLMRegistry (from google.adk.models).

load_dotenv(Path(__file__).with_name(".env"), override=True)


async def test_advanced_memory():
    # TODO 2: Instantiate EventsCompactionConfig with compaction_interval=2,
    # overlap_size=1, and summarizer=LlmEventSummarizer(llm=LLMRegistry.new_llm("gemini-3.8-flash")).
    compaction_config = None

    app = App(
        name="advanced_tutor_app",
        root_agent=root_agent,
        events_compaction_config=compaction_config,
    )

    async with InMemoryRunner(app=app) as runner:
        user_id = "student_42"
        session_id = "session_math_1"
        await runner.session_service.create_session(
            app_name=app.name,
            user_id=user_id,
            session_id=session_id,
        )

        # TODO 3: Run Turn 1 (setting preferences), Turn 2 (starting Python Lists),
        # and Turn 3 (starting an accidental topic like Quantum Tensor Calculus).
        # Capture `event.invocation_id` from Turn 3, then call:
        # await runner.rewind_async(user_id=user_id, session_id=session_id, rewind_before_invocation_id=...)
        # Print rewound.state afterward to verify session state rolled back while user: state stayed intact!


if __name__ == "__main__":
    asyncio.run(test_advanced_memory())
```

Run it from `adk-training` with:
```shell
uv run python personal_tutor/test_memory_advanced.py
```

---

### Lab Summary

You have built and verified a stateful Personal Learning Tutor backed by real ADK session management:
* Scoped state cleanly across `user:`, `app:`, unprefixed session keys, and ephemeral `temp:` keys.
* Interpolated optional state into instructions with `{app:course_version?}`.
* Inspected `EventActions(state_delta=...)` and `.adk/` local SQLite storage in `adk web`.
* Persisted multi-session state onto disk with `DatabaseSessionService` (`sqlite+aiosqlite`), archived sessions into `InMemoryMemoryService`, and queried sessions via `create_session`, `get_session`, and `list_sessions`.
* *(Bonus)* Configured `EventsCompactionConfig` and rolled back session-scoped state with `runner.rewind_async`.

### Self-Reflection & Interactive Knowledge Checks

<KnowledgeCheck
  id="m22-temp-state-scope"
  question="Why is the 'temp:' state prefix automatically stripped before SessionService commits an event to storage?"
  options={[
    "To save browser localStorage quota on the frontend client.",
    "To prevent single-turn scratchpad calculations or transient values from polluting persistent session context across future turns.",
    "Because Gemini models reject any state key containing a colon character.",
    "To automatically trigger sliding-window event compaction after every message."
  ]}
  correctIndex={1}
  hint="Consider what happens when you store a single-turn scratch variable (like a raw quiz percentage) in durable session storage."
  explanation="The 'temp:' prefix is strictly scoped to the current invocation. Stripping it before persistence prevents intermediate scratchpad calculations from cluttering future turns or database tables while still keeping them visible in the current turn's Trace View."
/>

<KnowledgeCheck
  id="m22-database-session-lifecycle"
  question="In Step 4, when you created 'session_2' in DatabaseSessionService for the same user_id ('student_42'), which keys were automatically present in session_2.state?"
  options={[
    "Only unprefixed session keys like current_topic and last_tutor_response.",
    "Both app:* keys and user:* keys for student_42, while unprefixed keys from session_1 were absent.",
    "All temp:* scratchpad keys calculated during session_1.",
    "An empty dictionary because SQLite cannot share state across distinct session IDs."
  ]}
  correctIndex={1}
  hint="Recall how DatabaseSessionService merges global app: state and per-user user: state whenever a new session is created."
  explanation="DatabaseSessionService stores app: and user: state in dedicated tables keyed by app_name and (app_name, user_id). Creating session_2 automatically merges those durable scopes while giving session_2 a clean slate for unprefixed session keys."
/>

<KnowledgeCheck
  id="m22-context-compaction"
  question="How does EventsCompactionConfig with LlmEventSummarizer keep long-running sessions healthy?"
  options={[
    "It deletes the entire session database every 6 turns.",
    "It condenses older conversation events into a structured LLM summary while preserving overlap_size recent events and persistent state keys.",
    "It lowers the Gemini model temperature to zero.",
    "It disables all function tools after 20 turns."
  ]}
  correctIndex={1}
  hint="How can an agent remember what was discussed an hour ago without exhausting the context window?"
  explanation="EventsCompactionConfig triggers LlmEventSummarizer once invocations reach compaction_interval, compressing older turn logs into a concise summary while retaining recent turns (overlap_size) and all structured state."
/>

#### Classroom Debrief Questions

1. How does `uv run adk web` persist sessions locally compared to `InMemorySessionService` and `DatabaseSessionService` (SQLite vs. PostgreSQL)?
2. Why is `temp:` state discarded after each turn, and why must secrets/API keys still never be placed in `temp:`?
3. How does `MemoryService` (`InMemoryMemoryService` / `VertexAiMemoryBankService`) complement `session.state`?
4. When `runner.rewind_async(...)` rolls back a turn, why does `user:` state remain untouched?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="22">

## Lab 22 Solution: Building a Personal Learning Tutor

### Goal

This solution provides the complete implementation for the Personal Learning Tutor (`personal_tutor/agent.py`), the SQLite multi-session persistence & memory archive script (`personal_tutor/test_session_persistence.py`), and the optional context compaction & rewind script (`personal_tutor/test_memory_advanced.py`).

### `personal_tutor/agent.py`

```python
"""
Personal Learning Tutor - Demonstrates Session State & Memory Management

This agent uses:
- user: prefix for persistent preferences (language, difficulty)
- Session state (unprefixed) for current topic tracking
- app: prefix for global catalog metadata ({app:course_version?})
- temp: prefix for single-turn quiz calculations
- Simulated long-term memory search across past lessons
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext

# Load local .env if present (override=True helps override stale shell vars during local labs)
load_dotenv(Path(__file__).with_name(".env"), override=True)

ALLOWED_DIFFICULTIES = {"beginner", "intermediate", "advanced"}

# ============================================================================
# TOOLS: State Management & Memory Operations
# ============================================================================


def set_user_preferences(
    language: str,
    difficulty_level: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """
    Set user learning preferences (stored persistently across all sessions).

    Args:
        language: Preferred language code or name (en, es, fr, it, etc.)
        difficulty_level: beginner, intermediate, or advanced
    """
    clean_lang = language.strip()[:20] or "en"
    norm_diff = difficulty_level.strip().lower()
    if norm_diff not in ALLOWED_DIFFICULTIES:
        norm_diff = "beginner"

    tool_context.state["user:language"] = clean_lang
    tool_context.state["user:difficulty_level"] = norm_diff

    return {
        "status": "success",
        "message": f"Preferences saved: {clean_lang}, {norm_diff} level",
    }


def record_topic_completion(
    topic: str,
    quiz_score: int,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """
    Record that the user completed a topic (stored persistently across sessions).

    Args:
        topic: Topic name (e.g., "Python Basics", "Data Structures")
        quiz_score: Score out of 100
    """
    topics = list(tool_context.state.get("user:topics_covered", []))
    scores = dict(tool_context.state.get("user:quiz_scores", {}))

    if topic not in topics:
        topics.append(topic)
    scores[topic] = quiz_score

    tool_context.state["user:topics_covered"] = topics
    tool_context.state["user:quiz_scores"] = scores

    return {
        "status": "success",
        "topics_count": len(topics),
        "message": f"Recorded: {topic} with score {quiz_score}/100",
    }


def get_user_progress(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Get the user's learning progress summary across all sessions.
    """
    language = tool_context.state.get("user:language", "en")
    difficulty = tool_context.state.get("user:difficulty_level", "beginner")
    topics = list(tool_context.state.get("user:topics_covered", []))
    scores = dict(tool_context.state.get("user:quiz_scores", {}))

    avg_score = sum(scores.values()) / len(scores) if scores else 0.0

    return {
        "status": "success",
        "language": language,
        "difficulty_level": difficulty,
        "topics_completed": len(topics),
        "topics": topics,
        "average_quiz_score": round(avg_score, 1),
        "all_scores": scores,
    }


def start_learning_session(
    topic: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """
    Start a new learning session for a topic.

    Uses unprefixed session state to track the active topic in this session only.
    """
    tool_context.state["current_topic"] = topic
    tool_context.state["session_start_time"] = datetime.now(timezone.utc).isoformat()

    difficulty = tool_context.state.get("user:difficulty_level", "beginner")

    return {
        "status": "success",
        "topic": topic,
        "difficulty_level": difficulty,
        "message": f"Started learning session: {topic} at {difficulty} level",
    }


def calculate_quiz_grade(
    correct_answers: int,
    total_questions: int,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """
    Calculate a quiz grade using temporary invocation-scoped state (temp:).
    """
    if total_questions <= 0:
        return {
            "status": "error",
            "message": "total_questions must be greater than zero.",
        }

    percentage = (correct_answers / total_questions) * 100
    tool_context.state["temp:raw_score"] = correct_answers
    tool_context.state["temp:quiz_percentage"] = percentage

    if percentage >= 90:
        grade = "A"
    elif percentage >= 80:
        grade = "B"
    elif percentage >= 70:
        grade = "C"
    elif percentage >= 60:
        grade = "D"
    else:
        grade = "F"

    return {
        "status": "success",
        "score": f"{correct_answers}/{total_questions}",
        "percentage": round(percentage, 1),
        "grade": grade,
        "message": f"Quiz grade: {grade} ({percentage:.1f}%)",
    }


def search_past_lessons(
    query: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """
    Search past learning history for relevant completed topics.

    In production, pair this with MemoryService.search_memory() for semantic recall.
    """
    topics = tool_context.state.get("user:topics_covered", [])
    relevant = [t for t in topics if query.lower() in t.lower()]

    if relevant:
        return {
            "status": "success",
            "found": True,
            "relevant_topics": relevant,
            "message": f'Found {len(relevant)} past sessions related to "{query}"',
        }
    return {
        "status": "success",
        "found": False,
        "message": f'No past sessions found for "{query}"',
    }


# ============================================================================
# AGENT DEFINITION
# ============================================================================

root_agent = Agent(
    name="personal_tutor",
    model="gemini-3.8-flash",
    description="Personal learning tutor that tracks preferences, active topics, and progress.",
    instruction="""
    You are a personalized learning tutor (Course Version {app:course_version?}) with memory of the user's progress.

    CAPABILITIES:
    - Set and remember user preferences (language, difficulty level)
    - Track completed topics and quiz scores across sessions
    - Start new learning sessions on specific topics
    - Calculate quiz grades and store results
    - Search past learning sessions for context

    WORKFLOW:
    1. When the user shares preferences, call set_user_preferences immediately.
    2. When starting a topic, call start_learning_session and adapt to their difficulty level.
    3. After a quiz, call calculate_quiz_grade and record_topic_completion.
    4. When asked about prior study history, call search_past_lessons or get_user_progress.

    Always be encouraging and concise!
    """,
    tools=[
        set_user_preferences,
        record_topic_completion,
        get_user_progress,
        start_learning_session,
        calculate_quiz_grade,
        search_past_lessons,
    ],
    output_key="last_tutor_response",
)
```

### `personal_tutor/test_session_persistence.py`

```python
"""
Step 4 Solution: Durable Session Lifecycle (SQLite) & Long-Term Memory Archive
"""

import asyncio
from pathlib import Path

from dotenv import load_dotenv
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

from agent import root_agent

load_dotenv(Path(__file__).with_name(".env"), override=True)


async def test_sqlite_sessions():
    db_file = Path(__file__).resolve().with_name("tutor_sessions.db")
    if db_file.exists():
        db_file.unlink()

    db_url = f"sqlite+aiosqlite:///{db_file.as_posix()}"
    app_name = "personal_tutor_app"
    user_id = "student_42"
    memory_service = InMemoryMemoryService()

    # Use async with so DatabaseSessionService cleanly disposes its SQLite pool on exit
    async with DatabaseSessionService(db_url=db_url) as session_service:
        runner = Runner(
            app_name=app_name,
            agent=root_agent,
            session_service=session_service,
            memory_service=memory_service,
        )

        # 1. Create Session 1 seeded with global app: state and session-scoped state
        await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id="session_1",
            state={
                "app:course_version": "2.1",
                "current_topic": "Onboarding",
            },
        )

        print("=== Session 1: Setting user preferences & starting a topic ===")
        prompt_1 = (
            "Please set my preferred language to Spanish and difficulty to intermediate, "
            "then start a learning session on Python Asyncio."
        )
        async for event in runner.run_async(
            user_id=user_id,
            session_id="session_1",
            new_message=types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt_1)],
            ),
        ):
            if event.is_final_response() and event.content and event.content.parts:
                print(f"Tutor: {event.content.parts[0].text}")

        s1_loaded = await session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id="session_1",
        )
        print(f"\nSession 1 events count: {len(s1_loaded.events)}")
        print(f"Session 1 persisted state keys: {list(s1_loaded.state.keys())}")

        # Archive Session 1 into MemoryService for cross-session recall
        await memory_service.add_session_to_memory(s1_loaded)
        recalled = await memory_service.search_memory(
            app_name=app_name,
            user_id=user_id,
            query="Asyncio",
        )
        print(f"MemoryService search hits for 'Asyncio': {len(recalled.memories)}")

        # 2. Open a brand-new Session 2 for the SAME user_id
        session_2 = await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id="session_2",
        )
        print("\n=== Session 2 (Fresh Thread for Same User) ===")
        print(f"Session 2 inherited state: {session_2.state}")
        print(
            "Notice: 'app:*' and 'user:*' keys persisted across sessions, "
            "while session-only keys ('current_topic', 'last_tutor_response') started clean!"
        )

        # 3. List all sessions stored in SQLite for student_42
        listed = await session_service.list_sessions(
            app_name=app_name,
            user_id=user_id,
        )
        print(f"Stored SQLite session IDs: {[s.id for s in listed.sessions]}")


if __name__ == "__main__":
    asyncio.run(test_sqlite_sessions())
```

### `personal_tutor/test_memory_advanced.py`

```python
"""
Step 5 Bonus Solution: Context Compaction and Session Rewind
"""

import asyncio
from pathlib import Path

from dotenv import load_dotenv
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models import LLMRegistry
from google.adk.runners import InMemoryRunner
from google.genai import types

from agent import root_agent

load_dotenv(Path(__file__).with_name(".env"), override=True)


async def test_advanced_memory():
    # 1. Configure sliding-window LLM event compaction (small interval=2 for demo)
    compaction_config = EventsCompactionConfig(
        summarizer=LlmEventSummarizer(llm=LLMRegistry.new_llm("gemini-3.8-flash")),
        compaction_interval=2,
        overlap_size=1,
    )

    app = App(
        name="advanced_tutor_app",
        root_agent=root_agent,
        events_compaction_config=compaction_config,
    )

    async with InMemoryRunner(app=app) as runner:
        user_id = "student_42"
        session_id = "session_math_1"
        await runner.session_service.create_session(
            app_name=app.name,
            user_id=user_id,
            session_id=session_id,
        )

        print("--- Turn 1: Save persistent user preferences ---")
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(
                role="user",
                parts=[types.Part.from_text(text="Set my language to English and difficulty to beginner.")],
            ),
        ):
            if event.is_final_response() and event.content and event.content.parts:
                print(f"Agent: {event.content.parts[0].text}")

        print("\n--- Turn 2: Study Python Lists (triggers compaction window) ---")
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(
                role="user",
                parts=[types.Part.from_text(text="Start a learning session on Python Lists.")],
            ),
        ):
            if event.is_final_response() and event.content and event.content.parts:
                print(f"Agent: {event.content.parts[0].text}")

        print("\n--- Turn 3: Accidental topic we want to undo via rewind ---")
        turn3_invocation_id = None
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(
                role="user",
                parts=[types.Part.from_text(text="Start a learning session on Quantum Tensor Calculus.")],
            ),
        ):
            if turn3_invocation_id is None and event.invocation_id:
                turn3_invocation_id = event.invocation_id
            if event.is_final_response() and event.content and event.content.parts:
                print(f"Agent: {event.content.parts[0].text}")

        # 2. Rewind session state to right before Turn 3
        if turn3_invocation_id:
            await runner.rewind_async(
                user_id=user_id,
                session_id=session_id,
                rewind_before_invocation_id=turn3_invocation_id,
            )
            rewound = await runner.session_service.get_session(
                app_name=app.name,
                user_id=user_id,
                session_id=session_id,
            )
            print(f"\nSession rewound before invocation {turn3_invocation_id}!")
            print(f"State after rewind: {rewound.state}")


if __name__ == "__main__":
    asyncio.run(test_advanced_memory())
```

### Self-Reflection Answers

1. **How does `uv run adk web` persist sessions locally compared to `InMemorySessionService` and `DatabaseSessionService`?**
   * **Answer:**
     * **`InMemorySessionService`** keeps sessions and state strictly in RAM—ideal for fast unit tests (`InMemoryRunner`), but everything vanishes when the Python process exits.
     * **`uv run adk web`** enables `--use_local_storage` by default, writing sessions to `<agent_folder>/.adk/session.db` via `SqliteSessionService` (unless `--no_use_local_storage` or `--session_service_uri="memory://"` is passed).
     * **`DatabaseSessionService`** (`google-adk[db]`) uses SQLAlchemy 2.0's async engine: `sqlite+aiosqlite:///` is great for single-instance local/CI testing, while `postgresql+asyncpg://` (Cloud SQL / AlloyDB) unlocks row-level `SELECT ... FOR UPDATE` locking for multi-replica Cloud Run / GKE deployments.

2. **Why is `temp:` state automatically discarded after each turn, and why must secrets still never be placed in `temp:`?**
   * **Answer:** `temp:` state is scoped strictly to the current `invocation_id` for transient scratchpad calculations, preventing database bloat and state pollution across turns. However, `temp:` deltas are still emitted inside live `Event` streams and observability traces—so API keys and OAuth tokens belong in Secret Manager or ADK `AuthCredential` stores, never `session.state`.

3. **How does `MemoryService` (`InMemoryMemoryService` / `VertexAiMemoryBankService`) complement `session.state`?**
   * **Answer:** `session.state` (including `user:` and `app:` prefixes) excels at **structured key-value attributes** looked up by exact key name (`user:language`, `current_topic`). `MemoryService` (`add_session_to_memory` / `search_memory`) archives **unstructured knowledge across past conversations** so an agent can recall open-ended discussions weeks later without keeping every historical event inside the active context window.

4. **When `runner.rewind_async(...)` rolls back a turn, why does `user:` state remain untouched?**
   * **Answer:** Rewind restores **session-scoped state and session artifacts** to their snapshot prior to `rewind_before_invocation_id` (resetting keys introduced after that point to `None`), undoing conversational missteps in the current thread without erasing global `app:` settings or durable `user:` profile preferences shared across other sessions.

</SolutionVault>
