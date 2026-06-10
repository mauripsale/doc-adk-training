---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 26 Solution: Building a Content Moderation Assistant

## Goal

This file contains the complete code for the `agent.py` script in the Content Moderation Assistant lab.

### `content_moderator/agent.py`

```python
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

# --- Callback 1: Caching (Check) ---
def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """Intercepts execution to check for a cached response."""
    cached_text = callback_context.state.get('cached_response')
    if cached_text:
        print("⚡ [CACHE HIT] Returning saved result, skipping LLM.")
        return types.Content(
            parts=[types.Part(text=f"[CACHED]: {cached_text}")],
            role="model"
        )
    return None

# --- Callback 2: Caching (Save) ---
def after_agent_callback(callback_context: CallbackContext) -> None:
    """Saves the final response to the session state for future use."""
    # Find the last model response in the session history
    events = callback_context.session.events
    for event in reversed(events):
        if event.author != "user" and event.content:
            response_text = event.content.parts[0].text
            callback_context.state['cached_response'] = response_text
            print("💾 [CACHE SAVE] Result persisted to session state.")
            break

# --- Callback 3: Input Guardrail ---
def before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Prevents inappropriate prompts from reaching the LLM."""
    user_text = "".join([p.text for c in llm_request.contents for p in c.parts if p.text])
    
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
    if not llm_response.content:
        return None
        
    original_text = llm_response.content.parts[0].text
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
    before_tool_callback=before_tool_callback
)
```

### Self-Reflection Answers

1.  **What is the key difference between a callback and a plugin in the ADK? When would you choose one over the other?**
    *   **Answer:** The key difference lies in their scope and primary role. **Callbacks** are agent-specific, designed for control, modification, and implementing guardrails *within a single agent's logic*. They can block or alter an agent's execution. **Plugins** are global (registered at the `Runner` level), designed for observation and telemetry (metrics, logging, alerting) *across all agents in an application*. Choose a callback to modify or block an agent's specific operations; choose a plugin to monitor behavior across the entire system without altering its logic.

2.  **Why does returning a `types.Content` object from `before_agent_callback` cause the agent to skip the LLM call entirely?**
    *   **Answer:** Returning an object from a callback signals to the ADK framework to *override* the default behavior. Since `before_agent_callback` happens at the very beginning of the agent's lifecycle, returning a final `Content` object tells the framework "I already have the answer, you don't need to do any work." The ADK accepts this `Content` as the final result and skips tool execution and LLM invocation, saving time and tokens. This is the core mechanism behind caching.

3.  **How does using callbacks for guardrails and validation make an agent more reliable and safer to deploy in a production environment?**
    *   **Answer:** Callbacks significantly enhance reliability and safety by introducing deterministic, hard-coded checks for critical functionalities, reducing reliance on the LLM's non-deterministic reasoning. For instance, `before_model_callback` can proactively prevent harmful input from reaching the LLM, and `after_model_callback` can filter sensitive data (PII) from responses before they are exposed. Similarly, `before_tool_callback` validates tool arguments, preventing runtime errors and ensuring tools are used correctly. This layered approach creates a more stable, secure, and predictable agent behavior in production.
