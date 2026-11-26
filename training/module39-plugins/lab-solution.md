---
sidebar_position: 3
title: "Lab Solution"
---

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
