---
sidebar_position: 30
title: "Module 30: Building a Custom Streaming Client"
pagination_label: "Module 30: Building Custom Streaming Clients — 📖 Theory & Overview"
---

# Module 30: Building a Custom Streaming Client

## Theory

![Real-time Bidirectional Voice Streaming Client (Light)](img/hero-light.webp#gh-light-mode-only)
![Real-time Bidirectional Voice Streaming Client (Dark)](img/hero-dark.webp#gh-dark-mode-only)
*Figure: Building real-time bidirectional voice streaming clients communicating over WebSockets with the Gemini Live API.*

### Beyond the Dev UI

The ADK Developer UI (`uv run adk web`) has a microphone button built in, giving you bidirectional voice streaming with your agent for free, with no client code of your own. It's a great way to demo an agent, but the Dev UI is a tool for development, not a production-ready application.

To integrate ADK's voice streaming capabilities into your own website or application, you need to build a **custom streaming client**. This involves creating a front-end (for example, using HTML and JavaScript) that communicates directly with the ADK API server over WebSockets using a Gemini Live model (`gemini-3.8-live`).

### The Architecture of a Streaming Application

A custom streaming application consists of two main components that communicate in real-time:

1.  **The ADK Server:** Run headlessly from your parent `adk-training` workspace with `uv run adk api_server`. For real-time bidirectional voice and video, it exposes a **WebSocket** endpoint at `/run_live` (backed by `gemini-3.8-live`).

2.  **The Custom Client:** The user-facing web page (served from a separate static folder so backend `.env` files stay private), responsible for:
    *   Unlocking browser audio playback (`await playbackAudioContext.resume()`) inside the user's click/press gesture so browser autoplay policies never mute the agent's voice.
    *   Creating a session on the server (`POST /apps/{app_name}/users/{user_id}/sessions`) before opening the WebSocket.
    *   Capturing audio from the user's microphone as raw 16kHz PCM samples via an `AudioWorklet`.
    *   Streaming those PCM chunks over the `/run_live` WebSocket and playing the 24kHz PCM audio chunks returned by the server.

> **A note on browser security:** Because the static client (`http://localhost:8081`) and the ADK API server (`http://localhost:8000`) run on different ports, this is a **cross-origin** setup. Start `adk api_server` with `--allow_origins=http://localhost:8081`, or the browser and ADK's origin middleware will reject both the session REST request and the `/run_live` WebSocket handshake.

### WebSockets: The Key to Real-time Communication

Standard HTTP (and SSE) cannot stream continuous microphone audio *upstream* from a browser while simultaneously streaming spoken audio *downstream*. **WebSockets** solve this by establishing a persistent, **full-duplex** (two-way) channel over a single TCP connection, enabling low-latency conversational voice with `gemini-3.8-live`.

### The Data Flow

![Full-Duplex Audio Streaming Pipeline (Light)](img/full-duplex-audio-pipeline-light.webp#gh-light-mode-only)
![Full-Duplex Audio Streaming Pipeline (Dark)](img/full-duplex-audio-pipeline-dark.webp#gh-dark-mode-only)
*Figure: The 5-stage bidirectional streaming loop: microphone capture, WebSocket framing, ADK event dispatch, Gemini Live synthesis, and browser audio playback.*

The interaction between a custom browser client and ADK's `/run_live` endpoint follows five stages:

1.  **Create a Session via REST:** Before connecting, send `POST /apps/{app_name}/users/{user_id}/sessions` with `{"session_id": "..."}`. ADK's `/run_live` handler looks up the session by ID and closes the socket with code `1002 ("Session not found")` if it does not exist yet.
2.  **Await Readiness cleanly (No `setTimeout` Races):** Open `ws://localhost:8000/run_live?app_name={app_name}&user_id={user_id}&session_id={session_id}` (which defaults to `modalities=["AUDIO"]`), await `micAudioContext.audioWorklet.addModule(...)`, and await a `Promise` around the WebSocket `open` event before starting microphone capture.
3.  **Client Streams 16kHz PCM Input:**
    *   Use `navigator.mediaDevices.getUserMedia` + `AudioWorklet` to capture **raw 16-bit little-endian PCM at 16kHz** (not compressed `webm/opus` from `MediaRecorder`).
    *   Base64-encode each chunk and send a `LiveRequest` JSON frame: `{"blob": {"data": "<base64>", "mime_type": "audio/pcm;rate=16000"}}`.
    *   When the user releases push-to-talk, send `{"audio_stream_end": true}` to flush cached server VAD audio.
4.  **Server Streams 24kHz PCM `Event` Responses:**
    *   ADK streams the audio to **`gemini-3.8-live`** over the Gemini Live API and forwards serialized ADK `Event` JSON frames back over the WebSocket.
    *   Spoken audio arrives in `event.content.parts[]` inside `inlineData` (`mimeType` starting with `"audio/"`) as **raw 16-bit PCM at 24kHz** (encoded as RFC 4648 `base64url`).
5.  **Gapless Client Playback:**
    *   Normalize `base64url` (`-`/`_` to `+`/`/`), convert 16-bit PCM samples to `Float32`, copy into a 24kHz `AudioBuffer`, and schedule each `AudioBufferSourceNode` at `Math.max(playbackAudioContext.currentTime, nextPlayTime)` so consecutive chunks play back-to-back without overlap or clicks.

> **A note on audio-first `/run_live` sessions:** By default, ADK's `/run_live` endpoint configures `modalities=["AUDIO"]` for natural, low-latency spoken dialogue with `gemini-3.8-live`. In this lab, our client focuses strictly on capturing 16kHz microphone audio and playing back the 24kHz spoken audio stream.

<KnowledgeCheck
  id="m30-live-api-audio-lifecycle"
  question="When building a browser voice client against ADK's /run_live endpoint with gemini-3.8-live, why must you unlock playbackAudioContext.resume() inside the button click handler and await the WebSocket 'open' event?"
  options={[
    "Modern browsers suspend AudioContexts created or resumed outside a user gesture (muting agent replies), and awaiting WebSocket 'open' + audioWorklet.addModule prevents dropping initial speech or crashing before readiness",
    "WebSockets automatically transcode 16kHz PCM into MP3 only when AudioContext.resume() is called before fetch()",
    "ADK's /run_live endpoint creates the user session automatically only when AudioContext sampleRate equals 48000",
    "Calling setTimeout(500) is required by the WebSocket RFC to negotiate CORS headers"
  ]}
  correctIndex={0}
  hint="Think about Chrome's Web Audio autoplay policy and asynchronous initialization order."
  explanation="Browsers block audio output unless an AudioContext is created or resumed directly inside a user gesture (like mousedown/click). Furthermore, awaiting the REST session creation, audioWorklet.addModule(), and the WebSocket 'open' Promise guarantees the entire pipeline is ready before microphone PCM frames start flowing."
/>

### Key Takeaways
- Build custom voice clients by pairing `uv run adk api_server` (running **`gemini-3.8-live`**) with a browser WebSocket + Web Audio client.
- Always create the session via `POST /apps/{app_name}/users/{user_id}/sessions` first, then open `ws://.../run_live?app_name=...&user_id=...&session_id=...`.
- Unlock `playbackAudioContext.resume()` inside the user's click/press gesture so browser autoplay policies never silence incoming agent audio, and await explicit Promises for `audioWorklet.addModule()` and WebSocket `open` rather than relying on `setTimeout` delays.
- Gemini Live (`gemini-3.8-live`) expects **16kHz 16-bit mono PCM** input (`audio/pcm;rate=16000`) and outputs **24kHz 16-bit mono PCM** audio chunks scheduled sequentially with `nextPlayTime`.
