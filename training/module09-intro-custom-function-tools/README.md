---
sidebar_position: 9
title: "Module 9: Creating Custom Function Tools"
---

# Module 9: Creating Custom Function Tools

## Theory

### Unlocking Unlimited Capabilities

While built-in tools like `google_search` are powerful, the true potential of your agent is realized when you give it custom capabilities tailored to your specific needs. This is done by creating **Custom Function Tools**.

A custom function tool is, at its core, a regular Python function that you write and then make available to your agent. This allows you to connect your agent to virtually anything you can program: a proprietary database, a third-party API, a complex business logic algorithm, or even another AI model.

### How it Works: From Python to Agent Tool

When you add one of your Python functions to an agent's `tools` list, the ADK framework performs a clever transformation behind the scenes. It inspects your function's **signature**
—its name, parameters, type hints, and docstring—and automatically generates a detailed description, or **schema**.

This schema is what's provided to the Large Language Model. The LLM doesn't see your Python code. It only sees this schema, which tells it:
1.  The tool's name (from your function name).
2.  What the tool does (from your function's docstring).
3.  What parameters it needs (from your function's arguments).
4.  What data type each parameter should be (from your type hints).

Based on this information, the LLM can intelligently decide when to use your function and what arguments to pass to it.

### The Anatomy of a Well-Defined Tool Function

For the LLM to use your tool correctly and reliably, it's crucial to define your Python function in a structured way.

#### 1. **Descriptive Function Name**
The name should clearly indicate the action the function performs.
*   **Good:** `get_weather`, `calculate_loan_payment`, `lookup_order_status`
*   **Bad:** `process_data`, `run_logic`, `my_function`

#### 2. **Clear Parameters with Type Hints**
Each argument your function takes must have a **type hint**. This is non-negotiable, as it tells the LLM what kind of data to provide.
```python
# The LLM knows 'city' must be a string and 'is_forecast' must be a boolean.
def get_weather(city: str, is_forecast: bool):
    ...
```

#### 3. **The All-Important Docstring**
The docstring is the **most critical part**. It serves as the tool's description for the LLM. A good docstring should explain:
*   **Purpose:** What does the tool do?
*   **Usage:** *When* should the agent use this tool? Provide context.
*   **Parameters:** Describe what each parameter represents.

```python
def get_weather(city: str, is_forecast: bool):
    """
    Fetches the current weather or a 3-day forecast for a specific city.

    Use this tool when a user asks about the weather.

    Args:
        city: The name of the city (e.g., "San Francisco").
        is_forecast: Set to True for a 3-day forecast, False for current conditions.
    """
    ...
```

#### 4. Structured Return Value
In ADK 2.0, a tool function can return a **dictionary** or, ideally, a **Pydantic model**. The LLM will receive this structured data and use its contents to formulate the final response.

```python
from pydantic import BaseModel

class WeatherReport(BaseModel):
    status: str
    temperature: float
    conditions: str

def get_weather(city: str) -> WeatherReport:
    """Fetches the current weather."""
    # ... logic ...
    return WeatherReport(status="success", temperature=22.0, conditions="Sunny")
```

### Advanced: The `ToolContext`

Sometimes your tool needs to know more than just its arguments. It might need to read from the session state or perform an action like transferring control to another agent. In ADK 2.0, you can add a `tool_context: ToolContext` argument to your function to gain access to these framework features.

```python
from google.adk.tools import ToolContext

def my_advanced_tool(query: str, tool_context: ToolContext):
    # Access session state!
    user_name = tool_context.session.state.get("user_name")
    ...
```


### Registering Tools with Your Agent Node

In ADK 2.0, registering your custom functions as tools is incredibly simple. You just import your functions and pass them directly into the **`Agent`** node's `tools` list. The ADK automatically wraps them.

```python
# In agent.py
from google.adk import Agent
from .tools.calculator import add, subtract # Import your functions

root_agent = Agent(
    # ... other params
    tools=[
        add,       # The ADK automatically converts this Python function
        subtract,  # into an LLM-compatible Tool!
    ]
)
```

In the lab for this module, you will put all these principles into practice by building a set of calculator functions and integrating them into a new "Calculator" agent.

### Key Takeaways
- **Custom Function Tools** connect your agent node to any Python capability.
- **Auto-Schema:** ADK 2.0 generates the tool schema from your function's signature and docstring.
- **Type Safety:** Use type hints and Pydantic return models for robust tool execution.
- **Context Awareness:** Use `ToolContext` for advanced interaction with the ADK runtime.
- **Workflow Ready:** Tools are nodes in your graph, allowing for modular and testable designs.

## Limitations: Mixing Tool Types

As you start building more complex agents, it's important to be aware of a current limitation in the ADK regarding tool usage.

### One Built-in Tool Per Agent

Currently, a single agent generally supports using **only one type of tool at a time**.

Specifically, you cannot easily mix a **Built-in Tool** (like `google_search`) with **Custom Function Tools** or other capabilities (like a code executor) within the same agent definition.

**Unsupported Example:**
You cannot simply list both `google_search` and your own `custom_function` in the same `tools` list for a single agent.

```python
# This approach is NOT currently supported
root_agent = Agent(
    name="MixedToolAgent",
    model="gemini-3.5-flash",
    tools=[google_search, custom_function], # Mixing types may cause issues
)
```

### The Workaround: Multi-Agent Systems

So, how do you build an agent that can search the web *and* use your custom calculator?

The solution is to use a **Multi-Agent System**. Instead of one agent doing everything, you create two specialized agents:
1.  A "Search Specialist" agent with the `google_search` tool.
2.  A "Calculator Specialist" agent with your custom function tools.
3.  A "Coordinator" agent that delegates tasks to the specialists.

You will learn exactly how to build these powerful multi-agent architectures in **Module 15**. For now, focus on mastering custom tools within a single agent.