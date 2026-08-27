---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 30: Interacting with a Custom Voice Client Challenge

## Goal

In this lab, you will run an ADK agent as a backend API server and interact with it using a custom, standalone HTML/JavaScript client, talking to the real `/run_live` WebSocket endpoint with a real Gemini Live API model. This will demonstrate how to build your own voice-enabled applications on top of the ADK's streaming capabilities.

### Step 1: Prepare the Streaming Agent

1.  **Create the project directory and agent:**
    ```shell
    mkdir custom_streaming_app
    cd custom_streaming_app
    uv run adk create --type=config streaming_agent
    ```

2.  **Configure the agent:**
    *   Navigate into `streaming_agent`.
    *   Configure the `.env` file for **Agent Platform** (Vertex AI).
    *   Replace the contents of `root_agent.yaml` with:
        ```yaml
        name: streaming_conversational_agent
        model: gemini-live-2.5-flash-native-audio
        instruction: |
          You are a friendly and talkative assistant. Keep your answers concise.
        ```
    *   **Important:** the model must be one of the Gemini **Live API** models — a regular model like `gemini-3.5-flash` will fail to connect on `/run_live`. This particular model is a *native-audio* model: it only supports **audio** output, not text. That's by design for this lab — see the README for why.

### Step 2: Add the Provided Audio Worklet

The microphone needs to be resampled to the 16kHz raw PCM format the Live API expects. This is signal-processing boilerplate, not the point of this lesson, so it's provided for you.

Create `audio-processor.js` inside `custom_streaming_app` (next to where `index.html` will go):

```javascript
// custom_streaming_app/audio-processor.js (provided)
class AudioProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.targetSampleRate = 16000;  // Live API expects 16 kHz PCM input
        this.originalSampleRate = sampleRate; // Browser's sample rate
        this.resampleRatio = this.originalSampleRate / this.targetSampleRate;
    }

    process(inputs, outputs, parameters) {
        const input = inputs[0];
        if (input.length > 0) {
            let audioData = input[0]; // Get first channel's data

            if (this.resampleRatio !== 1) {
                audioData = this.resample(audioData);
            }

            this.port.postMessage(audioData);
        }
        return true; // Keep processor alive
    }

    resample(audioData) {
        const newLength = Math.round(audioData.length / this.resampleRatio);
        const resampled = new Float32Array(newLength);

        const lastIndex = audioData.length - 1;
        for (let i = 0; i < newLength; i++) {
            const srcPos = i * this.resampleRatio;
            const srcIndex = Math.floor(srcPos);
            const nextIndex = Math.min(srcIndex + 1, lastIndex);
            const frac = srcPos - srcIndex;
            resampled[i] =
                audioData[srcIndex] * (1 - frac) + audioData[nextIndex] * frac;
        }
        return resampled;
    }
}

registerProcessor('audio-processor', AudioProcessor);
```

### Step 3: Create the Custom HTML/JavaScript Client

**Exercise:** Navigate back to the `custom_streaming_app` directory. Create an `index.html` file. A skeleton is provided below. Your task is to complete the five `// TODO` sections.

This client uses **push-to-talk**: hold the button to record and stream your voice, release it to signal the end of your turn.

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
    <button id="talkButton">🎤 Hold to Talk</button>
    <div id="status">Status: Disconnected</div>
    <div id="transcript"></div>

    <script>
        const APP_NAME = 'streaming_agent';
        const USER_ID = 'user_' + Math.random().toString(36).substring(7);
        const SESSION_ID = 'session_' + Math.random().toString(36).substring(7);
        const SERVER_URL = 'http://localhost:8000';

        const talkButton = document.getElementById('talkButton');
        const statusDiv = document.getElementById('status');
        const transcriptDiv = document.getElementById('transcript');

        let websocket;
        let micAudioContext;
        let workletNode;
        let mediaStream;
        let playbackAudioContext;
        let nextPlayTime = 0; // Tracks the playback queue so chunks play back-to-back
        let isConnected = false;
        let isRecording = false;

        function log(message) {
            const p = document.createElement('p');
            p.textContent = message;
            transcriptDiv.appendChild(p);
            transcriptDiv.scrollTop = transcriptDiv.scrollHeight;
        }

        // Provided: converts a Float32Array of mic samples (-1..1) into a
        // Base64-encoded buffer of 16-bit little-endian PCM samples.
        function float32ToBase64PCM(float32Array) {
            const int16 = new Int16Array(float32Array.length);
            for (let i = 0; i < float32Array.length; i++) {
                const s = Math.max(-1, Math.min(1, float32Array[i]));
                int16[i] = s < 0 ? s * 32768 : s * 32767;
            }
            const bytes = new Uint8Array(int16.buffer);
            let binary = '';
            for (let i = 0; i < bytes.length; i++) {
                binary += String.fromCharCode(bytes[i]);
            }
            return btoa(binary);
        }

        // TODO: 1. Implement audio playback.
        // Given a Base64-encoded chunk of raw 16-bit PCM audio (mono, 24kHz —
        // the Live API's OUTPUT sample rate, different from the 16kHz used
        // for your microphone input), this function should:
        //   a. Lazily create `playbackAudioContext` at sampleRate 24000.
        //   b. Decode the Base64 string into bytes (atob + a byte array).
        //   c. Convert those bytes, two at a time, from 16-bit little-endian
        //      signed integers into normalized Float32 samples (divide by
        //      32768). This is DIFFERENT from decoding an audio file format
        //      like mp3/wav — there's no header, just raw samples, so you
        //      can't use audioContext.decodeAudioData() here.
        //   d. Use playbackAudioContext.createBuffer(1, sampleCount, 24000)
        //      and buffer.copyToChannel(floatSamples, 0) to build an
        //      AudioBuffer from your Float32Array.
        //   e. Create an AudioBufferSourceNode, connect it to
        //      playbackAudioContext.destination, and schedule it at
        //      Math.max(playbackAudioContext.currentTime, nextPlayTime) —
        //      then advance nextPlayTime by the buffer's duration, so
        //      consecutive chunks play back-to-back without gaps.
        function playAudioChunk(base64Data) {
            // Your implementation here
        }

        async function connect() {
            // TODO: 2. Create the session before opening the WebSocket.
            // The /run_live endpoint requires a session that already exists.
            // Send a POST request (with an empty JSON body) to:
            //   `${SERVER_URL}/apps/${APP_NAME}/users/${USER_ID}/sessions/${SESSION_ID}`
            // and await the response before proceeding to open the WebSocket.

            const wsUrl = `ws://localhost:8000/run_live?app_name=${APP_NAME}&user_id=${USER_ID}&session_id=${SESSION_ID}`;
            websocket = new WebSocket(wsUrl);

            websocket.onopen = async () => {
                isConnected = true;
                statusDiv.textContent = 'Status: Connected';
                log('[CLIENT]: WebSocket connection opened.');

                micAudioContext = new (window.AudioContext || window.webkitAudioContext)();
                await micAudioContext.audioWorklet.addModule('audio-processor.js');
            };

            websocket.onmessage = (event) => {
                // TODO: 3. Parse the incoming event and handle its parts.
                // The server sends a full ADK Event as JSON (not a simple
                // {mime_type, data} message). The response audio lives at:
                //   JSON.parse(event.data).content.parts[]
                // Find any part whose `.inlineData.mimeType` starts with
                // "audio/", and call playAudioChunk(part.inlineData.data)
                // for each one.
            };

            websocket.onclose = () => {
                log('[CLIENT]: WebSocket connection closed.');
                isConnected = false;
                statusDiv.textContent = 'Status: Disconnected';
            };

            websocket.onerror = (error) => {
                log(`[CLIENT]: WebSocket Error: ${JSON.stringify(error)}`);
            };
        }

        async function startRecording() {
            if (!isConnected) {
                await connect();
                // Give the connection a moment to establish before recording.
                await new Promise((resolve) => setTimeout(resolve, 500));
            }

            mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const source = micAudioContext.createMediaStreamSource(mediaStream);
            workletNode = new AudioWorkletNode(micAudioContext, 'audio-processor');

            // TODO: 4. Send each captured audio chunk to the server.
            // The worklet posts a Float32Array of mic samples to
            // workletNode.port.onmessage every time it has enough audio.
            // On each message:
            //   a. Convert it to Base64 PCM using float32ToBase64PCM().
            //   b. Send a JSON message over the WebSocket shaped like:
            //      { blob: { data: <base64>, mime_type: "audio/pcm;rate=16000" } }
            workletNode.port.onmessage = (event) => {
                // Your implementation here
            };

            source.connect(workletNode);
            isRecording = true;
            talkButton.textContent = '🔴 Recording... (release to send)';
            log('[CLIENT]: Recording started.');
        }

        function stopRecording() {
            if (!isRecording) return;
            isRecording = false;
            talkButton.textContent = '🎤 Hold to Talk';

            if (workletNode) {
                workletNode.disconnect();
            }
            if (mediaStream) {
                mediaStream.getTracks().forEach((track) => track.stop());
            }

            // TODO: 5. Signal the end of the user's turn.
            // Send { audio_stream_end: true } over the WebSocket so the
            // server knows to stop waiting for more audio and respond.

            log('[CLIENT]: Recording stopped, waiting for response...');
        }

        talkButton.addEventListener('mousedown', startRecording);
        talkButton.addEventListener('mouseup', stopRecording);
        talkButton.addEventListener('mouseleave', () => {
            if (isRecording) stopRecording();
        });
    </script>
</body>
</html>
```

### Step 4: Run the Server and the Client

1.  **Terminal 1 (ADK Server):**
    *   Navigate to the `custom_streaming_app` directory.
    *   Run the server, allowing cross-origin requests from the client's port:
    ```shell
    cd /path/to/custom_streaming_app
    uv run adk api_server streaming_agent --allow_origins=http://localhost:8081
    ```

2.  **Terminal 2 (Client Web Server):**
    *   Navigate to the `custom_streaming_app` directory (where `index.html` and `audio-processor.js` live).
    *   Start a simple Python web server:
    ```shell
    python3 -m http.server 8081
    ```

### Step 5: Test Your Custom Application

1.  **Open the Client:** In your browser, navigate to `http://localhost:8081`.
    *   **Note on Browser Permissions:** Your browser will ask for permission to access your microphone. You must grant this for streaming to work.
2.  **Talk to the Agent:** Press and hold the button, speak a short sentence, then release the button.
3.  **Listen for the Response:** If your TODOs are implemented correctly, you should hear the agent's spoken reply play back automatically a few seconds after you release the button. This model only responds with audio — there's no text transcript to read (see the README for why).

### Having Trouble?
If you get stuck, you can find the complete, working `index.html` code in the `lab-solution.md` file.

### Lab Summary
You have successfully built a custom voice client for a streaming ADK agent. You have learned:
*   How to run an ADK agent as a backend service using `uv run adk api_server`, and why cross-origin requests need `--allow_origins`.
*   Why `/run_live` requires a session to be created via REST before you can connect to it.
*   How to capture raw 16kHz PCM audio from the microphone using an `AudioWorklet`, and send it to the server as correctly-shaped WebSocket messages.
*   How to parse ADK `Event` JSON to find audio response parts, and how to schedule decoded PCM buffers for gapless playback.

### Self-Reflection Questions
- Your `playAudioChunk` function schedules each chunk at `Math.max(playbackAudioContext.currentTime, nextPlayTime)` instead of just calling `source.start()` immediately. What audio artifact would you expect to hear if you removed `nextPlayTime` tracking and started every chunk immediately?
- The provided `audio-processor.js` posts a message to the main thread on every audio callback (small chunks, roughly 128 samples — a few milliseconds of audio). What would be the tradeoff of batching several of these callbacks together before sending each WebSocket message, instead of sending one message per callback?
- What are the benefits of using WebSockets for this application compared to the Server-Sent Events (SSE) approach used in the previous UI lab?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMzAtY3VzdG9tLXN0cmVhbWluZy1jbGllbnQvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module30-custom-streaming-client/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
