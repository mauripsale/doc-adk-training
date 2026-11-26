---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 30 Solution: Interacting with a Custom Voice Client

## Goal

This file contains the complete, working configuration and client code for the custom voice client connected to ADK's `/run_live` WebSocket endpoint with **`gemini-3.8-live`**.

### `streaming_agent/root_agent.yaml`

```yaml
name: streaming_conversational_agent
model: gemini-3.8-live
instruction: |
  You are a friendly and talkative assistant. Keep your answers concise.
```

### `streaming_client/audio-processor.js`

```javascript
class AudioProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.targetSampleRate = 16000;  // Live API expects 16 kHz PCM input
        this.originalSampleRate = sampleRate; // Browser's hardware sample rate
        this.resampleRatio = this.originalSampleRate / this.targetSampleRate;
    }

    process(inputs, outputs, parameters) {
        const input = inputs[0];
        if (input.length > 0) {
            let audioData = input[0]; // First mono channel

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

### `streaming_client/index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ADK Custom Streaming Client</title>
    <style>
        body { font-family: sans-serif; display: flex; flex-direction: column; align-items: center; }
        #status { margin: 10px; padding: 10px; border: 1px solid #ccc; }
        #transcript { width: 500px; height: 300px; border: 1px solid #ccc; padding: 10px; overflow-y: scroll; background-color: #f9f9f9; }
        p { margin: 5px 0; }
        button { margin: 10px; padding: 10px 18px; font-size: 16px; cursor: pointer; }
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
        let sessionCreated = false;
        let isConnected = false;
        let isRecording = false;

        function log(message) {
            const p = document.createElement('p');
            p.textContent = message;
            transcriptDiv.appendChild(p);
            transcriptDiv.scrollTop = transcriptDiv.scrollHeight;
        }

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

        function playAudioChunk(base64Data) {
            if (!playbackAudioContext) {
                playbackAudioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 24000 });
            }
            if (playbackAudioContext.state === 'suspended') {
                playbackAudioContext.resume();
            }

            // ADK's /run_live endpoint serializes bytes as RFC 4648 base64url
            // ('-' and '_' instead of '+' and '/'). Normalize before atob().
            const normalizedBase64 = base64Data.replace(/-/g, '+').replace(/_/g, '/');
            const binaryString = atob(normalizedBase64);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }

            const sampleCount = bytes.length / 2;
            const floatSamples = new Float32Array(sampleCount);
            for (let i = 0; i < sampleCount; i++) {
                let sample = bytes[i * 2] | (bytes[i * 2 + 1] << 8);
                if (sample >= 32768) sample -= 65536;
                floatSamples[i] = sample / 32768;
            }

            const audioBuffer = playbackAudioContext.createBuffer(1, sampleCount, 24000);
            audioBuffer.copyToChannel(floatSamples, 0);

            const source = playbackAudioContext.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(playbackAudioContext.destination);

            const startTime = Math.max(playbackAudioContext.currentTime, nextPlayTime);
            source.start(startTime);
            nextPlayTime = startTime + audioBuffer.duration;
        }

        async function connect() {
            if (!sessionCreated) {
                const res = await fetch(`${SERVER_URL}/apps/${APP_NAME}/users/${USER_ID}/sessions`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: SESSION_ID }),
                });
                if (!res.ok && res.status !== 409) {
                    throw new Error(`Session creation failed: ${res.status}`);
                }
                sessionCreated = true;
            }

            if (!micAudioContext) {
                micAudioContext = new (window.AudioContext || window.webkitAudioContext)();
                await micAudioContext.audioWorklet.addModule('audio-processor.js');
            }
            if (micAudioContext.state === 'suspended') {
                await micAudioContext.resume();
            }

            const wsUrl = `ws://localhost:8000/run_live?app_name=${APP_NAME}&user_id=${USER_ID}&session_id=${SESSION_ID}`;
            websocket = new WebSocket(wsUrl);

            websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                const parts = data.content?.parts || [];
                for (const part of parts) {
                    if (part.inlineData?.mimeType?.startsWith('audio/')) {
                        playAudioChunk(part.inlineData.data);
                    }
                }
            };

            websocket.onclose = () => {
                log('[CLIENT]: WebSocket connection closed.');
                isConnected = false;
                statusDiv.textContent = 'Status: Disconnected';
            };

            await new Promise((resolve, reject) => {
                websocket.addEventListener('open', () => {
                    isConnected = true;
                    statusDiv.textContent = 'Status: Connected';
                    log('[CLIENT]: WebSocket connection opened.');
                    resolve();
                }, { once: true });

                websocket.addEventListener('error', () => {
                    log('[CLIENT]: WebSocket handshake error.');
                    reject(new Error('WebSocket connection failed'));
                }, { once: true });
            });
        }

        async function startRecording() {
            try {
                // Resume playbackAudioContext inside the user's mousedown gesture
                // so Chrome's autoplay policy never mutes the agent's spoken reply!
                if (!playbackAudioContext) {
                    playbackAudioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 24000 });
                }
                if (playbackAudioContext.state === 'suspended') {
                    await playbackAudioContext.resume();
                }

                if (!isConnected) {
                    await connect();
                }

                mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                const source = micAudioContext.createMediaStreamSource(mediaStream);
                workletNode = new AudioWorkletNode(micAudioContext, 'audio-processor');

                workletNode.port.onmessage = (event) => {
                    const base64Audio = float32ToBase64PCM(event.data);
                    if (websocket && websocket.readyState === WebSocket.OPEN) {
                        websocket.send(JSON.stringify({
                            blob: { data: base64Audio, mime_type: 'audio/pcm;rate=16000' },
                        }));
                    }
                };

                source.connect(workletNode);
                isRecording = true;
                talkButton.textContent = '🔴 Recording... (release to send)';
                log('[CLIENT]: Recording started.');
            } catch (err) {
                log(`[CLIENT]: Failed to start recording: ${err.message}`);
                console.error(err);
            }
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

            if (websocket && websocket.readyState === WebSocket.OPEN) {
                websocket.send(JSON.stringify({ audio_stream_end: true }));
            }

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

### Troubleshooting

*   **"Session not found" and the WebSocket closes immediately (code `1002`):**
    *   **Cause:** `/run_live` requires a session that already exists — the `POST .../sessions` REST call either failed or was skipped.
    *   **Solution:** Check the browser Network tab for `POST http://localhost:8000/apps/streaming_agent/users/.../sessions` and verify it returns `200 OK` before opening the WebSocket.

*   **CORS or `Origin not allowed` error (`403` / WebSocket close code `1008`):**
    *   **Cause:** The client (`http://localhost:8081`) and ADK API server (`http://localhost:8000`) run on different origins.
    *   **Solution:** Start the server from `adk-training/` with `uv run adk api_server --allow_origins=http://localhost:8081`.

*   **The connection closes with an error like `... is not supported in the live api`:**
    *   **Cause:** `streaming_agent/root_agent.yaml` is not configured with a Gemini Live API model.
    *   **Solution:** Set `model: gemini-3.8-live` in `streaming_agent/root_agent.yaml` — regular non-live models like `gemini-3.8-flash` do not support `/run_live`.

*   **`NotAllowedError: Permission denied` in browser console:**
    *   **Cause:** Microphone access was denied in the browser.
    *   **Solution:** Allow Microphone permission in your browser's site settings for `localhost:8081`.

*   **You hear nothing after releasing the button:**
    *   **Cause:** Either `playbackAudioContext.resume()` was omitted from the click/mousedown handler (leaving Web Audio suspended under Chrome's autoplay policy), an error occurred in `playAudioChunk`, or the spoken input was too brief to detect.
    *   **Solution:** Confirm `await playbackAudioContext.resume()` runs at the start of `startRecording()`, check the DevTools Console for exceptions, and hold the button while speaking a complete sentence.

### Self-Reflection Answers

1.  **Your `playAudioChunk` function schedules each chunk at `Math.max(playbackAudioContext.currentTime, nextPlayTime)` instead of just calling `source.start()` immediately. What audio artifact would you expect to hear if you removed `nextPlayTime` tracking and started every chunk immediately?**
    *   **Answer:** Without `nextPlayTime` scheduling, every incoming chunk calls `source.start()` at roughly `audioContext.currentTime` ("play right now"). Because network chunks arrive much faster than their real-time playback duration, chunk 2 starts playing on top of chunk 1, chunk 3 on top of 1 and 2, producing garbled overlapping voices. Tracking `nextPlayTime` queues each buffer back-to-back into a single seamless voice stream.

2.  **The provided `audio-processor.js` posts a message to the main thread on every audio callback (small chunks, roughly 128 samples — a few milliseconds of audio). What would be the tradeoff of batching several of these callbacks together before sending each WebSocket message, instead of sending one message per callback?**
    *   **Answer:** Batching reduces JSON serialization and WebSocket framing overhead (fewer frames per second), at the cost of buffering latency before the server receives the user's speech. Small, frequent chunks minimize conversational latency, though modest batching (e.g., 20–40ms frames) is a common production sweet spot between frame overhead and responsiveness.

3.  **What are the benefits of using WebSockets for this application compared to the Server-Sent Events (SSE) approach used in the previous UI lab?**
    *   **Answer:** WebSockets provide a persistent **full-duplex (bidirectional)** channel over a single connection, enabling continuous upstream microphone streaming alongside simultaneous downstream agent audio playback (and barge-in interruption) — capabilities that unidirectional server-to-client SSE cannot support.
