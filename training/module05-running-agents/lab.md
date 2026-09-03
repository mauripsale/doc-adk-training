---
sidebar_position: 2
title: "Challenge Lab"
---

import { ChainSetup } from '../_chain-setup-snippet.mdx';

# Lab 5: Exploring Different Execution Modes Challenge

## Goal
Your task is to run and interact with your **"Support Analyzer"** agent using the three primary execution modes provided by the ADK CLI. **Always run these commands from your main `adk-training` directory.**

<ChainSetup module={4} project="support_analyzer" />

## Lab Tasks
1.  **`uv run adk web`:**
    *   Run the command `uv run adk web`.
    *   **Note:** When running from the parent directory, you don't need to specify the agent name; the Dev UI will allow you to select any agent in the subdirectories.
    *   Interact with your `support_analyzer` in the Dev UI and inspect the "Trace" view to see the full prompt sent to the LLM.
2.  **`uv run adk run`:**
    *   Stop the web server (`Ctrl+C`).
    *   Run the command `uv run adk run support_analyzer`.
    *   Interact with the agent directly in your terminal.
3.  **`uv run adk api_server`:**
    *   Stop the command-line runner.
    *   Run the command `uv run adk api_server`.
    *   Open a **separate terminal window** to act as the client.
    *   **Step A (The Failure):** Try to send a message *without* creating a session first. Copy and run this command:
        ```bash
        curl -X POST http://127.0.0.1:8000/run_sse \
             -H "Content-Type: application/json" \
             -d '{
                   "app_name": "support_analyzer",
                   "user_id": "test_user",
                   "session_id": "missing_session",
                   "new_message": {"role": "user", "parts": [{"text": "Hello"}]}
                 }'
        ```
        Observe the error response. Why did it fail?
    *   **Step B (The Fix):** Create the session explicitly.
        ```bash
        curl -X POST http://127.0.0.1:8000/apps/support_analyzer/users/test_user/sessions/test_session
        ```
    *   **Step C (Success):** Now send the message again, targeting the session you just created (`test_session`).
        ```bash
        curl -X POST http://127.0.0.1:8000/run_sse \
             -H "Content-Type: application/json" \
             -d '{
                   "app_name": "support_analyzer",
                   "user_id": "test_user",
                   "session_id": "test_session",
                   "new_message": {"role": "user", "parts": [{"text": "I am so happy with your service!"}]}
                 }'
        ```
    *   Verify that you receive a stream of JSON responses containing the structured analysis (category, sentiment, summary).

### Self-Reflection Questions
- In what scenarios would the detailed "Trace View" in `uv run adk web` be more useful than the simple chat interface of `uv run adk run`?
- The `curl` command in the `uv run adk api_server` section is a simple example of a programmatic client. What kind of real-world applications could you build that would interact with your agent's API in this way?
- Why is it necessary to run the `uv run adk api_server` and the `curl` command in two separate terminal windows? What does this separation represent in a real-world application architecture?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMDUtcnVubmluZy1hZ2VudHMvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module05-running-agents/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
