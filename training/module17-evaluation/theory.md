# Module 17: Evaluating Agent Performance

## Theory

### Why Traditional Tests Aren't Enough

In traditional software development, we rely on unit tests and integration tests to ensure our code is correct. These tests check for specific, predictable outcomes. For example, `assert add(2, 2) == 4`. This works because the `add` function is **deterministic**—it will always produce the same output for the same input.

However, `LlmAgent`s are **non-deterministic**. Due to the probabilistic nature of Large Language Models, asking the same question twice might yield slightly different, yet equally correct, answers.

*   **User:** "What's the weather in Paris?"
*   **Acceptable Answer 1:** "The weather in Paris is currently sunny and 22°C."
*   **Acceptable Answer 2:** "It's a sunny day in Paris, with a temperature of 22 degrees Celsius."

A simple string comparison would fail for the second answer, even though it's perfectly valid. This variability means we need a more sophisticated way to evaluate our agents.

### The Principles of Agent Evaluation

Agent evaluation is less about "pass/fail" and more about measuring **quality** and **correctness**. The ADK's evaluation framework is built on comparing an agent's actual behavior against a "golden" or "reference" example that you provide.

This evaluation can be broken down into two key areas:

#### 1. **Evaluating the Final Response**
This assesses the quality of the agent's final answer to the user. Instead of an exact match, we can use more flexible criteria:
*   **Semantic Similarity:** Does the agent's response *mean* the same thing as the reference response? This can be judged by another LLM.
*   **Rubrics:** Does the response meet certain quality criteria? (e.g., "Is the tone helpful?", "Is the answer concise?").
*   **Groundedness:** Does the agent's answer contain any "hallucinations" (facts that it made up), or is it properly grounded in the information it received from its tools?

#### 2. **Evaluating the Trajectory**
This is unique to agents and is often more important than the final response. The **trajectory** is the sequence of steps the agent took to arrive at its answer. This includes which tools it called, in what order, and with what arguments.

By evaluating the trajectory, you are testing the agent's **reasoning process**. Did it use the right tool for the job? Did it call its tools in the correct sequence?

For example, if a user asks to book a flight and then a hotel, the expected trajectory might be:
1.  Call `search_flights` tool.
2.  Call `book_flight` tool.
3.  Call `search_hotels` tool.
4.  Call `book_hotel` tool.

If the agent tries to book the hotel before searching for flights, its trajectory is incorrect, even if it eventually produces a valid booking. The ADK's evaluation tools allow you to perform an **exact match** on the tool trajectory, ensuring your agent follows the correct process every time.

### How Evaluation Works in the ADK

The ADK evaluation workflow revolves around creating **Evaluation Cases**. An evaluation case is a recording of a conversation, including:
*   The user's messages.
*   The expected final response from the agent.
*   The expected intermediate tool calls (the trajectory).

You can create these evaluation cases manually in a JSON file, but the easiest way is to use the **ADK Developer UI**. You can have a conversation with your agent, and if you're satisfied with the outcome, you can save that entire conversation as a new evaluation case with a single click.

Once you have a set of evaluation cases, you can run them automatically:
*   From the Dev UI, to get a quick visual report.
*   From the command line (`adk eval`), for automated checks.
*   Programmatically (using `pytest`), to integrate agent evaluation into your CI/CD pipeline.

By building a suite of evaluation cases, you create a safety net. Every time you change your agent's instructions or tools, you can re-run your evaluations to ensure you haven't caused a regression in its behavior. This brings the reliability of traditional software testing to the non-deterministic world of AI agents.
