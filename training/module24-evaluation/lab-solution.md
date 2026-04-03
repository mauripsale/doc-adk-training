---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 24 Solution: Creating an Evaluation Case for the Calculator Agent

## Goal

This file contains the expected output for the `eval_results/calculator_tests.evalset.json` file that is generated during the lab. This demonstrates the structure of a "golden path" test case that can be used for automated regression testing.

### `eval_results/calculator_tests.evalset.json`

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
            "parts": [
              {
                "text": "What is 10 + 5?"
              }
            ]
          },
          "final_response": {
            "role": "model",
            "parts": [
              {
                "text": "The result of 10 + 5 is 15."
              }
            ]
          },
          "intermediate_data": {
            "tool_uses": [
              {
                "name": "tools.calculator.add",
                "args": {
                  "a": 10,
                  "b": 5
                }
              }
            ],
            "tool_responses": [
              {
                "name": "tools.calculator.add",
                "response": {
                  "status": "success",
                  "result": 15
                }
              }
            ]
          }
        }
      ]
    }
  ]
}
```

### Self-Reflection Answers

1.  **Why is testing the `tool_trajectory` often more important for ensuring an agent's correctness than just testing its final text response?**
    *   **Answer:** Testing the `tool_trajectory` is crucial because it validates the agent's underlying *reasoning process*. An LLM might coincidentally produce a correct final answer even if it used the wrong tools or called them in an incorrect order. Trajectory testing ensures that the agent follows the intended workflow, using the right tools with the correct arguments. This is vital for predictability, reliability, and preventing unexpected failures or inefficient resource usage in complex scenarios.

2.  **The `response_match_score` is not a simple "equals" check. Why is this fuzzy matching necessary for evaluating LLM-generated text?**
    *   **Answer:** LLMs are non-deterministic. For the same input, they can produce semantically identical but syntactically different responses (e.g., "The weather is sunny" vs. "It's a sunny day"). A simple exact-match `equals` check would fail these valid variations. Fuzzy matching (like ROUGE scores) measures the overlap of n-grams or semantic similarity, allowing tests to pass if the key information and meaning are conveyed, even if the exact wording differs from the reference. This makes evaluation more robust and less prone to false negatives.

3.  **How could you integrate the `adk eval` command into a CI/CD pipeline (like GitHub Actions) to automatically test your agent every time you push new code?**
    *   **Answer:** You would add a step to your CI/CD workflow (e.g., a `.github/workflows/main.yml` file for GitHub Actions). After checking out your code and installing dependencies, you would run the `adk eval` command. For example:

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
                  pip install adk-python
                  # Install any agent-specific dependencies
              - name: Run agent evaluations
                run: adk eval . eval_results/calculator_tests.evalset.json
        ```
        If `adk eval` returns a non-zero exit code (indicating test failures), the CI/CD pipeline step will fail, preventing regressions from being merged or deployed. This provides an automated safety net for agent development.

4.  **What is the difference between "Golden Path" testing and "User Simulation"?**
    *   **Answer:** "Golden Path" testing (Regression Testing) uses *static*, recorded conversations to ensure the agent performs exactly as it did in the past for known inputs. It verifies correctness and prevents breaking changes. "User Simulation" (Stress/Dynamic Testing) uses a generative model to act as a *dynamic* user. It creates varied, unpredictable conversations based on a scenario, helping to find edge cases, safety issues, or robustness failures that static tests might miss.
