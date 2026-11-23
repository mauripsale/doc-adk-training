---
sidebar_position: 3
title: "Lab Solution"
---

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
