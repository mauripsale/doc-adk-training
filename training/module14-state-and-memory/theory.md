# Module 14: Managing Conversation State and Memory

## Theory

### Giving Agents Memory

A key feature that elevates a simple chatbot to a capable assistant is **memory**. A conversation with an agent that can't remember anything from one turn to the next is frustrating and unnatural. The ADK provides a robust system for managing two different kinds of memory: short-term **State** and long-term **Memory**.

In this module, we will focus on **State**, which is the agent's "working memory" or "scratchpad" for a single, continuous conversation.

### What is Session State?

For every conversation, the ADK creates a `Session` object. Attached to this session is a dictionary-like object called `state`. This `session.state` is where the agent can store, retrieve, and update information that is relevant *only to the current conversation*.

**Think of it like this:**
*   The conversation history (`session.events`) is a transcript of everything that has been said.
*   The `session.state` is a set of sticky notes that the agent keeps on the side to remember key details *right now*.

**Common uses for `session.state`:**
*   **Tracking Task Progress:** Remembering which step of a multi-turn process the user is on (e.g., `'booking_step': 'confirm_payment'`).
*   **Storing User Input:** Holding onto a piece of information the user provided earlier (e.g., `'destination_city': 'Paris'`).
*   **Personalization:** Remembering a preference the user mentioned in the current conversation (e.g., `'preferred_color': 'blue'`).

### Scoping State with Prefixes

Not all "short-term" memory is the same. The ADK allows you to define the **scope** of a piece of state by using special prefixes on the keys you use to store it.

#### 1. **No Prefix (Session State)**
*   **Scope:** Specific to the *current conversation* (`session_id`).
*   **Persistence:** Lasts only as long as the current session.
*   **Use Case:** The most common type of state. Used for tracking details of the current task.
*   **Example:** `state['current_order_id'] = '12345'`

#### 2. **`user:` Prefix (User State)**
*   **Scope:** Tied to the `user_id`. This state is shared across **all conversations** that the same user has with your agent.
*   **Persistence:** Lasts across different sessions.
*   **Use Case:** Remembering user-specific preferences that shouldn't have to be repeated every time, like their name, language, or favorite settings.
*   **Example:** `state['user:name'] = 'Alex'`

#### 3. **`app:` Prefix (App State)**
*   **Scope:** Tied to the `app_name`. This state is global and shared across **all users and all conversations** for that specific agent application.
*   **Persistence:** Lasts as long as the application is running.
*   **Use Case:** Storing global configuration or information, like a "message of the day" or an API endpoint.
*   **Example:** `state['app:api_version'] = 'v2.1'`

#### 4. **`temp:` Prefix (Temporary State)**
*   **Scope:** Specific to a single "turn" or "invocation."
*   **Persistence:** It is discarded as soon as the agent has finished generating its response for the current turn.
*   **Use Case:** Passing data between tools that are called within the same turn. For example, one tool could calculate a raw value and save it to `temp:raw_value`, and a second tool could then read that temporary value to format it.

### How to Modify State

The recommended and safest way to modify state is from within a **custom tool** using the `ToolContext`. As you learned in Module 8, a tool can access `tool_context.state` to read and write data.

When a tool modifies the state, the ADK automatically tracks this change and ensures it is saved correctly according to its scope.

### How to Read State

Agents can access state information directly in their `instruction` prompts using curly brace `{}` syntax.

```yaml
instruction: |
  You are a friendly assistant.
  The user's name is {user:name}.
  Greet them by their name.
```
If `state['user:name']` has been set to "Alex", the LLM will receive the instruction: "You are a friendly assistant. The user's name is Alex. Greet them by their name." This allows you to create highly dynamic and personalized agent behaviors.

In the lab for this module, you will build an agent that uses `user:` state to remember a user's name across multiple conversations.
