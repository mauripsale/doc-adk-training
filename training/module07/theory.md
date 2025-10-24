# Module 7: Creating Custom Function Tools

## Theory

### Unlocking Unlimited Capabilities

While built-in tools like `google_search` are powerful, the true potential of your agent is realized when you give it custom capabilities tailored to your specific needs. This is done by creating **Custom Function Tools**.

A custom function tool is, at its core, a regular Python function that you write and then make available to your agent. This allows you to connect your agent to virtually anything you can program: a proprietary database, a third-party API, a complex business logic algorithm, or even another AI model.

### How it Works: From Python to Agent Tool

When you add one of your Python functions to an agent's `tools` list, the ADK framework performs a clever transformation behind the scenes. It inspects your function's **signature**—its name, parameters, type hints, and docstring—and automatically generates a detailed description, or **schema**.

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

#### 4. **Structured Return Value**
A tool function in the ADK **must return a dictionary**. This allows you to provide a structured result that the LLM can easily understand. It is a best practice to include a `status` key to indicate the outcome.

```python
def get_weather(city: str, is_forecast: bool) -> dict:
    """... docstring ..."""
    # ... logic to fetch weather ...
    if success:
        return {"status": "success", "report": "It is sunny."}
    else:
        return {"status": "error", "message": "Could not find weather for that city."}
```
The LLM will receive this dictionary and use its contents to formulate the final response to the user.

In the lab for this module, you will put all these principles into practice by building a set of calculator functions and integrating them into a new "Calculator" agent.
