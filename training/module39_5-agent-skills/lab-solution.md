---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 39.5 Solution: Loading and Using Agent Skills

## Goal

This file contains the complete code for the `agent.py` script in the Agent Skills lab.

### `skills_agent/agent.py`

```python
import pathlib
from google.adk.agents import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset
from google.adk.code_executors.unsafe_local_code_executor import UnsafeLocalCodeExecutor

# 1. Load the skill from the directory you created.
# We use pathlib to reliably point to the folder relative to this script.
greeting_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "greeting-skill"
)

# 2. Create the SkillToolset.
# The toolset acts as a manager for one or more skills.
# WARNING: UnsafeLocalCodeExecutor is used here for local execution.
# In a real production environment, you would use a secure, sandboxed executor.
my_skill_toolset = SkillToolset(
    skills=[greeting_skill],
    # We could add additional_tools=[] here if the skill needed python functions
    code_executor=UnsafeLocalCodeExecutor(),
)

# 3. Configure the Agent.
# The toolset is passed just like any other tool. The instruction names the
# skill and its trigger condition explicitly -- a generic "check your skills
# if relevant" instruction is too weak in practice for a message as simple
# as a greeting; the model won't reliably call load_skill() without being
# told exactly when to.
root_agent = Agent(
    model="gemini-3.5-flash",
    name="skill_user_agent",
    description="An agent that can use specialized skills.",
    instruction=(
        "You have a skill named 'greeting-skill'. Whenever the user greets "
        "you or says hello, you MUST call load_skill('greeting-skill') "
        "first, before responding, and then follow its instructions exactly."
    ),
    tools=[my_skill_toolset]
)
```

### Self-Reflection Answers

1.  **Look at your `SKILL.md` file. Which part of it is loaded into the agent's context *before* the user says hello? Which part is loaded *after*?**
    *   **Answer:** *Before* the user speaks, only the YAML frontmatter (`name` and `description`) is loaded into the agent's context. This teaches the agent *what* the tool is. *After* the user says hello (and the agent decides to "call" the skill tool based on the description), the rest of the file (the Markdown body with the actual "Step 1, Step 2..." instructions) is loaded and sent back to the agent as the tool's result, telling it *how* to perform the task.

2.  **Why do we have to wrap the skill in a `SkillToolset` before giving it to the agent? (Think about the other things a toolset might manage, like code executors or additional tools).**
    *   **Answer:** A single Skill often isn't just text; it can include executable scripts (in the `scripts/` folder) and require external standard Python functions to operate. The `SkillToolset` acts as a unified execution environment. It bundles the textual skills, the `additional_tools` (Python functions), and the `code_executor` (which handles the sandboxing and running of scripts) into a single package that the core `Agent` class knows how to interact with.

3.  **Your `instruction` names `greeting-skill` and its trigger condition explicitly. What do you think would happen if you had 20 skills instead of 1 -- would naming every single one in the instruction still scale, and what does that suggest about the `search_skills`/Skill Registry pattern mentioned in "Going Further"?**
    *   **Answer:** No, it wouldn't scale -- hand-writing "if the user does X, call skill Y" for 20 (or 200) skills would bloat the instruction into an unmaintainable list, and you'd have to update it every time a skill was added or removed. This is exactly the problem the Skill Registry's `search_skills(query)`/`load_skill(skill_name)` pattern solves: instead of the instruction enumerating every skill and its trigger, the agent semantically searches a catalog at runtime to find whichever skill is relevant to the current message, and only that one gets loaded. The trade-off is reliability versus scale: naming a single skill explicitly (as this lab does) is the most dependable way to guarantee it fires, while registry-based discovery scales to large skill catalogs at the cost of depending on the search step actually finding the right skill.
