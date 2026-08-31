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

2.  **Ensure your virtual environment is active** and your `.env` file is configured with your API key. Also make sure the evaluation extra is installed — `adk eval` (Step 8) will fail without it:
    ```shell
    uv add "google-adk[eval]"
    ```

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
                "name": "add",
                "args": { "a": 10, "b": 5 }
              }
            ],
            "tool_responses": [
              {
                "name": "add",
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
2.  **Create an `__init__.py`** in your `calculator_agent` root, if you don't already have one:
    ```shell
    echo "from . import agent" > __init__.py
    ```
    `adk eval` loads your agent through this file, unlike `adk run`/`adk web`, which discover `agent.py` directly and don't need it.
3.  **Run the `uv run adk eval` command:**
    From your `calculator_agent` directory, run the following command:

    ```shell
    PYTHONPATH=. uv run adk eval . eval_results/calculator_tests.evalset.json
    ```
    *   **`PYTHONPATH=.`**: Required so that `agent.py`'s `from tools.calculator import ...` resolves — unlike `adk run`, `adk eval` doesn't add the current directory to Python's import path automatically.
    *   **`uv run adk eval`**: The main command.
    *   **`.`**: The path to the agent to be tested (the current directory, `calculator_agent`).
    *   **`eval_results/calculator_tests.evalset.json`**: The path to the evaluation file to run.

3.  **Analyze the Output:**
    The command will run the evaluation and print the results directly to your terminal.

    ```
    *********************************************************************
    Eval Run Summary
    calculator_tests:
      Tests passed: 1
      Tests failed: 0
    ```
### Bonus: Writing a Custom Metric (Optional)

> **Heads up:** the three Bonus/Extra Challenge sections below (Custom Metric, Dynamic User Simulation, Locust load testing) are each substantially denser than the core lab -- each introduces new API surface (`EvalConfig`, `ConversationScenarios`, Locust) on its own. Treat Steps 1-8 as the complete lab, and budget extra time separately if you plan to work through the bonus sections too.

Built-in criteria like `tool_trajectory_avg_score` can't check business-specific logic — for example, whether the calculator's result is actually mathematically correct. For that, you write a custom metric: a Python function matching ADK's expected signature, wired into `EvalConfig.custom_metrics`.

1.  **Create `custom_metrics.py`** in your `calculator_agent` directory:
    ```python
    from google.adk.evaluation.evaluator import EvaluationResult, PerInvocationResult
    from google.adk.evaluation.eval_metrics import EvalStatus

    def check_math_is_correct(eval_metric, actual_invocations, expected_invocations, conversation_scenario):
        """Custom metric: verifies the calculator's tool result is arithmetically correct."""
        results = [
            PerInvocationResult(actual_invocation=inv, score=1.0, eval_status=EvalStatus.PASSED)
            for inv in actual_invocations
        ]
        return EvaluationResult(
            overall_score=1.0,
            overall_eval_status=EvalStatus.PASSED,
            per_invocation_results=results,
        )
    ```
    *(This skeleton always passes — as a challenge, make it actually re-compute the expected result from the tool call arguments and compare it against the tool's response.)*

2.  **Create `eval_config.json`** in the same directory. Registering the function under `custom_metrics` is not enough on its own — it must *also* be listed in `criteria` (with a threshold) for ADK to actually run it. Note that `custom_metrics` is a dict keyed by metric name, not a list:
    ```json
    {
      "criteria": {
        "check_math_is_correct": 0.5
      },
      "custom_metrics": {
        "check_math_is_correct": {
          "code_config": { "name": "custom_metrics.check_math_is_correct" }
        }
      }
    }
    ```

3.  **Run the evaluation, pointing at your config file:**
    ```shell
    PYTHONPATH=. uv run adk eval . eval_results/calculator_tests.evalset.json --config_file_path eval_config.json
    ```
    Your custom metric now runs alongside the built-in ones in the same report.

### Bonus: Dynamic User Simulation (Optional)

Static "Golden Path" cases are great for regression testing, but they can't test how your agent handles a real, unpredictable user. **User Simulation** lets an LLM play the user instead, following a `conversation_plan` and an optional persona (`NOVICE`, `EXPERT`, `EVALUATOR`).

1.  **Create `scenarios.json`**, a `ConversationScenarios` file, instead of a fixed conversation:
    ```json
    {
      "scenarios": [
        {
          "starting_prompt": "What's 7 times 8?",
          "conversation_plan": "Ask for one more calculation, then thank the agent.",
          "user_persona": "NOVICE"
        }
      ]
    }
    ```

2.  **Create a `session_input.json`** describing which app/user this simulated conversation belongs to:
    ```json
    { "app_name": "calculator_agent", "user_id": "test_user" }
    ```

3.  **Create a new eval set and add the scenario to it.** Unlike the Dev UI (which stores eval sets under `eval_results/`), the `adk eval_set` CLI commands always store them directly in your agent's root directory — so this uses a separate eval set (`user_sim_tests`) rather than mixing locations with `calculator_tests`:
    ```shell
    uv run adk eval_set create . user_sim_tests
    uv run adk eval_set add_eval_case . user_sim_tests \
        --scenarios_file scenarios.json \
        --session_input_file session_input.json
    ```

4.  **Run the evaluation** against the new eval set:
    ```shell
    PYTHONPATH=. uv run adk eval . user_sim_tests.evalset.json
    ```
    Instead of replaying your exact recorded messages, ADK generates the follow-up turns dynamically, simulating how a hesitant, first-time user might actually phrase things.

5.  Since there's no single "expected" response for a dynamically generated conversation, pair this with reference-free metrics like `safety_v1` and `hallucinations_v1` rather than `response_match_score`.

### Extra Challenge: Performance Load Testing with Locust (Optional)

In production, evaluations are not just about correctness, but also about **performance and latency**. To test if your asynchronous agent endpoints can scale under concurrent user traffic without blocking the Python event loop, you can use **Locust**.

1. **Install Locust** (inside your virtual environment):
   ```shell
   uv pip install locust
   ```
2. **Create a `locustfile.py`:**
   Create a file inside your directory and use this skeletal template. Your task is to fill in the **ADK-specific payload** and **validation logic** where marked with `TODO`:

   ```python
   import json
   from locust import HttpUser, task, between

   class ADKAgentUser(HttpUser):
       # Wait between 1 and 3 seconds between tasks per user
       wait_time = between(1, 3)

       @task
       def ask_calculator_agent(self):
           headers = {"Content-Type": "application/json"}
           
           # TODO: Define the JSON payload matching ADK's native API contract
           # It must include a session_id and a prompt (e.g. asking the calculator)
           payload = {
               # "session_id": "...",
               # "prompt": "..."
           }
           
           # TODO: Complete the POST request to the API server's execution endpoint (e.g., "/run")
           with self.client.post("/run", json=payload, headers=headers, catch_response=True) as response:
               if response.status_code == 200:
                   try:
                       data = response.json()
                       # TODO: Check if the expected mathematical result is present in the response
                       # if expected_value_present:
                       #     response.success()
                       # else:
                       #     response.failure(...)
                       pass
                   except json.JSONDecodeError:
                       response.failure("Malformed JSON response")
               else:
                   response.failure(f"HTTP error: {response.status_code}")
   ```

3. **Execute the load test:**
   ```shell
   locust -f locustfile.py
   ```
   Open `http://localhost:8089` to start the test and observe your agent response latency and success rate under load.

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
