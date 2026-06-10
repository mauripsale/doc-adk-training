---
sidebar_position: 21.7
title: "Module 21.7: Collaborative Agent Teams - Using Modes"
---

# Module 21.7: Collaborative Agent Teams - Using Modes

## Theory

In standard orchestration, a coordinator calls a sub-agent and control stays with that specialist until a manual hand-off happens. ADK 2.0 introduces a more structured way to manage these relationships: **Collaboration Modes**.

### What are Collaboration Modes?

When you add a sub-agent to an `Agent` or `Workflow`, you can specify its **`mode`**. This setting controls how the sub-agent behaves and, crucially, how it **returns control to the parent**.

There are three primary modes:

1.  **`chat` (Default):** Full multi-turn interaction. The sub-agent keeps control until it explicitly performs another transfer or the session ends.
2.  **`task`:** Used for specific sub-tasks. The sub-agent can interact with the user for clarifications but **automatically returns control** to the parent once its task is complete.
3.  **`single_turn`:** No user interaction allowed. The sub-agent performs a single reasoning step and returns the result to the parent immediately. This is ideal for parallel background tasks.

### The Power of Automatic Return

In ADK 1.x, you often had to prompt your sub-agents to "hand back control." In ADK 2.0, using `mode="task"`, this is handled by the framework.

```python
from google.adk import Agent

# 1. Define a specialist in 'task' mode
researcher = Agent(
    name="researcher",
    mode="task", # 🔄 Automatic return to parent!
    instruction="Research the topic and provide a 3-point summary."
)

# 2. Assign to a coordinator
root_agent = Agent(
    name="coordinator",
    sub_agents=[researcher], # Framework auto-injects 'request_task_researcher' tool
    instruction="Delegate research to the specialist, then write a conclusion."
)
```

### Why use Collaboration Modes?

*   **Predictability:** You know exactly when and how control will flow back to your main orchestrator.
*   **Parallelism:** Agents in `single_turn` mode can be executed concurrently within a Workflow graph.
*   **Cleaner Prompts:** You no longer need to pollute your specialist's instructions with "how to return control" rules.

### Key Takeaways
- **Collaboration Modes** (`chat`, `task`, `single_turn`) manage sub-agent lifecycle.
- **`mode="task"`** is the standard for delegation where you want the specialist to finish and "come back" to the main flow.
- The framework handles the low-level tool injection (`request_task_...`) automatically based on the `sub_agents` list.
