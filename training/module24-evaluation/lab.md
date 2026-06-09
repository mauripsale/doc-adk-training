---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 24: Creating an Evaluation Case for the Calculator Agent Challenge

## Goal

In this lab, you will learn the fundamental workflow of the ADK's evaluation feature. You will use the ADK Developer UI to have a "golden path" conversation with the Calculator agent you built in Module 9. Then, you will save that conversation as an evaluation case and re-run it to validate the agent's behavior.

### Step 1: Prepare the Agent

1.  **Navigate to your Calculator Agent directory:**

    ```shell
    cd /path/to/your/adk-training/calculator_agent
    ```

2.  **Ensure your virtual environment is active** and your `.env` file is configured with your API key.

3.  **Start the web server:**

    ```shell
    uv run adk web calculator_agent
    ```

### Step 2: Record the "Golden Path" Conversation

First, we need to have a conversation with the agent that represents the exact behavior we want to test.

1.  **Open the Dev UI** in your browser.

2.  **Have the following, precise conversation:**
    *   **User:** "What is 10 + 5?"
    *   Wait for the agent to respond. It should say something like: "The result of 10 + 5 is 15."
    *   This single-turn conversation will be our test case. We will test both the tool call (`add(a=10, b=5)`) and the final text response.

### Step 3: Create the Evaluation Case

Now, let's save this conversation as a reusable test.

1.  **Navigate to the "Eval" Tab:**
    In the right-hand panel of the Dev UI, click on the "Eval" tab.

2.  **Create a New Eval Set:**
    *   An "Eval Set" is a collection of test cases.
    *   Click the **"New Eval Set"** button.
    *   Give it a name, for example, `calculator_tests`, and click "Create".

3.  **Add the Session to the Eval Set:**
    *   With your `calculator_tests` set selected, click the button that says **"Add current session to eval set"**.
    *   You will be prompted for an "Eval Case ID". Give it a descriptive name like `addition_test`. Click "Save".

4.  **Inspect the Saved Case:**
    *   You will now see `addition_test` in the list of evaluation cases.
    *   Click on it. The UI will show you the recorded conversation, including the user message, the expected tool calls, and the expected final response. This is the "golden path" that future test runs will be compared against.
    *   Behind the scenes, the Dev UI has created a file in your agent directory at `eval_results/calculator_tests.evalset.json` containing this test case data. The `eval_results` directory is automatically created by the ADK.

### Step 4: Run the Evaluation

Now that we have a saved test case, we can run it to validate the agent's behavior.

1.  **Select the Test Case:**
    In the "Eval" tab, make sure the checkbox next to `addition_test` is checked.

2.  **Run the Evaluation:**
    *   Click the **"Run Evaluation"** button.
    *   A dialog will appear allowing you to set the evaluation criteria. For this lab, the defaults are fine:
        *   `tool_trajectory_avg_score`: 1.0 (requires a perfect match of the tool calls)
        *   `response_match_score`: 0.8 (requires a high degree of similarity for the text response)
    *   Click **"Start"**.

3.  **Analyze the Results:**
    *   The evaluation will run. This involves the ADK running the user message ("What is 10 + 5?") through the agent again and capturing the new results.
    *   You should see a **"Pass"** result appear in the "Evaluation History".
    *   Click on the "Pass" result to see the details. It will show you that the `tool_trajectory_score` was 1.0 (a perfect match) and the `response_match_score` was also 1.0.

### Step 5: Test a Failure (Optional)

Let's see what a failure looks like.

1.  **Temporarily break the agent:**
    *   Stop the `uv run adk web` server (`Ctrl+C`).
    *   Open `tools/calculator.py`.
    *   In the `add` function, change the calculation to `result = a + b + 1`.
    *   Start the server again: `uv run adk web`.

2.  **Re-run the evaluation:**
    *   Go back to the "Eval" tab.
    *   Select the `addition_test` case again and click "Run Evaluation".
    *   This time, the result should be a **"Fail"**.

3.  **Analyze the failure:**
    *   Click on the "Fail" result.
    *   Hover over the red "Fail" label in the details. A tooltip will appear showing a side-by-side comparison.
    *   You will see that the **Actual Output** ("...result is 16") did not match the **Expected Output** ("...result is 15"), causing the `response_match_score` to be below the threshold.
    *   This demonstrates how evaluations can catch regressions in your agent's logic.

4.  **Don't forget to fix the bug!** Stop the server, change the `add` function back to `result = a + b`, and restart it.

### Step 6: Explore Advanced Metrics (Optional)

In Step 4, we used the default metrics. However, for a production agent, you might care about more than just accuracy.

1.  **Open the "Run Evaluation" Dialog** again.
2.  **Examine the Criteria Dropdown:**
    *   Notice options like `safety_v1` and `hallucinations_v1`.
    *   **`safety_v1`** checks if your agent is generating harmful content.
    *   **`hallucinations_v1`** checks if your agent is making up facts not present in its context.
3.  **Rubric-Based Evaluation:**
    *   You can also see options for **Rubric-based** evaluation. This allows you to define custom criteria (e.g., "Is the tone professional?") and have an LLM judge your agent's response against it.

*Note: Enabling these advanced metrics often requires an LLM call for the evaluation itself (LLM-as-a-judge), which may take longer than simple text matching.*

### Step 7: Understanding the EvalSet File

When you saved the evaluation case, the ADK created a JSON file in your agent's directory at `eval_results/calculator_tests.evalset.json`. Understanding this file is key to creating more complex tests manually.

The structure looks like this:

```json
{
  "eval_set_id": "calculator_tests",
  "eval_cases": [
    {
      "eval_id": "addition_test",
      "conversation": [
        {
          "user_content": {
            "role": "user",
            "parts": [{ "text": "What is 10 + 5?" }]
          },
          "final_response": {
            "role": "model",
            "parts": [{ "text": "The result of 10 + 5 is 15." }]
          },
          "intermediate_data": {
            "tool_uses": [
              {
                "name": "tools.calculator.add",
                "args": { "a": 10, "b": 5 }
              }
            ],
            "tool_responses": [
              {
                "name": "tools.calculator.add",
                "response": { "status": "success", "result": 15 }
              }
            ]
          }
        }
      ]
    }
  ]
}
```

*   **`eval_set_id`**: The name of the collection of tests.
*   **`eval_cases`**: An array of individual test cases.
*   **`conversation`**: An array of turns in the conversation.
*   **`user_content`**: The user's message for this turn.
*   **`final_response`**: The expected final text from the agent.
*   **`intermediate_data`**: This is where the expected **trajectory** is defined.
    *   **`tool_uses`**: A list of the tools the agent is expected to call, with the exact arguments.
    *   **`tool_responses`**: The expected results from those tool calls.

### Step 8: Running Evaluations from the Command Line

While the Dev UI is great for creating and running evaluations interactively, you can also run them from the command line. This is essential for integrating your agent tests into an automated CI/CD pipeline.

1.  **Stop the `uv run adk web` server.**
2.  **Run the `uv run adk eval` command:**
    From your `calculator_agent` directory, run the following command:

    ```shell
    uv run adk eval . eval_results/calculator_tests.evalset.json
    ```
    *   **`uv run adk eval`**: The main command.
    *   **`.`**: The path to the agent to be tested (the current directory, `calculator_agent`).
    *   **`eval_results/calculator_tests.evalset.json`**: The path to the evaluation file to run.

3.  **Analyze the Output:**
    The command will run the evaluation and print the results directly to your terminal.

    ```
    Running evaluations for: .
    Eval Set: calculator_tests
      ✓ addition_test PASSED

    Total: 1/1 passed (100%)
    ```
    This provides a fast, automated way to confirm your agent is still behaving as expected after you make changes.

### Lab Summary

You have successfully created and run your first agent evaluation! This is a critical skill for building reliable, production-ready agents.

You have learned to:
*   Use the ADK Dev UI to record a conversation as an evaluation case.
*   Organize test cases into "Eval Sets".
*   Run an evaluation and interpret the "Pass/Fail" results.
*   Analyze the detailed scores for tool trajectory and response matching.
*   Understand how evaluations help you catch regressions in your agent's behavior.

### Self-Reflection Questions
- Why is testing the `tool_trajectory` often more important for ensuring an agent's correctness than just testing its final text response?
- The `response_match_score` is not a simple "equals" check. Why is this fuzzy matching necessary for evaluating LLM-generated text?
- How could you integrate the `uv run adk eval` command into a CI/CD pipeline (like GitHub Actions) to automatically test your agent every time you push new code?
- What is the difference between "Golden Path" testing and "User Simulation"?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMjQtZXZhbHVhdGlvbi9sYWItc29sdXRpb24=`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module24-evaluation/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
