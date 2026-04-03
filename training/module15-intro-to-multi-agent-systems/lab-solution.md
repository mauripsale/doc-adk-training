---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 15 Solution: Designing a Multi-Agent System

## Goal

This lab was a conceptual design exercise. There is no single "correct" solution, but this file provides a more detailed example of the design planned in the lab, prioritizing the Python-first approach.

### Python Design (Primary Approach)

Here is a more fleshed-out version of the agent designs as they would be implemented in Python files.

#### `greeting_agent/agent.py` (The Router)

```python
from google.adk.agents import LlmAgent
from . import spanish_greeter_agent

root_agent = LlmAgent(
    name="router_agent",
    model="gemini-2.5-flash",
    instruction="""
You are a language routing specialist for a greeting service. Your primary function is to identify the language requested by the user and delegate the task to the correct sub-agent.

Available specialists:
- `spanish_greeter_agent`: Handles greetings in Spanish.

Your rules:
1.  Analyze the user's query to determine the language.
2.  If the user requests a greeting in Spanish, you MUST delegate to the `spanish_greeter_agent`.
3.  If the user requests a greeting in a language for which you do not have a specialist, you MUST respond with: "I'm sorry, I don't have a specialist for that language yet."
4.  Do not attempt to provide greetings yourself. Your only job is to route the request.
""",
    sub_agents=[spanish_greeter_agent.agent]
)
```

#### `greeting_agent/spanish_greeter_agent.py` (The Specialist)

```python
from google.adk.agents import LlmAgent

agent = LlmAgent(
    name="spanish_greeter_agent",
    model="gemini-2.5-flash",
    description="This agent is an expert at providing warm, friendly, and culturally appropriate greetings in Spanish. Use this for any user request related to Spanish greetings.",
    instruction="""
You are a friendly and enthusiastic assistant who communicates ONLY in Spanish.
Your sole responsibility is to provide a single, warm greeting to the user.

Examples of good greetings:
- "¡Hola! ¿Qué tal? ¡Mucho gusto en conocerte!"
- "¡Hola, bienvenido! Es un placer saludarte."

Your rules:
1.  Your entire response MUST be in Spanish.
2.  Do not translate the user's request or your response.
3.  Greet the user warmly and then stop. Do not engage in further conversation.
"""
)
```

---

### YAML Design (Alternative Approach)

Here is how the same system would be designed using YAML configuration files.

#### `greeting_agent/root_agent.yaml` (The Router)

```yaml
name: router_agent
model: gemini-2.5-flash
instruction: |
  You are a language routing specialist for a greeting service. Your primary function is to identify the language requested by the user and delegate the task to the correct sub-agent.

  Available specialists:
  - `spanish_greeter_agent`: Handles greetings in Spanish.

  Your rules:
  1.  Analyze the user's query to determine the language.
  2.  If the user requests a greeting in Spanish, you MUST delegate to the `spanish_greeter_agent`.
  3.  If the user requests a greeting in a language for which you do not have a specialist, you MUST respond with: "I'm sorry, I don't have a specialist for that language yet."
  4.  Do not attempt to provide greetings yourself. Your only job is to route the request.
sub_agents:
  - config_path: spanish_greeter_agent.yaml
```

#### `greeting_agent/spanish_greeter_agent.yaml` (The Specialist)

```yaml
name: spanish_greeter_agent
model: gemini-2.5-flash
description: This agent is an expert at providing warm, friendly, and culturally appropriate greetings in Spanish. Use this for any user request related to Spanish greetings.
instruction: |
  You are a friendly and enthusiastic assistant who communicates ONLY in Spanish.
  Your sole responsibility is to provide a single, warm greeting to the user.

  Examples of good greetings:
  - "¡Hola! ¿Qué tal? ¡Mucho gusto en conocerte!"
  - "¡Hola, bienvenido! Es un placer saludarte."

  Your rules:
  1.  Your entire response MUST be in Spanish.
  2.  Do not translate the user's request or your response.
  3.  Greet the user warmly and then stop. Do not engage in further conversation.
```

---

### Alternative Design: Using an `AgentTool`

While LLM-driven delegation is powerful, another way to structure this would be to use an `AgentTool`. In this alternative design, the `router_agent` would treat the `spanish_greeter_agent` as a tool.

*   **`spanish_greeter_agent`:** Would be wrapped in an `AgentTool`.
*   **`router_agent`:**
    *   Its instruction would be to *call* the `spanish_greeter_tool` when appropriate.
    *   This would allow the `router_agent` to get a result back from the specialist and potentially do more work. For example, it could log that a greeting was successfully delivered.

This approach is less of a hand-off and more of a function call, giving the parent agent more control over the workflow. You will learn more about this pattern in later modules.

### Self-Reflection Answers

1.  **What is the most important piece of information that allows the `router_agent` to decide which specialist to delegate to?**
    *   **Answer:** The `description` field of the sub-agent. The parent agent's LLM reads the descriptions of all available sub-agents to understand their capabilities. A clear, specific description like "An expert at providing friendly greetings in Spanish" is crucial for accurate routing.

2.  **How would you extend this system to support a new language, like French? What new files or modifications would you need to make?**
    *   **Answer:** You would need to:
        1.  Create a new file `french_greeter_agent.py` (or `.yaml`).
        2.  Define the `french_greeter_agent` with instructions for French greetings.
        3.  Modify the `agent.py` of the router agent to import the new module and add `french_greeter_agent.agent` to the `sub_agents` list.

3.  **This lab uses LLM-driven delegation (agent transfer). What might be the advantages or disadvantages of this approach compared to the `router_agent` using an `AgentTool` to explicitly call the `spanish_greeter_agent`?**
    *   **Answer:**
        *   **Agent Transfer (Delegation):**
            *   **Advantage:** Simpler flow. Once the router hands off, it's done. The specialist interacts directly with the user, which is great for long conversations or expert-led interactions.
            *   **Disadvantage:** The router loses control. It doesn't know what the specialist said or did.
        *   **AgentTool (Invocation):**
            *   **Advantage:** Control. The router calls the specialist like a function, gets the result back, and can then decide what to do next (e.g., summarize, log, or call another tool).
            *   **Disadvantage:** More complex to set up. The router stays "in the loop" for every turn, which might be unnecessary if the goal is just a simple hand-off.
