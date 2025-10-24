# Module 8: Advanced Tool Concepts: Tool Context

## Theory

### Giving Tools "Situational Awareness"

So far, your custom tools have been simple, stateless functions: they take inputs, perform a calculation, and return a result. However, in more advanced scenarios, a tool might need more information than just its input arguments. It might need to:

*   Read or write data to the conversation's memory.
*   Know which user is making the request.
*   Access files that have been uploaded.
*   Influence the agent's workflow, for example, by telling it to transfer to another agent.

This is where the **`ToolContext`** comes in. The `ToolContext` is a special object that the ADK can automatically provide to your tool function, giving it "situational awareness" and a powerful set of capabilities to interact with the agent's runtime environment.

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

### Key Capabilities of `ToolContext`

The `ToolContext` object provides access to several key pieces of information and control levers:

#### 1. **State Management (`tool_context.state`)**

This is the most common use case. The `tool_context.state` attribute gives your tool direct read and write access to the current conversation's `Session.state`. This allows your tool to:

*   **Read from state:** Make decisions based on information saved by previous tools or agents.
    ```python
    user_preference = tool_context.state.get('user:theme', 'light')
    ```
*   **Write to state:** Save information that can be used by the agent or other tools later in the conversation.
    ```python
    tool_context.state['last_order_id'] = 'XYZ-123'
    ```
This turns your stateless functions into stateful tools that can participate in building up a shared understanding of the conversation.

#### 2. **Flow Control (`tool_context.actions`)**

The `tool_context.actions` attribute allows your tool to influence what the agent does *after* the tool finishes.

*   **`transfer_to_agent`:** Your tool can dynamically decide to hand off the conversation to a different, more specialized agent.
    ```python
    if "urgent" in user_query:
        tool_context.actions.transfer_to_agent = 'human_support_agent'
    ```
*   **`skip_summarization`:** If your tool's output is already a perfect, user-ready message, you can set this to `True` to prevent the LLM from rephrasing it.

#### 3. **Accessing Files (`tool_context.load_artifact`)**

If a user has uploaded files (known as "artifacts" in the ADK), your tool can access them via the `ToolContext`.
```python
# Load a file the user uploaded named 'report.txt'
uploaded_file = tool_context.load_artifact('report.txt')
if uploaded_file:
    text_content = uploaded_file.text
    # ... process the text ...
```

By leveraging the `ToolContext`, you can elevate your custom functions from simple calculators to powerful, context-aware components that are deeply integrated into the agent's lifecycle. In the following lab, you will use the `tool_context.state` to create a tool that can remember information across turns.
