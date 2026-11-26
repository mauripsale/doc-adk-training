---
sidebar_position: 3
title: "Lab Solution"
---

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
