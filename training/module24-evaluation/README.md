---
sidebar_position: 24
title: "Module 24: Evaluating Agent Performance"
---

# Module 24: Evaluating Agent Performance

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

### A Deeper Dive into Evaluation

#### The Testing Pyramid

A robust testing strategy for AI agents involves multiple layers, often visualized as a pyramid. This approach, adapted from traditional software engineering, ensures you have a fast and reliable feedback loop.

```text
                    ╔══════════════════════════════════════════════╗
                    ║              EVALUATION TESTS                ║
                    ║ (End-to-End Quality, LLM-in-the-loop)        ║
                    ╚══════════════════════════════════════════════╝
                                       │
                                       │ Slowest, most realistic, checks overall quality
                                       ▼
                    ╔══════════════════════════════════════════════╗
                    ║            INTEGRATION TESTS                 ║
                    ║ (Agent logic, tool orchestration)            ║
                    ╚══════════════════════════════════════════════╝
                                       │
                                       │ Medium speed, validates system interactions
                                       ▼
                    ╔══════════════════════════════════════════════╗
                    ║             UNIT TESTS                       ║
                    ║ (Tool functions, deterministic logic)        ║
                    ╚══════════════════════════════════════════════╝
```

*   **Unit Tests (Base):** These are fast, deterministic tests for the smallest parts of your agent, primarily your custom tool functions. You test them with `pytest` just like any other Python code, mocking any external dependencies. The vast majority of your tests should be here.
*   **Integration Tests (Middle):** These tests verify that the components of your agent work together. For example, does your agent correctly call a sequence of tools? These tests often involve running the agent but mocking the final LLM call to keep them deterministic.
*   **Evaluation Tests (Top):** This is the layer you've been learning about. These are end-to-end tests that involve the real LLM. They are the most realistic but also the slowest and non-deterministic. You use them to validate the overall quality of the agent's reasoning and final responses.

#### Available Evaluation Metrics

The ADK provides a comprehensive set of built-in metrics, categorized by what they assess:

**1. Tool Use Trajectory (Reasoning)**
*   **`tool_trajectory_avg_score`:** Measures the accuracy of the agent's tool call sequence against an expected list. It supports `EXACT`, `IN_ORDER`, or `ANY_ORDER` matching. This is critical for regression testing workflows.
*   **`rubric_based_tool_use_quality_v1`:** Uses an LLM-as-a-judge to evaluate tool usage against a custom rubric (e.g., "Did the agent select the most efficient tool?").

**2. Final Response Quality (Accuracy & Style)**
*   **`response_match_score` (ROUGE):** Measures n-gram overlap. Good for checking if key keywords are present.
*   **`final_response_match_v2`:** Uses an LLM to check for *semantic equivalence*. Allows for different phrasing as long as the meaning is the same as the reference.
*   **`rubric_based_final_response_quality_v1`:** Rates the response against subjective criteria you define (e.g., "politeness", "conciseness") using an LLM judge.

**3. Groundedness and Safety (Compliance)**
*   **`hallucinations_v1`:** Checks if the response contains claims unsupported by the context (tool outputs). Essential for preventing misinformation.
*   **`safety_v1`:** Evaluates the response for harmful content, ensuring compliance with safety guidelines.

### Automating Interaction: User Simulation

Static test cases (like the "Golden Path" above) are excellent for regression testing—ensuring yesterday's features still work today. However, they can't test how your agent handles the unpredictable nature of real users.

For this, the ADK provides **User Simulation**.

*   **Dynamic Prompt Generation:** Instead of hard-coding user questions, you configure a `ConversationScenario`.
*   **Conversation Scenarios:** You define a `starting_prompt` (e.g., "I want to buy a car") and a `conversation_plan` (e.g., "The user is budget-conscious and indecisive").
*   **The Simulator:** An LLM acts as the "User," generating dynamic responses based on your plan and the agent's replies.

This allows you to "stress test" your agent against hundreds of diverse, generated conversations to find edge cases you might have missed manually. Note that for dynamic scenarios, you typically use reference-free metrics like `safety_v1` and `hallucinations_v1` since there is no single "expected" response.

### Key Takeaways
- `LlmAgent`s are non-deterministic, so traditional pass/fail tests are insufficient.
- The ADK evaluation framework measures quality by comparing an agent's behavior against a recorded "golden path" or **Evaluation Case**.
- **Metrics Categories:** Evaluation covers **Trajectory** (did it follow the right steps?), **Response Quality** (is the answer correct/good?), and **Safety/Groundedness** (is it harmless and factual?).
- **User Simulation:** Use dynamic user simulation to test your agent against varied, LLM-generated personas and scenarios, going beyond static examples.
- **Importance of Trajectory Testing:** Testing the `tool_trajectory` is often more critical than just the final response because it validates the agent's underlying reasoning process.
- **CI/CD Integration:** The `adk eval` command can be integrated as a standard test step in CI/CD pipelines to prevent regressions.