---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 25.5 Solution: Building Enterprise Multi-Layer Safety Guardrails

## Goal

This file contains the complete, reference implementation for `safety_guardrail/agent.py` and the automated verification suite using Google ADK 2.0 and `gemini-3.8-flash`.

### `safety_guardrail/agent.py`

```python
import re
from google.adk import Agent
from google.adk.events import Event
from google.adk.apps import App
from google.adk.plugins import BasePlugin

# --- 1. Output Guardrail: PII Data Redaction / Block ---
class PIIGuardrailPlugin(BasePlugin):
    """
    Fail-Closed output guardrail: intercepts agent responses and overwrites
    or redacts sensitive financial data (credit cards, PII) before reaching the user.
    """
    def __init__(self, name: str = 'pii_guardrail', mode: str = 'block'):
        super().__init__(name)
        self.mode = mode  # 'block' or 'mask'
        self.cc_pattern = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")
        self.interventions_count = 0

    async def on_event_callback(self, *, event: Event, **kwargs):
        if event.is_final_response() and event.content and event.content.parts:
            response_text = event.content.parts[0].text
            if response_text and self.cc_pattern.search(response_text):
                self.interventions_count += 1
                if self.mode == 'block':
                    # Fail-Closed Intervention: Overwrite output with a safe warning
                    event.content.parts[0].text = (
                        "🛑 [SECURITY BLOCK] This response was withheld because it contained "
                        "sensitive information (PII/Card Data). Please do not share financial details."
                    )
                elif self.mode == 'mask':
                    event.content.parts[0].text = self.cc_pattern.sub("[REDACTED_CARD]", response_text)
                
                print(f"🛑 [SAFETY AUDIT] Guardrail triggered in invocation: {getattr(event, 'invocation_id', 'unknown')}")

# --- 2. Input Guardrail: Prompt Injection & Jailbreak Defense ---
class PromptInjectionDefensePlugin(BasePlugin):
    """
    Fail-Closed input guardrail: intercepts user input before the model reasons,
    detecting jailbreak triggers (e.g. 'ignore previous instructions').
    """
    def __init__(self, name: str = 'prompt_injection_defense'):
        super().__init__(name)
        self.jailbreak_patterns = [
            re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
            re.compile(r"system\s+override\s+mode", re.IGNORECASE),
            re.compile(r"disregard\s+safety\s+guidelines", re.IGNORECASE),
        ]
        self.blocked_inputs_count = 0

    async def before_model_callback(self, *, agent, request, **kwargs):
        if hasattr(request, "contents") and request.contents:
            for content in request.contents:
                if hasattr(content, "parts") and content.parts:
                    for part in content.parts:
                        text = getattr(part, "text", "")
                        if text:
                            for pattern in self.jailbreak_patterns:
                                if pattern.search(text):
                                    self.blocked_inputs_count += 1
                                    print(f"⚠️ [INJECTION ALERT] Detected malicious prompt attempt: '{text}'")
                                    raise PermissionError("Security Policy Violation: Malicious prompt injection detected.")

# --- 3. Agent Definition ---
agent = Agent(
    name="secure_enterprise_assistant",
    model="gemini-3.8-flash",
    instruction="""
    You are a secure corporate assistant. 
    If the user asks for 'mock card', respond with 'Here is your card: 1234-5678-9012-3456'.
    Otherwise, assist the user with professional inquiries.
    """
)

# --- 4. App Definition ---
pii_plugin = PIIGuardrailPlugin(mode="block")
injection_plugin = PromptInjectionDefensePlugin()

app = App(
    name="rai_safety_app",
    root_agent=agent,
    plugins=[pii_plugin, injection_plugin]
)

if __name__ == "__main__":
    print("RAI Safety Guardrails App loaded successfully.")
```

### Self-Reflection Answers

1. **Why is it better to block the response in a plugin rather than just adding "Don't say credit card numbers" to the agent's instructions?**
   * **Answer:** LLMs are probabilistic engines vulnerable to prompt injections, role-play jailbreaks, and context overflows. An ADK `BasePlugin` runs deterministic code on the hosting server outside the LLM reasoning loop, providing verifiable mathematical certainty for data loss prevention.

2. **How would you extend this plugin to log all blocked responses to a security database for auditing?**
   * **Answer:** Inside the `on_event_callback` intervention branch, dispatch an asynchronous task (via `asyncio.create_task`) sending structured telemetry containing `event.invocation_id`, timestamp, agent name, and redacted sample snippet to Cloud Logging, BigQuery, or a SIEM pipeline.

3. **Can you think of other safety use cases for this pattern?**
   * **Answer:**
     * **Tool Execution Guardrails:** Using `before_tool_callback` to enforce policy-based access control (e.g., blocking `execute_sql` with `DROP` or `DELETE` statements).
     * **Toxic Content & Competitor Redaction:** Using regex or lightweight local classification models to filter profane or unauthorized competitor trademarks.
     * **Error Stack Sanitization:** Using `on_tool_error_callback` to scrub internal SQL connection strings, hostnames, and stack traces before they leak to the user.
