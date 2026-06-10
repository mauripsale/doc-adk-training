---
sidebar_position: 2
title: "Challenge Lab"
---

# Module 26: Callbacks and Guardrails - Building a Content Moderator

## Lab 26: Building a Content Moderation Assistant with Caching

### Goal

In this lab, you will implement a suite of callbacks to create a **Content Moderation Assistant**. You will learn to build safety guardrails, validate tool arguments, filter responses, and, crucially, implement a **Caching mechanism** using `before_agent_callback` to save tokens and time.

### Step 1: Create the Project Structure

1.  **Create the agent project:**
    ```shell
    uv run adk create content_moderator
    ```
    When prompted, choose the **Programmatic (Python script)** option.

2.  **Navigate into the new directory:**
    ```shell
    cd content_moderator
    ```

### Step 2: Implement the Callbacks

**Exercise:** Open `agent.py`. Your task is to implement the logic for the five core callbacks. Use the `# TODO` comments as your guide.

```python
# ... [previous imports] ...

# ============================================================================ 
# CALLBACK FUNCTIONS
# ============================================================================ 

# ... [before_agent, after_agent, before_model stay the same] ...

def after_model_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """
    TODO: Output Filtering.
    Use re.sub to redact email addresses from the LLM response text.
    If redacted, return a new LlmResponse; otherwise return None.
    """
    pass

def before_tool_callback(
    # ...
```

# ============================================================================ 
# AGENT DEFINITION
# ============================================================================ 

# TODO: Define root_agent and register ALL callbacks
root_agent = Agent(
    name="secure_moderator",
    model="gemini-3.5-flash",
    # tools=[...],
    # before_agent_callback=...,
    # ...
)
```

```

### Self-Reflection Questions
- What is the key difference between a callback and a plugin in the ADK? When would you choose one over the other?
- Why does returning a `types.Content` object from `before_agent_callback` cause the agent to skip the LLM call entirely?
- How does using callbacks for guardrails and validation make an agent more reliable and safer to deploy in a production environment?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMjYtY2FsbGJhY2tzL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module26-callbacks/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
