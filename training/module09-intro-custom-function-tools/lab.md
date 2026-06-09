---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 9: Building a "Calculator" Agent Challenge

## Goal

In this lab, you will build an agent that can perform basic arithmetic. You will do this by creating your own custom function tools in Python and integrating them into a Python-based agent.

### Step 1: Create the Project and File Structure

We will use `uv` to create a modern Python environment for our agent.

1.  **Initialize the agent project:**
    ```bash
    uv init calculator_agent --python 3.10
    cd calculator_agent
    uv add google.adk python-dotenv
    ```

2.  **Setup Authentication:**
    Create a `.env` file in your `calculator_agent` directory and add your `GOOGLE_API_KEY` (or Vertex AI settings).

3.  **Create the tools module:**
    It's good practice to organize your tool code in a separate module. The empty `__init__.py` file tells Python to treat the `tools` directory as a package, which allows us to import functions from it.
    ```bash
    mkdir tools
    touch tools/__init__.py
    touch tools/calculator.py
    ```

### Step 2: Implement the Tool Functions

**Exercise:** Open `tools/calculator.py` and implement the four arithmetic functions below. Pay close attention to the docstrings and type hints, as this is what the agent will see.

```python
# In tools/calculator.py

def add(a: int, b: int) -> dict:
    """
    Adds two numbers together.
    Use this tool when the user asks to find the sum of two numbers.
    Args:
        a: The first number.
        b: The second number.
    """
    # TODO: Calculate the sum of a and b.
    # Return a dictionary with {"status": "success", "result": ...}
    pass

def subtract(a: int, b: int) -> dict:
    """
    Subtracts the second number from the first number.
    Use this tool when the user asks to find the difference between two numbers.
    Args:
        a: The first number.
        b: The second number to subtract.
    """
    # TODO: Calculate the difference between a and b.
    # Return a dictionary with {"status": "success", "result": ...}
    pass

def multiply(a: int, b: int) -> dict:
    """
    Multiplies two numbers together.
    Use this tool when the user asks to find the product of two numbers.
    Args:
        a: The first number.
        b: The second number.
    """
    # TODO: Calculate the product of a and b.
    # Return a dictionary with {"status": "success", "result": ...}
    pass

def divide(a: int, b: int) -> dict:
    """
    Divides the first number by the second number.
    Use this tool when the user asks to divide one number by another.
    Args:
        a: The numerator.
        b: The denominator.
    """
    # TODO: Handle the case where b is 0, returning an error dictionary.
    # Otherwise, calculate the division and return the result.
    pass

> **Pro Tip:** While we use simple dictionaries in this lab for simplicity, ADK 2.0 strongly recommends returning **Pydantic models** for better type safety and structured reasoning (as you will see in the Lab Solution).

### Step 3: Configure the Agent Node

**Exercise:** Create `agent.py` and complete the configuration using the modern ADK 2.0 **`Agent`** class.

```python
# In agent.py
from google.adk import Agent
from tools.calculator import add, subtract, multiply, divide

root_agent = Agent(
    name="calculator_agent",
    model="gemini-3.5-flash",
    description="An agent node that performs arithmetic.",
    instruction=\"\"\"
You are a helpful calculator assistant.
When the user asks you to perform a calculation, you MUST use the appropriate tool.
\"\"\",
    # TODO: Add the four imported functions directly to this list.
    tools=[add, subtract, multiply, divide]
)
```

### Step 4: Test the Calculator Agent

You can test your new agent directly using the ADK CLI's interactive mode.

1.  **Run the agent in interactive mode:**
    ```bash
    uv run adk run agent.py
    ```
2.  **Interact with the agent** in the terminal:
    *   "What is 42 + 118?"
    *   "Multiply 15 by 3."
    *   "What is 10 divided by 0?"
    *   "What is the capital of France?" (Should be gracefully declined).

### Having Trouble?

If you get stuck, you can find the complete, working code and configuration in the `lab-solution.md` file.

### Lab Summary

You have successfully built an agent with custom capabilities! You have learned to:
*   Organize tool code into a separate Python module.
*   Write well-defined Python functions with type hints and docstrings to serve as tools.
*   Import and register your custom tools directly in the `agent.py` file.
*   Write instructions that effectively guide the agent on how and when to use its new tools.

### Self-Reflection Questions
- The docstring for each function is critical. What do you think would happen if you removed the docstrings from your calculator functions? Would the agent still be able to use them?
- Why is it a good practice to return a dictionary with a `status` key from a tool function, especially for operations that can fail (like division)?
- How would you add a new tool to this agent, for example, a function to calculate the square root of a number? What steps would you need to take?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMDktaW50cm8tY3VzdG9tLWZ1bmN0aW9uLXRvb2xzL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module09-intro-custom-function-tools/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
