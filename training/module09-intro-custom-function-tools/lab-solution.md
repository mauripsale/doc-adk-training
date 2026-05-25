---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 9 Solution: Building a "Calculator" Agent

## Goal

This file contains the complete, step-by-step guide to creating the "Calculator" agent using modern ADK practices.

### Step 1: Create the Calculator Agent Project

1.  **Initialize the project:**
    ```shell
    uv init calculator_agent --python 3.10
    cd calculator_agent
    uv add google-adk python-dotenv
    ```

2.  **Set up authentication:**
    Create a `.env` file in your `calculator_agent` directory and add your `GOOGLE_API_KEY` (or Vertex AI configuration).

### Step 2: Write the Custom Tool Functions

1.  **Create a `tools` directory and package files:**
    ```shell
    mkdir tools
    touch tools/__init__.py
    ```

2.  **Create the `calculator.py` file:**
    Create `tools/calculator.py` and add the following code:

    ```python
    def add(a: int, b: int) -> dict:
        """
        Adds two numbers together.

        Use this tool when the user asks to find the sum of two numbers.

        Args:
            a: The first number.
            b: The second number.
        
        Returns:
            A dictionary with the result of the addition.
        """
        result = a + b
        return {"status": "success", "result": result}

    def subtract(a: int, b: int) -> dict:
        """
        Subtracts the second number from the first number.

        Use this tool when the user asks to find the difference between two numbers.

        Args:
            a: The first number.
            b: The second number to subtract.

        Returns:
            A dictionary with the result of the subtraction.
        """
        result = a - b
        return {"status": "success", "result": result}

    def multiply(a: int, b: int) -> dict:
        """
        Multiplies two numbers together.

        Use this tool when the user asks to find the product of two numbers.

        Args:
            a: The first number.
            b: The second number.

        Returns:
            A dictionary with the result of the multiplication.
        """
        result = a * b
        return {"status": "success", "result": result}

    def divide(a: int, b: int) -> dict:
        """
        Divides the first number by the second number.

        Use this tool when the user asks to divide one number by another.

        Args:
            a: The numerator.
            b: The denominator.

        Returns:
            A dictionary with the result or an error if division by zero occurs.
        """
        if b == 0:
            # Crucial: Returning a structured error instead of crashing the Python process
            return {"status": "error", "message": "Cannot divide by zero."}
        result = a / b
        return {"status": "success", "result": result}
    ```

### Step 3: Configure the Agent to Use the Tools

Open `agent.py` and replace its contents with the following. Notice how we pass the raw Python functions directly into the `tools` list. The ADK automatically converts them into LLM-compatible tools based on their docstrings and type hints.

```python
from google.adk.agents import LlmAgent

# Import the functions from your tools module
from tools.calculator import add, subtract, multiply, divide

root_agent = LlmAgent(
    name="calculator_agent",
    model="gemini-3.5-flash",
    description="An agent that can perform basic arithmetic calculations.",
    instruction="""
You are a helpful calculator assistant.
When the user asks you to perform a calculation (add, subtract, multiply, or divide), you MUST use the appropriate tool.
Clearly state the result of the calculation to the user.
If the user asks a question that is not a calculation, politely state that you can only perform math.
""",
    tools=[
        add,
        subtract,
        multiply,
        divide,
    ],
)
```

### Step 4: Test the Calculator Agent

You can now start the agent using the modern ADK CLI command:

```bash
uv run adk run agent.py
```

Interact with the agent in the terminal and ask it to perform calculations:
*   "What is 42 + 118?"
*   "Multiply 15 by 3."
*   "What is 10 divided by 0?"
*   "What is the capital of France?" (Should be gracefully declined).

### Self-Reflection Answers

1.  **What do you think would happen if you removed the docstrings from your calculator functions? Would the agent still be able to use them?**
    *   **Answer:** If you remove the docstrings, the LLM receives an empty description for the tool. While it *might* occasionally guess what a tool named `add` does based purely on the name and parameters, its behavior will become highly unpredictable. It might use the wrong tool, pass incorrect arguments, or refuse to use it entirely. The docstring is the LLM's only instruction manual for your function.

2.  **Why is it a good practice to return a dictionary with a `status` key from a tool function, especially for operations that can fail (like division)?**
    *   **Answer:** If `divide(10, 0)` simply raised a Python `ZeroDivisionError`, your entire script (and the agent) would crash. By returning `{"status": "error", "message": "..."}`, you handle the error gracefully. The LLM receives this error message and can formulate a polite response to the user (e.g., "I'm sorry, but I cannot divide by zero.").

3.  **How would you add a new tool to this agent, for example, a function to calculate the square root of a number? What steps would you need to take?**
    *   **Answer:**
        1.  Open `tools/calculator.py` and write the new function: `def square_root(a: float) -> dict:`
        2.  Add type hints and a clear docstring explaining its purpose.
        3.  Implement the logic (e.g., using `math.sqrt(a)`).
        4.  Return the structured dictionary.
        5.  Open `agent.py`, update the import statement to include `square_root`.
        6.  Add `square_root` to the `tools=[]` list in the `root_agent` definition.

### Lab Summary

You have successfully built an agent with custom capabilities, learning to:
*   Organize tool code into a separate Python module.
*   Write well-defined Python functions with type hints and docstrings to serve as tools.
*   Register your custom tools directly in `agent.py` without needing extra wrappers.
*   Write instructions that effectively guide the agent on how and when to use its new tools.
