---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 24 Solution: Creating an Evaluation Case for the Calculator Agent

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

### Extra Challenge: `locustfile.py` Template

This script simulates concurrent users sending prompts to your ADK Agent API server (`uv run adk API_SERVER_ARGS`) to test system latency and endpoint throughput under load.

```python
import json
from locust import HttpUser, task, between

class ADKAgentUser(HttpUser):
    # Wait between 1 and 3 seconds between tasks per user
    wait_time = between(1, 3)

    @task
    def ask_calculator_agent(self):
        # Target the native ADK API Server runner execution endpoint
        headers = {"Content-Type": "application/json"}
        payload = {
            "session_id": "locust-load-test-session",
            "prompt": "What is 15 + 27?"
        }
        
        # We hit the standard synchronous runner execution endpoint
        with self.client.post("/run", json=payload, headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Check if final response text contains expected result
                    if "42" in data.get("response", ""):
                        response.success()
                    else:
                        response.failure(f"Incorrect agent response: {data}")
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
          test:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v3
              - name: Set up Python
                uses: actions/setup-python@v4
                with:
                  python-version: '3.10'
              - name: Install dependencies
                run: | 
                  pip install --upgrade pip
                  pip install "google-adk[eval]"
                  # Install any agent-specific dependencies
              - name: Run agent evaluations
                run: PYTHONPATH=. uv run adk eval . calculator_tests.evalset.json
        ```
        If `uv run adk eval` returns a non-zero exit code (indicating test failures), the CI/CD pipeline step will fail, preventing regressions from being merged or deployed. This provides an automated safety net for agent development.

4.  **What is the difference between "Golden Path" testing and "User Simulation"?**
    *   **Answer:** "Golden Path" testing (Regression Testing) uses *static*, recorded conversations to ensure the agent performs exactly as it did in the past for known inputs. It verifies correctness and prevents breaking changes. "User Simulation" (Stress/Dynamic Testing) uses a generative model to act as a *dynamic* user. It creates varied, unpredictable conversations based on a scenario, helping to find edge cases, safety issues, or robustness failures that static tests might miss.
