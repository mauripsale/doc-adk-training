---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 39.5: Loading and Using Agent Skills

## Goal

In this lab, you will create a simple ADK Skill on your file system and configure an agent to use it via the `SkillToolset`.

### Step 1: Create the Project

1.  **Create a new agent project:**
    ```shell
    uv run adk create skills_agent
    ```
    Choose the **Programmatic (Python script)** option.

2.  **Navigate to the directory:**
    ```shell
    cd skills_agent
    ```

### Step 2: Create the Skill Directory

We need to create the physical structure for our skill.

1.  Inside `skills_agent`, create a directory called `skills`:
    ```shell
    mkdir skills
    ```
2.  Inside `skills`, create a directory for our specific skill:
    ```shell
    mkdir skills/greeting-skill
    ```
3.  Inside `skills/greeting-skill`, create the required `SKILL.md` file:
    ```shell
    touch skills/greeting-skill/SKILL.md
    ```

### Step 3: Write the Skill Instructions

Open `skills/greeting-skill/SKILL.md` in your editor and paste the following content. This defines the metadata (how the agent knows *when* to use it) and the body (the actual instructions).

```markdown
---
name: greeting-skill
description: The official Nebula-9 Collective greeting protocol. Use this skill any time the user greets you, says hello, or asks to be greeted.
---

# Nebula-9 Collective Greeting Protocol

You are now using the official Nebula-9 Collective Greeting Skill!

Step 1: Read the user's input to see if they provided a name.
Step 2: Respond using EXACTLY this template, replacing [NAME] with their name (or "traveler" if you don't know it):
"🌌 Greetings, [NAME]! Welcome aboard the Nebula-9 Collective. May your orbit be ever bright. 🚀✨"
Step 3: Do not deviate from this template under any circumstances -- no extra commentary before or after it.
```

This gives the skill a distinctive, made-up phrase ("Nebula-9 Collective") that a model could never produce on its own -- so if you see it in the final response, that's proof the skill actually loaded and was followed, not just the model being generically friendly.

### Step 4: Configure the Agent

**Exercise:** Open your main `agent.py` file. Your task is to load the skill from the directory and provide it to the agent.

```python
import pathlib
from google.adk.agents import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset
from google.adk.code_executors.unsafe_local_code_executor import UnsafeLocalCodeExecutor

# TODO: 1. Load the skill from the directory you created.
# Hint: Use pathlib.Path(__file__).parent / "skills" / "greeting-skill"
greeting_skill = None

# TODO: 2. Create the SkillToolset.
# Pass your loaded skill in a list to the `skills` parameter.
# We must include the code_executor even if we don't have scripts yet.
my_skill_toolset = None

# TODO: 3. Configure the Agent.
# Add your `my_skill_toolset` to the agent's `tools` list.
# Also add an `instruction` that names the skill explicitly and tells the
# agent it MUST call `load_skill('greeting-skill')` whenever the user
# greets it. A generic "check your skills if relevant" instruction is too
# weak in practice -- the model won't reliably invoke a skill for a message
# as simple as "hi" unless the skill and the trigger condition are named
# directly.
root_agent = Agent(
    model="gemini-3.5-flash",
    name="skill_user_agent",
    description="An agent that can use specialized skills.",
    # Add instruction and tools here
)
```

*(Note: The full implementation is available in the `lab-solution.md` if you need a hint.)*

### Step 5: Test the Skill

1.  **Set up your `.env` file.**
2.  **Navigate to the parent directory** (`cd ..`) and start the Dev UI:
    ```shell
    uv run adk web skills_agent
    ```
3.  **Interact with the system:**
    *   Say "Hello there, my name is Alex."
    *   You should receive the exact Nebula-9 Collective greeting template, including the made-up "Nebula-9 Collective" phrase -- proof the agent loaded and followed the `SKILL.md` instructions, not just a generic friendly reply.
4.  **Examine the Trace View:**
    *   Look at the trace. You should see the agent making a "tool call" to activate the `greeting-skill` skill. This is progressive disclosure in action!

### Self-Reflection Questions
- Look at your `SKILL.md` file. Which part of it is loaded into the agent's context *before* the user says hello? Which part is loaded *after*?
- Why do we have to wrap the skill in a `SkillToolset` before giving it to the agent? (Think about the other things a toolset might manage, like code executors or additional tools).
- Your `instruction` names `greeting-skill` and its trigger condition explicitly. What do you think would happen if you had 20 skills instead of 1 -- would naming every single one in the instruction still scale, and what does that suggest about the `search_skills`/Skill Registry pattern mentioned in "Going Further"?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMzlfNS1hZ2VudC1za2lsbHMvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module39_5-agent-skills/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
