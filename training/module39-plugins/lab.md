---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 39: ADK Plugins Deep Dive — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 39: Self-Healing Tool Recovery with Plugins

## Goal

In this lab, you will work with an agent whose instructions force it to pass legacy `'x'` multiplication syntax (`"6 x 7"`) to a strict expression calculator tool that raises a `ValueError`. Your task is to attach `ReflectAndRetryToolPlugin` so the agent intercepts the exception, reflects on the error message, and retries with `'6 * 7'` *without* changing the agent's prompt!

### Step 1: Create the Project

1.  **Create a new agent project:**

    <Setup/>

    ```shell
    uv run adk create retry_agent
    ```
    This prompts for a model choice (any option is fine, you'll set `gemini-3.8-flash` in `agent.py` below) and, if needed, a backend -- `agent.py`/Code is already the default.

2.  **Navigate to the directory:**
    ```shell
    cd retry_agent
    ```

### Step 2: The "Broken" Tool Call

**Exercise:** Open `agent.py` and replace its content with the starter code below.

This script defines `secret_calculator(expression: str)`, which evaluates simple `+`, `-`, `*`, `/` arithmetic expressions using Python's `ast` module—and explicitly raises `ValueError("Legacy operator 'x' is not supported; retry using '*' instead.")` if `'x'` is used. Meanwhile, the agent's `instruction` strictly forces it to use `'x'` (`"6 x 7"`) on its **first** attempt!

> **Why raise `ValueError` inside the tool?** In ADK 2.14+, calling a nonexistent tool name no longer crashes with an unhandled `ValueError` (the framework returns a tool-not-found dictionary natively). However, **exceptions raised inside a tool's Python body**—such as strict argument validation `ValueError`s or transient `ConnectionError`s—still propagate out and crash the runner unless intercepted by `ReflectAndRetryToolPlugin`! Scoping the legacy `'x'` rule to the "first attempt only" guarantees you observe both the genuine crash in Step 3 and the self-healing retry in Step 5.

```python
import ast
import asyncio
import operator
from dotenv import load_dotenv
from google.genai import types

from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.runners import InMemoryRunner
from google.adk.tools import FunctionTool

load_dotenv(override=True)

_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def secret_calculator(expression: str) -> float:
    """Evaluates a binary arithmetic expression using +, -, *, or /."""
    if "x" in expression.lower():
        raise ValueError(
            "Legacy operator 'x' is not supported; retry using '*' instead."
        )
    try:
        tree = ast.parse(expression, mode="eval").body
        if isinstance(tree, ast.BinOp) and type(tree.op) in _SAFE_OPS:
            left = float(ast.literal_eval(tree.left))
            right = float(ast.literal_eval(tree.right))
            return float(_SAFE_OPS[type(tree.op)](left, right))
    except Exception as exc:
        raise ValueError(
            f"Invalid arithmetic syntax {expression!r}; pass 'a * b' with +, -, *, or /."
        ) from exc
    raise ValueError(
        f"Unsupported expression {expression!r}; pass a simple binary expression like '6 * 7'."
    )


# The agent with MISLEADING legacy syntax instructions
root_agent = Agent(
    name="confused_agent",
    model="gemini-3.8-flash",
    instruction="""You are a math helper that MUST use `secret_calculator` to compute answers.
        Strict legacy formatting rule for your FIRST attempt only: whenever multiplying
        two numbers, you MUST format the expression using the letter `x` (for example,
        `6 x 7`), never `*`, on your first tool call.

        However, if that first tool call fails or returns an error, the legacy `x` rule
        no longer applies: read the error guidance carefully and retry `secret_calculator`
        using the standard `*` operator suggested by the error message.""",
    tools=[FunctionTool(secret_calculator)],
)


async def main():
    # TODO: 1. Import ReflectAndRetryToolPlugin from google.adk.plugins

    # TODO: 2. Initialize the plugin here with max_retries=3

    # TODO: 3. Pass plugins=[retry_plugin] into App(...)
    app = App(
        name="retry_agent",
        root_agent=root_agent,
        # Add your plugins list here
    )

    runner = InMemoryRunner(app=app)

    # /run_async requires a session that already exists.
    await runner.session_service.create_session(
        app_name=app.name, user_id="test", session_id="1"
    )

    print("User: What is 6 times 7?")
    async for event in runner.run_async(
        user_id="test",
        session_id="1",
        new_message=types.Content(
            role="user", parts=[types.Part.from_text(text="What is 6 times 7?")]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(f"Agent: {event.content.parts[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
```

### Step 3: Observe the Failure

1.  **Run the agent without the plugin:**
    ```shell
    uv run python agent.py
    ```
2.  **Analyze the Output:**
    You will see an unhandled `ValueError: Legacy operator 'x' is not supported; retry using '*' instead.` traceback that crashes the script! Because no `on_tool_error_callback` plugin is registered, the exception raised inside `secret_calculator("6 x 7")` terminates the invocation immediately.

### Step 4: Add the Self-Healing Safety Net

Now fix the crash using `ReflectAndRetryToolPlugin` *instead* of editing the agent's prompt:

1.  **Import the Plugin:**
    Add `from google.adk.plugins import ReflectAndRetryToolPlugin` to your imports.

2.  **Initialize the Plugin:**
    Instantiate `retry_plugin = ReflectAndRetryToolPlugin(max_retries=3)`.

3.  **Register the Plugin:**
    Pass `plugins=[retry_plugin]` to `App(...)`.

### Step 5: Verify Self-Healing Recovery

1.  **Run the agent again:**
    ```shell
    uv run python agent.py
    ```
2.  **Analyze the Output:**
    *   Instead of crashing with a traceback, the script completes cleanly and prints: `Agent: 6 times 7 is 42.` (or similar).
    *   **What happened under the hood?**
        1. `confused_agent` called `secret_calculator(expression="6 x 7")`.
        2. `secret_calculator` raised `ValueError("Legacy operator 'x' is not supported; retry using '*' instead.")`.
        3. `ReflectAndRetryToolPlugin` intercepted the exception via `on_tool_error_callback` and returned a structured `ToolFailureResponse` (`retry_count: 1` of `3`) containing the error details and reflection guidance.
        4. Gemini read the reflection guidance, adapted its arguments to `secret_calculator(expression="6 * 7")`, received `42.0`, and answered the user!

### Step 6: Bonus Challenge — Enterprise Multi-Plugin Chaining (`GlobalInstructionPlugin`)

In enterprise architectures, plugins are composed together into a defense-in-depth pipeline.

**Exercise:** Create a script `enterprise_plugins.py` that combines `ReflectAndRetryToolPlugin` with `GlobalInstructionPlugin` to inject enterprise compliance rules across all agent invocations, then run it with `uv run python enterprise_plugins.py`:

```python
# enterprise_plugins.py (Starter Code)
import asyncio
from dotenv import load_dotenv
from google.genai import types

from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.plugins import ReflectAndRetryToolPlugin
# TODO: 1. Import GlobalInstructionPlugin from google.adk.plugins
from google.adk.runners import InMemoryRunner
from google.adk.tools import FunctionTool

load_dotenv(override=True)


def system_status() -> str:
    """Returns the internal cluster health status."""
    return "Cluster operational: 100% healthy."


root_agent = Agent(
    name="ops_agent",
    model="gemini-3.8-flash",
    instruction="You are an IT Ops assistant. Check system status when asked.",
    tools=[FunctionTool(system_status)],
)


async def main():
    # TODO: 2. Instantiate ReflectAndRetryToolPlugin(max_retries=2)
    retry_plugin = None

    # TODO: 3. Instantiate GlobalInstructionPlugin(global_instruction=...) to enforce:
    # "All outputs must be strictly professional and tagged with [CONFIDENTIAL]."
    compliance_plugin = None

    # TODO: 4. Register both plugins in App(plugins=[retry_plugin, compliance_plugin])
    app = App(
        name="enterprise_ops_app",
        root_agent=root_agent,
        plugins=[],  # Add your plugins here
    )

    runner = InMemoryRunner(app=app)
    await runner.session_service.create_session(
        app_name=app.name, user_id="ops_user", session_id="session_1"
    )

    print("User: Check system status.")
    async for event in runner.run_async(
        user_id="ops_user",
        session_id="session_1",
        new_message=types.Content(
            role="user", parts=[types.Part.from_text(text="Check system status.")]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(f"Agent: {event.content.parts[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
```

### Self-Reflection Questions
- Why is it better to handle tool argument/execution errors with `ReflectAndRetryToolPlugin` rather than only trying to anticipate every mistake in the prompt?
- What would happen if we set `max_retries=0`?
- How does this plugin help with "transient" errors, like a temporary network glitch in a tool?
- How does `GlobalInstructionPlugin` ensure enterprise governance across large multi-agent fleets without modifying individual agent instructions?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="39">

# Lab 39 Solution: Self-Healing Tool Recovery with Plugins

## Goal

This solution demonstrates how `ReflectAndRetryToolPlugin` intercepts unhandled tool exceptions (such as legacy operator `ValueError`s in ADK 2.14), feeds structured reflection guidance back to Gemini, and lets the agent self-correct without modifying its prompt or crashing the runner.

### `retry_agent/agent.py`

```python
import ast
import asyncio
import operator
from dotenv import load_dotenv
from google.genai import types

from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.plugins import ReflectAndRetryToolPlugin  # 1. Import built-in plugin
from google.adk.runners import InMemoryRunner
from google.adk.tools import FunctionTool

load_dotenv(override=True)

_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def secret_calculator(expression: str) -> float:
    """Evaluates a binary arithmetic expression using +, -, *, or /."""
    if "x" in expression.lower():
        raise ValueError(
            "Legacy operator 'x' is not supported; retry using '*' instead."
        )
    try:
        tree = ast.parse(expression, mode="eval").body
        if isinstance(tree, ast.BinOp) and type(tree.op) in _SAFE_OPS:
            left = float(ast.literal_eval(tree.left))
            right = float(ast.literal_eval(tree.right))
            return float(_SAFE_OPS[type(tree.op)](left, right))
    except Exception as exc:
        raise ValueError(
            f"Invalid arithmetic syntax {expression!r}; pass 'a * b' with +, -, *, or /."
        ) from exc
    raise ValueError(
        f"Unsupported expression {expression!r}; pass a simple binary expression like '6 * 7'."
    )


# The agent with MISLEADING legacy syntax instructions:
# On its FIRST attempt, it MUST format multiplication with 'x' (e.g. '6 x 7'),
# which raises a ValueError inside secret_calculator. Without ReflectAndRetryToolPlugin,
# that unhandled ValueError crashes the run immediately. With ReflectAndRetryToolPlugin,
# the exception is caught and turned into structured reflection guidance so the
# model adapts and retries with '6 * 7'.
root_agent = Agent(
    name="confused_agent",
    model="gemini-3.8-flash",
    instruction="""You are a math helper that MUST use `secret_calculator` to compute answers.
        Strict legacy formatting rule for your FIRST attempt only: whenever multiplying
        two numbers, you MUST format the expression using the letter `x` (for example,
        `6 x 7`), never `*`, on your first tool call.

        However, if that first tool call fails or returns an error, the legacy `x` rule
        no longer applies: read the error guidance carefully and retry `secret_calculator`
        using the standard `*` operator suggested by the error message.""",
    tools=[FunctionTool(secret_calculator)],
)


async def main():
    # 2. Configure the built-in self-healing tool plugin
    retry_plugin = ReflectAndRetryToolPlugin(max_retries=3)

    # 3. Register the plugin globally on the App
    app = App(
        name="retry_agent",
        root_agent=root_agent,
        plugins=[retry_plugin],
    )

    runner = InMemoryRunner(app=app)
    await runner.session_service.create_session(
        app_name=app.name, user_id="test", session_id="1"
    )

    print("User: What is 6 times 7?")
    async for event in runner.run_async(
        user_id="test",
        session_id="1",
        new_message=types.Content(
            role="user", parts=[types.Part.from_text(text="What is 6 times 7?")]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(f"Agent: {event.content.parts[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
```

### `retry_agent/enterprise_plugins.py`

```python
"""
Enterprise Multi-Plugin Chaining: Global Instruction & Self-Healing Retries
"""
import asyncio
from dotenv import load_dotenv
from google.genai import types

from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.plugins import GlobalInstructionPlugin, ReflectAndRetryToolPlugin
from google.adk.runners import InMemoryRunner
from google.adk.tools import FunctionTool

load_dotenv(override=True)


def system_status() -> str:
    """Returns the internal cluster health status."""
    return "Cluster operational: 100% healthy."


root_agent = Agent(
    name="ops_agent",
    model="gemini-3.8-flash",
    instruction="You are an IT Ops assistant. Check system status when asked.",
    tools=[FunctionTool(system_status)],
)


async def main():
    # 1. Self-healing tool retry plugin
    retry_plugin = ReflectAndRetryToolPlugin(max_retries=2)

    # 2. Enterprise-wide governance header injection
    compliance_plugin = GlobalInstructionPlugin(
        global_instruction="All outputs must be strictly professional and tagged with [CONFIDENTIAL]."
    )

    # 3. Register both plugins on the App container
    app = App(
        name="enterprise_ops_app",
        root_agent=root_agent,
        plugins=[retry_plugin, compliance_plugin],
    )

    runner = InMemoryRunner(app=app)
    await runner.session_service.create_session(
        app_name=app.name, user_id="ops_user", session_id="session_1"
    )

    print("User: Check system status.")
    async for event in runner.run_async(
        user_id="ops_user",
        session_id="session_1",
        new_message=types.Content(
            role="user", parts=[types.Part.from_text(text="Check system status.")]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(f"Agent: {event.content.parts[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
```

### Self-Reflection Answers

1.  **Why is it better to handle tool argument/execution errors with `ReflectAndRetryToolPlugin` rather than only trying to anticipate every mistake in the prompt?**
    *   **Answer:** While clear prompts prevent *known* mistakes, `ReflectAndRetryToolPlugin` provides a universal, concurrency-safe safety net against *unexpected* runtime failures across dozens of tools—such as strict parser `ValueError`s, date/schema mismatches, or transient API errors—turning unhandled exceptions into structured reflection opportunities instead of hard crashes.

2.  **What would happen if we set `max_retries=0`?**
    *   **Answer:** With `max_retries=0` (and default `throw_exception_if_retry_exceeded=True`), the plugin allows zero retries: on the first `ValueError` raised by `secret_calculator("6 x 7")`, the retry limit is immediately exceeded and the exception propagates out, crashing the run just as if the plugin were absent.

3.  **How does this plugin help with "transient" errors, like a temporary network glitch in a tool?**
    *   **Answer:** When a tool raises a transient `ConnectionError` or `TimeoutError`, `ReflectAndRetryToolPlugin` intercepts it via `on_tool_error_callback` and returns a structured `ToolFailureResponse` to the model rather than aborting the session. The model sees the transient failure details and can re-invoke the tool within `max_retries`.

4.  **How does `GlobalInstructionPlugin` ensure enterprise governance across large multi-agent fleets without modifying individual agent instructions?**
    *   **Answer:** Registered once on `App(plugins=[...])`, `GlobalInstructionPlugin(global_instruction=...)` intercepts every LLM request across the root agent and all sub-agents, injecting mandatory compliance, safety, and formatting policies centrally so individual agent authors cannot accidentally omit them.

</SolutionVault>
