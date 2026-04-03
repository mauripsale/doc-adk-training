---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 30: Interacting with a Custom Voice Client Challenge

## Goal

In this lab, you will run an ADK agent as a backend API server and interact with it using a custom, standalone HTML/JavaScript client. This will demonstrate how to build your own user-facing applications on top of the ADK's streaming capabilities.

### Step 1: Prepare the Streaming Agent

We will use the same streaming agent configuration from Module 22.

1.  **Create the project directory and agent:**
    ```shell
    mkdir custom_streaming_app
    cd custom_streaming_app
    adk create --type=config streaming_agent
    ```

2.  **Configure the agent:**
    *   Navigate into `streaming_agent`.
    *   Configure the `.env` file for **Vertex AI**.
    *   Replace the contents of `root_agent.yaml` with:
        ```yaml
        name: streaming_conversational_agent
        model="gemini-2.5-flash",
        instruction: |
          You are a friendly and talkative assistant. Keep your answers concise.
        streaming: True
        ```

### Step 2: Create the Custom HTML/JavaScript Client

**Exercise:** Navigate back to the `custom_streaming_app` directory. Create an `index.html` file. A skeleton is provided below. Your task is to complete the JavaScript logic for the `startStreaming` function based on the `# TODO` comments.

```html
<!-- In index.html (Starter Code) -->
<!DOCTYPE html>
<html>
<head>
    <title>ADK Custom Streaming Client</title>
    <style>
        body { font-family: sans-serif; display: flex; flex-direction: column; align-items: center; }
        #transcript { width: 500px; height: 300px; border: 1px solid #ccc; padding: 10px; overflow-y: scroll; }
        button { margin: 10px; padding: 10px; font-size: 16px; }
    </style>
</head>
<body>
    <h1>ADK Custom Streaming Client</h1>
    <button id="streamButton">Start Streaming</button>
    <div id="transcript"></div>

    <script>
        const streamButton = document.getElementById('streamButton');
        const statusDiv = document.getElementById('status');
        const transcriptDiv = document.getElementById('transcript');

        let websocket;
        let audioContext;
        let mediaStream;
        let mediaRecorder;
        let isStreaming = false;

        streamButton.onclick = () => {
            if (!isStreaming) {
                startStreaming();
            } else {
                stopStreaming();
            }
        };

        function log(message) {
            const p = document.createElement('p');
            p.textContent = message;
            transcriptDiv.appendChild(p);
            transcriptDiv.scrollTop = transcriptDiv.scrollHeight;
        }

        async function startStreaming() {
            try {
                // 1. Get microphone access
                mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                
                // 2. Establish WebSocket connection
                const sessionId = Math.random().toString(36).substring(7);
                const wsUrl = `ws://localhost:8000/live/${sessionId}?is_audio=true`;
                websocket = new WebSocket(wsUrl);

                websocket.onopen = () => {
                    isStreaming = true;
                    streamButton.textContent = 'Stop Streaming';
                    statusDiv.textContent = 'Status: Connected';
                    log('[CLIENT]: WebSocket connection opened.');

                    // 3. Start recording and sending audio
                    mediaRecorder = new MediaRecorder(mediaStream, { mimeType: 'audio/webm;codecs=opus' });
                    mediaRecorder.ondataavailable = (event) => {
                        if (event.data.size > 0 && websocket.readyState === WebSocket.OPEN) {
                            websocket.send(event.data);
                        }
                    };
                    mediaRecorder.start(100); // Send data every 100ms
                };

                websocket.onmessage = (event) => {
                    // 4. Handle incoming messages (agent's response)
                    const data = JSON.parse(event.data);
                    if (data.mime_type === 'text/plain') {
                        log(`[AGENT]: ${data.data}`);
                    }
                    // A production client would also handle 'audio/mp3' mime_type for playback.
                };

                websocket.onclose = () => {
                    log('[CLIENT]: WebSocket connection closed.');
                    stopStreaming();
                };

                websocket.onerror = (error) => {
                    log(`[CLIENT]: WebSocket Error: ${JSON.stringify(error)}`);
                    stopStreaming();
                };

            } catch (error) {
                log(`[CLIENT]: Error starting stream: ${error}`);
            }
        }

        function stopStreaming() {
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
            }
            if (mediaStream) {
                mediaStream.getTracks().forEach(track => track.stop());
            }
            if (websocket && websocket.readyState === WebSocket.OPEN) {
                websocket.close();
            }
            isStreaming = false;
            streamButton.textContent = 'Start Streaming';
            statusDiv.textContent = 'Status: Disconnected';
        }
    </script>
</body>
</html>
```

### Step 3: Run the Server and the Client

1.  **Terminal 1 (ADK Server):**
    *   Navigate to the `custom_streaming_app` directory.
    *   Run `adk api_server streaming_agent`.
    ```shell
    cd /path/to/custom_streaming_app
    adk api_server streaming_agent
    ```

2.  **Terminal 2 (Client Web Server):**
    *   Navigate to the `custom_streaming_app` directory (where `index.html` is).
    *   Start a simple Python web server.
    ```shell
    python3 -m http.server 8081
    ```

### Step 4: Test Your Custom Application

1.  **Open the Client:** In your browser, navigate to `http://localhost:8081`.
    *   **Note on Browser Permissions:** Your browser will likely ask for permission to access your microphone. You must grant this for the streaming to work.
2.  **Start Streaming:** Click the "Start Streaming" button.
3.  **Talk to the Agent:** Speak into your microphone and watch the transcript area for the agent's real-time text response.
    *   **Note on Audio Playback:** This client currently only displays the agent's text response. A production client would also handle the `audio/mp3` mime type from the server for voice playback.

### Having Trouble?
If you get stuck, you can find the complete, working `index.html` code in the `lab-solution.md` file.

### Lab Summary
You have successfully built a custom client for a streaming ADK agent. You have learned:
*   How to run an ADK agent as a backend service using `adk api_server`.
*   The basic structure of an HTML/JavaScript client for streaming.
*   How to use the `WebSocket` and Web Audio APIs to create a real-time voice application.

### Self-Reflection Questions
- This lab's client only displays the text from the agent. How would you modify the `websocket.onmessage` handler to also process and play back the `audio/mp3` data that the server sends?
- What are the benefits of using WebSockets for this application compared to the Server-Sent Events (SSE) approach used in the previous UI lab?
- The `MediaRecorder` is configured to send audio data every 100ms. What do you think would be the impact on the user experience if you increased this value to 1000ms (1 second)?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMzAtY3VzdG9tLXN0cmVhbWluZy1jbGllbnQvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module30-custom-streaming-client/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
