---
sidebar_position: 3
title: "Lab Solution"
---

## Lab 25.5 Solution: Enterprise Multi-Layer Safety Guardrails

### `safety_guardrail/agent.py`

```python
import re
from google.adk import Agent
from google.adk.apps import App
from google.adk.events import Event
from google.adk.models.llm_response import LlmResponse
from google.adk.plugins import BasePlugin
from google.genai import types

# --- 1. Output Guardrail: PII Data Redaction / Block ---
class PIIGuardrailPlugin(BasePlugin):
    """
    Fail-Closed output guardrail: intercepts agent responses and overwrites
    or redacts sensitive financial data (credit cards, PII) before reaching the user.
    """
    def __init__(self, name: str = "pii_guardrail", mode: str = "block"):
        super().__init__(name)
        self.mode = mode  # 'block' or 'mask'
        self.cc_pattern = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")
        self.interventions_count = 0

    async def on_event_callback(self, *, event: Event, **kwargs):
        if event.is_final_response() and event.content and event.content.parts:
            response_text = event.content.parts[0].text
            if response_text and self.cc_pattern.search(response_text):
                self.interventions_count += 1
                if self.mode == "block":
                    event.content.parts[0].text = (
                        "🛑 [SECURITY BLOCK] This response was withheld because it contained "
                        "sensitive information (PII/Card Data). Please do not share financial details."
                    )
                elif self.mode == "mask":
                    event.content.parts[0].text = self.cc_pattern.sub("[REDACTED_CARD]", response_text)

                print(f"🛑 [SAFETY AUDIT] Egress guardrail triggered in invocation: {getattr(event, 'invocation_id', 'unknown')}")
                return event
        return None


# --- 2. Input Guardrail: Prompt Injection & Jailbreak Defense ---
class PromptInjectionDefensePlugin(BasePlugin):
    """
    Fail-Closed input guardrail: inspects the current user turn before the model reasons,
    returning a safe LlmResponse block without crashing or poisoning future turns.
    """
    def __init__(self, name: str = "prompt_injection_defense"):
        super().__init__(name)
        self.jailbreak_patterns = [
            re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
            re.compile(r"system\s+override\s+mode", re.IGNORECASE),
            re.compile(r"disregard\s+safety\s+guidelines", re.IGNORECASE),
        ]
        self.blocked_inputs_count = 0

    async def before_model_callback(self, *, callback_context, llm_request, **kwargs):
        # Scope inspection strictly to the current user turn so an earlier blocked message
        # in session history never poisons subsequent benign questions in the same session!
        current_contents = []
        if callback_context is not None:
            inv_ctx = callback_context.get_invocation_context()
            if inv_ctx and inv_ctx.user_content:
                current_contents = [inv_ctx.user_content]
        elif hasattr(llm_request, "contents") and llm_request.contents:
            current_contents = [llm_request.contents[-1]]

        for content in current_contents:
            if hasattr(content, "parts") and content.parts:
                for part in content.parts:
                    text = getattr(part, "text", "")
                    if text and any(p.search(text) for p in self.jailbreak_patterns):
                        self.blocked_inputs_count += 1
                        print("⚠️ [INJECTION ALERT] Blocked adversarial prompt injection attempt.")
                        return LlmResponse(
                            content=types.Content(
                                role="model",
                                parts=[
                                    types.Part(
                                        text="🛑 [SECURITY BLOCK] Security Policy Violation: Malicious prompt injection detected."
                                    )
                                ],
                            )
                        )
        return None


# --- 3. Agent Definition ---
root_agent = Agent(
    name="secure_enterprise_assistant",
    model="gemini-3.8-flash",
    instruction="""
    You are a secure corporate assistant.
    If the user asks for 'mock card', respond with 'Here is your card: 1234-5678-9012-3456'.
    Otherwise, assist the user with professional inquiries.
    """,
)

# --- 4. App Definition ---
pii_plugin = PIIGuardrailPlugin(mode="block")
injection_plugin = PromptInjectionDefensePlugin()

app = App(
    name="safety_guardrail",
    root_agent=root_agent,
    plugins=[pii_plugin, injection_plugin],
)

if __name__ == "__main__":
    print("RAI Safety Guardrails App loaded successfully.")
```

### Self-Reflection Answers

1. **Deterministic vs. Stochastic Defense:** System prompt instructions are probabilistic; jailbreaks or novel token alignments can manipulate the LLM into disregarding instructions. A `BasePlugin` runs deterministic Python code outside the LLM context window, guaranteeing that sensitive patterns are intercepted 100% of the time.
2. **Performance Impact:** In-process regex checks execute in sub-millisecond time (`< 0.1ms`), introducing negligible latency compared to secondary LLM judge calls (which add 300ms–1500ms and incur API token costs).
3. **Audit Trail Compliance:** Logging `event.invocation_id`, timestamp, user ID, and redaction metadata provides an immutable compliance trail for regulatory frameworks like SOC 2, HIPAA, and GDPR Article 30 without persisting raw sensitive payload data.
