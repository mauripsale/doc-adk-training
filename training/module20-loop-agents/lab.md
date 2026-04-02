---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 20: Building an Essay Refinement System Challenge

## Goal

### Goal

In this lab, you will build a self-improving agent system that uses a `LoopAgent` to iteratively refine an essay, demonstrating the powerful "Critic -> Refiner" pattern.

### The Architecture

1.  **Initial Writer:** An agent runs once to create the first draft.
2.  **Refinement Loop:** A `LoopAgent` runs repeatedly. In each loop:
    *   **Critic Agent:** Evaluates the current draft and provides feedback or an "APPROVED" message.
    *   **Refiner Agent:** Applies the feedback to improve the draft, or calls an `exit_loop` tool if the draft is approved.

### Step 1: Create the Project Structure

1.  **Create the agent project:**
    ```shell
    adk create essay_refiner
    ```
    When prompted, choose the **Programmatic (Python script)** option.

2.  **Navigate into the new directory:**
    ```shell
    cd essay_refiner
    ```

### Step 2: Assemble the Refinement System

**Exercise:** Open `agent.py`. The `exit_loop` tool and the three specialist agents (`initial_writer`, `critic`, `refiner`) have been provided for you. Your task is to assemble them into the complete looping architecture.

```python
# In agent.py (Starter Code)

from __future__ import annotations
from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent
from google.adk.tools.tool_context import ToolContext

# ===== Specialist Agents and Tools (Provided for you) =====

def exit_loop(tool_context: ToolContext):
    """Signals that the essay refinement is complete."""
    tool_context.actions.escalate = True
    # Return a minimal valid content part so the backend always produces a valid LlmResponse.
    return {"text": "Loop exited successfully."}

initial_writer = LlmAgent(name="InitialWriter", model="gemini-2.5-flash", ..., output_key="current_essay")
critic = LlmAgent(name="Critic", model="gemini-2.5-flash", ..., output_key="critique")
refiner = LlmAgent(name="Refiner", model="gemini-2.5-flash", ..., tools=[exit_loop], output_key="current_essay")

# =====================================================
# ASSEMBLE THE AGENT SYSTEM
# =====================================================

# ===== Create Refinement Loop =====

# TODO: 1. Create a `LoopAgent` named `refinement_loop`.
# TODO: 2. Add the `critic` and `refiner` agents to its `sub_agents` list
# in the correct order.
# TODO: 3. Set the `max_iterations` to a safe number, like 5, to prevent
# infinite loops.
refinement_loop = None

# ===== COMPLETE SYSTEM: Initial Draft + Refinement Loop =====

# TODO: 4. Create a `SequentialAgent` named `essay_refinement_system`.
# TODO: 5. Add the `initial_writer` as the first step and the
# `refinement_loop` as the second step.
essay_refinement_system = None

# TODO: 6. Set the `root_agent` to be your `essay_refinement_system`.
root_agent = None
```
*(Note: The full agent definitions are in the `lab-solution.md` if you need to inspect them.)*

### Step 3: Run and Test the System

1.  **Set up your `.env` file.**
2.  **Navigate to the parent directory** (`cd ..`) and start the Dev UI:
    ```shell
    adk web essay_refiner
    ```
3.  **Interact with the system:**
    *   Give it a topic, like: "The impact of artificial intelligence on society".
4.  **Analyze the Trace View:**
    *   Expand the trace to see the `InitialWriter` run once.
    *   Expand the `RefinementLoop` to see the multiple "Iterations".
    *   Inside each iteration, observe the `Critic` and `Refiner` at work.
    *   Watch the `current_essay` in the **State** tab improve with each loop.
    *   Find the final iteration where the `Refiner` calls the `exit_loop` tool.

### Having Trouble?

If you get stuck, you can find the complete, working code in the `lab-solution.md` file.

### Lab Summary

You have successfully built a self-correcting system using a `LoopAgent`. You have learned to:
*   How to implement the "Critic -> Refiner" pattern.
*   How to create and use an `exit_loop` tool for smart loop termination.
*   How to use state overwriting to refine data over multiple iterations.
*   How to combine a `LoopAgent` with a `SequentialAgent` to create complex workflows.

### Self-Reflection Questions
- Why is the `max_iterations` parameter a crucial safety feature for a `LoopAgent`? What could go wrong without it?
- In our "Critic -> Refiner" pattern, the `refiner` agent overwrites the `current_essay` in the state on each iteration. Why is this overwriting behavior essential for the loop to work correctly?
- Can you think of another problem, besides writing an essay, that could be solved effectively using a `LoopAgent` with a "Critic -> Refiner" pattern?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMjAtbG9vcC1hZ2VudHMvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module20-loop-agents/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
