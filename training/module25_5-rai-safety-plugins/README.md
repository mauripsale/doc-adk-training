---
sidebar_position: 25.5
title: "Module 25.5: Responsible AI (RAI) & Safety Plugins"
---

# Module 25.5: Responsible AI (RAI) & Safety Plugins

## Theory

Observability (Module 25) lets you see what your agent is doing. **Safety Plugins** let you *control* what your agent is allowed to say. In an enterprise environment, you cannot rely solely on the model's internal safety filters; you need a programmatic "Kill Switch" that enforces your company's specific policies.

### The "Fail-Closed" Pattern

The gold standard for AI safety is the **Fail-Closed** architecture. In this model, every response from an agent must pass through a mandatory safety check *before* it reaches the end user.

*   **Intercept**: The plugin intercepts the `request_complete` event.
*   **Evaluate**: A separate, specialized safety model or a regex-based engine checks the response for violations (e.g., PII leakage, competitor mentions, or harmful tone).
*   **Action**: If a violation is found, the plugin **blocks** the original message and replaces it with a safe, canned response.

### Implementing RAI with Plugins

ADK 2.0 plugins are perfect for this because they have access to the full `Event` object and can modify the context of the interaction.

```python
from google.adk.plugins import BasePlugin
from google.adk.events import Event

class SafetyGuardrailPlugin(BasePlugin):
    async def on_event_callback(self, *, event: Event, **kwargs):
        if event.event_type == 'request_complete':
            response_text = event.content.parts[0].text
            
            # Simple example: Block mentions of "Competitor X"
            if "Competitor X" in response_text:
                # 🛡️ THE INTERVENTION: Replace the output
                event.content.parts[0].text = "I'm sorry, but I cannot discuss other companies. How can I help you with our products?"
                print("🛑 [SAFETY] Response blocked due to policy violation.")
```

### Why use a Plugin for RAI?

1.  **Centralized Policy**: You can apply the same safety plugin to every agent in your organization, ensuring consistent compliance.
2.  **Immutability**: The core business logic of the agent remains unchanged. The safety layer is a "wrapper" that can be updated independently.
3.  **Auditability**: Your safety plugin can log all "interventions" to a secure audit trail (e.g., BigQuery), which is crucial for regulated industries.

### Key Takeaways
- **RAI is a requirement, not an option**, for production agents.
- **Fail-Closed** ensures that unsafe messages never reach the user.
- **Plugins** allow you to implement safety guardrails without polluting your agent's business logic.
- **Separation of Expertise**: The team managing safety policies can update the plugin without needing to understand the internal prompts of every agent.
