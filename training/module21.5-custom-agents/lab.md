---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 21.5: Building a Smart Support Router Challenge

## Goal

### Goal

In this lab, you will build a complex orchestration system using a **Custom Agent**. You will create a `SmartRouterAgent` that intercepts user requests, uses a fast LLM to classify the sentiment (angry, neutral, happy), and then deterministically routes the request to the appropriate specialist agent based on that sentiment.

This is a powerful pattern for customer support systems, where angry customers need immediate human escalation, while neutral queries can be handled by an AI.

### Step 1: Create the Project Structure

1.  **Create a new project:**
    ```shell
    adk create support_router
    ```
    When prompted, choose the **Programmatic (Python script)** option.

2.  **Navigate into the new directory:**
    ```shell
    cd support_router
    ```

### Step 2: Implement the Custom Router

**Exercise:** Open `agent.py`. The two specialist agents (`ai_support` and `human_escalation`) have been provided for you. 

Your task is to implement the `SmartRouterAgent` class, which must inherit from `BaseAgent` and override its `_run_async_impl` method. 

```python
# In agent.py (Starter Code)

from __future__ import annotations
from pydantic import BaseModel, Field
from google.adk.agents import Agent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from typing import AsyncGenerator, Literal

# ===== Specialist Agents (Provided for you) =====

ai_support = Agent(
    name="ai_support_bot",
    model="gemini-2.5-flash",
    instruction="You are a helpful customer support AI. Answer the user's technical questions clearly."
)

human_escalation = Agent(
    name="human_escalation_team",
    model="gemini-2.5-flash",
    instruction="You are a human support representative. A customer is frustrated. Apologize profusely and tell them a human agent will call them immediately at the number on their account."
)

# ===== 1. Define Sentiment Schema =====

# TODO: We need a fast classification agent. Let's force it to output structured data.
# Define a Pydantic BaseModel called `SentimentClassification` with a single field 
# `sentiment` that must be a Literal of "angry", "neutral", or "happy".
class SentimentClassification(BaseModel):
    pass

# ===== 2. Create the Classifier Agent =====

# TODO: Create a very fast `LlmAgent` named `classifier`.
# Give it an instruction to "Classify the sentiment of the user's latest message."
# Use your `SentimentClassification` schema for its `output_schema` and 
# set `output_key="user_sentiment"`.
classifier = None

# ===== 3. Build the Custom Router =====

# TODO: Create the `SmartRouterAgent` class inheriting from `BaseAgent`.
class SmartRouterAgent(BaseAgent):
    
    # Accept our sub-components in the constructor
    def __init__(self, name: str, classifier: Agent, ai_support: Agent, human_escalation: Agent, **kwargs):
        super().__init__(name=name, **kwargs)
        self.classifier = classifier
        self.ai_support = ai_support
        self.human_escalation = human_escalation

    # TODO: Implement the engine
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        pass
        
        # Step 3a: Run the classifier agent to determine sentiment.
        # Hint: Use `async for event in self.classifier.run_async(ctx):` but DO NOT yield 
        # these events to the user. We just want the classifier to populate the state silently.
        
        # Step 3b: Read the classification from the state.
        # Hint: `ctx.session.state.get("user_sentiment")`
        
        # Step 3c: Routing Logic.
        # If the sentiment dict has a "sentiment" value of "angry", choose the `human_escalation` agent.
        # Otherwise, choose the `ai_support` agent.
        
        # Step 3d: Execute the chosen agent.
        # Hint: Use `async for event in chosen_agent.run_async(ctx):` and this time, 
        # YOU MUST yield the event so the user sees the final response!

# ===== COMPLETE SYSTEM =====

# Instantiate your custom router
support_system = SmartRouterAgent(
    name="SupportSystem",
    classifier=classifier,
    ai_support=ai_support,
    human_escalation=human_escalation
)

# Set the root agent for the ADK
root_agent = support_system
```

*(Note: The full implementation is available in the `lab-solution.md` if you need a hint.)*

### Step 3: Run and Test the Router

1.  **Set up your `.env` file.**
2.  **Navigate to the parent directory** (`cd ..`) and start the Dev UI:
    ```shell
    adk web support-router
    ```
3.  **Interact with the system:**
    *   **Test 1 (Neutral):** Send "How do I reset my password?". You should get a helpful technical response from the `ai_support_bot`.
    *   **Test 2 (Angry):** Send "THIS APP IS TERRIBLE! I WANT A REFUND NOW!". You should instantly get an apology and an escalation message from the `human_escalation_team`.
4.  **Examine the Trace View:**
    *   Look closely at the Trace. Notice how the `classifier` agent runs first, but its output is hidden from the main chat interface. 
    *   Then, notice how your custom router decides which agent to execute next based on the hidden state.

### Lab Summary

You have successfully built a sophisticated routing orchestrator using a Custom Agent! You have learned:
*   How to inherit from `BaseAgent` and override `_run_async_impl`.
*   How to execute sub-agents silently to populate the session state.
*   How to read from the `InvocationContext` (`ctx.session.state`) to make deterministic routing decisions.
*   How to yield events from a delegated sub-agent back to the user interface.

### Self-Reflection Questions
- Why did we build a custom `SmartRouterAgent` instead of just giving an `LlmAgent` a tool called `escalate_to_human`? (Think about control and determinism).
- In Step 3a, why did we loop over `self.classifier.run_async(ctx)` but intentionally *not* yield the events? What would happen if we did yield them?
- How could you extend this custom agent to also include a Loop Agent? (e.g., if the AI support bot's answer isn't helpful, loop back to the user for clarification before escalating).

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMjEuNS1jdXN0b20tYWdlbnRzL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module21.5-custom-agents/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
