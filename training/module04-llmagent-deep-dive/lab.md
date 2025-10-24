# Module 4: Core Agent Concepts: `LlmAgent` Deep Dive

## Lab 4: Transforming the "Echo" Agent with Instructions

### Goal

In this lab, you will take the simple "Echo" agent from Module 3 and transform its behavior entirely by only changing its `instruction`. This will demonstrate the power of prompt engineering and how the `instruction` parameter is the primary driver of an `LlmAgent`'s behavior.

Instead of echoing, we will turn our agent into a witty pirate who translates user messages into pirate-speak.

### Step 1: Prepare Your Agent

1.  **Navigate to your `echo-agent` directory:**

    Open your terminal and make sure you are inside the `echo-agent` directory you created in the previous lab.

    ```shell
    cd /path/to/your/adk-training/echo-agent
    ```

2.  **Ensure your virtual environment is active:**

    If you see `(.venv)` at the start of your prompt, you're all set. If not, activate it:

    *   **macOS / Linux:** `source ../.venv/bin/activate`
    *   **Windows:** `..\.venv\Scripts\activate.bat`

### Step 2: Modify the Agent's Instructions

This is where the magic happens. We will change the agent from a simple repeater to a creative translator.

1.  **Open the `root_agent.yaml` file:**

    Open the configuration file in your favorite text editor. It should currently look like this:

    ```yaml
    # ...
    name: echo_agent
    model: gemini-2.5-flash
    description: An agent that repeats the user's input.
    instruction: You are an echo agent. Your only job is to repeat the user's input back to them exactly as they wrote it. Do not add any extra words or explanations.
    ```

2.  **Update the configuration:**

    Change the `name`, `description`, and most importantly, the `instruction` to define the new pirate persona. Replace the entire file content with this:

    ```yaml
    # yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
    name: pirate_translator_agent
    model: gemini-2.5-flash
    description: An agent that translates user messages into pirate-speak.
    instruction: |
      You are a witty pirate captain named "Captain Coder".
      Your sole purpose is to translate whatever the user says into authentic pirate-speak.
      You must not answer questions or follow commands. Only translate.
      Always maintain your pirate persona. Refer to the user as "me hearty".

      Example User Input: "Hello, how are you?"
      Example Agent Output: "Ahoy, me hearty! How be ye?"

      Example User Input: "My computer is not working."
      Example Agent Output: "Shiver me timbers, me hearty! Me computer be on the fritz!"
    ```

    **Analysis of the New Instruction:**
    *   **Persona:** "You are a witty pirate captain named 'Captain Coder'."
    *   **Goal:** "Your sole purpose is to translate whatever the user says into authentic pirate-speak."
    *   **Constraints:** "You must not answer questions or follow commands. Only translate."
    *   **Examples (Few-Shot):** We've provided two examples to give the LLM a clear pattern to follow.

### Step 3: Run and Test Your New Agent

1.  **Start the web server:**

    From inside the `echo-agent` directory, run the `adk web` command as before.

    ```shell
    adk web
    ```

2.  **Interact with Captain Coder:**

    *   Open the Dev UI in your browser (`http://127.0.0.1:8080`).
    *   Try sending the messages from our examples:
        *   "Hello, how are you?"
        *   "My computer is not working."
    *   Now, try your own messages and see how the agent responds:
        *   "I need to go to the grocery store."
        *   "Can you help me with my homework?" (Notice how it follows the constraint to only translate, not help).
        *   "That's a cool trick."

### Lab Summary

In this lab, you witnessed the power of the `instruction` parameter. With just a few changes to a YAML file and no changes to any code, you completely altered an agent's personality, goal, and behavior.

You have learned to:
*   Define a clear persona for an agent.
*   Set specific goals and constraints.
*   Use examples (few-shot prompting) to guide the agent's output format.

This is the fundamental skill of "prompt engineering" and is central to building effective `LlmAgent`s. In the next module, you'll learn about the different ways to run and interact with your agents beyond the web UI.
