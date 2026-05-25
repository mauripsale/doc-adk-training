---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 20 Solution: Building an Essay Refinement System

## Goal

This file contains the complete code for the `agent.py` script in the Essay Refinement System lab.

### `essay_refiner/agent.py`

````python
# Part of agent.py --> Follow https://google.github.io/adk-docs/get-started/quickstart/ to learn the setup
import asyncio
import os
from google.adk.agents import LoopAgent, LlmAgent, BaseAgent, SequentialAgent
from google.genai import types
from google.adk.runners import InMemoryRunner
from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools.tool_context import ToolContext
from typing import AsyncGenerator, Optional
from google.adk.events import Event, EventActions

# --- Constants ---
APP_NAME = "doc_writing_app_v3"
USER_ID = "dev_user_01"
SESSION_ID_BASE = "loop_exit_tool_session"
GEMINI_MODEL = "gemini-3.5-flash"
STATE_INITIAL_TOPIC = "initial_topic"

# --- State Keys ---
STATE_CURRENT_DOC = "current_document"
STATE_CRITICISM = "criticism"

# Define the exact phrase the Critic should use to signal completion
COMPLETION_PHRASE = "No major issues found."

# --- Tool Definition ---
def exit_loop(tool_context: ToolContext):
    """Call this function ONLY when the critique indicates no further changes are needed, signaling the iterative process should end."""
    print(f" [Tool Call] exit_loop triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    # Return empty dict as tools should typically return JSON-serializable output
    return {}

# --- Agent Definitions ---

# STEP 1: Initial Writer Agent (Runs ONCE at the beginning)
initial_writer_agent = LlmAgent(
    name="InitialWriterAgent",
    model=GEMINI_MODEL,
    include_contents='none',
    # MODIFIED Instruction: Ask for a slightly more developed start
    instruction=f"""You are a Creative Writing Assistant tasked with starting a story.
Write the *first draft* of a short story (aim for 2-4 sentences).
Base the content *only* on the topic provided below.
Try to introduce a specific element (like a character, a setting detail, or a starting action) to make it engaging.

Topic: {{initial_topic}}

Output *only* the story/document text. Do not add introductions or explanations.
""",
    description="Writes the initial document draft based on the topic, aiming for some initial substance.",
    output_key=STATE_CURRENT_DOC
)

# STEP 2a: Critic Agent (Inside the Refinement Loop)
critic_agent_in_loop = LlmAgent(
    name="CriticAgent",
    model=GEMINI_MODEL,
    include_contents='none',
    # MODIFIED Instruction: More nuanced completion criteria, look for clear improvement paths.
    instruction=f"""You are a Constructive Critic AI reviewing a short document draft (typically 2-6 sentences).
Your goal is balanced feedback.

**Document to Review:**
```
{{current_document}}
```

**Task:**
Review the document for clarity, engagement, and basic coherence according to the initial topic (if known).

IF you identify 1-2 *clear and actionable* ways the document could be improved to better capture the topic or enhance reader engagement (e.g., "Needs a stronger opening sentence", "Clarify the character's goal"):
    Provide these specific suggestions concisely. Output *only* the critique text.

ELSE IF the document is coherent, addresses the topic adequately for its length, and has no glaring errors or obvious omissions:
    Respond *exactly* with the phrase "{COMPLETION_PHRASE}" and nothing else.
    It doesn't need to be perfect, just functionally complete for this stage.
    Avoid suggesting purely subjective stylistic preferences if the core is sound.

Do not add explanations. Output only the critique OR the exact completion phrase.
""",
    description="Reviews the current draft, providing critique if clear improvements are needed, otherwise signals completion.",
    output_key=STATE_CRITICISM
)

# STEP 2b: Refiner/Exiter Agent (Inside the Refinement Loop)
refiner_agent_in_loop = LlmAgent(
    name="RefinerAgent",
    model=GEMINI_MODEL,
    # Relies solely on state via placeholders
    include_contents='none',
    instruction=f"""You are a Creative Writing Assistant refining a document based on feedback OR exiting the process.

**Current Document:**
```
{{current_document}}
```

**Critique/Suggestions:**
{{criticism}}

**Task:**
Analyze the 'Critique/Suggestions'.

IF the critique is *exactly* "{COMPLETION_PHRASE}":
    You MUST call the 'exit_loop' function. Do not output any text.

ELSE (the critique contains actionable feedback):
    Carefully apply the suggestions to improve the 'Current Document'.
    Output *only* the refined document text. Do not add explanations.

Either output the refined document OR call the exit_loop function.
""",
    description="Refines the document based on critique, or calls exit_loop if critique indicates completion.",
    tools=[exit_loop], # Provide the exit_loop tool
    output_key=STATE_CURRENT_DOC # Overwrites state['current_document'] with the refined version
)

# STEP 2: Refinement Loop Agent
refinement_loop = LoopAgent(
    name="RefinementLoop",
    # Agent order is crucial: Critique first, then Refine/Exit
    sub_agents=[
        critic_agent_in_loop,
        refiner_agent_in_loop,
    ],
    max_iterations=5 # Limit loops
)

# STEP 3: Overall Sequential Pipeline
# For ADK tools compatibility, the root agent must be named `root_agent`
root_agent = SequentialAgent(
    name="IterativeWritingPipeline",
    sub_agents=[
        initial_writer_agent, # Run first to create initial doc
        refinement_loop       # Then run the critique/refine loop
    ],
    description="Writes an initial document and then iteratively refines it with critique using an exit tool."
)
````

### Self-Reflection Answers

1.  **Why is the `max_iterations` parameter a crucial safety feature for a `LoopAgent`? What could go wrong without it?**
    *   **Answer:** LLMs are non-deterministic. It is possible for the `critic` and `refiner` to get stuck in an endless cycle where the critic is never satisfied ("infinite loop"). Without `max_iterations`, the agent would run forever, consuming API credits and time, until the system crashed or timed out. The `max_iterations` parameter guarantees that the loop will eventually stop, even if the logical exit condition is never met.

2.  **In our "Critic -> Refiner" pattern, the `refiner` agent overwrites the `current_essay` in the state on each iteration. Why is this overwriting behavior essential for the loop to work correctly?**
    *   **Answer:** The goal is *iterative improvement*. Each time the loop runs, we want the agents to work on the *latest, best version* of the essay, not the original draft. By overwriting `current_essay` (or `current_document`), the Refiner ensures that in the next iteration, the Critic will evaluate the *revised* version. If we didn't overwrite it, the Critic would just critique the same original draft over and over again.

3.  **Can you think of another problem, besides writing an essay, that could be solved effectively using a `LoopAgent` with a "Critic -> Refiner" pattern?**
    *   **Answer:**
        *   **Code Generation:** Writer generates code -> Critic runs tests/linters -> Refiner fixes errors -> Loop until tests pass.
        *   **Translation:** Writer translates text -> Critic checks for nuance/accuracy -> Refiner adjusts phrasing.
        *   **Plan Generation:** Planner proposes a schedule -> Critic checks for conflicts -> Refiner adjusts times.