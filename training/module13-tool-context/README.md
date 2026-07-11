---
sidebar_position: 13
title: "Module 13: Advanced Interactions: Actions & HITL"
---

# Module 13: Advanced Interactions: Actions & HITL

## Theory

By now, you know how to build stateful tools using the `ToolContext`. But `ToolContext` is much more than just a window into the session state; it is your gateway to controlling the **ADK Runtime** itself.

In this module, we will explore how to implement **Human-in-the-Loop (HITL)** safety and how tools can dynamically influence the agent's next steps.

### Accessing the Tool Context

To get access to the `ToolContext`, you simply add a special parameter to your tool function's signature: `tool_context: ToolContext`.

```python
from google.adk.tools import ToolContext

def my_advanced_tool(some_argument: str, tool_context: ToolContext) -> dict:
    # Now you can use tool_context inside your function
    ...
```

When the agent calls your tool, the ADK framework will see this special parameter and automatically inject the `ToolContext` object for the current request.

**Important:** You should **not** mention the `tool_context` parameter in your function's docstring. The LLM doesn't know or care about the context object; it's a mechanism for your code to interact with the ADK framework *after* the LLM has decided to call your tool.

### 1. Human-in-the-Loop (`require_confirmation`)

For sensitive or destructive actions (like financial transfers, deleting files, or sending emails), you shouldn't trust the LLM to act alone. ADK 2.0 provides a native mechanism to pause execution and wait for a human "OK."

To enable this, you must wrap your Python function in a **`FunctionTool`** object.

```python
from google.adk.tools import FunctionTool

# Wrap the tool and enable confirmation
secure_tool = FunctionTool(
    my_sensitive_function, 
    require_confirmation=True # 🛡️ The safety trigger
)
```

When the agent calls this tool, the ADK will:
1.  Pause the interaction.
2.  Send a `RequestInput` event to the user (via the Dev UI or API).
3.  Execute the Python code **only if** the user clicks "Approve."

### 2. Influencing the Workflow (`tool_context.actions`)

Sometimes a tool needs to tell the framework: *"Wait, don't just return my result to the agent; do something else first!"* You do this via the `actions` attribute.

#### Dynamic Agent Transfers
A tool can decide to hand over the entire conversation to another specialist node in the graph.

```python
def check_emergency(level: int, tool_context: ToolContext):
    if level > 9:
        # 🏃 Dynamic hand-off
        tool_context.actions.transfer_to_agent = "emergency_specialist"
        return "Escalating to emergency support."
    return "All clear."
```

#### Skipping Summarization
If your tool returns a perfect, ready-to-use message for the user, you can prevent the LLM from rewriting it.
```python
tool_context.actions.skip_summarization = True
```

### 3. Accessing Artifacts (`load_artifact`)

Tools can also interact with files uploaded by the user (like images, logs, or reports).

```python
def analyze_logs(file_name: str, tool_context: ToolContext):
    log_file = tool_context.load_artifact(file_name)
    if log_file:
        content = log_file.text
        # ... logic ...
```

By leveraging the `ToolContext`, you can elevate your custom functions from simple calculators to powerful, context-aware components that are deeply integrated into the agent's lifecycle. 

> [!NOTE]
> **Pedagogical Note:** Although we will dive deep into multi-agent orchestration and workflows on **Day 3 (Module 15+)**, in the following lab we will use a simple, single-edge `Workflow` container. This is a technical requirement in ADK 2.0 to support the dynamic hand-off (escalation) from our main agent to a supervisor agent.
>
> In the following lab, you will use human confirmation and workflow actions to build a secure financial escalation system.

### Key Takeaways
- **HITL** is a mandatory pattern for high-stakes enterprise agents.
- Use **`FunctionTool`** to add metadata and safety controls to your Python functions.
- **`tool_context.actions`** allows tools to steer the Workflow Runtime (Transfers, Skipping).
- Tools are "Framework Aware" components, not just isolated functions.