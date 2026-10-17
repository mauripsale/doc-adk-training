---
sidebar_position: 2
title: "Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Module 26: Callbacks and Guardrails - Building a Content Moderator

## Lab 26: Building a Content Moderation Assistant with Caching

### Goal

In this lab, you will implement a suite of callbacks to create a **Content Moderation Assistant**. You will learn to build safety guardrails, validate tool arguments, filter responses, and, crucially, implement a **Caching mechanism** using `before_agent_callback` to save tokens and time.

### Step 1: Create the Project Structure

<Setup/>

1.  **Create the agent project:**
    ```shell
    uv run adk create content_moderator
    ```

2.  **Navigate into the new directory:**
    ```shell
    cd content_moderator
    ```

### Step 2: Implement the Callbacks

**Exercise:** Open `agent.py`. Your task is to implement the logic for the six core callbacks. Use the `# TODO` comments as your guide.

```python
import hashlib
import os
import re
import logging
from typing import Dict, Any, Optional
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext
from google.adk.tools.base_tool import BaseTool
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
BLOCKED_WORDS = ['unsafe', 'offensive']

# ============================================================================
# CALLBACK FUNCTIONS
# ============================================================================

def _cache_key(callback_context: CallbackContext) -> str:
    """
    TODO: Helper.
    A cache keyed by a single global name (e.g. 'cached_response') would
    return the SAME cached answer no matter what the user asks next — you
    must derive the key from the CURRENT turn's user input instead.
    Use callback_context.get_invocation_context().user_content to get the
    current user message (a types.Content), concatenate its parts' text,
    and hash it (e.g. hashlib.md5(...).hexdigest()) into a key such as
    f"cache:{digest}".
    """
    pass

def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    TODO: Caching (Check).
    Compute this turn's cache key with _cache_key() and read it from
    callback_context.state. If present, print a cache-hit message and
    return a types.Content wrapping it (role="model") to skip the LLM
    entirely. Otherwise return None.
    """
    pass

def after_agent_callback(callback_context: CallbackContext) -> None:
    """
    TODO: Caching (Save).
    Walk callback_context.session.events in reverse to find the last
    non-user event with content, and save its text into
    callback_context.state[_cache_key(callback_context)] for future reuse.
    Using the same per-input key as before_agent_callback is essential —
    otherwise a later, unrelated question would incorrectly hit the cache
    entry saved for a previous, different question.
    Guard against event.content.parts being empty before indexing
    parts[0] — a content object with no parts would otherwise raise an
    IndexError.
    """
    pass

def before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    TODO: Input Guardrail.
    Check ONLY the current turn's user input against BLOCKED_WORDS — do
    NOT scan the full llm_request.contents history. llm_request.contents
    holds the ENTIRE conversation so far, and once a blocked word appears
    anywhere in it, every later turn would keep matching and get refused
    forever, even completely unrelated questions. Mirror the pattern
    _cache_key() uses: pull the current message via
    callback_context.get_invocation_context().user_content, concatenate
    its parts' text, and check only that against BLOCKED_WORDS. If a
    blocked word is found, print a warning and return an LlmResponse with
    a refusal message instead of calling the model. Otherwise return None.
    """
    pass

def after_model_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """
    TODO: Output Filtering.
    Use re.sub to redact email addresses from the LLM response text.
    If redacted, return a new LlmResponse; otherwise return None.
    Note: llm_response.content.parts[0].text can be None — the model's
    response may be a pure function call (e.g. deciding to invoke
    generate_text) with no text to filter. Guard against that first.
    """
    pass

def before_tool_callback(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext
) -> Optional[Dict[str, Any]]:
    """
    TODO: Tool Validation.
    If tool.name == 'generate_text' and args['word_count'] exceeds 5000,
    print a warning and return an error dict (e.g. {'status': 'error',
    'message': '...'}) to block execution. Otherwise return None.
    """
    pass

def after_tool_callback(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext,
    tool_response: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    TODO: Output Audit.
    If tool.name == 'generate_text', check tool_response['text'] against
    BLOCKED_WORDS (defense-in-depth, in case the model injects one via
    arguments). If found, print a warning and return a modified copy of
    tool_response with the blocked words replaced by '***'. Otherwise,
    print an audit log line (e.g. tool name + status) and return None.
    """
    pass

# --- Tools ---
def generate_text(topic: str, word_count: int) -> dict:
    """Generates text on a topic."""
    return {"status": "success", "text": f"A {word_count}-word essay on {topic}..."}

# ============================================================================
# AGENT DEFINITION
# ============================================================================

# TODO: Define root_agent and register ALL six callbacks defined above.
root_agent = Agent(
    name="secure_moderator",
    model="gemini-3.5-flash",
    # instruction=...,
    # tools=[...],
    # before_agent_callback=...,
    # after_agent_callback=...,
    # before_model_callback=...,
    # after_model_callback=...,
    # before_tool_callback=...,
    # after_tool_callback=...,
)
```

### Step 3: Run and Test

Start the agent and try both paths: a normal prompt (should reach the model), and a prompt containing a blocked word like "unsafe" (should be refused by `before_model_callback` without ever calling the model). Then repeat the same prompt in the same session — `before_agent_callback` should return the cached response instantly. Finally, ask a *different* question in the same session — this should NOT return the previous answer; it should call the LLM again and get a fresh, correct response. This third check is what actually proves the cache is keyed per-question rather than one global slot for the whole session.

```shell
uv run adk run content_moderator
```

### Self-Reflection Questions
- What is the key difference between a callback and a plugin in the ADK? When would you choose one over the other?
- Why does returning a `types.Content` object from `before_agent_callback` cause the agent to skip the LLM call entirely?
- How does using callbacks for guardrails and validation make an agent more reliable and safer to deploy in a production environment?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="26">

# Lab 26 Solution: Building a Content Moderation Assistant

## Goal

This file contains the complete code for the `agent.py` script in the Content Moderation Assistant lab.

### `content_moderator/agent.py`

```python
import hashlib
import os
import re
import logging
from typing import Dict, Any, Optional
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext
from google.adk.tools.base_tool import BaseTool
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
BLOCKED_WORDS = ['unsafe', 'offensive']

# --- Caching helper: key the cache by the CURRENT turn's user input ---
def _current_user_text(callback_context: CallbackContext) -> str:
    """Extracts the text of the current turn's user message."""
    user_content = callback_context.get_invocation_context().user_content
    if not user_content or not user_content.parts:
        return ""
    return "".join(p.text or "" for p in user_content.parts)

def _cache_key(callback_context: CallbackContext) -> str:
    """
    Derives a cache key from the current user input, not a single global
    slot. Without this, ANY cached response would be replayed for EVERY
    subsequent question in the session, regardless of what was asked.
    """
    user_text = _current_user_text(callback_context)
    digest = hashlib.md5(user_text.strip().lower().encode("utf-8")).hexdigest()
    return f"cache:{digest}"

# --- Callback 1: Caching (Check) ---
def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """Intercepts execution to check for a cached response for THIS input."""
    key = _cache_key(callback_context)
    cached_text = callback_context.state.get(key)
    if cached_text:
        print("⚡ [CACHE HIT] Returning saved result, skipping LLM.")
        return types.Content(
            parts=[types.Part(text=f"[CACHED]: {cached_text}")],
            role="model"
        )
    return None

# --- Callback 2: Caching (Save) ---
def after_agent_callback(callback_context: CallbackContext) -> None:
    """Saves the final response to session state, keyed by the input that produced it."""
    # Find the last model response in the session history
    events = callback_context.session.events
    for event in reversed(events):
        if event.author != "user" and event.content and event.content.parts:
            response_text = event.content.parts[0].text
            key = _cache_key(callback_context)
            callback_context.state[key] = response_text
            print("💾 [CACHE SAVE] Result persisted to session state.")
            break

# --- Callback 3: Input Guardrail ---
def before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Prevents inappropriate prompts from reaching the LLM."""
    # Scope the check to the CURRENT turn only, mirroring _cache_key().
    # Scanning llm_request.contents would inspect the ENTIRE conversation
    # history, so a blocked word from any earlier turn would keep matching
    # forever, refusing every later (and otherwise unrelated) turn too.
    user_text = _current_user_text(callback_context)

    for word in BLOCKED_WORDS:
        if word in user_text.lower():
            print(f"🛑 [GUARDRAIL] Blocked prompt containing: {word}")
            return LlmResponse(
                content=types.Content(
                    parts=[types.Part(text="I'm sorry, I cannot process offensive prompts.")],
                    role="model"
                )
            )
    return None

# --- Callback 4: Output Filtering ---
def after_model_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Removes sensitive email addresses from the LLM response."""
    if not llm_response.content or not llm_response.content.parts:
        return None

    original_text = llm_response.content.parts[0].text
    if not original_text:
        # The model's response may be a pure function call (e.g. deciding to
        # invoke generate_text) with no text part to filter.
        return None
    # Simple email regex
    redacted_text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', original_text)
    
    if redacted_text != original_text:
        print("🛡️ [FILTER] Redacted PII from model response.")
        # Return a modified copy of the response
        return llm_response.model_copy(update={
            "content": types.Content(parts=[types.Part(text=redacted_text)], role="model")
        })
    return None

# --- Callback 5: Tool Validation ---
def before_tool_callback(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext
) -> Optional[Dict[str, Any]]:
    """Validates tool arguments before execution."""
    if tool.name == 'generate_text':
        count = args.get('word_count', 0)
        if count > 5000:
            print(f"⚠️ [VALIDATION] Blocked tool call: word_count {count} is too high.")
            return {
                'status': 'error', 
                'message': 'Word count exceeds the maximum limit of 5000.'
            }
    return None

# --- Callback 6: Tool Output Audit ---
def after_tool_callback(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext,
    tool_response: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Audits tool output and redacts blocked words as a defense-in-depth layer."""
    if tool.name == 'generate_text':
        text = tool_response.get('text', '')
        if any(word in text.lower() for word in BLOCKED_WORDS):
            print("🛡️ [AUDIT] Redacted blocked word from tool output.")
            redacted = text
            for word in BLOCKED_WORDS:
                redacted = redacted.replace(word, '***')
            return {**tool_response, 'text': redacted}
        print(f"📋 [AUDIT] Tool '{tool.name}' executed successfully.")
    return None

# --- Tools ---
def generate_text(topic: str, word_count: int) -> dict:
    """Generates text on a topic."""
    return {"status": "success", "text": f"A {word_count}-word essay on {topic}..."}

# --- Agent Registration ---
root_agent = Agent(
    name="secure_moderator",
    model="gemini-3.5-flash",
    instruction="You are a professional content assistant.",
    tools=[generate_text],
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback
)
```

### Self-Reflection Answers

1.  **What is the key difference between a callback and a plugin in the ADK? When would you choose one over the other?**
    *   **Answer:** The key difference lies in their scope and primary role. **Callbacks** are agent-specific, designed for control, modification, and implementing guardrails *within a single agent's logic*. They can block or alter an agent's execution. **Plugins** are global (registered at the `Runner` level), designed for observation and telemetry (metrics, logging, alerting) *across all agents in an application*. Choose a callback to modify or block an agent's specific operations; choose a plugin to monitor behavior across the entire system without altering its logic.

2.  **Why does returning a `types.Content` object from `before_agent_callback` cause the agent to skip the LLM call entirely?**
    *   **Answer:** Returning an object from a callback signals to the ADK framework to *override* the default behavior. Since `before_agent_callback` happens at the very beginning of the agent's lifecycle, returning a final `Content` object tells the framework "I already have the answer, you don't need to do any work." The ADK accepts this `Content` as the final result and skips tool execution and LLM invocation, saving time and tokens. This is the core mechanism behind caching.

3.  **How does using callbacks for guardrails and validation make an agent more reliable and safer to deploy in a production environment?**
    *   **Answer:** Callbacks significantly enhance reliability and safety by introducing deterministic, hard-coded checks for critical functionalities, reducing reliance on the LLM's non-deterministic reasoning. For instance, `before_model_callback` can proactively prevent harmful input from reaching the LLM, and `after_model_callback` can filter sensitive data (PII) from responses before they are exposed. Similarly, `before_tool_callback` validates tool arguments, preventing runtime errors and ensuring tools are used correctly. This layered approach creates a more stable, secure, and predictable agent behavior in production.

</SolutionVault>
