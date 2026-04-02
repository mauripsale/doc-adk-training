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
    adk create skills_agent
    ```
    Choose the **Programmatic (Python script)** option.

2.  **Navigate to the directory:**
    ```shell
    cd skills_agent
    ```

### Step 2: Create the Skill Directory

We need to create the physical structure for our skill.

1.  Inside `skills-agent`, create a directory called `skills`:
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
description: A friendly greeting skill that can say hello to a specific person. Use this skill whenever the user asks to be greeted or says hello.
---

# Greeting Skill Instructions

You are now using the Greeting Skill!

Step 1: Read the user's input to see if they provided a name.
Step 2: Respond with a very enthusiastic, friendly greeting using emojis (like 👋 and ✨).
Step 3: If you don't know their name, greet them as "friend".
```

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
root_agent = Agent(
    model="gemini-2.5-flash",
    name="skill_user_agent",
    description="An agent that can use specialized skills.",
    # Add tools here
)
```

*(Note: The full implementation is available in the `lab-solution.md` if you need a hint.)*

### Step 5: Test the Skill

1.  **Set up your `.env` file.**
2.  **Navigate to the parent directory** (`cd ..`) and start the Dev UI:
    ```shell
    adk web skills-agent
    ```
3.  **Interact with the system:**
    *   Say "Hello there, my name is Alex."
    *   You should receive a highly enthusiastic response with emojis, proving the agent loaded and followed the `SKILL.md` instructions!
4.  **Examine the Trace View:**
    *   Look at the trace. You should see the agent making a "tool call" to activate the `greeting-skill`. This is progressive disclosure in action!

### Self-Reflection Questions
- Look at your `SKILL.md` file. Which part of it is loaded into the agent's context *before* the user says hello? Which part is loaded *after*?
- Why do we have to wrap the skill in a `SkillToolset` before giving it to the agent? (Think about the other things a toolset might manage, like code executors or additional tools).

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMzkuNS1hZ2VudC1za2lsbHMvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module39.5-agent-skills/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
