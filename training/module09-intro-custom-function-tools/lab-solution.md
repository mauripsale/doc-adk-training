---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 9 Solution: Building a "Calculator" Agent

## Goal

This file contains the complete, step-by-step guide to creating the "Calculator" agent.

### Goal

You will build an agent that can perform basic arithmetic by creating your own custom function tools in Python and integrating them into a Python-based agent.

### Step 1: Create the Calculator Agent Project

1.  **Navigate to your training directory:**
    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Create the agent project:**
    ```shell
    adk create calculator_agent
    ```

3.  **Navigate into the new directory:**
    ```shell
    cd calculator_agent
    ```

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
            return {"status": "error", "message": "Cannot divide by zero."}
        result = a / b
        return {"status": "success", "result": result}
    ```

### Step 3: Configure the Agent to Use the Tools

1.  **Set up your environment variables** in the `.env` file.

2.  **Update the `agent.py` file (Python approach):**
    Open `agent.py` and replace its contents with the following:

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.tools import FunctionTool

    # Import the functions from your tools module
    from .tools.calculator import add, subtract, multiply, divide

    # Create a FunctionTool for each function
    add_tool = FunctionTool(fn=add)
    subtract_tool = FunctionTool(fn=subtract)
    multiply_tool = FunctionTool(fn=multiply)
    divide_tool = FunctionTool(fn=divide)

    root_agent = LlmAgent(
        name="calculator_agent",
        model="gemini-2.5-flash",
        description="An agent that can perform basic arithmetic calculations.",
        instruction="""
    You are a helpful calculator assistant.
    When the user asks you to perform a calculation (add, subtract, multiply, or divide), you MUST use the appropriate tool.
    Clearly state the result of the calculation to the user.
    If the user asks a question that is not a calculation, politely state that you can only perform math.
    """,
        tools=[
            add_tool,
            subtract_tool,
            multiply_tool,
            divide_tool,
        ],
    )
    ```

    **Alternative (YAML approach):**

    If you had created a `config` type agent, you would open `root_agent.yaml` and replace its contents with the following:

    ```yaml
    # yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
    name: calculator_agent
    model: gemini-2.5-flash
    description: An agent that can perform basic arithmetic calculations.
    instruction: |
      You are a helpful calculator assistant.
      When the user asks you to perform a calculation (add, subtract, multiply, or divide), you MUST use the appropriate tool.
      Clearly state the result of the calculation to the user.
      If the user asks a question that is not a calculation, politely state that you can only perform math.
    tools:
      - name: tools.calculator.add
      - name: tools.calculator.subtract
      - name: tools.calculator.multiply
      - name: tools.calculator.divide
    ```

### Step 4: Test the Calculator Agent

1.  **Start the web server:** `adk web` (run this from the `adk-training` parent directory).
2.  **Interact with the agent** in the Dev UI and ask it to perform calculations. Check the Trace View to see the tools being executed.
    *   "What is 42 + 118?"
    *   "Multiply 15 by 3."
    *   "What is 10 divided by 0?"
    *   "What is the capital of France?" (Should be gracefully declined).

### Self-Reflection Answers

1.  **The docstring for each function is critical. What do you think would happen if you removed the docstrings from your calculator functions? Would the agent still be able to use them?**
    *   **Answer:** If you remove the docstrings, the agent (LLM) loses the primary description of what the tool does and how to use it. While the function name and type hints provide *some* information, the docstring provides the context. Without it, the agent might struggle to understand *when* to call the tool or might misinterpret its purpose, leading to unreliable behavior or failure to use the tool at all.

2.  **Why is it a good practice to return a dictionary with a `status` key from a tool function, especially for operations that can fail (like division)?**
    *   **Answer:** Returning a dictionary allows you to provide structured feedback to the agent. The `status` key gives the agent an explicit signal about whether the operation succeeded (`success`) or failed (`error`). If it failed, you can include an `error` message (like "Cannot divide by zero") which the agent can then read and explain to the user. This makes the agent more robust and capable of handling edge cases gracefully.

3.  **How would you add a new tool to this agent, for example, a function to calculate the square root of a number? What steps would you need to take?**
    *   **Answer:** You would need to follow the same three steps:
        1.  **Write the function:** Add a `sqrt(n: float) -> dict` function to `tools/calculator.py` with a clear docstring.
        2.  **Import it:** Import the `sqrt` function in your `agent.py`.
        3.  **Register it:** Wrap it in a `FunctionTool` and add it to the `tools` list in the `LlmAgent` definition.

### Lab Summary

You have successfully built an agent with custom capabilities, learning to:
*   Organize tool code into a separate Python module.
*   Write well-defined Python functions with type hints and docstrings to serve as tools.
*   Reference and register your custom tools in both `agent.py` and `root_agent.yaml`.
*   Write instructions that effectively guide the agent on how and when to use its new tools.
