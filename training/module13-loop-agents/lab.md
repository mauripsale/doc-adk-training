# Module 13: Advanced Orchestration: Loop Agents

## Lab 13: Building a Number Guessing Game with `LoopAgent`

### Goal

In this lab, you will build an agent that plays a number guessing game. The agent will repeatedly try to guess a secret number until it gets it right. This will teach you how to use a `LoopAgent` for iterative tasks and how to terminate a loop based on a dynamic condition using a custom tool and escalation.

The game will work like this:
1.  We'll set a secret number in the agent's state.
2.  The `LoopAgent` will run. In each iteration, a "guesser" agent will make a guess.
3.  A "checker" tool will compare the guess to the secret number and report if it was too high, too low, or correct.
4.  If the guess is correct, the tool will "escalate" to stop the loop.

### Step 1: Create the Project and Tool

1.  **Create the agent project:**

    ```shell
    cd /path/to/your/adk-training
    adk create --type=config guessing-game
    cd guessing-game
    ```

2.  **Create the `checker` tool:**
    This tool will contain the core logic of our game. It will read the agent's guess and the secret number from the state, compare them, and escalate if the guess is correct.

    *   Create the `tools` directory and `__init__.py` file:
        ```shell
        mkdir tools
        touch tools/__init__.py
        ```
    *   Create `tools/checker.py` and add the following code:
        ```python
        from google.adk.tools import ToolContext

        def check_guess(tool_context: ToolContext) -> dict:
            """
            Checks the agent's guess against the secret number.

            This tool reads `state['secret_number']` and `state['current_guess']`.
            It returns 'correct', 'too_low', or 'too_high'.
            If the guess is correct, it escalates to stop the loop.
            """
            secret = tool_context.state.get('secret_number')
            guess = tool_context.state.get('current_guess')

            if secret is None or guess is None:
                return {"status": "error", "message": "Secret number or guess not found in state."}

            if guess == secret:
                # This is the key to stopping the loop!
                tool_context.actions.escalate = True
                return {"status": "correct", "message": f"Correct! The number was {guess}."}
            elif guess < secret:
                return {"status": "too_low", "message": f"{guess} is too low."}
            else: # guess > secret
                return {"status": "too_high", "message": f"{guess} is too high."}
        ```

### Step 2: Create the Sub-Agent for Guessing

This agent's job is to make a guess in each iteration of the loop.

*   Create a file named `guesser_agent.yaml` and add the following:
    ```yaml
    # Filename: guesser_agent.yaml
    name: guesser_agent
    model: gemini-1.5-flash
    instruction: |
      You are a number guesser. Your goal is to guess the secret number.
      The number is between 1 and 100.
      I will give you hints like "too_low" or "too_high".
      Based on the hint in `state['hint']`, make a new guess.
      Your response should be ONLY the number you are guessing.

      Previous hint: {hint}
    # Save the guess to the state so the checker tool can read it.
    output_key: current_guess
    ```

### Step 3: Configure the Loop Agent Orchestrator

Now, let's define our main agent, which will be a `LoopAgent` that orchestrates the guesser and the checker.

1.  **Create a `checker_agent.yaml`:**
    We need an agent to host our `check_guess` tool. Create this file:
    ```yaml
    # Filename: checker_agent.yaml
    name: checker_agent
    model: gemini-1.5-flash
    instruction: |
      You are the guess checker.
      You must call the `check_guess` tool.
      Then, save the result message to the `hint` state variable.
    tools:
      - name: tools.checker.check_guess
    output_key: hint
    ```

2.  **Update `root_agent.yaml`:**
    This is our main `LoopAgent`. It will run the `guesser_agent` and `checker_agent` in a loop.

    ```yaml
    # Filename: root_agent.yaml
    agent_class: LoopAgent
    name: guessing_game_loop
    # Set a max_iterations as a safety measure.
    max_iterations: 10
    sub_agents:
      - config_path: guesser_agent.yaml
      - config_path: checker_agent.yaml
    ```

### Step 4: Test the Game

1.  **Set up your `.env` file** with your API key or Vertex AI project.

2.  **Start the web server:** `adk web`

3.  **Play the game:**
    *   Open the Dev UI.
    *   Go to the **"State"** tab. We need to set the initial state: the secret number and a starting hint.
    *   In the "Set State" box, enter the following JSON and click "Set State":
        ```json
        {
          "secret_number": 42,
          "hint": "I've picked a number between 1 and 100. Make your first guess."
        }
        ```
    *   Go to the **"Chat"** tab and send a message like "Start guessing".

4.  **Observe the Loop:**
    *   You will see the agent start guessing. The final response will likely be the "Correct!" message from the `check_guess` tool.
    *   **Go to the Trace View.** This is where you can see the loop in action. You will see the `LoopAgent` running, and nested inside it, you'll see multiple iterations.
    *   Expand each iteration. You'll see the `guesser_agent` run, followed by the `checker_agent`.
    *   Look at the state changes between iterations. You'll see the `current_guess` and `hint` values being updated each time.
    *   In the final iteration, you'll see that the `check_guess` tool set `escalate: true`, which caused the `LoopAgent` to terminate.

### Lab Summary

You have successfully built an iterative agent using the `LoopAgent`! This is a powerful pattern for solving problems that require multiple refinement steps.

You have learned to:
*   Configure and use the `LoopAgent` to repeat a sequence of sub-agents.
*   Use `max_iterations` as a safeguard against infinite loops.
*   Use a custom tool to check a condition within a loop.
*   Terminate a loop dynamically by setting `tool_context.actions.escalate = True`.
*   Observe the iterative process and state changes using the Dev UI's Trace View.
