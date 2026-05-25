---
sidebar_position: 22
title: "Module 22: State and Memory - Persistent Agent Context"
---

# Module 22: State and Memory - Persistent Agent Context

## Theory

### Giving Agents Memory

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

### Accessing State in Instructions

You can directly inject session state values into your agent's instructions using `{key}` templating. This makes your prompts dynamic and context-aware.

```python
agent = LlmAgent(
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

### Session Rewind (New!)

The ADK supports **rewinding** a session to a previous point. This is useful for undoing mistakes or exploring alternative conversation paths.

*   **How it works:** You specify an `invocation_id` to rewind *before*. The system restores the session state and artifacts to that moment.
*   **What is restored:** Session-level state and artifacts.
*   **What is NOT restored:** Global resources like `app:` or `user:` state, and external side effects (like API calls already made).

### Memory Service

The Memory Service provides **long-term, searchable memory** for your agent, like an archive of past conversations.

**Implementations**:

1.  **`InMemoryMemoryService`**: A simple, non-persistent keyword search for development and testing. Stores full conversation history.
2.  **`VertexAiMemoryBankService`**: A production-grade service managed by Google Cloud. It uses semantic search and "Memory Extraction" to consolidate meaningful information rather than just storing raw logs.

**Workflow**:

1.  **Ingest:** After a meaningful conversation, call `memory_service.add_session_to_memory(session)`.
2.  **Recall:** In a future session, use a tool to call `memory_service.search_memory(query)`.
3.  **Act:** The agent uses the retrieved context to answer questions like "What did we discuss last week?".

### Key Takeaways
- **Session State** manages short-term context with scoped prefixes (`user:`, `app:`, `temp:`).
- **Inject State** directly into instructions using `{key}` syntax for dynamic behavior.
- **Update State** via `tool_context` or `callback_context` to ensure safety and persistence.
- **Session Rewind** allows reverting a conversation to a previous state (with limitations).
- **Memory Service** provides long-term recall, with `VertexAiMemoryBankService` offering advanced semantic capabilities.