---
sidebar_position: 2
title: "Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 29: Building a Simple Custom Chat UI Challenge

## Goal

In this lab, you will build a simple, standalone HTML file with JavaScript that acts as a custom chat client for an ADK agent, demonstrating how to connect a UI to the ADK's native API server.

### Step 1: Create the Agent Project

<Setup/>

1.  **Create and navigate to the agent project:**
    ```shell
    uv run adk create ui_agent
    cd ui_agent
    ```
    `adk create` will prompt you for a model (any option is fine, since you'll replace it in `agent.py` below) and a backend (choose the one matching your environment, e.g. **Vertex AI**).

2.  **Implement the agent:**
    Open `agent.py` and replace its contents with this simple agent:
    ```python
    from google.adk.agents import Agent

    root_agent = Agent(
        model="gemini-3.5-flash",
        name="ui_agent",
        instruction="You are a helpful and friendly assistant.",
    )
    ```

3.  **Set up your `.env` file.**

### Step 2: Create the Custom HTML/JavaScript Client

**Exercise:** Create an `index.html` file. A skeleton is provided below. Your task is to complete the JavaScript logic inside the `submit` event listener to handle the streaming chat.

```html
<!-- In index.html (Starter Code) -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ADK Custom UI</title>
    <style>
        body { font-family: sans-serif; display: flex; flex-direction: column; height: 100vh; margin: 0; }
        #chat-container { flex: 1; overflow-y: auto; padding: 20px; }
        .message { margin-bottom: 15px; padding: 10px; border-radius: 10px; max-width: 80%; }
        .user { background-color: #dcf8c6; align-self: flex-end; }
        .assistant { background-color: #f1f0f0; align-self: flex-start; }
        #input-form { display: flex; padding: 20px; border-top: 1px solid #ccc; }
        input { flex: 1; padding: 10px; border-radius: 5px; }
        button { padding: 10px 20px; margin-left: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <div id="chat-container"></div>
    <form id="input-form">
        <input type="text" id="message-input" placeholder="Type your message..." autocomplete="off">
        <button type="submit">Send</button>
    </form>

    <script>
        const chatContainer = document.getElementById('chat-container');
        const inputForm = document.getElementById('input-form');
        const messageInput = document.getElementById('message-input');
        // This is a simple client-side session ID for the lab.
        // In a real app, you would manage this more robustly.
        const userId = "student-user";
        const sessionId = `session-${Date.now()}`;
        let sessionReady = null;

        // Provided: the `/run_sse` endpoint requires a session that already
        // exists on the server -- it doesn't create one for you. This POSTs
        // to the session-management endpoint once, before the first message.
        function ensureSession() {
            if (!sessionReady) {
                sessionReady = fetch(`http://localhost:8080/apps/ui_agent/users/${userId}/sessions/${sessionId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({})
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

                // TODO: 1. Use the `fetch` API to make a POST request to the
                // ADK's `/run_sse` endpoint (http://localhost:8080/run_sse).
                // Remember to include `user_id` in the body -- it's required,
                // and unlike `app_name`/`session_id` it's easy to forget.
                const response = await fetch('http://localhost:8080/run_sse', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        app_name: "ui_agent",
                        user_id: userId,
                        session_id: sessionId,
                        new_message: {
                            role: "user",
                            parts: [{ "text": query }]
                        }
                    })
                });

                // TODO: 2. Get the `reader` from the response body to process the stream.
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let fullResponse = '';

                // TODO: 3. Write a `while (true)` loop to read chunks from the stream.
                // - Inside the loop, get the `value` and `done` from `reader.read()`.
                // - If `done`, break the loop.
                // - Decode the chunk, split it by newlines, and parse the SSE `data:` lines.
                // - Extract the `text` from the event data and append it to the UI.
                
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

1.  **Terminal 1 (Agent Server):** In the `ui_agent` directory, run `uv run adk api_server --port=8080 --allow_origins=http://localhost:8081`. (Since you're already inside the `ui_agent` directory, `adk api_server` auto-detects it as the agent to serve — don't pass `ui_agent` again as an argument, or it will look for a subdirectory of that name and fail.)
    *   **Note on CORS:** the ADK API server does *not* allow cross-origin requests by default — since your web page (port 8081) and your agent (port 8080) are different origins, you must explicitly allow the client's origin with `--allow_origins`, or the browser will reject every request with a 403.
2.  **Terminal 2 (Client Server):** In the same directory, run `python3 -m http.server 8081`.

### Step 4: Test Your Custom UI

1.  **Open the Client:** In your browser, navigate to `http://localhost:8081`.
2.  **Chat with the Agent:** Send a message and watch the agent's response stream in.

### Having Trouble?
If you get stuck, you can find the complete, working code in the `lab-solution.md` file.

### Lab Summary
You have successfully built a full-stack agent application with a custom front-end. You have learned:
*   How to run an ADK agent as a backend service using `uv run adk api_server`.
*   How to connect a custom JavaScript client to the ADK's native `/run_sse` streaming endpoint.
*   The basic principles of handling streaming responses in a web UI.

### Self-Reflection Questions
- The ADK server sends events using Server-Sent Events (SSE). What are the advantages of SSE for a chat application compared to a traditional request-response model?
- Our simple client generates a new `sessionId` every time the page loads. What problems would this cause in a real application, and how would you solve it (e.g., using cookies or `localStorage`)?
- This lab uses the native ADK API. What are the potential benefits of using a higher-level framework like the AG-UI Protocol and CopilotKit for a more complex, production-ready application?

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="29">

# Lab 29 Solution: Building a Simple Custom Chat UI

## Goal

This file contains the complete code for the `index.html` custom chat client.

### `ui_agent/index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADK Custom UI</title>
    <style>
        body { font-family: sans-serif; display: flex; flex-direction: column; height: 100vh; margin: 0; }
        #chat-container { flex: 1; overflow-y: auto; padding: 20px; }
        .message { margin-bottom: 15px; padding: 10px; border-radius: 10px; max-width: 80%; }
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
        const chatContainer = document.getElementById('chat-container');
        const inputForm = document.getElementById('input-form');
        const messageInput = document.getElementById('message-input');
        const userId = "student-user";
        const sessionId = `session-${Date.now()}`; // Simple session ID for this example
        let sessionReady = null;

        function ensureSession() {
            if (!sessionReady) {
                sessionReady = fetch(`http://localhost:8080/apps/ui_agent/users/${userId}/sessions/${sessionId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({})
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

            const assistantMessageDiv = addMessage('', 'assistant');
            
            try {
                await ensureSession();

                const response = await fetch('http://localhost:8080/run_sse', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        app_name: "ui_agent",
                        user_id: userId,
                        session_id: sessionId,
                        new_message: {
                            role: "user",
                            parts: [{ "text": query }]
                        }
                    })
                });

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let fullResponse = '';

                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;
                    
                    const chunk = decoder.decode(value, { stream: true });
                    // SSE sends data in "data: {...}\n\n" format. We need to parse it.
                    const lines = chunk.split('\n');
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const jsonStr = line.substring(6);
                            if (jsonStr.trim()) {
                                const eventData = JSON.parse(jsonStr);
                                if (eventData.content && eventData.content.parts) {
                                    const textChunk = eventData.content.parts[0].text || '';
                                    fullResponse += textChunk;
                                    assistantMessageDiv.textContent = fullResponse;
                                    chatContainer.scrollTop = chatContainer.scrollHeight;
                                }
                            }
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
    *   **Answer:** SSE offers significant advantages for chat applications primarily because it enables **real-time, low-latency streaming** of data from the server to the client. In a traditional request-response model, the client would have to wait for the entire agent response to be generated before it could display anything, leading to perceived latency. With SSE, the LLM-generated text can be streamed character-by-character or word-by-word as it becomes available, providing a much more responsive and engaging user experience. SSE is also simpler for one-way server-to-client streaming than WebSockets.

2.  **Our simple client generates a new `sessionId` every time the page loads. What problems would this cause in a real application, and how would you solve it (e.g., using cookies or `localStorage`)?**
    *   **Answer:** Generating a new `sessionId` on every page load means the agent loses all conversational memory and state from previous interactions. The agent would treat every page refresh as a brand new conversation, forgetting context, user preferences, or any ongoing tasks. To solve this in a real application, you would persist the `sessionId` on the client-side. Common methods include:
        *   **`localStorage`:** Store the `sessionId` in the browser's `localStorage` (e.g., `localStorage.setItem('sessionId', sessionId)` and retrieve it on subsequent loads).
        *   **Cookies:** Use HTTP cookies to store the `sessionId`, which are automatically sent with each request.
        This ensures the same session is maintained across page reloads, providing a continuous user experience.

3.  **This lab uses the native ADK API. What are the potential benefits of using a higher-level framework like the AG-UI Protocol and CopilotKit for a more complex, production-ready application?**
    *   **Answer:** For complex, production-ready applications, higher-level frameworks like the AG-UI Protocol and CopilotKit offer several benefits:
        *   **Reduced Boilerplate:** They provide pre-built UI components (e.g., `<CopilotChat>`) that automatically handle stream parsing, state management, tool suggestion, and invocation, significantly reducing the amount of custom frontend code needed.
        *   **Standardization:** They enforce a standardized protocol for agent-UI communication, making integrations more robust.
        *   **Advanced Features:** They often include advanced features out-of-the-box, such as visual feedback for tool calls, context management, and support for complex conversational flows.
        *   **Official Support & Ecosystem:** They are often officially supported and come with a growing ecosystem of tools and best practices, making development faster and more reliable.

</SolutionVault>
