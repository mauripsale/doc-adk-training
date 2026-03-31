---
sidebar_position: 2
title: "Challenge Lab"
---

# Module 26: Callbacks and Guardrails - Building a Content Moderator

## Lab 26: Building a Content Moderation Assistant with Caching

### Goal

In this lab, you will implement a suite of callbacks to create a **Content Moderation Assistant**. You will learn to build safety guardrails, validate tool arguments, filter responses, and, crucially, implement a **Caching mechanism** using `before_agent_callback` to save tokens and time.

### Step 1: Create the Project Structure

1.  **Create the agent project:**
    ```shell
    adk create content-moderator
    ```
    When prompted, choose the **Programmatic (Python script)** option.

2.  **Navigate into the new directory:**
    ```shell
    cd content-moderator
    ```

### Step 2: Implement the Callbacks

**Exercise:** Open `agent.py`. The full starter code is provided below. Your task is to implement the logic inside the `# TODO` comments for each callback function, and then register them with the agent.

```python
# In agent.py (Starter Code)

from google.adk.agents import Agent, CallbackContext, InMemoryRunner
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from typing import Dict, Any, Optional, List
import re
import logging
import time
from dataclasses import dataclass, field

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
    TODO: Implement a caching mechanism.
    1. Check if 'cached_response' exists in callback_context.state.
    2. If it does, return a `types.Content` object containing that text, 
       skipping the LLM execution entirely!
    3. If it doesn't, return None to proceed normally.
    """
    logger.info(f"[AGENT START] Session: {callback_context.invocation_id}")
    pass # TODO: Implement caching check

def after_agent_callback(callback_context: CallbackContext, content: types.Content) -> Optional[types.Content]:
    """
    Called after agent completes processing.
    TODO: Save the final content into the state so the `before_agent_callback` can cache it.
    1. Extract the text from the `content` object.
    2. Save it to `callback_context.state['cached_response']`.
    3. Return None to allow the normal flow.
    """
    logger.info(f"[AGENT COMPLETE] Generated {len(content.parts)} parts")
    pass # TODO: Implement caching save

def before_model_callback(
    callback_context: CallbackContext,
    llm_request: types.GenerateContentRequest
) -> Optional[types.GenerateContentResponse]:
    """
    Input Guardrail: Blocks requests containing inappropriate words.
    TODO: Loop through BLOCKED_WORDS. If a blocked word is in the user text,
    return a `types.GenerateContentResponse` with a safety message to block the LLM call.
    """
    user_text = "".join([p.text for c in llm_request.contents for p in c.parts if p.text])

    for word in BLOCKED_WORDS:
        if word.lower() in user_text.lower():
            logger.warning(f"[LLM BLOCKED] Found blocked word: {word}")
            # TODO: Return a GenerateContentResponse blocking the execution
            return None # Replace this

    return None

def after_model_callback(
    callback_context: CallbackContext,
    llm_response: types.GenerateContentResponse
) -> Optional[types.GenerateContentResponse]:
    """
    Output Filtering: Removes PII from LLM responses.
    TODO: Use `re.sub` and PII_PATTERNS to redact sensitive info.
    If the text changes, return a new `GenerateContentResponse`.
    """
    # Logic simplified for the exercise
    return None

def before_tool_callback(
    callback_context: CallbackContext,
    tool_name: str,
    args: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Argument Validation: Blocks tool calls with invalid arguments.
    TODO: If `tool_name` is 'generate_text' and `word_count` > 5000,
    return an error dict instead of None to block execution.
    """
    logger.info(f"[TOOL CALL] {tool_name} with args: {args}")
    # TODO: Implement validation
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

# TODO: Define the `root_agent`. Register all tools and callback functions.
root_agent = None

```

### Self-Reflection Questions
- What is the key difference between a callback and a plugin in the ADK? When would you choose one over the other?
- Why does returning a `types.Content` object from `before_agent_callback` cause the agent to skip the LLM call entirely?
- How does using callbacks for guardrails and validation make an agent more reliable and safer to deploy in a production environment?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMjYtY2FsbGJhY2tzL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module26-callbacks/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
