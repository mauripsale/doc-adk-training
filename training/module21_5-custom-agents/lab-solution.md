---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 21.5 Solution: Building a Smart Support Router

## Goal

This file contains the complete code for the `agent.py` script in the Smart Support Router lab.

### `support_router/agent.py`

```python
from __future__ import annotations
from pydantic import BaseModel, Field
from google.adk.agents import Agent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from typing import AsyncGenerator, Literal

# ===== Specialist Agents (Provided for you) =====

ai_support = Agent(
    name="ai_support_bot",
    model="gemini-3.5-flash",
    instruction="You are a helpful customer support AI. Answer the user's technical questions clearly."
)

human_escalation = Agent(
    name="human_escalation_team",
    model="gemini-3.5-flash",
    instruction="You are a human support representative. A customer is frustrated. Apologize profusely and tell them a human agent will call them immediately at the number on their account."
)

# ===== 1. Define Sentiment Schema =====
class SentimentClassification(BaseModel):
    sentiment: Literal["angry", "neutral", "happy"] = Field(
        description="The sentiment of the user's message."
    )

# ===== 2. Create the Classifier Agent =====
classifier = Agent(
    name="classifier",
    model="gemini-3.5-flash",
    instruction="Classify the sentiment of the user's latest message.",
    output_schema=SentimentClassification,
    output_key="user_sentiment"  # Saves JSON to state['user_sentiment']
)

# ===== 3. Build the Custom Router =====
class SmartRouterAgent(BaseAgent):
    
    def __init__(self, name: str, classifier: Agent, ai_support: Agent, human_escalation: Agent, **kwargs):
        super().__init__(name=name, **kwargs)
        self.classifier = classifier
        self.ai_support = ai_support
        self.human_escalation = human_escalation

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        
        # Step 3a: Run the classifier SILENTLY.
        # We execute the generator, but we DO NOT `yield` its events.
        # We just want it to do its job and save the structured output to the state.
        async for _ in self.classifier.run_async(ctx):
            pass 
        
        # Step 3b: Read the classification from the state.
        sentiment_data = ctx.session.state.get("user_sentiment")
        
        # Step 3c: Routing Logic.
        # We access the 'sentiment' key from the dictionary returned by the Pydantic schema
        if sentiment_data and sentiment_data.get("sentiment") == "angry":
            chosen_agent = self.human_escalation
            # Optional: Add an internal trace event so developers can see the routing decision
            yield Event(author=self.name, content="[System Log] Routing to Human Escalation due to angry sentiment.")
        else:
            chosen_agent = self.ai_support
            
        # Step 3d: Execute the chosen agent and stream its response to the user.
        # We MUST yield these events so the UI receives the final answer.
        async for event in chosen_agent.run_async(ctx):
            yield event

# ===== COMPLETE SYSTEM =====
support_system = SmartRouterAgent(
    name="SupportSystem",
    classifier=classifier,
    ai_support=ai_support,
    human_escalation=human_escalation
)

# Set the root agent for the ADK
root_agent = support_system
```

### Self-Reflection Answers

1.  **Why did we build a custom `SmartRouterAgent` instead of just giving an `LlmAgent` a tool called `escalate_to_human`? (Think about control and determinism).**
    *   **Answer:** If we gave an `LlmAgent` an escalation tool, we would be relying entirely on the LLM's unpredictable reasoning to decide *when* to use it. A custom `BaseAgent` provides **deterministic control**. We enforce a strict, unbreakable rule: *If sentiment == angry, route to human*. This guarantees that angry customers are *always* escalated without fail, avoiding the risk of a conversational AI trying to argue with a frustrated user instead of calling the tool.

2.  **In Step 3a, why did we loop over `self.classifier.run_async(ctx)` but intentionally *not* yield the events? What would happen if we did yield them?**
    *   **Answer:** The `classifier` agent generates text (the JSON string `{"sentiment": "angry"}`). If we yielded those events, the user would see raw JSON pop up in their chat interface before receiving the actual response. By running the generator but swallowing the events (`async for _ in ... pass`), we allow the agent to execute its internal side-effects (saving the output to `ctx.session.state` via `output_key`), but we hide the messy intermediate generation from the final user.

3.  **How could you extend this custom agent to also include a Loop Agent? (e.g., if the AI support bot's answer isn't helpful, loop back to the user for clarification before escalating).**
    *   **Answer:** You could create a `LoopAgent` that contains the `ai_support` agent and a `UserClarificationAgent`. In your `SmartRouterAgent`'s `_run_async_impl`, instead of routing directly to `self.ai_support`, you would route to the `self.support_loop_agent` you instantiated. The custom agent orchestrator doesn't care if its sub-components are simple `LlmAgent`s, `SequentialAgent`s, or complex `LoopAgent`s—it just calls `run_async()` on whichever component it decides should handle the execution.
