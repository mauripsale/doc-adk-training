---
sidebar_position: 2
title: "Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 25.5: Building a "Fail-Closed" Safety Guardrail

## Goal

In this lab, you will implement a professional **RAI (Responsible AI) Plugin** that acts as a mandatory safety guardrail. You will build a system that detects sensitive information (like credit card numbers) and blocks the agent's response if such data is present.

This demonstrates the **Fail-Closed** pattern used in enterprise AI applications.

### Step 1: Create the Project

<Setup/>

1.  **Create a new project:**
    ```shell
    uv run adk create safety_guardrail
    ```

### Step 2: Implement the Safety Plugin

Open `agent.py`. You need to create a class that intercepts the agent's final response and checks it for PII (Personally Identifiable Information).

**Exercise:** Complete the `on_event_callback` to detect a simple credit card pattern (4-4-4-4 digits) and block the response.

```python
# In agent.py (Starter Code)
import re
from google.adk import Agent, Context
from google.adk.events import Event
from google.adk.apps import App
from google.adk.plugins import BasePlugin

class PIIGuardrailPlugin(BasePlugin):
    """Blocks responses containing potential credit card numbers."""
    def __init__(self, name: str = 'pii_guardrail'):
        super().__init__(name)
        # Simple regex for XXXX-XXXX-XXXX-XXXX
        self.cc_pattern = re.compile(r"\b\d{4}-\d{4}-\d{4}-\d{4}\b")

    async def on_event_callback(self, *, event: Event, **kwargs):
        # TODO: 1. Only act on final responses -- check event.is_final_response()
        # (there's no separate "event_type" field to compare against).

        # TODO: 2. Extract the response text from event.content.parts[0].text
        # (guard against event.content or the text being empty/None).

        # TODO: 3. Use self.cc_pattern.search() to check for violations

        # TODO: 4. If a violation is found:
        # - Overwrite event.content.parts[0].text with a safety warning.
        # - Print a log message including event.invocation_id (events don't
        #   have a session_id field).
        pass

# --- Agent that might 'leak' data (for testing) ---
agent = Agent(
    name="leak_agent",
    model="gemini-3.5-flash",
    instruction="""
    You are a testing assistant. 
    If the user asks for 'test data', respond with: 'Here is your card: 1234-5678-9012-3456'.
    Otherwise, answer normally.
    """
)

# --- Register Plugin with App ---
app = App(
    name="safety_demo",
    root_agent=agent,
    plugins=[PIIGuardrailPlugin()]
)
```

### Step 3: Test the Guardrail

1.  **Launch the Dev UI:**
    ```shell
    uv run adk web .
    ```
2.  **Trigger the Leak:**
    - Ask: "Give me some test data."
    - **Observe:** The agent's raw response (seen in the Trace) will contain the card number, but the **Final Response** shown to the user should be your safety warning.
3.  **Normal Interaction:**
    - Ask: "What is the capital of Italy?" -> Should work normally.

### Lab Summary

You have built an active safety layer for your agent!
- You implemented the **Fail-Closed** pattern using a Plugin.
- You learned how to **intercept and modify** agent events before they reach the user.
- You realized that safety logic can be managed centrally, independently of the LLM's own internal filters.

### Self-Reflection Questions
- Why is it better to block the response in a plugin rather than just adding "Don't say credit card numbers" to the agent's instructions?
- How would you extend this plugin to log all blocked responses to a security database for auditing?
- Can you think of other "safety" use cases for this pattern (e.g., detecting competitor names, preventing offensive language)?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMjVfNS1yYWktc2FmZXR5LXBsdWdpbnMvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module25_5-rai-safety-plugins/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
