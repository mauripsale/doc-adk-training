---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 24: Evaluating Agent Performance — 🧪 Challenge Lab"
---

import { ChainSetup } from '../_chain-setup-snippet.mdx';

# Lab 24: Creating an Evaluation Case for the Calculator Agent Challenge

## Goal

In this lab, you will learn the fundamental workflow of the ADK's evaluation feature. You will use the ADK Developer UI to have a "golden path" conversation with the Calculator agent you built in Module 9. Then, you will save that conversation as an evaluation case and re-run it to validate the agent's behavior.

### Step 1: Prepare the Agent

<ChainSetup module={9} project="calculator_agent" />

1.  **Stay in your `adk-training` workspace parent directory** (which contains your `calculator_agent/` package from Module 9):

    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Verify `calculator_agent/.env` is configured** and install the evaluation extra — `adk eval` (Step 8) requires it:
    ```shell
    uv add "google-adk[eval]"
    ```

3.  **Start the web server from the parent directory:**

    Because `calculator_agent/agent.py` uses a clean package-relative import (`from .tools.calculator import ...`), `adk web` discovers `calculator_agent` directly from the parent directory:

    ```shell
    uv run adk web
    ```
    *(Troubleshooting note: if your earlier Module 9 `agent.py` used a non-relative `from tools.calculator import ...`, update it to `from .tools.calculator import ...` so both `adk web` and `adk eval` resolve the package cleanly!)*

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
    *   Behind the scenes, the Dev UI has created a file at `calculator_tests.evalset.json`, directly inside your agent's directory — there is no separate `eval_results/` folder.

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
    *   Click on the "Pass" result to see the details. It will show you that the `tool_trajectory_score` was 1.0 (a perfect match) and the `response_match_score` was also 1.0 for this run.

    > **Note:** LLMs aren't perfectly deterministic. If you re-run this eval later, don't be surprised if `response_match_score` comes back slightly below 1.0 (e.g. the agent says "The sum of 10 and 5 is 15." instead of the recorded "The result of 10 + 5 is 15."). As long as the score stays above the 0.8 threshold, the case still passes — see the Self-Reflection Questions for why this fuzzy matching exists.

### Step 5: Test a Failure (Optional)

Let's see what a failure looks like.

1.  **Temporarily break the agent:**
    *   Stop the `uv run adk web` server (`Ctrl+C`).
    *   Open `calculator_agent/tools/calculator.py`.
    *   In the `add` function, change `MathResult(status="success", result=a + b)` to `MathResult(status="success", result=a + b + 1)`.
    *   Start the server again from `adk-training`: `uv run adk web`.

2.  **Re-run the evaluation:**
    *   Go back to the "Eval" tab.
    *   Select the `addition_test` case again and click "Run Evaluation".
    *   This time, the result should be a **"Fail"**.

3.  **Analyze the failure:**
    *   Click on the "Fail" result.
    *   Hover over the red "Fail" label in the details. A tooltip will appear showing a side-by-side comparison.
    *   You will see that the **Actual Output** ("...result is 16") did not match the **Expected Output** ("...result is 15"), causing the `response_match_score` to be below the threshold.
    *   This demonstrates how evaluations can catch regressions in your agent's logic.

4.  **Don't forget to fix the bug!** Stop the server, change `add` back to `result=a + b`, and restart if needed.

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

When you saved the evaluation case, the ADK created a JSON file at `calculator_tests.evalset.json`, directly inside your agent's directory. Understanding this file is key to creating more complex tests manually.

The structure looks like this (some noisy fields like `thought_signature` and generated ids are trimmed here for readability):

```json
{
  "eval_set_id": "calculator_tests",
  "name": "calculator_tests",
  "eval_cases": [
    {
      "eval_id": "addition_test",
      "conversation": [
        {
          "invocation_id": "e-933e9ee1-7815-4968-8efb-87526500b140",
          "user_content": {
            "parts": [{ "text": "What is 10 + 5?" }],
            "role": "user"
          },
          "final_response": {
            "parts": [{ "text": "The sum of 10 and 5 is 15." }],
            "role": "model"
          },
          "intermediate_data": {
            "invocation_events": [
              {
                "author": "calculator_agent",
                "content": {
                  "parts": [
                    {
                      "function_call": {
                        "id": "adk-a88c727b-cc15-491e-824e-dce2dd58429c",
                        "args": { "a": 10, "b": 5 },
                        "name": "add"
                      }
                    }
                  ],
                  "role": "model"
                }
              },
              {
                "author": "calculator_agent",
                "content": {
                  "parts": [
                    {
                      "function_response": {
                        "id": "adk-a88c727b-cc15-491e-824e-dce2dd58429c",
                        "name": "add",
                        "response": { "result": { "status": "success", "result": 15.0 } }
                      }
                    }
                  ],
                  "role": "user"
                }
              }
            ]
          },
          "creation_timestamp": 1788247633.650866
        }
      ],
      "session_input": {
        "app_name": "calculator_agent",
        "user_id": "u"
      },
      "creation_timestamp": 1788247717.6404831
    }
  ],
  "creation_timestamp": 1788247708.200742
}
```

*   **`eval_set_id`**: The name of the collection of tests.
*   **`eval_cases`**: An array of individual test cases.
*   **`conversation`**: An array of turns in the conversation.
*   **`user_content`**: The user's message for this turn.
*   **`final_response`**: The expected final text from the agent.
*   **`intermediate_data`**: This is where the expected **trajectory** is defined.
    *   **`invocation_events`**: The raw list of ADK events recorded for this turn. A tool call shows up as an event whose `content.parts` contains a `function_call` (the tool name and arguments); the tool's result shows up in the following event as a `function_response`. This is what `tool_trajectory_avg_score` replays and compares against.

### Step 8: Running Evaluations from the Command Line

While the Dev UI is great for creating and running evaluations interactively, you can also run them from the command line. This is essential for integrating your agent tests into an automated CI/CD pipeline.

1.  **Stop the `uv run adk web` server.**
2.  **Verify `calculator_agent/__init__.py` exists** (created automatically by `adk create`, containing `from . import agent`):
    ```shell
    ls calculator_agent/__init__.py
    ```
3.  **Run the `uv run adk eval` command from `adk-training`:**

    ```shell
    uv run adk eval calculator_agent calculator_agent/calculator_tests.evalset.json
    ```
    *   **`uv run adk eval`**: The main CLI evaluation runner.
    *   **`calculator_agent`**: Path to the agent package folder to test.
    *   **`calculator_agent/calculator_tests.evalset.json`**: Path to the evaluation set saved by the Dev UI in Step 3.

4.  **Analyze the Output:**
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

1.  **Create `calculator_agent/custom_metrics.py`:**
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

2.  **Create `calculator_agent/eval_config.json`**. Registering the function under `custom_metrics` is not enough on its own — list both your custom metric and the built-in criteria under `criteria` so they all run together in the same report:
    ```json
    {
      "criteria": {
        "tool_trajectory_avg_score": 1.0,
        "response_match_score": 0.8,
        "check_math_is_correct": 0.5
      },
      "custom_metrics": {
        "check_math_is_correct": {
          "code_config": { "name": "custom_metrics.check_math_is_correct" }
        }
      }
    }
    ```

3.  **Run the evaluation, pointing at your config file** (with `PYTHONPATH=calculator_agent` so ADK resolves `custom_metrics.py`):
    ```shell
    PYTHONPATH=calculator_agent uv run adk eval calculator_agent calculator_agent/calculator_tests.evalset.json --config_file_path calculator_agent/eval_config.json
    ```
    Your custom metric now runs alongside the built-in ones in the same report.

### Bonus: Dynamic User Simulation (Optional)

Static "Golden Path" cases are great for regression testing, but they can't test how your agent handles a real, unpredictable user. **User Simulation** lets an LLM play the user instead, following a `conversation_plan` and an optional persona (`NOVICE`, `EXPERT`, `EVALUATOR`).

1.  **Create `calculator_agent/scenarios.json`**, a `ConversationScenarios` file, instead of a fixed conversation:
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

2.  **Create `calculator_agent/session_input.json`** describing which app/user this simulated conversation belongs to:
    ```json
    { "app_name": "calculator_agent", "user_id": "test_user" }
    ```

3.  **Create a new eval set and add the scenario to it** from `adk-training`:
    ```shell
    uv run adk eval_set create calculator_agent user_sim_tests
    uv run adk eval_set add_eval_case calculator_agent user_sim_tests \
        --scenarios_file calculator_agent/scenarios.json \
        --session_input_file calculator_agent/session_input.json
    ```

4.  **Create `calculator_agent/user_sim_eval_config.json`** pointing at reference-free metrics. Because simulated conversations have no fixed `expected_invocations`, use LLM-judged criteria like `hallucinations_v1` *(if you are authenticated to Google Cloud Vertex AI with `GOOGLE_CLOUD_PROJECT`, you can also add `"safety_v1": 0.8`)*:
    ```json
    {
      "criteria": {
        "hallucinations_v1": 0.8
      }
    }
    ```

5.  **Run the evaluation** from `adk-training` against the new eval set:
    ```shell
    uv run adk eval calculator_agent calculator_agent/user_sim_tests.evalset.json --config_file_path calculator_agent/user_sim_eval_config.json
    ```
    Instead of replaying your exact recorded messages, ADK generates the follow-up turns dynamically, simulating how a hesitant, first-time user might actually phrase things — then the `safety_v1` and `hallucinations_v1` judges score the resulting conversation instead of comparing it against a fixed reference.

### Extra Challenge: Performance Load Testing with Locust (Optional)

In production, evaluations are not just about correctness, but also about **performance and latency**. To test if your asynchronous agent endpoints can scale under concurrent user traffic without blocking the Python event loop, you can use **Locust**.

1. **Install Locust** in your `adk-training` workspace:
   ```shell
   uv add --dev locust
   ```
2. **Create `calculator_agent/locustfile.py`:**
   Use this skeletal template and fill in ADK's native `RunAgentRequest` `/run` contract where marked with `TODO`:

   ```python
   import json
   import uuid
   from locust import HttpUser, task, between

   class ADKAgentUser(HttpUser):
       wait_time = between(1, 3)

       def on_start(self):
           self.user_id = f"locust_{uuid.uuid4().hex[:8]}"
           self.session_id = f"sess_{uuid.uuid4().hex[:8]}"
           # Create the session on the ADK API server before sending /run turns
           self.client.post(
               f"/apps/calculator_agent/users/{self.user_id}/sessions/{self.session_id}",
               json={},
           )

       @task
       def ask_calculator_agent(self):
           headers = {"Content-Type": "application/json"}

           # TODO: Build the RunAgentRequest payload with app_name, user_id,
           # session_id, and new_message={"role": "user", "parts": [{"text": "What is 15 + 27?"}]}
           payload = {}

           # TODO: POST to "/run" and verify the returned JSON list of Event dicts contains "42"
           with self.client.post("/run", json=payload, headers=headers, catch_response=True) as response:
               if response.status_code == 200:
                   try:
                       events = response.json()
                       # TODO: Inspect events (list[dict]) for the final text containing "42"
                       pass
                   except json.JSONDecodeError:
                       response.failure("Malformed JSON response")
               else:
                   response.failure(f"HTTP error: {response.status_code}")
   ```

3. **Start the ADK API server in Terminal 1, then execute Locust in Terminal 2** (both from `adk-training`):
   ```shell
   # Terminal 1:
   uv run adk api_server

   # Terminal 2:
   uv run locust -f calculator_agent/locustfile.py --host http://127.0.0.1:8000
   ```
   Open `http://localhost:8089` to start the load test and observe latency and throughput.

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

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="24">

## Lab 24 Solution: Creating an Evaluation Case for the Calculator Agent

## Goal

This file contains the expected output for the `calculator_tests.evalset.json` file that is generated during the lab, directly inside the `calculator_agent` directory (not in a separate `eval_results/` folder). This demonstrates the structure of a "golden path" test case that can be used for automated regression testing.

### `calculator_tests.evalset.json`

```json
{
  "eval_set_id": "calculator_tests",
  "name": "calculator_tests",
  "eval_cases": [
    {
      "eval_id": "addition_test",
      "conversation": [
        {
          "invocation_id": "e-933e9ee1-7815-4968-8efb-87526500b140",
          "user_content": {
            "parts": [
              {
                "text": "What is 10 + 5?"
              }
            ],
            "role": "user"
          },
          "final_response": {
            "parts": [
              {
                "text": "The sum of 10 and 5 is 15."
              }
            ],
            "role": "model"
          },
          "intermediate_data": {
            "invocation_events": [
              {
                "author": "calculator_agent",
                "content": {
                  "parts": [
                    {
                      "function_call": {
                        "id": "adk-a88c727b-cc15-491e-824e-dce2dd58429c",
                        "args": {
                          "a": 10,
                          "b": 5
                        },
                        "name": "add"
                      }
                    }
                  ],
                  "role": "model"
                }
              },
              {
                "author": "calculator_agent",
                "content": {
                  "parts": [
                    {
                      "function_response": {
                        "id": "adk-a88c727b-cc15-491e-824e-dce2dd58429c",
                        "name": "add",
                        "response": {
                          "result": {
                            "status": "success",
                            "result": 15.0
                          }
                        }
                      }
                    }
                  ],
                  "role": "user"
                }
              }
            ]
          },
          "creation_timestamp": 1788247633.650866
        }
      ],
      "session_input": {
        "app_name": "calculator_agent",
        "user_id": "u"
      },
      "creation_timestamp": 1788247717.6404831
    }
  ],
  "creation_timestamp": 1788247708.200742
}
```

(Some noisy fields, such as `thought_signature`, are trimmed here for readability — the real file includes them.)

### Extra Challenge: `calculator_agent/locustfile.py`

This script simulates concurrent users sending prompts to your ADK API server (`uv run adk api_server`) to test system latency and endpoint throughput under load.

```python
import json
import uuid
from locust import HttpUser, task, between


class ADKAgentUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.user_id = f"locust_{uuid.uuid4().hex[:8]}"
        self.session_id = f"sess_{uuid.uuid4().hex[:8]}"
        self.client.post(
            f"/apps/calculator_agent/users/{self.user_id}/sessions/{self.session_id}",
            json={},
        )

    @task
    def ask_calculator_agent(self):
        headers = {"Content-Type": "application/json"}
        payload = {
            "app_name": "calculator_agent",
            "user_id": self.user_id,
            "session_id": self.session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": "What is 15 + 27?"}],
            },
        }

        with self.client.post("/run", json=payload, headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                try:
                    events = response.json()
                    full_text = " ".join(
                        part.get("text", "")
                        for ev in events
                        for part in (ev.get("content") or {}).get("parts", [])
                    )
                    if "42" in full_text:
                        response.success()
                    else:
                        response.failure(f"Expected '42' in agent events, got: {full_text}")
                except json.JSONDecodeError:
                    response.failure("Malformed JSON response from agent server")
            else:
                response.failure(f"HTTP error: {response.status_code}")
```

### Self-Reflection Answers

1.  **Why is testing the `tool_trajectory` often more important for ensuring an agent's correctness than just testing its final text response?**
    *   **Answer:** Testing the `tool_trajectory` is crucial because it validates the agent's underlying *reasoning process*. An LLM might coincidentally produce a correct final answer even if it used the wrong tools or called them in an incorrect order. Trajectory testing ensures that the agent follows the intended workflow, using the right tools with the correct arguments. This is vital for predictability, reliability, and preventing unexpected failures or inefficient resource usage in complex scenarios.

2.  **The `response_match_score` is not a simple "equals" check. Why is this fuzzy matching necessary for evaluating LLM-generated text?**
    *   **Answer:** LLMs are non-deterministic. For the same input, they can produce semantically identical but syntactically different responses (e.g., "The weather is sunny" vs. "It's a sunny day"). A simple exact-match `equals` check would fail these valid variations. Fuzzy matching (like ROUGE scores) measures the overlap of n-grams or semantic similarity, allowing tests to pass if the key information and meaning are conveyed, even if the exact wording differs from the reference. This makes evaluation more robust and less prone to false negatives.

3.  **How could you integrate the `uv run adk eval` command into a CI/CD pipeline (like GitHub Actions) to automatically test your agent every time you push new code?**
    *   **Answer:** You would add a step to your CI/CD workflow (e.g., a `.github/workflows/main.yml` file for GitHub Actions). After checking out your code and installing dependencies, you would run the `uv run adk eval` command. For example:

        ```yaml
        jobs:
          eval:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v4
              - uses: astral-sh/setup-uv@v5
              - name: Install dependencies
                run: uv sync --extra eval
              - name: Run agent evaluations
                env:
                  GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
                run: uv run adk eval calculator_agent calculator_agent/calculator_tests.evalset.json
        ```
        If `uv run adk eval` returns a non-zero exit code (indicating test failures), the CI/CD pipeline step fails, preventing regressions from being merged or deployed.

        > **Enterprise AgentOps Tip:** In automated pipelines using the Google Agents CLI suite, you can run `uvx google-agents-cli eval run` to benchmark multiple golden datasets and enforce trajectory quality gates directly before cloud deployments (requires an `agents-cli-manifest.yaml` generated via `uvx google-agents-cli scaffold enhance .`).

4.  **What is the difference between "Golden Path" testing and "User Simulation"?**
    *   **Answer:** "Golden Path" testing (Regression Testing) uses *static*, recorded conversations to ensure the agent performs exactly as it did in the past for known inputs. It verifies correctness and prevents breaking changes. "User Simulation" (Stress/Dynamic Testing) uses a generative model to act as a *dynamic* user. It creates varied, unpredictable conversations based on a scenario, helping to find edge cases, safety issues, or robustness failures that static tests might miss.

</SolutionVault>
