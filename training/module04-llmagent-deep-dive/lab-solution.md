---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 4 Solution: Transforming an Agent by Duplication and Modification

## Goal

In this lab, you will create a new "Haiku Poet" agent by duplicating and then modifying the "Echo" agent from Module 3. This will demonstrate the power of prompt engineering and show how to build upon an existing agent's foundation.

Instead of echoing, we will turn our agent into a wise poet who transforms user topics into haikus.

### Step 1: Prepare Your New Agent

1.  **Navigate to your `adk-training` directory:**

    Open your terminal and make sure you are inside the `adk-training` directory.

    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Duplicate the existing agent:**

    Copy the `echo_agent` directory and rename the copy to `haiku_poet_agent`.

    *   **macOS / Linux:**
        ```shell
        cp -r echo_agent haiku_poet_agent
        ```
    *   **Windows:**
        ```shell
        xcopy echo_agent haiku_poet_agent /E /I
        ```

3.  **Ensure your virtual environment is active:**

    If you see `(.venv)` at the start of your prompt, you're all set. If not, activate it:

    *   **macOS / Linux:** `source .venv/bin/activate`
    *   **Windows:** `.venv\Scripts\activate.bat`

### Step 2: Modify the Agent's Instructions (Python Approach)

This is where the magic happens. We will change the agent from a simple repeater to a creative poet.

1.  **Open the `agent.py` file:**

    Navigate into the new `haiku-poet-agent` directory and open the Python file in your favorite text editor.

2.  **Update the `LlmAgent` constructor:**

    Change the `name`, `description`, and most importantly, the `instruction` to define the new poet persona. Replace the entire file content with this:

    ```python
    from google.adk.agents import LlmAgent

    root_agent = LlmAgent(
        name="haiku_poet_agent",
        model="gemini-2.5-flash",
        description="An agent that turns any topic into a haiku.",
        instruction="""
          You are a wise and calm poet who only speaks in haikus (three lines with a 5, 7, 5 syllable structure).
          Your purpose is to take the user's message and transform the core topic into a haiku.
          Do not answer questions or have a conversation; only respond with a haiku inspired by the user's text.

          Example User Input: "I'm having trouble with my computer."
          Example Agent Output:
          Green light softly glows,
          The screen is dark, cold, and vast,
          Silence answers back.

          Example User Input: "The weather is so nice today!"
          Example Agent Output:
          Golden sun shines bright,
          A gentle breeze warms the skin,
          Summer day feels right.
        """
    )
    ```

    **Analysis of the New Instruction:**
    *   **Persona:** "You are a wise and calm poet..."
    *   **Goal:** "...transform the core topic into a haiku."
    *   **Constraints:** "Do not answer questions or have a conversation; only respond with a haiku..."
    *   **Output Format:** "...only speaks in haikus (three lines with a 5, 7, 5 syllable structure)."
    *   **Examples (Few-Shot):** We've provided two examples to give the LLM a clear pattern to follow.

### Alternative: Defining the Agent in YAML

If you are using a config-based agent:

1.  **Open the `root_agent.yaml` file:**

    Navigate into the `haiku-poet-agent` directory and open the configuration file.

2.  **Update the configuration:**

    Replace the entire file content with this:

    ```yaml
    # yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
    name: haiku_poet_agent
    model: gemini-2.5-flash
    description: An agent that turns any topic into a haiku.
    instruction: |
      You are a wise and calm poet who only speaks in haikus (three lines with a 5, 7, 5 syllable structure).
      Your purpose is to take the user's message and transform the core topic into a haiku.
      Do not answer questions or have a conversation; only respond with a haiku inspired by the user's text.

      Example User Input: "I'm having trouble with my computer."
      Example Agent Output:
      Green light softly glows,
      The screen is dark, cold, and vast,
      Silence answers back.

      Example User Input: "The weather is so nice today!"
      Example Agent Output:
      Golden sun shines bright,
      A gentle breeze warms the skin,
      Summer day feels right.
    ```

### Step 3: Run and Test Your New Agent

1.  **Start the web server:**

    From your `adk-training` directory, run the `adk web` command, specifying the new agent's folder.

    ```shell
    adk web haiku-poet-agent
    ```

2.  **Interact with the Haiku Poet:**

    *   Open the Dev UI in your browser (`http://127.0.0.1:8080`).
    *   Try sending the topics from our examples:
        *   "I'm having trouble with my computer."
        *   "The weather is so nice today!"
    *   Now, try your own topics and see how the agent responds:
        *   "My favorite food is pizza."
        *   "Can you tell me the capital of France?" (Notice how it follows the constraint to only provide a haiku, not answer the question).
        *   "Learning to code is fun."

### Challenge Yourself

Now that you've seen how to change the agent's persona, try creating a new one!
1.  Stop the `adk web` server (`Ctrl+C`).
2.  Duplicate the `haiku-poet-agent` directory and give it a new name.
3.  Open your `agent.py` or `root_agent.yaml` file in the new directory.
4.  Change the `instruction` to create a completely different character. How about a formal Shakespearean poet, a futuristic robot, or a pessimistic philosopher?
5.  Relaunch the server and test your new creation!

### Lab Summary

In this lab, you witnessed the power of the `instruction` parameter. By duplicating an existing agent and changing its instructions, you completely altered its personality, goal, and behavior.

You have learned to:
*   Build upon existing agents by duplicating them.
*   Define a clear persona for an agent.
*   Set specific goals and constraints.
*   Use examples (few-shot prompting) to guide the agent's output format.

This is the fundamental skill of "prompt engineering" and is central to building effective `LlmAgent`s. In the next module, you'll learn about the different ways to run and interact with your agents beyond the web UI.

### Self-Reflection Answers

1.  **How does providing examples (few-shot prompting) in the instruction help the LLM understand the task better than just describing it?**
    *   **Answer:** Few-shot prompting provides concrete demonstrations of the desired input-output format and behavior. While a textual description sets the general rules, examples clarify nuances, specific formatting requirements, and implicit constraints that might be ambiguous in text alone. This significantly reduces the chances of the LLM misinterpreting the instruction.

2.  **What would happen if you removed the constraint "Do not answer questions or have a conversation"? How would the agent's behavior change?**
    *   **Answer:** If this constraint were removed, the agent would likely become more conversational. It might attempt to answer questions directly, engage in dialogue, or provide additional context beyond just the haiku. This would deviate from its intended role as a dedicated haiku poet and could lead to less focused or less predictable responses.

3.  **Experiment with creating a new persona for the agent (e.g., a Shakespearean poet, a futuristic robot). What are the key elements you need to include in the instruction to make the new persona convincing?**
    *   **Answer:** Key elements for a convincing persona include:
        *   **Role/Identity:** Explicitly state who the agent is (e.g., "You are a Shakespearean poet...").
        *   **Tone/Style:** Describe the language and emotional register (e.g., "speak in archaic English, using flowery language and dramatic flair").
        *   **Constraints:** Define what the agent *should* and *should not* do (e.g., "always respond in iambic pentameter," "do not use modern slang").
        *   **Examples:** Provide few-shot examples that demonstrate the new persona's typical responses and adherence to its style and constraints.
        *   **Goals:** Clearly state the agent's primary objective (e.g., "to transform user input into a sonnet").