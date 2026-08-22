---
sidebar_position: 39.5
title: "Module 39.5: Agent Skills"
---

# Module 39.5: Enhancing Agents with Skills

## Theory

### What is a Skill?

You've learned how to give agents basic tools (like calculators or weather APIs) to extend their capabilities. But what happens when an agent needs to perform a highly complex, domain-specific task? 

A **Skill** is a self-contained package that provides an agent with specialized procedural knowledge. Think of it as an "onboarding manual" for a specific job. While a basic tool is just a function, a Skill bundles together:

1.  **Instructions (`SKILL.md`):** High-level guidance on *when* and *how* to perform the task.
2.  **References (`references/`):** Domain-specific documentation (e.g., schemas, style guides) that the agent can read *if* it needs it.
3.  **Scripts (`scripts/`):** Executable code for tasks that require deterministic reliability (e.g., a Python script to parse a complex PDF, rather than trusting the LLM to write the code from scratch).
4.  **Tools (`additional_tools`):** The standard Python functions the skill relies on.

### The Problem: Context Window Bloat

If you put the instructions, schemas, and logic for every possible task directly into your agent's system prompt, you will quickly exhaust the LLM's context window. This makes the agent slow, expensive, and easily confused.

### The Solution: Progressive Disclosure

Skills solve this through **Progressive Disclosure**:
1.  The agent is only given the name and a short description of the Skill.
2.  If the user's request matches the description, the agent *activates* the Skill.
3.  Only then are the instructions (`SKILL.md`) loaded into the context window.
4.  If the instructions say to read a specific reference file, the agent uses a tool to read just that file.

This keeps the main agent incredibly lightweight, loading heavy documentation only precisely when needed.

### Using Skills in the ADK

In the modern ADK, Skills are managed using the `SkillToolset`. Note that as of ADK 2.0, the Skills feature is still marked **experimental** in the official documentation — the core API you'll use here (`load_skill_from_dir`, `SkillToolset`) is stable enough for this course, but expect it to keep evolving.

```python
import pathlib
from google.adk.agents import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset
from google.adk.code_executors.unsafe_local_code_executor import UnsafeLocalCodeExecutor

# 1. Load a skill from a local directory
weather_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "weather-skill"
)

# 2. Create a Toolset to manage the skills and any extra tools they need
# WARNING: UnsafeLocalCodeExecutor allows the agent to run the scripts/ folder
# locally. Do not use in untrusted production environments!
my_skill_toolset = SkillToolset(
    skills=[weather_skill],
    additional_tools=[get_current_humidity_tool], 
    code_executor=UnsafeLocalCodeExecutor(),
)

# 3. Give the entire toolset to the Agent
agent = Agent(
    model="gemini-3.5-flash",
    name="skill_user_agent",
    description="An agent that can use specialized skills.",
    tools=[my_skill_toolset]
)
```

### The Structure of a Skill Directory

When you use `load_skill_from_dir`, the ADK expects a specific directory layout:

```text
my-skill/
├── SKILL.md           <-- Required: YAML frontmatter (name/desc) + Markdown body
├── scripts/           <-- Optional: Executable code (Python, Bash, etc.)
├── references/        <-- Optional: Documentation for the agent to read
└── assets/            <-- Optional: Files used in the output (templates, etc.)
```

### Going Further: The Skill Registry (Preview)

Everything above loads skills from your local filesystem — fine for a handful of skills you wrote yourself. In an enterprise setting with hundreds or thousands of skills shared across teams, ADK offers a **Skill Registry** (currently a Preview feature) that lets an agent discover and load skills on demand from a remote catalog instead of bundling them all upfront.

You connect it by passing a registry (e.g. `GCPSkillRegistry` from `google.adk.integrations.skill_registry`) to your `SkillToolset`. ADK then automatically injects two extra tools for the agent: `search_skills(query)` to find relevant skills semantically, and `load_skill(skill_name)` to pull one in only when needed — the same Progressive Disclosure idea, just applied to a catalog instead of a local folder. Locally loaded skills always take priority over registry ones with the same name. This is beyond the scope of this lab, but worth knowing about if you're designing a skill strategy for a larger organization.

### Key Takeaways
- **Skills** are modular packages containing instructions, references, and scripts to teach an agent complex domain knowledge.
- They prevent context bloat via **Progressive Disclosure**—loading detailed instructions only when the skill is activated.
- In ADK 2.0, you load skills from a directory using `load_skill_from_dir()`.
- You provide skills to an Agent by bundling them inside a `SkillToolset`, which handles the activation and execution logic.