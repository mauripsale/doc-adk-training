---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 26 Solution: Building a Content Moderation Assistant

## Goal

This file contains the complete code for the `agent.py` script in the Content Moderation Assistant lab.

### `content_moderator/agent.py`

```python
"""
Content Moderation Assistant - Demonstrates Callbacks, Guardrails, and Caching

This agent uses:
- Caching: Skip LLM call if answer exists (before_agent_callback/after_agent_callback)
- Guardrails: Block inappropriate content (before_model_callback)
- Validation: Check tool arguments (before_tool_callback)
"""

from google.adk.agents import Agent, CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from typing import Dict, Any, Optional
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================ 
# CONFIGURATION
# ============================================================================ 

BLOCKED_WORDS = ['profanity1', 'profanity2', 'hate-speech']

PII_PATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
}

# ============================================================================ 
# CALLBACK FUNCTIONS
# ============================================================================ 

def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Called before agent starts processing a request.
    Implements a caching mechanism to skip LLM execution.
    """
    logger.info(f"[AGENT START] Session: {callback_context.invocation_id}")
    
    # 1. Check if 'cached_response' exists in the state
    cached_text = callback_context.state.get('cached_response')
    
    if cached_text:
        logger.info("[CACHE HIT] Returning cached response, skipping LLM!")
        # 2. Return a Content object to override normal execution
        return types.Content(
            parts=[types.Part(text=f"[From Cache]: {cached_text}")],
            role="model"
        )
        
    # 3. No cache found, return None to proceed to the LLM
    logger.info("[CACHE MISS] Proceeding to LLM.")
    return None

def after_agent_callback(callback_context: CallbackContext, content: types.Content) -> Optional[types.Content]:
    """
    Called after agent completes processing.
    Saves the final content into the state for future caching.
    """
    logger.info(f"[AGENT COMPLETE] Generated {len(content.parts)} parts")
    
    # 1. Extract the text from the content object
    response_text = "".join([p.text for p in content.parts if p.text])
    
    # 2. Save it to state
    callback_context.state['cached_response'] = response_text
    
    # 3. Allow normal flow
    return None

def before_model_callback(
    callback_context: CallbackContext,
    llm_request: types.GenerateContentRequest
) -> Optional[types.GenerateContentResponse]:
    """
    Input Guardrail: Blocks requests containing inappropriate words.
    """
    user_text = "".join([p.text for c in llm_request.contents for p in c.parts if p.text])

    for word in BLOCKED_WORDS:
        if word.lower() in user_text.lower():
            logger.warning(f"[LLM BLOCKED] Found blocked word: {word}")
            return types.GenerateContentResponse(
                candidates=[
                    types.Candidate(
                        content=types.Content(
                            parts=[types.Part(
                                text="I cannot process this request as it contains inappropriate content."
                            )],
                            role="model"
                        )
                    )
                ]
            )

    return None

def after_model_callback(
    callback_context: CallbackContext,
    llm_response: types.GenerateContentResponse
) -> Optional[types.GenerateContentResponse]:
    """
    Output Filtering: Removes PII from LLM responses.
    """
    response_text = ""
    if llm_response.candidates:
        for part in llm_response.candidates[0].content.parts:
            if part.text:
                response_text += part.text

    filtered_text = response_text
    for pii_type, pattern in PII_PATTERNS.items():
        filtered_text = re.sub(pattern, f'[{pii_type.upper()}_REDACTED]', filtered_text)

    if filtered_text != response_text:
        return types.GenerateContentResponse(
            candidates=[
                types.Candidate(
                    content=types.Content(
                        parts=[types.Part(text=filtered_text)],
                        role="model"
                    )
                )
            ]
        )
    return None

def before_tool_callback(
    callback_context: CallbackContext,
    tool_name: str,
    args: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Argument Validation: Blocks tool calls with invalid arguments.
    """
    if tool_name == 'generate_text':
        word_count = args.get('word_count', 0)
        if word_count <= 0 or word_count > 5000:
            logger.warning(f"[TOOL BLOCKED] Invalid word_count: {word_count}")
            return {
                'status': 'error',
                'message': f'Invalid word_count: {word_count}. Must be between 1 and 5000.'
            }
    return None

# ============================================================================ 
# TOOLS
# ============================================================================ 

def generate_text(topic: str, word_count: int, tool_context: ToolContext) -> Dict[str, Any]:
    """Generates text on a topic with a specified word count."""
    return {'status': 'success', 'message': f'Generated {word_count}-word article on "{topic}"'}

# ============================================================================ 
# AGENT DEFINITION
# ============================================================================ 

root_agent = Agent(
    name="content_moderator",
    model="gemini-2.5-flash",
    description="Content moderation assistant with safety guardrails and caching.",
    instruction="You are a helpful assistant. Keep your answers brief.",
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
