---
sidebar_position: 4
title: "Module 4: Core Agent Concepts: `LlmAgent` Deep Dive"
---

# Module 4: Core Agent Concepts: `LlmAgent` Deep Dive

## Theory

### The "Brain" of the Operation

At the heart of most agents you build with the ADK is the `LlmAgent`. This is the component that acts as the "thinking" part of your application. It uses the power of a Large Language Model (LLM) like Gemini to understand user requests, reason about them, and decide on a course of action.

Unlike a traditional program that follows a fixed, deterministic path, an `LlmAgent` is non-deterministic. It interprets the context of a conversation and its own instructions to dynamically figure out what to do next. This flexibility is what makes agents so powerful.

Building an effective `LlmAgent` requires a clear understanding of its core configuration parameters. In this module, we'll take a deep dive into the most important one: the `instruction`.

### Defining the Agent's Identity

As you saw in the previous module, every `LlmAgent` has a few basic identity parameters, which can be set in `agent.py` or, for simpler agents, in a `root_agent.yaml` file:

*   **`name` (Required):** A unique identifier for the agent (e.g., `echo_agent`).
*   **`description` (Optional):** A short summary of the agent's purpose.
*   **`model` (Required):** The specific LLM that powers the agent (e.g., `gemini-3.5-flash`).

### The Art of the Instruction

While the `name` and `model` are essential, the **`instruction`** parameter is where you truly shape your agent's behavior. The instruction is the master prompt that is sent to the LLM with every user request. It is your primary tool for controlling the agent.

A well-crafted instruction tells the agent:

*   **Its Persona:** How should it behave? Is it a formal assistant, a witty pirate, a helpful teacher?
    *   *Example:* `"You are a cheerful and enthusiastic assistant."*
*   **Its Core Goal:** What is its primary function?
    *   *Example:* `"Your main goal is to help users find information about movies."*
*   **Its Constraints and Rules:** What should it *not* do? Are there topics it should avoid?
    *   *Example:* `"You must never give financial advice. If asked, politely decline."*
    *   **Production Readiness:** Defining clear constraints is a critical practice for ensuring the safety and reliability of an agent in a production environment.
*   **Its Process:** If the task involves multiple steps, you can outline them.
    *   *Example:* `"First, ask the user for their location. Second, find the weather for that location. Third, report the weather to the user."*
*   **Its Output Format:** How should it format its responses?
    *   *Example:* `"Always present your final answer as a JSON object with a 'result' key."*

### Tips for Effective Instructions (Prompt Engineering)

Crafting good instructions is a skill often called "prompt engineering." Here are some tips:

*   **Be Clear and Specific:** Ambiguity is the enemy. The more precise your instructions, the more reliable the agent's behavior will be.
*   **Use Simple Language:** Write instructions as if you were talking to a person. Avoid jargon.
*   **Provide Examples (Few-Shot Prompting):** One of the most powerful techniques is to include examples directly in the instruction. This is especially useful for categorization tasks.

    **Python Example (`agent.py`):**
    ```python
    from google.adk.agents import LlmAgent

    root_agent = LlmAgent(
        name="support_classifier",
        model="gemini-3.5-flash",
        instruction="""
          You are a customer support triage agent. 
          Your purpose is to read the user's message and categorize it into one of three departments: "billing", "technical", or "general".
          You must also determine the urgency as "high" or "low".
          Do not try to solve the user's problem; only respond with the categorization and urgency.

          Example User Input: "I was overcharged on my last invoice."
          Example Agent Output: Category: billing, Urgency: high

          Example User Input: "How do I reset my password?"
          Example Agent Output: Category: technical, Urgency: low
          
          Example User Input: "What are your business hours?"
          Example Agent Output: Category: general, Urgency: low
        """
    )
    ```

    **YAML Alternative (`root_agent.yaml`):**
    ```yaml
    instruction: |
      You are a customer support triage agent. 
      Your purpose is to read the user's message and categorize it into one of three departments: "billing", "technical", or "general".
      You must also determine the urgency as "high" or "low".
      Do not try to solve the user's problem; only respond with the categorization and urgency.

      Example User Input: "I was overcharged on my last invoice."
      Example Agent Output: Category: billing, Urgency: high

      Example User Input: "How do I reset my password?"
      Example Agent Output: Category: technical, Urgency: low
      
      Example User Input: "What are your business hours?"
      Example Agent Output: Category: general, Urgency: low
    ```
*   **Iterate and Refine:** Your first instruction will rarely be your last. Test your agent with different inputs and refine the instruction based on its responses.

In the lab for this module, you will practice this skill by building a structured version of this Support Classifier agent.

### Advanced Configuration: Structured Output & State (v1.0)

In many production scenarios, you don't just want a text response; you need **structured data**. The ADK v1.0 provides two powerful parameters for this:

#### 1. Enforcing JSON with `output_schema`
You can pass a Pydantic model to the `output_schema` parameter. This forces the LLM to respond *only* with a JSON object that matches that schema.

```python
from pydantic import BaseModel
from google.adk.agents import LlmAgent

class SentimentOutput(BaseModel):
    sentiment: str
    confidence: float

analyzer_agent = LlmAgent(
    name="sentiment_analyzer",
    model="gemini-3.5-flash",
    instruction="Analyze the sentiment of the user's message.",
    output_schema=SentimentOutput # Force JSON output
)
```
**CRITICAL LIMITATION:** When `output_schema` is set, the agent **cannot use tools** or delegate to other agents. Use it for data extraction, classification, or formatting tasks.

#### 2. Passing Data with `output_key`
The `output_key` parameter (a string) tells the ADK to take the final text of the agent's response and save it automatically into the session state dictionary (`ctx.session.state`).

```python
agent = LlmAgent(
    # ...
    output_key="analysis_result" # Saves output to state['analysis_result']
)
```
This is essential for building multi-agent systems where one agent's output is needed as another agent's input.

### Key Takeaways
- The `LlmAgent` is the "brain" of an ADK application, using an LLM to reason and decide on actions.
- The `instruction` parameter is the most powerful tool for controlling an agent's behavior, defining its persona, goals, constraints, and process.
- **`output_schema`** (v1.0): Allows enforcing a strict JSON structure for the agent's response using Pydantic. **Note:** Enabling this disables tool use and agent transfers.
- **`output_key`** (v1.0): Automatically saves the agent's final response into the session state (`ctx.session.state`) under the specified key, facilitating data passing between agents.
- Effective prompt engineering involves being specific, using simple language, providing examples (few-shot prompting), and iterating on your instructions.
