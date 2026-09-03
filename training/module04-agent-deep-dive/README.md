---
sidebar_position: 4
title: "Module 4: Core Agent Concepts: Agent Deep Dive"
---

# Module 4: Core Agent Concepts: Agent Deep Dive

## Theory

### The "Brain" of the Operation

At the heart of most applications you build with the ADK is the **`Agent`**. This is the component that acts as the "thinking" part of your application. It uses the power of a Large Language Model (LLM) like Gemini to understand user requests, reason about them, and decide on a course of action.

In ADK 2.0, the `Agent` class (formerly `Agent`) is the primary node type for LLM-powered reasoning. Unlike a traditional program that follows a fixed, deterministic path, an `Agent` is non-deterministic. It interprets the context of a conversation and its own instructions to dynamically figure out what to do next. This flexibility is what makes agents so powerful.

Building an effective `Agent` requires a clear understanding of its core configuration parameters. In this module, we'll take a deep dive into the most important one: the `instruction`.

### Defining the Agent's Identity

Every `Agent` has a few basic identity parameters:

*   **`name` (Required):** A unique identifier for the agent (e.g., `echo_agent`).
*   **`description` (Optional):** A short summary of the agent's purpose.
*   **`model` (Required):** The specific LLM that powers the agent (e.g., `gemini-3.5-flash`).

### The Art of the Instruction

While the `name` and `model` are essential, the **`instruction`** parameter is where you truly shape your agent's behavior. The instruction is the master prompt that is sent to the LLM with every user request. It is your primary tool for controlling the agent.

A well-crafted instruction tells the agent:

*   **Its Persona:** How should it behave? Is it a formal assistant, a witty pirate, a helpful teacher?
    *   *Example:* `"You are a cheerful and enthusiastic assistant."`
*   **Its Core Goal:** What is its primary function?
    *   *Example:* `"Your main goal is to help users find information about movies."`
*   **Its Constraints and Rules:** What should it *not* do? Are there topics it should avoid?
    *   *Example:* `"You must never give financial advice. If asked, politely decline."`
    *   **Production Readiness:** Defining clear constraints is a critical practice for ensuring the safety and reliability of an agent in a production environment.
*   **Its Process:** If the task involves multiple steps, you can outline them.
    *   *Example:* `"First, ask the user for their location. Second, find the weather for that location. Third, report the weather to the user."`
*   **Its Output Format:** How should it format its responses?
    *   *Example:* `"Always present your final answer as a JSON object with a 'result' key."`

### Tips for Effective Instructions (Prompt Engineering)

Crafting good instructions is a skill often called "prompt engineering." Here are some tips:

*   **Be Clear and Specific:** Ambiguity is the enemy. The more precise your instructions, the more reliable the agent's behavior will be.
*   **Use Simple Language:** Write instructions as if you were talking to a person. Avoid jargon.
*   **Provide Examples (Few-Shot Prompting):** One of the most powerful techniques is to include examples directly in the instruction. This is especially useful for categorization tasks.

    **Python Example (`agent.py`):**
    ```python
    from google.adk import Agent

    root_agent = Agent(
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

### Advanced Configuration: Structured Output & State

In many production scenarios, you don't just want a text response; you need **structured data**. ADK 2.0 provides two powerful parameters for this:

#### 1. Enforcing JSON with `output_schema`
You can pass a Pydantic model to the `output_schema` parameter. This forces the LLM to respond *only* with a JSON object that matches that schema.

```python
from pydantic import BaseModel
from google.adk import Agent

class SentimentOutput(BaseModel):
    sentiment: str
    confidence: float

analyzer_agent = Agent(
    name="sentiment_analyzer",
    model="gemini-3.5-flash",
    instruction="Analyze the sentiment of the user's message.",
    output_schema=SentimentOutput # Force JSON output
)
```
**Note:** ADK 2.0 supports using `output_schema` and `tools` together -- the agent can still call tools during its thought loop, and structure is only enforced on the final output. `output_schema` is best suited for data extraction, classification, or formatting tasks where the final answer needs a strict shape.

#### 2. Passing Data with `output_key`
The `output_key` parameter (a string) tells the ADK to take the final text of the agent's response and save it automatically into the session state dictionary (`ctx.session.state`).

```python
agent = Agent(
    # ...
    output_key="analysis_result" # Saves output to state['analysis_result']
)
```
This is essential for building multi-agent systems where one agent's output is needed as another agent's input.

### Key Takeaways
- The **`Agent`** class is the "brain" of an ADK 2.0 application.
- The `instruction` parameter is the most powerful tool for controlling behavior.
- **`output_schema`**: Enforces strict JSON output via Pydantic on the final response -- the agent can still call tools during its thought loop; only the final answer is constrained to the schema.
- **`output_key`**: Automatically saves the agent's response into the session state for cross-node data passing.
