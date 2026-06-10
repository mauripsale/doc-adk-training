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
from google.adk.runners import InMemoryRunner

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
            # Check if it's already a cached response to avoid double prefixing in simulation
            text = event.content.parts[0].text
            if not text.startswith("[CACHED]:"):
                callback_context.state['cached_response'] = text
                print(f"💾 [CACHE SAVE] Result persisted to session state: {text}")
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

# --- Callback 4: Tool Validation ---
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
            # ADK expectation for blocking tool execution is usually returning an error result
            # or a modified args dict. If we return a dict with 'status'='error', 
            # the framework handles it as the tool's output.
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
    before_tool_callback=before_tool_callback
)
