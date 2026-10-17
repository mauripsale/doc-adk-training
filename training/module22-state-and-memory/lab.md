---
title: "Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Module 22: State and Memory - Building a Personal Tutor Agent

## Lab 22: Building a Personal Learning Tutor

### Goal

Understanding how to manage an agent's state and memory is crucial for developing intelligent, personalized, and robust AI assistants. In this lab, you'll put theory into practice by building a personal tutor that remembers user preferences, tracks progress, and simulates long-term knowledge retrieval.

In this lab, you will build a **Personal Learning Tutor** that uses all four state scopes (`user:`, `app:`, session, and `temp:`) and simulates interacting with a long-term memory service. This will teach you how to create a truly stateful and personalized agent.

### The Use Case

You will build a tutor that:
*   Stores a user's preferences (language, difficulty) in **`user:`** state.
*   Tracks the current topic in **session** state.
*   Uses **`temp:`** state for an intermediate quiz calculation.
*   Reads a global "course version" from **`app:`** state.
*   Simulates searching its **long-term memory** for past lessons.

### Step 1: Create the Project Structure

<Setup/>

1.  **Create the agent project:**
    ```shell
    uv run adk create personal_tutor
    ```
    This prompts for a model choice (any option is fine, you'll set the real model in `agent.py` below) and, if needed, a backend -- there's no separate "type" prompt, `agent.py`/Code is already the default.

2.  **Navigate into the new directory:**
    ```shell
    cd personal_tutor
    ```

### Step 2: Implement the State-Management Tools

**Exercise:** Open `agent.py`. You will find a skeleton script. Your task is to complete the tool functions by using the correct state prefixes (`user:`, `temp:`, or no prefix) based on the requirements in the docstrings.

```python
# agent.py (Starter Code)

from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any

# ============================================================================
# TOOLS: State Management & Memory Operations
# ============================================================================

def set_user_preferences(
    language: str,
    difficulty_level: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Set user learning preferences (stored persistently).

    Args:
        language: Preferred language (en, es, fr, etc.)
        difficulty_level: beginner, intermediate, or advanced
    """
    # TODO: Store the language and difficulty_level in the tool_context.state.
    # Use the correct prefix for data that should persist for the user.
    pass # Implement here

    return {
        'status': 'success',
        'message': f'Preferences saved: {language}, {difficulty_level} level'
    }


def record_topic_completion(
    topic: str,
    quiz_score: int,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Record that user completed a topic (stored persistently).

    Args:
        topic: Topic name (e.g., "Python Basics", "Data Structures")
        quiz_score: Score out of 100
    """
    # TODO: Get existing lists or create new ones for topics and scores.
    # TODO: Update persistent user state with the new topic and score.
    pass # Implement here

    return {
        'status': 'success',
        'topics_count': 0, # Placeholder
        'message': f'Recorded: {topic} with score {quiz_score}/100'
    }


def get_user_progress(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Get user's learning progress summary.

    Returns persistent user data across all sessions.
    """
    # TODO: Read persistent user state for language, difficulty, topics, and scores.
    # TODO: Calculate average score.
    language = "en" # Placeholder
    difficulty = "beginner" # Placeholder
    topics = [] # Placeholder
    scores = {} # Placeholder
    avg_score = 0 # Placeholder

    return {
        'status': 'success',
        'language': language,
        'difficulty_level': difficulty,
        'topics_completed': len(topics),
        'topics': topics,
        'average_quiz_score': round(avg_score, 1),
        'all_scores': scores
    }


def start_learning_session(
    topic: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Start a new learning session for a topic.

    Uses session state (no prefix) to track current topic.
    """
    # TODO: Store the topic and a simplified start time in session-level state.
    # TODO: Get user's difficulty level for personalization.
    difficulty = "beginner" # Placeholder

    return {
        'status': 'success',
        'topic': topic,
        'difficulty_level': difficulty,
        'message': f'Started learning session: {topic} at {difficulty} level'
    }


def calculate_quiz_grade(
    correct_answers: int,
    total_questions: int,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Calculate quiz grade using temporary state.

    Demonstrates temp: prefix for invocation-scoped data.
    """
    # TODO: Store the 'percentage' and 'raw_score' in temp state.
    # TODO: Determine grade letter based on percentage.
    grade = "F" # Placeholder

    return {
        'status': 'success',
        'score': f'{correct_answers}/{total_questions}',
        'percentage': 0.0, # Placeholder
        'grade': grade,
        'message': f'Quiz grade: {grade} ({0.0:.1f}%)' # Placeholder
    }


def search_past_lessons(
    query: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Search memory for relevant past learning sessions.

    This demonstrates memory service integration.
    In production, this would use MemoryService.search_memory().
    """
    # TODO: Simulate searching past lessons based on topics covered in user state.
    # NOTE: This is a simplified simulation for demonstration purposes. In a real application,
    # this would integrate with a persistent MemoryService like VertexAiMemoryBankService.
    return {
        'status': 'success',
        'found': False,
        'message': f'No past sessions found for "{query}"' # Placeholder
    }


# ============================================================================
# AGENT DEFINITION
# ============================================================================

# TODO: Define the root_agent.
# 1. Register all six tool functions you just implemented.
# 2. In the instruction, try using the special syntax {app:course_version?}
#    to dynamically inject the course version from the app state!
root_agent = None
```

### Step 3: Run and Test the State Scopes

1.  **Set up your API key** in the `.env` file.
2.  **Navigate to the parent directory** (`cd ..`) and start the Dev UI:
    ```shell
    uv run adk web personal_tutor
    ```
3.  **Interact with the agent:**
    *   Go to the **State** tab in the Dev UI. Set the global app state by entering `{"app:course_version": "2.1"}` and clicking "Set State".
    *   Go back to the **Chat** tab and test your agent. Ask it to set your preferences, start a lesson, and check your progress.
    *   **Note on Persistence:** The default `InMemorySessionService` used in development will lose `user:` and `app:` state if the `uv run adk web` server is restarted. For true persistence, a database-backed `SessionService` would be required.
    *   Start a new session (refresh the page) and verify that your preferences were remembered but the current lesson topic was forgotten.

### Bonus Challenge: Dynamic Instructions

Did you notice the `app:course_version` in Step 3?
Try to modify your `root_agent` instruction to include:
`"You are a personalized learning tutor (Course Version {app:course_version?}) ..."`

This demonstrates **Instruction Injection**, where the ADK automatically replaces `{key}` placeholders with values from the state before sending the prompt to the LLM. The `?` makes it optional, so it won't crash if the state key is missing!

### Having Trouble?

If you get stuck, you can find the complete, working code in the `lab-solution.md` file.

### Lab Summary

You have successfully built a sophisticated agent that leverages all four state scopes to provide a continuous, personalized experience. You have learned:
*   How to use `user:` state for persistent user preferences.
*   How to use session state for conversation-specific context.
*   How to use `temp:` state for single-turn, intermediate data.
*   How to use `app:` state for global, application-wide data.
*   How these state mechanisms work together to create agents with memory.
*   **Bonus:** How to inject state directly into instructions.

### Self-Reflection Questions
- The `InMemorySessionService` loses `user:` and `app:` state on restart. What are the advantages and disadvantages of using a persistent `SessionService` (like one backed by a database) in a production environment?
- The `temp:` state is automatically discarded after each turn. Why is this a useful feature? What kind of problems could arise if this temporary data was accidentally persisted?
- Our `search_past_lessons` tool simulates a memory search. In a real application using `VertexAiMemoryBankService`, the search would be semantic (based on meaning) rather than keyword-based. How does this change the kinds of queries the user could make?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="22">

# Lab 22 Solution: Building a Personal Learning Tutor

## Goal

This file contains the complete code for the `agent.py` script in the Personal Learning Tutor lab.

### `personal_tutor/agent.py`

```python
"""
Personal Learning Tutor - Demonstrates State & Memory Management

This agent uses:
- user: prefix for persistent preferences (language, difficulty)
- Session state for current topic tracking
- temp: prefix for temporary quiz calculations
- Memory service for retrieving past learning sessions
"""

from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any

# ============================================================================
# TOOLS: State Management & Memory Operations
# ============================================================================

def set_user_preferences(
    language: str,
    difficulty_level: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Set user learning preferences (stored persistently).

    Args:
        language: Preferred language (en, es, fr, etc.)
        difficulty_level: beginner, intermediate, or advanced
    """
    # Use user: prefix for persistent cross-session storage
    tool_context.state['user:language'] = language
    tool_context.state['user:difficulty_level'] = difficulty_level

    return {
        'status': 'success',
        'message': f'Preferences saved: {language}, {difficulty_level} level'
    }


def record_topic_completion(
    topic: str,
    quiz_score: int,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Record that user completed a topic (stored persistently).

    Args:
        topic: Topic name (e.g., "Python Basics", "Data Structures")
        quiz_score: Score out of 100
    """
    # Get existing lists or create new ones
    topics = tool_context.state.get('user:topics_covered', [])
    scores = tool_context.state.get('user:quiz_scores', {})

    # Update persistent user state
    if topic not in topics:
        topics.append(topic)
    scores[topic] = quiz_score

    tool_context.state['user:topics_covered'] = topics
    tool_context.state['user:quiz_scores'] = scores

    return {
        'status': 'success',
        'topics_count': len(topics),
        'message': f'Recorded: {topic} with score {quiz_score}/100'
    }


def get_user_progress(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Get user's learning progress summary.

    Returns persistent user data across all sessions.
    """
    # Read persistent user state
    language = tool_context.state.get('user:language', 'en')
    difficulty = tool_context.state.get('user:difficulty_level', 'beginner')
    topics = tool_context.state.get('user:topics_covered', [])
    scores = tool_context.state.get('user:quiz_scores', {})

    # Calculate average score
    avg_score = sum(scores.values()) / len(scores) if scores else 0

    return {
        'status': 'success',
        'language': language,
        'difficulty_level': difficulty,
        'topics_completed': len(topics),
        'topics': topics,
        'average_quiz_score': round(avg_score, 1),
        'all_scores': scores
    }


def start_learning_session(
    topic: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Start a new learning session for a topic.

    Uses session state (no prefix) to track current topic.
    """
    # Session-level state (persists within this session only)
    tool_context.state['current_topic'] = topic
    tool_context.state['session_start_time'] = 'now'  # Simplified

    # Get user's difficulty level for personalization
    difficulty = tool_context.state.get('user:difficulty_level', 'beginner')

    return {
        'status': 'success',
        'topic': topic,
        'difficulty_level': difficulty,
        'message': f'Started learning session: {topic} at {difficulty} level'
    }


def calculate_quiz_grade(
    correct_answers: int,
    total_questions: int,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Calculate quiz grade using temporary state.

    Demonstrates temp: prefix for invocation-scoped data.
    """
    # Store intermediate calculation in temp state (discarded after invocation)
    percentage = (correct_answers / total_questions) * 100
    tool_context.state['temp:raw_score'] = correct_answers
    tool_context.state['temp:quiz_percentage'] = percentage

    # Determine grade letter
    if percentage >= 90:
        grade = 'A'
    elif percentage >= 80:
        grade = 'B'
    elif percentage >= 70:
        grade = 'C'
    elif percentage >= 60:
        grade = 'D'
    else:
        grade = 'F'

    return {
        'status': 'success',
        'score': f'{correct_answers}/{total_questions}',
        'percentage': round(percentage, 1),
        'grade': grade,
        'message': f'Quiz grade: {grade} ({percentage:.1f}%)'
    }


def search_past_lessons(
    query: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Search memory for relevant past learning sessions.

    This demonstrates memory service integration.
    In production, this would use MemoryService.search_memory().
    """
    # NOTE: This is a simplified simulation
    topics = tool_context.state.get('user:topics_covered', [])
    relevant = [t for t in topics if query.lower() in t.lower()]

    if relevant:
        return {
            'status': 'success',
            'found': True,
            'relevant_topics': relevant,
            'message': f'Found {len(relevant)} past sessions related to "{query}"'
        }
    else:
        return {
            'status': 'success',
            'found': False,
            'message': f'No past sessions found for "{query}"'
        }


# ============================================================================
# AGENT DEFINITION
# ============================================================================

root_agent = Agent(
    name="personal_tutor",
    model="gemini-3.5-flash",
    description="Personal learning tutor that tracks your progress, preferences, and learning history.",
    instruction="""
    You are a personalized learning tutor (Course Version {app:course_version?}) with memory of the user's progress.

    CAPABILITIES:
    - Set and remember user preferences (language, difficulty level)
    - Track completed topics and quiz scores across sessions
    - Start new learning sessions on specific topics
    - Calculate quiz grades and store results
    - Search past learning sessions for context
    - Adapt teaching based on user's level and history

    WORKFLOW:
    1. If new user, ask about preferences (language, difficulty).
    2. For learning requests, start a session with start_learning_session and teach the topic.
    3. After teaching, record completion with the user's quiz score.
    4. When asked, search past lessons to provide context.

    Always be encouraging and adapt to the user's learning pace!
    """,
    tools=[
        set_user_preferences,
        record_topic_completion,
        get_user_progress,
        start_learning_session,
        calculate_quiz_grade,
        search_past_lessons
    ],
    output_key="last_tutor_response"
)
```

### Self-Reflection Answers

1.  **The `InMemorySessionService` loses `user:` and `app:` state on restart. What are the advantages and disadvantages of using a persistent `SessionService` (like one backed by a database) in a production environment?**
    *   **Answer:**
        *   **Advantages:** True persistence across restarts/deployments; enables long-term personalization; supports horizontal scaling (multiple instances of your agent can access the same state); critical for user-facing applications that need to remember users.
        *   **Disadvantages:** Adds operational overhead (database management, network latency); requires careful schema design; potential for data consistency issues in distributed systems if not managed well.

2.  **The `temp:` state is automatically discarded after each turn. Why is this a useful feature? What kind of problems could arise if this temporary data was accidentally persisted?**
    *   **Answer:** `temp:` state is useful for intermediate calculations or ephemeral data that is only relevant for a single turn (e.g., a quiz score before it's saved to `user:` state). If this data was accidentally persisted:
        *   **State Bloat:** The state object would grow unnecessarily large over time, slowing down processing.
        *   **Data Pollution:** Irrelevant data would clutter the state, potentially confusing the LLM in later turns or leading to incorrect decisions.
        *   **Security Risks:** Sensitive temporary data might be unintentionally exposed or stored longer than intended.

3.  **Our `search_past_lessons` tool simulates a memory search. In a real application using `VertexAiMemoryBankService`, the search would be semantic (based on meaning) rather than keyword-based. How does this change the kinds of queries the user could make?**
    *   **Answer:** Semantic search is much more powerful. Instead of needing to remember exact keywords or topic titles, a user could ask conceptual questions like:
        *   "What did we discuss about data transformation last week?" (Even if the topic was 'ETL processes').
        *   "Remind me about the security implications of that code review we did." (Even if the exact phrase 'security implications' wasn't used).
        *   "I'm confused about asynchronous programming; what did you teach me about Python coroutines?"
        This allows for a more natural, intuitive, and flexible interaction with the agent's long-term knowledge.

</SolutionVault>
