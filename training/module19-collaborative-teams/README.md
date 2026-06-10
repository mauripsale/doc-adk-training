---
sidebar_position: 19
title: "Module 19: Collaborative Teams - Using Modes and Hand-offs"
---

# Module 19: Collaborative Teams - Using Modes and Hand-offs

## Theory

So far, you have learned how to define a graph structure from the outside. But what if the nodes themselves could decide how to collaborate? 

ADK 2.0 introduces **Collaboration Modes** and **Native Hand-offs** to create fluid, self-managing agent teams.

### 1. Collaboration Modes

When you add a sub-agent to an `Agent` or `Workflow`, you can specify its **`mode`**. This setting controls how the sub-agent behaves and how it returns control to the parent.

*   **`chat` (Default):** Full multi-turn interaction. The sub-agent keeps control until it explicitly performs another transfer.
*   **`task`:** The sub-agent can ask the user questions but **automatically returns control** to the parent once its task is complete.
*   **`single_turn`:** No user interaction allowed. The sub-agent performs a single reasoning step and returns the result immediately.

### 2. The Power of `task` Mode

In ADK 1.x, you often had to prompt your sub-agents to "hand back control." In ADK 2.0, using `mode="task"`, this is handled by the framework.

```python
from google.adk import Agent

# Specialist in 'task' mode
researcher = Agent(
    name="researcher",
    mode="task", # 🔄 Automatic return to parent!
    instruction="Research the topic and provide a summary."
)

# Coordinator
root_agent = Agent(
    name="coordinator",
    sub_agents=[researcher], # Framework auto-injects 'request_task_researcher' tool
    instruction="Delegate research to the specialist, then write a conclusion."
)
```

### 3. Agent Transfer (The "Hand-off")

Even without modes, an agent can decide to hand over the entire conversation to another node in the graph. This is the **Agent Transfer** pattern. 

The framework automatically injects tools like `request_task_<agent_name>` into the parent's toolkit based on the `sub_agents` list. The LLM then "calls" these tools to perform the hand-off.

### Why use Collaborative Teams?

*   **Predictability:** You know exactly when and how control will flow back to your main orchestrator.
*   **Natural Conversation:** The transition is seamless for the user, as the context is preserved across nodes.
*   **Cleaner Prompts:** You no longer need to write complex instructions about "how to return control."

### Key Takeaways
- **Collaboration Modes** (`chat`, `task`, `single_turn`) manage sub-agent lifecycle.
- **`mode="task"`** is the standard for delegation where you want the specialist to finish and "come back" to the main flow.
- The framework handles the low-level tool injection (`request_task_...`) automatically.
