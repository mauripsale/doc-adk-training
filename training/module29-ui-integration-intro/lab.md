---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 29: Introduction to UI Integration — 🧪 Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 29: Building a Simple Custom Chat UI Challenge

## Goal

In this lab, you will build a standalone HTML/JavaScript chat frontend that connects to ADK's native FastAPI backend (`uv run adk api_server`), creates sessions via REST, and streams live token-by-token responses over `/run_sse`.

### Step 1: Create the Backend Agent (`ui_agent`)

<Setup/>

1.  **Navigate to your `adk-training` workspace directory and scaffold `ui_agent`:**
    ```shell
    cd /path/to/your/adk-training
    uv run adk create ui_agent
    ```
    `adk create` prompts you for a model and backend (Google AI Studio or Vertex AI) and generates `ui_agent/__init__.py`, `ui_agent/agent.py`, `ui_agent/.env`, and `ui_agent/.gitignore`.

2.  **Implement `ui_agent/agent.py`:**
    Open `ui_agent/agent.py` and replace its contents with:
    ```python
    from google.adk import Agent

    root_agent = Agent(
        model="gemini-3.8-flash",
        name="ui_agent",
        instruction="You are a helpful and friendly assistant.",
    )
    ```

3.  **Verify `ui_agent/.env`:** Confirm your API key (`GOOGLE_API_KEY`) or Vertex AI settings (`GOOGLE_GENAI_USE_ENTERPRISE=1`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`) are configured inside `ui_agent/.env`.

### Step 2: Create the Isolated Frontend Client (`frontend/index.html`)

1.  **Create a separate `frontend/` folder inside `adk-training`:**
    ```shell
    cd /path/to/your/adk-training
    mkdir -p frontend
    ```
    > **Security Best Practice — Never serve static files from inside `ui_agent/`!**
    > Running `python3 -m http.server` inside `ui_agent/` exposes *every* file in that directory over HTTP — including `ui_agent/.env` and your API keys! Keeping static web assets in a separate `frontend/` folder ensures backend secrets are never reachable by a browser.

2.  **Complete `frontend/index.html`:**
    **Exercise:** Create `frontend/index.html` using the starter skeleton below and complete `# TODO: 1`, `# TODO: 2`, and `# TODO: 3` inside the `submit` handler.

    Pay close attention to three real-world SSE streaming details:
    *   **Enable incremental token streaming:** Include `"streaming": true` in the `/run_sse` JSON body (without it, `RunAgentRequest.streaming` defaults to `false` and waits until the entire response finishes!).
    *   **Buffer split TCP chunks:** Network reads can split an SSE `data: {...}\n` line mid-packet. Accumulate decoded text in a `buffer` string, split by `'\n'`, and keep the trailing partial line with `buffer = lines.pop()`.
    *   **Prevent duplicate final messages:** With `"streaming": true`, ADK emits incremental chunks marked `eventData.partial === true` and finishes the turn with one final aggregated `Event` (`!eventData.partial`) containing the entire response text. Only append a non-partial event's text if no partial chunks were already streamed for that step!

```html
<!-- frontend/index.html (Starter Code) -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADK Custom UI</title>
    <style>
        body { font-family: sans-serif; display: flex; flex-direction: column; height: 100vh; margin: 0; }
        #chat-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; }
        .message { margin-bottom: 15px; padding: 10px 14px; border-radius: 10px; max-width: 80%; white-space: pre-wrap; }
        .user { background-color: #dcf8c6; align-self: flex-end; }
        .assistant { background-color: #f1f0f0; align-self: flex-start; }
        #input-form { display: flex; padding: 20px; border-top: 1px solid #ccc; }
        input { flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
        button { padding: 10px 20px; margin-left: 10px; border: none; background-color: #007bff; color: white; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div id="chat-container"></div>
    <form id="input-form">
        <input type="text" id="message-input" placeholder="Type your message..." autocomplete="off">
        <button type="submit">Send</button>
    </form>

    <script>
        const API_BASE_URL = 'http://localhost:8000';
        const APP_NAME = 'ui_agent';
        const chatContainer = document.getElementById('chat-container');
        const inputForm = document.getElementById('input-form');
        const messageInput = document.getElementById('message-input');

        // Simple client-side IDs for this lab (use localStorage in production).
        const userId = 'student-user';
        const sessionId = `session-${Date.now()}`;
        let sessionReady = null;

        // Provided: `/run_sse` requires an existing session on the server.
        // Uses ADK's non-deprecated `POST /apps/{app_name}/users/{user_id}/sessions` route.
        function ensureSession() {
            if (!sessionReady) {
                sessionReady = fetch(`${API_BASE_URL}/apps/${APP_NAME}/users/${userId}/sessions`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: sessionId }),
                }).then((res) => {
                    if (!res.ok) {
                        sessionReady = null;
                        throw new Error(`Session creation failed: ${res.status}`);
                    }
                    return res.json();
                });
            }
            return sessionReady;
        }

        inputForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const query = messageInput.value.trim();
            if (!query) return;

            addMessage(query, 'user');
            messageInput.value = '';
            const assistantMessageDiv = addMessage('...', 'assistant');

            try {
                await ensureSession();

                // TODO: 1. Send a POST request via `fetch` to `${API_BASE_URL}/run_sse`
                // with `Content-Type: application/json` and a JSON body containing:
                // - app_name: APP_NAME
                // - user_id: userId
                // - session_id: sessionId
                // - streaming: true  (REQUIRED so ADK streams tokens incrementally!)
                // - new_message: { role: "user", parts: [{ text: query }] }
                const response = ...;

                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }

                // TODO: 2. Obtain a stream reader (`response.body.getReader()`),
                // a `new TextDecoder()`, and initialize state variables:
                // `let buffer = '';`, `let fullResponse = '';`, and `let hasStreamedPartials = false;`


                // TODO: 3. Write a `while (true)` loop calling `await reader.read()`:
                // - Break when `done` is true.
                // - Append `decoder.decode(value, { stream: true })` to `buffer`,
                //   split `buffer` on `'\n'`, and save the incomplete tail with `buffer = lines.pop()`.
                // - For each line starting with `'data: '`, parse the JSON payload after `'data: '`.
                // - Extract text from non-thought parts (`eventData.content?.parts`).
                // - If `eventData.partial` is truthy: set `hasStreamedPartials = true` and append the text chunk to `fullResponse`.
                // - Else (`!eventData.partial`, the final aggregated event): ONLY append the text if `!hasStreamedPartials`, then reset `hasStreamedPartials = false`.
                // - Update `assistantMessageDiv.textContent = fullResponse` and scroll `chatContainer` to the bottom.

            } catch (error) {
                assistantMessageDiv.textContent = 'Error: Could not connect to the agent.';
                console.error('Error:', error);
            }
        });

        function addMessage(text, role) {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message', role);
            messageDiv.textContent = text;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            return messageDiv;
        }
    </script>
</body>
</html>
```

### Step 3: Run the Full-Stack Application

1.  **Terminal 1 — Start the ADK API Server from the parent `adk-training` directory:**
    ```shell
    cd /path/to/your/adk-training
    uv run adk api_server --allow_origins="*"
    ```
    *   `adk api_server` starts on **`http://127.0.0.1:8000`** by default and discovers `ui_agent` inside `adk-training/`.
    *   **Note on CORS:** Because your frontend (`http://localhost:8081`) and API server (`http://localhost:8000`) run on different ports, browsers enforce Cross-Origin Resource Sharing (CORS). `--allow_origins="*"` is convenient for local development; in production, always lock it down to your exact frontend origin (e.g., `--allow_origins=https://app.example.com`).

2.  **Terminal 2 — Serve the isolated `frontend/` directory on port `8081`:**
    ```shell
    cd /path/to/your/adk-training/frontend
    python3 -m http.server 8081
    ```

### Step 4: Test Your Custom UI

1.  **Open the Client:** Navigate to `http://localhost:8081` in your browser.
2.  **Verify Live Streaming & Memory:**
    *   Ask *"Write a short 4-line poem about distributed systems."* Watch tokens stream into the assistant bubble progressively, and verify the poem appears **once** (not duplicated when the stream closes!).
    *   Follow up with *"Now translate the second line into French."* Because `sessionId` is reused across turns, the agent remembers the poem from Turn 1.

### Having Trouble?
If you get stuck, check `lab-solution.md` or unlock the Reference Solution Vault below.

### Lab Summary
You have built a full-stack custom chat UI backed by ADK's native FastAPI server:
*   Served `ui_agent` headlessly from the parent `adk-training` workspace via `uv run adk api_server --allow_origins="*"`.
*   Isolated static frontend assets in `frontend/` so `.env` credentials are never exposed over HTTP.
*   Created sessions with the non-deprecated `POST /apps/ui_agent/users/{user_id}/sessions` endpoint and streamed incremental tokens via `/run_sse` with `"streaming": true`, line buffering, and `partial` deduplication.

### Self-Reflection Questions
- The ADK server sends events using Server-Sent Events (SSE). What are the advantages of SSE for a chat application compared to a traditional request-response model?
- Our simple client generates a new `sessionId` every time the page loads. What problems would this cause in a real application, and how would you solve it (e.g., using cookies or `localStorage`)?
- This lab uses the native ADK API. What are the potential benefits of using a higher-level framework like the AG-UI Protocol and CopilotKit for a more complex, production-ready application?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="29">

# Lab 29 Solution: Building a Simple Custom Chat UI

## Goal

This file contains the complete reference implementation for `ui_agent/agent.py` and `frontend/index.html`.

### `ui_agent/agent.py`

```python
from google.adk import Agent

root_agent = Agent(
    model="gemini-3.8-flash",
    name="ui_agent",
    instruction="You are a helpful and friendly assistant.",
)
```

### `frontend/index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADK Custom UI</title>
    <style>
        body { font-family: sans-serif; display: flex; flex-direction: column; height: 100vh; margin: 0; }
        #chat-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; }
        .message { margin-bottom: 15px; padding: 10px 14px; border-radius: 10px; max-width: 80%; white-space: pre-wrap; }
        .user { background-color: #dcf8c6; align-self: flex-end; }
        .assistant { background-color: #f1f0f0; align-self: flex-start; }
        #input-form { display: flex; padding: 20px; border-top: 1px solid #ccc; }
        input { flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
        button { padding: 10px 20px; margin-left: 10px; border: none; background-color: #007bff; color: white; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div id="chat-container"></div>
    <form id="input-form">
        <input type="text" id="message-input" placeholder="Type your message..." autocomplete="off">
        <button type="submit">Send</button>
    </form>

    <script>
        const API_BASE_URL = 'http://localhost:8000';
        const APP_NAME = 'ui_agent';
        const chatContainer = document.getElementById('chat-container');
        const inputForm = document.getElementById('input-form');
        const messageInput = document.getElementById('message-input');
        const userId = 'student-user';
        const sessionId = `session-${Date.now()}`;
        let sessionReady = null;

        function ensureSession() {
            if (!sessionReady) {
                sessionReady = fetch(`${API_BASE_URL}/apps/${APP_NAME}/users/${userId}/sessions`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: sessionId }),
                }).then((res) => {
                    if (!res.ok) {
                        sessionReady = null;
                        throw new Error(`Session creation failed: ${res.status}`);
                    }
                    return res.json();
                });
            }
            return sessionReady;
        }

        inputForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const query = messageInput.value.trim();
            if (!query) return;

            addMessage(query, 'user');
            messageInput.value = '';

            const assistantMessageDiv = addMessage('...', 'assistant');

            try {
                await ensureSession();

                const response = await fetch(`${API_BASE_URL}/run_sse`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        app_name: APP_NAME,
                        user_id: userId,
                        session_id: sessionId,
                        streaming: true,
                        new_message: {
                            role: 'user',
                            parts: [{ text: query }],
                        },
                    }),
                });

                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';
                let fullResponse = '';
                let hasStreamedPartials = false;

                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;

                    // Buffer across TCP chunks so split SSE lines never break JSON.parse.
                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n');
                    buffer = lines.pop();

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const jsonStr = line.slice(6).trim();
                            if (!jsonStr) continue;

                            const eventData = JSON.parse(jsonStr);
                            const parts = eventData.content?.parts || [];
                            const textChunk = parts
                                .filter((part) => !part.thought && part.text)
                                .map((part) => part.text)
                                .join('');

                            if (!textChunk) continue;

                            if (eventData.partial) {
                                hasStreamedPartials = true;
                                fullResponse += textChunk;
                            } else {
                                // Final aggregated event: only append if no partial deltas arrived
                                // for this step, preventing duplicate full-response rendering!
                                if (!hasStreamedPartials) {
                                    fullResponse += textChunk;
                                }
                                hasStreamedPartials = false;
                            }

                            assistantMessageDiv.textContent = fullResponse;
                            chatContainer.scrollTop = chatContainer.scrollHeight;
                        }
                    }
                }
            } catch (error) {
                assistantMessageDiv.textContent = 'Error: Could not connect to the agent.';
                console.error('Error:', error);
            }
        });

        function addMessage(text, role) {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message', role);
            messageDiv.textContent = text;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            return messageDiv;
        }
    </script>
</body>
</html>
```

### Self-Reflection Answers

1.  **The ADK server sends events using Server-Sent Events (SSE). What are the advantages of SSE for a chat application compared to a traditional request-response model?**
    *   **Answer:** SSE enables **real-time, low-latency streaming** from server to client over standard HTTP. Instead of staring at a spinner while the entire response generates, users read tokens immediately as they arrive (`partial: true` events). SSE is also lighter-weight than WebSockets when communication during a turn only needs to stream one way from server to client.

2.  **Our simple client generates a new `sessionId` every time the page loads. What problems would this cause in a real application, and how would you solve it (e.g., using cookies or `localStorage`)?**
    *   **Answer:** Generating a fresh `sessionId` on every reload abandons the previous session's history and state. Persisting `sessionId` in `localStorage` (or tying it to an authenticated backend session cookie) allows the client to resume existing conversations seamlessly across refreshes.

3.  **This lab uses the native ADK API. What are the potential benefits of using a higher-level framework like the AG-UI Protocol and CopilotKit for a more complex, production-ready application?**
    *   **Answer:** Higher-level frameworks like AG-UI and CopilotKit eliminate low-level stream buffering, `partial` deduplication, reconnection handling, and state synchronization boilerplate. They provide ready-made React components, rich generative UI tool rendering, and human-in-the-loop approval widgets out of the box.

</SolutionVault>
