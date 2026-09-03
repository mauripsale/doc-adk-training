---
sidebar_position: 30
title: "Module 30: Building a Custom Streaming Client"
---

# Module 30: Building a Custom Streaming Client

## Theory

### Beyond the Dev UI

The ADK Developer UI (`uv run adk web`) has a microphone button built in, giving you bidirectional voice streaming with your agent for free, with no client code of your own. It's a great way to demo an agent, but the Dev UI is a tool for development, not a production-ready application.

To integrate ADK's streaming capabilities into your own website or application, you need to build a **custom streaming client**. This involves creating a front-end (e.g., using HTML and JavaScript) that can communicate directly with the ADK agent server.

### The Architecture of a Streaming Application

A custom streaming application consists of two main components that communicate in real-time:

1.  **The ADK Server:** This is your ADK agent, but instead of being run with `uv run adk web`, it's run as a headless API server using `uv run adk api_server`. This command exposes the agent's functionality over a network protocol. For streaming, it specifically opens a **WebSocket** endpoint at `/run_live`.

2.  **The Custom Client:** This is the user-facing part of the application (e.g., a web page). It's responsible for:
    *   Creating a session on the server (via a plain HTTP request) before connecting.
    *   Capturing audio from the user's microphone as raw PCM samples.
    *   Sending that audio data to the ADK server's WebSocket endpoint.
    *   Receiving audio data back from the server.
    *   Playing the received audio through the user's speakers.

> **A note on browser security:** since the client (a static HTML page) and the ADK server run on different ports, this is a **cross-origin** setup. You'll need to start the server with `--allow_origins` pointing at the client's origin, or the browser will refuse both the WebSocket connection and the session-creation request.

### WebSockets: The Key to Real-time Communication

Standard HTTP is a request-response protocol. The client sends a request, and the server sends a response. This is not suitable for real-time, continuous conversation.

**WebSockets** solve this problem. A WebSocket is a protocol that provides a persistent, **full-duplex** (two-way) communication channel over a single TCP connection. Once a WebSocket connection is established between the client (your browser) and the server (the ADK `api_server`), both sides can send data to each other at any time.

This is the technology that enables the continuous, low-latency flow of audio data required for a natural voice conversation.

### The Data Flow

The interaction between a custom client and the ADK server follows a specific flow:

1.  **Create a session:** Before opening the WebSocket, the client sends a plain HTTP `POST` to `/apps/{app_name}/users/{user_id}/sessions/{session_id}`. The `/run_live` endpoint requires the session to already exist — it looks it up by ID and refuses the connection ("Session not found") if it doesn't.
2.  **Connection:** The JavaScript client opens a WebSocket connection to the ADK server's `/run_live` endpoint, passing `app_name`, `user_id`, and `session_id` as query parameters.
3.  **Client Sends Audio:**
    *   The client uses the browser's Web Audio API (`navigator.mediaDevices.getUserMedia` plus an `AudioWorklet`) to access the microphone and capture **raw 16-bit PCM samples at 16kHz** — this is the format the Live API expects for input, not a compressed codec like the `webm/opus` a `MediaRecorder` would normally produce.
    *   Each chunk is Base64-encoded and sent as a JSON message shaped like `{"blob": {"data": "<base64>", "mime_type": "audio/pcm;rate=16000"}}`.
    *   When the user finishes speaking, the client sends `{"audio_stream_end": true}` to signal the end of that turn.
4.  **Server Processes and Responds:**
    *   The ADK server receives the audio chunks and streams them to the Gemini Live API.
    *   As the model processes the audio and formulates a response, the ADK server sends full ADK `Event` objects back over the same WebSocket, each serialized as JSON.
    *   The agent's spoken response arrives as one or more parts under `event.content.parts[]`, each with an `inlineData` field whose `mimeType` starts with `audio/` — raw 16-bit PCM again, but this time at **24kHz** (the Live API's output sample rate, different from the 16kHz used for input).
5.  **Client Renders Response:**
    *   The client's JavaScript code listens for these incoming messages, finds the `inlineData` audio parts, decodes them, and schedules them for playback through the user's speakers — back-to-back, so consecutive chunks don't overlap or leave gaps.

> **A note on text output:** the Live API's native-audio models (the ones built for natural-sounding speech) only support **audio** output — asking for `TEXT` alongside `AUDIO` on the same connection gets rejected. That's why the client in this lab doesn't attempt to display a live transcript of the agent's reply: what you get back is *spoken audio only*, matching this lab's title.

In the lab for this module, you'll implement the pieces of this flow that are specific to the ADK's actual wire protocol: sending correctly-shaped audio messages, parsing the incoming events, and playing back raw PCM audio. The microphone-capture plumbing (the `AudioWorklet` processor) is provided, since it's signal-processing boilerplate rather than the point of this lesson.

### Key Takeaways
- To build a custom voice-enabled UI, you need a **custom streaming client** (front-end) and an **ADK server** (back-end).
- The ADK server is run with `uv run adk api_server`, which exposes a `/run_live` **WebSocket** endpoint for real-time, bidirectional communication — but only after a session has been created via a REST call.
- Cross-origin setups (client and server on different ports) need `--allow_origins` on the server, or the browser blocks both the session-creation request and the WebSocket handshake.
- The client uses the browser's Web Audio API (`AudioWorklet`) to capture raw 16kHz PCM microphone input, and the WebSocket API to send it and receive the agent's raw 24kHz PCM audio response.
- The data flow is a continuous, full-duplex stream: the client sends audio chunks to the server, and the server sends back full ADK `Event` objects as they're generated, containing spoken audio.
- **Impact of Audio Chunk Interval:** How often the client sends captured audio chunks is critical for perceived latency. Batching a full second of audio before sending it would introduce a full second of dead air before the server can start processing speech, leading to unnatural pauses and a sluggish, non-real-time conversational flow.
- **WebSockets vs. SSE for Voice:** While SSE (used in the previous lab) is excellent for one-way streaming (server to client), WebSockets are necessary for voice applications because they provide a **full-duplex** (bidirectional) channel. This allows the client to continuously stream microphone audio *to* the server while simultaneously receiving the agent's audio response *from* the server, which is not possible with SSE.
- **Handling Audio Playback:** Unlike a compressed audio file, raw PCM has no container format to decode — you can't hand it to `audioContext.decodeAudioData()`. Instead, you manually convert the 16-bit samples to normalized `Float32` values, copy them into an `AudioBuffer` via `copyToChannel`, and schedule an `AudioBufferSourceNode` to start exactly when the previous chunk ends — that scheduling is what keeps consecutive chunks sounding like one continuous voice instead of overlapping or gapping.