---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 30 Solution: Interacting with a Custom Voice Client

## Goal

This file contains the complete, working code for the `index.html` custom client.

### `custom_streaming_app/index.html`

```html
<!DOCTYPE html>
<html>
<head>
    <title>ADK Custom Streaming Client</title>
    <style>
        body { font-family: sans-serif; display: flex; flex-direction: column; align-items: center; }
        #status { margin: 10px; padding: 10px; border: 1px solid #ccc; }
        #transcript { width: 500px; height: 300px; border: 1px solid #ccc; padding: 10px; overflow-y: scroll; background-color: #f9f9f9; }
        p { margin: 5px 0; }
        button { margin: 10px; padding: 10px; font-size: 16px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>ADK Custom Streaming Client</h1>
    <button id="streamButton">Start Streaming</button>
    <div id="status">Status: Disconnected</div>
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

### Troubleshooting

*   **"WebSocket connection to 'ws://localhost:8000/...' failed":**
    *   **Cause:** The ADK `api_server` is not running or is running on a different port.
    *   **Solution:** Make sure you have a terminal window running `uv run adk api_server` in your `streaming_agent` directory.

*   **"NotAllowedError: Permission denied" in browser console:**
    *   **Cause:** You denied the browser's request to access your microphone.
    *   **Solution:** Go into your browser's site settings for `localhost:8081` and change the Microphone permission to "Allow".

*   **Connection opens but agent doesn't respond:**
    *   **Cause:** The agent server may have encountered an error. This is often because the `.env` file is not configured for Vertex AI.
    *   **Solution:** Check the terminal window running `uv run adk api_server` for any error messages. Ensure your `streaming_agent/.env` file is correctly configured with your Agent Platform project details.

### Self-Reflection Answers

1.  **This lab's client only displays the text from the agent. How would you modify the `websocket.onmessage` handler to also process and play back the `audio/mp3` data that the server sends?**
    *   **Answer:** You would extend the `websocket.onmessage` handler to detect messages with an `audio/mp3` `mime_type`. When such a message is received, you would:
        1.  Decode the Base64-encoded audio data (from `event.data.data`) into a binary format.
        2.  Use the Web Audio API (`AudioContext`) to decode this binary audio data into an `AudioBuffer`.
        3.  Create an `AudioBufferSourceNode` from the `AudioBuffer`.
        4.  Connect this source node to the `AudioContext`'s destination (speakers).
        5.  Start playing the audio chunk. This needs to be done continuously for each incoming audio chunk to create a seamless voice experience.

2.  **What are the benefits of using WebSockets for this application compared to the Server-Sent Events (SSE) approach used in the previous UI lab?**
    *   **Answer:** WebSockets are essential for this voice streaming application because they provide a **full-duplex (bidirectional) communication channel**. This is crucial as the client needs to continuously stream microphone audio *to* the server while simultaneously receiving the agent's audio and text responses *from* the server. SSE, on the other hand, is a **unidirectional** protocol (server-to-client only), making it unsuitable for scenarios requiring continuous client input like voice interaction.

3.  **The `MediaRecorder` is configured to send audio data every 100ms. What do you think would be the impact on the user experience if you increased this value to 1000ms (1 second)?**
    *   **Answer:** Increasing the `MediaRecorder` interval to 1000ms (1 second) would dramatically degrade the user experience and introduce significant latency. The user would have to speak for a full second before any of their audio data is sent to the ADK server for processing. This would lead to noticeable and unnatural pauses in the conversation, making the interaction feel sluggish, broken, and far from a real-time conversational experience. It would break the illusion of a continuous voice interaction.
