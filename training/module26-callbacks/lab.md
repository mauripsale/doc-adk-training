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
    uv run adk create content_moderator
    ```

2.  **Navigate into the new directory:**
    ```shell
    cd content_moderator
    ```

### Step 2: Implement the Callbacks

**Exercise:** Open `agent.py`. Your task is to implement the logic for the six core callbacks. Use the `# TODO` comments as your guide.

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

# ============================================================================
# CALLBACK FUNCTIONS
# ============================================================================

def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    TODO: Caching (Check).
    Read 'cached_response' from callback_context.state. If present, print a
    cache-hit message and return a types.Content wrapping it (role="model")
    to skip the LLM entirely. Otherwise return None.
    """
    pass

def after_agent_callback(callback_context: CallbackContext) -> None:
    """
    TODO: Caching (Save).
    Walk callback_context.session.events in reverse to find the last
    non-user event with content, and save its text into
    callback_context.state['cached_response'] for future reuse.
    """
    pass

def before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    TODO: Input Guardrail.
    Concatenate the text of llm_request.contents and check it against
    BLOCKED_WORDS. If a blocked word is found, print a warning and return an
    LlmResponse with a refusal message instead of calling the model.
    Otherwise return None.
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

Start the agent and try both paths: a normal prompt (should reach the model), and a prompt containing a blocked word like "unsafe" (should be refused by `before_model_callback` without ever calling the model). Then repeat the same prompt in the same session — `before_agent_callback` should return the cached response instantly.

```shell
uv run adk run content_moderator
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
