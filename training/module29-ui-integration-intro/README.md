---
sidebar_position: 29
title: "Module 29: Introduction to UI Integration"
pagination_label: "Module 29: Introduction to UI Integration — 📖 Theory & Overview"
---

# Module 29: Introduction to UI Integration

## Theory

![Multi-Platform Agent UI Integration (Light)](img/hero-light.webp#gh-light-mode-only)
![Multi-Platform Agent UI Integration (Dark)](img/hero-dark.webp#gh-dark-mode-only)
*Figure: Integrating AI agents into modern multi-platform frontends (React, WebSockets, Streamlit, and conversational UI).*

### Why UI Integration Matters

While agents can be run from the command line or via an API, their full potential is unlocked when they are integrated into a user interface. A UI makes your agent accessible to non-technical users and enables rich, interactive experiences.

### The UI Integration Landscape

The ADK is flexible and supports several approaches for UI integration, each suited for different use cases:

| Approach | Best For | Key Features |
| :--- | :--- | :--- |
| **AG-UI Protocol** | Modern web apps (React/Next.js) | Pre-built components, official support |
| **Native ADK API** | Custom frameworks (Vue, Angular, Vanilla JS) | Full control, zero frontend SDK lock-in |
| **Direct Python** | Data apps (Streamlit, Gradio) | In-process, no HTTP overhead |
| **Messaging Platforms**| Team bots (Slack, Teams) | Native platform UX |
| **Event-Driven** | High-scale, async workflows | Decoupled, scalable (Pub/Sub) |

### Understanding the AG-UI Protocol

**AG-UI (Agent-Generative UI)** is an open protocol for agent-user interaction, developed through an **official partnership between the Google ADK and CopilotKit teams**. It provides a standardized, event-based way for AI agents to communicate with web UIs.

**The Stack:**

![AG-UI Fullstack Architecture (Light)](img/ag-ui-fullstack-architecture-light.webp#gh-light-mode-only)
![AG-UI Fullstack Architecture (Dark)](img/ag-ui-fullstack-architecture-dark.webp#gh-dark-mode-only)
*Figure: Fullstack AG-UI architecture bridging frontend React/Next.js components with backend ADK FastAPI agents via bidirectional streaming.*

By using the AG-UI protocol and the associated libraries, you can quickly build a production-ready chat interface with minimal front-end code, as the pre-built components handle the complexities of state management and streaming.

### Under the Hood: Native ADK API & `/run_sse` Streaming

**A note on this module's scope:** the lab in this module builds directly against the **Native ADK API** (`uv run adk api_server`) instead of AG-UI — on purpose. Writing a raw `fetch` + Server-Sent Events (SSE) client by hand teaches you the exact wire mechanics that higher-level frameworks like AG-UI and CopilotKit abstract away:

1.  **Explicit Session Creation (`POST /apps/{app_name}/users/{user_id}/sessions`):** Before calling `/run_sse`, the client creates a session via REST, passing `{"session_id": "..."}` in the request body (or `{}` to let the server generate one).
2.  **Enabling Token Streaming (`"streaming": true`):** In ADK's `RunAgentRequest` schema, `streaming` defaults to `false`. Including `"streaming": true` in your `/run_sse` JSON payload activates `StreamingMode.SSE` so tokens arrive incrementally as the model generates them rather than in a single block at the end of the turn.
3.  **Partial Chunks vs. Final Aggregated Event (`event.partial`):** During an active SSE stream, ADK emits incremental `Event` objects with `"partial": true`, followed at the end of the turn by one final **aggregated** `Event` (where `partial` is omitted/`false`) containing the full accumulated response text. A well-behaved UI appends `partial === true` chunks live and skips re-appending the final aggregated text so responses are never duplicated!
4.  **Line Buffering Across TCP Chunks:** `ReadableStreamDefaultReader.read()` yields arbitrary network byte slices that can split a `data: {...}\n\n` line mid-JSON. Buffering incomplete trailing text across `reader.read()` iterations prevents `JSON.parse` crashes on large events.

Once you understand these mechanics, adopting AG-UI for a production React/Next.js project is as simple as dropping in `@copilotkit/react-core` — see the [CopilotKit + ADK docs](https://docs.copilotkit.ai/adk) to explore that path.

<KnowledgeCheck
  id="m29-sse-streaming-deduplication"
  question="When consuming ADK's /run_sse endpoint with 'streaming': true, why must a custom frontend inspect eventData.partial before appending text?"
  options={[
    "ADK streams incremental token chunks with partial: true and then emits a final non-partial aggregated event containing the full text, which would duplicate the message if appended blindly",
    "Events with partial: true contain encrypted binary audio rather than UTF-8 text",
    "ADK requires the browser to send an HTTP ACK for every partial: true event before emitting the next token",
    "Events without partial: true are system errors that must always be discarded"
  ]}
  correctIndex={0}
  hint="Recall what ADK's StreamingResponseAggregator emits when a streamed model turn finishes."
  explanation="With 'streaming': true, ADK yields incremental token chunks marked with partial: true for low-latency rendering, and then yields a final non-partial aggregated Event containing the complete accumulated turn text. Tracking partial events ensures your UI renders tokens live without duplicating the full reply at the end of the stream."
/>

### Key Takeaways
- Integrating an agent with a UI makes it accessible to a wider audience and enables richer interactions.
- The ADK supports multiple UI integration strategies, including the official **AG-UI Protocol**, the native ADK API, direct Python integration, and messaging platforms.
- The **AG-UI Protocol**, developed in partnership with CopilotKit, is Google's officially supported path for production React/Next.js applications, providing pre-built components that handle streaming and state for you.
- When building custom clients against `uv run adk api_server` and `/run_sse`, pass `"streaming": true`, buffer SSE lines across network chunks, and distinguish `partial: true` deltas from the final aggregated `Event`.
- **Static Asset Isolation:** Never run a static file server (like `python3 -m http.server`) inside your agent package directory, or it will expose `.env` credentials over HTTP. Keep frontend files in a separate `frontend/` directory.
- **Session ID Persistence:** Generating a new `sessionId` on every page load loses conversational memory on refresh; persist `sessionId` in `localStorage` or an HTTP-only session cookie in real apps.
