# Module 7: Creating Custom Function Tools

## Lab 7: Building a "Calculator" Agent

### Goal

In this lab, you will build an agent that can perform basic arithmetic. You will do this by creating your own custom function tools in Python and integrating them into a config-based agent. This will teach you the end-to-end process of extending an agent's capabilities with your own code.

### Step 1: Create the Calculator Agent Project

1.  **Navigate to your training directory:**

    Open your terminal and make sure you are in the `adk-training` directory.

    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Create the agent project:**

    ```shell
    adk create --type=config calculator-agent
    ```

3.  **Navigate into the new directory:**

    ```shell
    cd calculator-agent
    ```

### Step 2: Write the Custom Tool Functions

Now, we'll write the Python code for our calculator.

1.  **Create a `tools` directory:**

    Inside your `calculator-agent` project directory, create a new directory named `tools`. By convention, it's good practice to organize your tool code in a separate module.

    ```shell
    mkdir tools
    ```

2.  **Create an `__init__.py` file:**

    To make the `tools` directory a Python package, create an empty file named `__init__.py` inside it.

    ```shell
    touch tools/__init__.py
    ```

3.  **Create the `calculator.py` file:**

    Inside the `tools` directory, create a new file named `calculator.py`. This file will contain the logic for our arithmetic operations.

    Add the following code to `tools/calculator.py`:

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
    Notice how each function has a clear name, type hints, a descriptive docstring, and returns a structured dictionary.

### Step 3: Configure the Agent to Use the Tools

Now we need to tell our agent about these new tools.

1.  **Set up your environment variables:**

    Open the `.env` file and ensure it's configured with your Google API key or Vertex AI project, just as you did in previous labs.

2.  **Update the `root_agent.yaml` file:**

    Open `root_agent.yaml` and replace its contents with the following:

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
    **Analysis:**
    *   **`tools` section:** We've added a `tools` list. Each item uses the format `[directory_name].[file_name].[function_name]` (e.g., `tools.calculator.add`) to tell the ADK where to find the Python function.
    *   **`instruction`:** The instruction clearly tells the agent its purpose and explicitly directs it to use the tools for calculations.

### Step 4: Test the Calculator Agent

1.  **Start the web server:**

    From the `calculator-agent` directory, run `adk web`.

2.  **Interact with the agent:**
    *   Open the Dev UI and ask it to perform calculations:
        *   "What is 42 + 118?"
        *   "Multiply 15 by 3."
        *   "What is 100 divided by 5?"
        *   "What is 10 divided by 0?" (See how it handles the error).
    *   **Check the Trace View:** For a successful calculation, expand the trace and look for the `execute_tool` step. You'll see the specific function (e.g., `tools.calculator.add`) that was called and the arguments the LLM provided.
    *   Try asking a non-math question:
        *   "What is the capital of France?"
        *   The agent should follow its instructions and state that it can only perform math.

### Lab Summary

You have successfully built an agent with custom capabilities! You have learned to:
*   Organize tool code into a separate Python module.
*   Write well-defined Python functions with type hints and docstrings to serve as tools.
*   Reference and register your custom tools in the `root_agent.yaml` configuration.
*   Write instructions that effectively guide the agent on how and when to use its new tools.

This is a fundamental pattern for building powerful agents. In the next module, you'll learn how to make your tools even more powerful by allowing them to interact with the agent's memory.
