# Module 26: Building a Custom Streaming Client

## Lab 26: Interacting with a Custom Voice Client

### Goal

In this lab, you will run an ADK agent as a backend API server and interact with it using a custom, standalone HTML/JavaScript client. This will demonstrate how to build your own user-facing applications on top of the ADK's powerful streaming capabilities, completely independent of the `adk web` Dev UI.

### Step 1: Prepare the Streaming Agent

We will use the same streaming agent configuration from Module 16.

1.  **Create the project directory:**

    ```shell
    cd /path/to/your/adk-training
    mkdir custom-streaming-app
    cd custom-streaming-app
    ```

2.  **Create the agent project:**

    ```shell
    adk create --type=config streaming_agent
    ```

3.  **Configure the agent:**
    *   Navigate into the `streaming_agent` directory.
    *   Configure the `.env` file for **Vertex AI**, as streaming requires it.
    *   Replace the contents of `root_agent.yaml` with the following:
        ```yaml
        name: streaming_conversational_agent
        model: gemini-1.5-flash
        description: A conversational agent that can chat in real-time.
        instruction: |
          You are a friendly and talkative assistant. Keep your answers concise.
        streaming: True
        ```

### Step 2: Create the Custom HTML/JavaScript Client

This single HTML file contains all the logic to capture microphone audio, communicate with the ADK server via WebSockets, and play back the agent's audio response.

1.  **Navigate back to the root of your project:**
    Go back to the `custom-streaming-app` directory.

2.  **Create an `index.html` file:**
    Create the file and paste the following code into it. This code is a simplified but functional implementation of a streaming client.

    ```html
    <!DOCTYPE html>
    <html>
    <head>
        <title>ADK Custom Streaming Client</title>
        <style>
            body { font-family: sans-serif; display: flex; flex-direction: column; align-items: center; }
            #status { margin: 10px; padding: 10px; border: 1px solid #ccc; }
            #transcript { width: 500px; height: 300px; border: 1px solid #ccc; padding: 10px; overflow-y: scroll; }
            button { margin: 10px; padding: 10px; font-size: 16px; }
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
                        // A production client would handle audio playback here
                    };

                    websocket.onclose = () => {
                        log('[CLIENT]: WebSocket connection closed.');
                        stopStreaming();
                    };

                    websocket.onerror = (error) => {
                        log(`[CLIENT]: WebSocket Error: ${error}`);
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

This requires two separate terminal windows.

1.  **Terminal 1: Start the ADK Agent Server**
    *   Navigate to the `streaming_agent` directory.
    *   Run the `adk api_server` command. This starts the agent as a headless server, ready to accept WebSocket connections.

    ```shell
    cd /path/to/your/adk-training/custom-streaming-app/streaming_agent
    adk api_server
    ```

2.  **Terminal 2: Start a Web Server for the Client**
    *   Navigate to the `custom-streaming-app` directory (where your `index.html` is).
    *   We need a simple web server to serve our HTML file. Python has one built-in.

    ```shell
    cd /path/to/your/adk-training/custom-streaming-app
    python3 -m http.server 8081
    ```
    This will serve the files in the current directory on port 8081.

### Step 4: Test Your Custom Application

1.  **Open the Client:**
    In your web browser, navigate to `http://localhost:8081`. You should see the "ADK Custom Streaming Client" page.

2.  **Start Streaming:**
    *   Click the "Start Streaming" button.
    *   Your browser will ask for microphone permission. Click "Allow".
    *   The status should change to "Connected".

3.  **Talk to the Agent:**
    *   Speak into your microphone. For example: "Hello, what can you do?"
    *   Watch the transcript area. You should see the agent's text response appear in real-time.

4.  **Stop Streaming:**
    Click the "Stop Streaming" button to close the connection and release the microphone.

### Lab Summary

You have successfully built and run a custom client for a streaming ADK agent! This is a major step towards building fully custom, voice-enabled web applications.

You have learned:
*   How to run an ADK agent as a backend service using `adk api_server`.
*   The basic structure of an HTML/JavaScript client for streaming.
*   How to use the `WebSocket` API in JavaScript to connect to the ADK server.
*   How to use `navigator.mediaDevices.getUserMedia` to capture microphone audio.
*   The fundamental data flow of a real-time voice application.
