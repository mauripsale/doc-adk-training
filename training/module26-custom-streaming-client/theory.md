# Module 26: Building a Custom Streaming Client

## Theory

### Beyond the Dev UI

In Module 16, you experienced the power of bidirectional streaming through the ADK Developer UI. The UI's microphone button provided a convenient way to have a voice conversation with your agent. However, the Dev UI is a tool for development, not a production-ready application.

To integrate ADK's streaming capabilities into your own website or application, you need to build a **custom streaming client**. This involves creating a front-end (e.g., using HTML and JavaScript) that can communicate directly with the ADK agent server.

### The Architecture of a Streaming Application

A custom streaming application consists of two main components that communicate in real-time:

1.  **The ADK Server:** This is your ADK agent, but instead of being run with `adk web`, it's run as a headless API server using `adk api_server`. This command exposes the agent's functionality over a network protocol. For streaming, it specifically opens a **WebSocket** endpoint, typically at `/live`.

2.  **The Custom Client:** This is the user-facing part of the application (e.g., a web page). It's responsible for:
    *   Capturing audio from the user's microphone.
    *   Sending that audio data to the ADK server's WebSocket endpoint.
    *   Receiving audio and text data back from the server.
    *   Playing the received audio through the user's speakers.
    *   Displaying the received text on the screen.

### WebSockets: The Key to Real-time Communication

Standard HTTP is a request-response protocol. The client sends a request, and the server sends a response. This is not suitable for real-time, continuous conversation.

**WebSockets** solve this problem. A WebSocket is a protocol that provides a persistent, **full-duplex** (two-way) communication channel over a single TCP connection. Once a WebSocket connection is established between the client (your browser) and the server (the ADK `api_server`), both sides can send data to each other at any time.

This is the technology that enables the continuous, low-latency flow of audio data required for a natural voice conversation.

### The Data Flow

The interaction between a custom client and the ADK server follows a specific flow:

1.  **Connection:** The JavaScript client opens a WebSocket connection to the ADK server's `/live` endpoint.
2.  **Client Sends Audio:**
    *   The client uses the browser's Web Audio API (`navigator.mediaDevices.getUserMedia`) to access the microphone.
    *   It captures audio in small chunks (e.g., every 100 milliseconds).
    *   Each audio chunk is encoded (e.g., into Base64 format) and sent as a message over the WebSocket to the server.
3.  **Server Processes and Responds:**
    *   The ADK server receives the audio chunks and streams them to the Gemini Live API.
    *   As the Gemini model processes the audio and formulates a response, the ADK server sends events back to the client over the same WebSocket. These events can be:
        *   **Partial Text:** Transcriptions of what the user is saying or what the agent is starting to say.
        *   **Audio Chunks:** The agent's voice response, sent as small chunks of audio data.
        *   **Status Events:** Messages indicating the end of a conversational turn.
4.  **Client Renders Response:**
    *   The client's JavaScript code listens for these incoming messages.
    *   When it receives text, it displays it on the page.
    *   When it receives an audio chunk, it decodes it and plays it through the user's speakers, creating a continuous stream of speech.

In the lab for this module, you will be provided with a complete HTML and JavaScript client that implements this entire flow. You will run it against your own ADK agent to see how a custom streaming application is built.
