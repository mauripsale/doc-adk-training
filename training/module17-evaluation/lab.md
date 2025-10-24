# Module 17: Evaluating Agent Performance

## Lab 17: Creating an Evaluation Case for the Calculator Agent

### Goal

In this lab, you will learn the fundamental workflow of the ADK's evaluation feature. You will use the ADK Developer UI to have a "golden path" conversation with the Calculator agent you built in Module 7. Then, you will save that conversation as an evaluation case and re-run it to validate the agent's behavior.

### Step 1: Prepare the Agent

1.  **Navigate to your Calculator Agent directory:**

    ```shell
    cd /path/to/your/adk-training/calculator-agent
    ```

2.  **Ensure your virtual environment is active** and your `.env` file is configured.

3.  **Start the web server:**

    ```shell
    adk web
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
    *   Behind the scenes, the Dev UI has created a file in your agent directory at `eval_results/calculator_tests.evalset.json` containing this test case data.

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
    *   Stop the `adk web` server (`Ctrl+C`).
    *   Open `tools/calculator.py`.
    *   In the `add` function, change the calculation to `result = a + b + 1`.
    *   Start the server again: `adk web`.

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

### Lab Summary

You have successfully created and run your first agent evaluation! This is a critical skill for building reliable, production-ready agents.

You have learned to:
*   Use the ADK Dev UI to record a conversation as an evaluation case.
*   Organize test cases into "Eval Sets".
*   Run an evaluation and interpret the "Pass/Fail" results.
*   Analyze the detailed scores for tool trajectory and response matching.
*   Understand how evaluations help you catch regressions in your agent's behavior.
