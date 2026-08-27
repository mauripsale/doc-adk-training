---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 30 Solution: Interacting with a Custom Voice Client

## Goal

This file contains the complete, working code for the custom voice client, talking to the real `/run_live` endpoint with a real Gemini Live API model.

### `custom_streaming_app/audio-processor.js` (provided, unchanged from `lab.md`)

```javascript
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
            const binaryString = atob(base64Data);
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
            await fetch(`${SERVER_URL}/apps/${APP_NAME}/users/${USER_ID}/sessions/${SESSION_ID}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({}),
            });

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

            websocket.onerror = (error) => {
                log(`[CLIENT]: WebSocket Error: ${JSON.stringify(error)}`);
            };
        }

        async function startRecording() {
            if (!isConnected) {
                await connect();
                await new Promise((resolve) => setTimeout(resolve, 500));
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

*   **"Session not found" and the WebSocket closes immediately:**
    *   **Cause:** `/run_live` requires a session that already exists — the `connect()` REST call to create it either failed or was skipped.
    *   **Solution:** Check the Network tab for the `POST .../sessions/...` request; it must return `200` before the WebSocket connects.

*   **The WebSocket connection fails, or the REST call to create a session fails, with a CORS-related error in the browser console:**
    *   **Cause:** The client (`http://localhost:8081`) and the ADK server (`http://localhost:8000`) are different origins, and the server wasn't told to allow the client's origin.
    *   **Solution:** Make sure you started the server with `--allow_origins=http://localhost:8081` (Step 4).

*   **The connection closes with an error like "... is not supported in the live api":**
    *   **Cause:** `root_agent.yaml`'s `model` isn't a Gemini Live API model.
    *   **Solution:** Use `gemini-live-2.5-flash-native-audio` (or another Live API model) — a regular model like `gemini-3.5-flash` doesn't support `/run_live` at all.

*   **"NotAllowedError: Permission denied" in browser console:**
    *   **Cause:** You denied the browser's request to access your microphone.
    *   **Solution:** Go into your browser's site settings for `localhost:8081` and change the Microphone permission to "Allow".

*   **You hear nothing after releasing the button:**
    *   **Cause:** Usually a silent failure in `playAudioChunk` (check the browser console for exceptions), or the agent genuinely had nothing to say back (e.g. it didn't recognize any speech in what was captured).
    *   **Solution:** Check the console for JS errors first. If there are none, try speaking a longer, clearer sentence — very short or quiet input can fail to produce a response at all.

### Self-Reflection Answers

1.  **Your `playAudioChunk` function schedules each chunk at `Math.max(playbackAudioContext.currentTime, nextPlayTime)` instead of just calling `source.start()` immediately. What audio artifact would you expect to hear if you removed `nextPlayTime` tracking and started every chunk immediately?**
    *   **Answer:** Without `nextPlayTime` scheduling, every incoming chunk would call `source.start()` at (roughly) `audioContext.currentTime` — i.e., "play this right now." Since chunks arrive faster than a human can perceive gaps but each chunk still takes real time to play, chunk 2 would start playing while chunk 1 is still going, chunk 3 while 1 and 2 are still going, and so on. The result is many overlapping audio sources talking over each other — a garbled, buzzing mess — rather than a single continuous voice. `nextPlayTime` fixes this by always scheduling the next chunk to start exactly when the previous one ends, turning a pile of overlapping clips into one gapless stream.

2.  **The provided `audio-processor.js` posts a message to the main thread on every audio callback (small chunks, roughly 128 samples — a few milliseconds of audio). What would be the tradeoff of batching several of these callbacks together before sending each WebSocket message, instead of sending one message per callback?**
    *   **Answer:** Sending one WebSocket message per tiny callback means more messages overall, each with its own JSON/framing overhead — more CPU spent on serialization and network stack overhead per byte of actual audio. Batching several callbacks into one larger message reduces that per-message overhead and the number of WebSocket frames sent, which is more network-efficient. The tradeoff is latency: batching means holding audio in a buffer before sending it, so the server (and the user on the other end of a real conversation) hears that audio later than if it had been sent immediately. For a fast, natural-feeling voice interaction, low latency usually wins — which is why sending small chunks frequently, despite the overhead, is the right default for this kind of application.

3.  **What are the benefits of using WebSockets for this application compared to the Server-Sent Events (SSE) approach used in the previous UI lab?**
    *   **Answer:** WebSockets are essential for this voice streaming application because they provide a **full-duplex (bidirectional) communication channel**. This is crucial as the client needs to continuously stream microphone audio *to* the server while simultaneously receiving the agent's audio response *from* the server. SSE, on the other hand, is a **unidirectional** protocol (server-to-client only), making it unsuitable for scenarios requiring continuous client input like voice interaction.
