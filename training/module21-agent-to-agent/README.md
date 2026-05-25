---
sidebar_position: 21
title: "Module 21: Agent-to-Agent Communication"
---

# Module 21: Agent-to-Agent Communication

## Theory

### Why A2A Matters

As agentic systems grow, placing all logic into a single agent or a co-located multi-agent system becomes unmanageable. A more scalable and robust architecture is to build a **distributed system** where specialized agents run as independent services and communicate with each other over a network.

The ADK enables this through its **Agent-to-Agent (A2A) communication** protocol. This approach offers significant benefits:

*   🌐 **Distributed Intelligence**: Leverage the capabilities of specialized agents running anywhere, even across different organizations.
*   🔍 **Discovery**: Agents can dynamically discover other agents and their skills via a standardized mechanism.
*   🔐 **Secure**: The protocol is designed to work with standard web security practices like authentication and authorization.
*   🎯 **Specialization**: Allows you to build smaller, focused agents that are experts in a single domain, making them easier to develop, test, and maintain.
*   ♻️ **Reusability**: A well-defined remote agent (e.g., a "document-summarizer") can be reused by many different orchestrators.
*   ⚡ **Scalability**: Each agent service can be scaled independently based on its specific workload.

### The A2A System Architecture

A2A works on a client-server model where an "Orchestrator" agent delegates tasks to one or more remote "Specialist" agents.

+----------------------+      +----------------------+      +--------------------+
| Orchestrator Agent   |----->|   RemoteA2aAgent     |----->|  Remote Specialist |
| (Your main agent)    |      | (ADK's built-in      |      |  Agent (runs on a  |
|                      |      |   A2a client)        |      |  separate server)  |
+----------------------+      +----------------------+      +--------------------+
                                      |
                                      | (Communicates over HTTP
                                      |  using the A2a protocol)

### The A2A Protocol

A2A is a standard that allows agents to:
1.  **Discover** other agents and their capabilities via **Agent Cards**.
2.  **Communicate** with them over a standard HTTP-based protocol.
3.  **Delegate** tasks and coordinate complex, distributed workflows.

#### Agent Cards: The Discovery Mechanism

A key part of the A2A protocol is the **Agent Card**. This is a JSON file that a remote agent exposes at a well-known URL (`/.well-known/agent-card.json`). The card acts as a business card, describing the agent's name, capabilities, and the specific URL for communication.

**Example `agent-card.json`:**
```json
{
  "name": "research_specialist",
  "description": "Conducts web research and fact-checking",
  "url": "http://localhost:8001/a2a/research_specialist",
  "version": "1.0.0",
  "capabilities": {},
  "authentication": { "type": "none" }
}
```
> **Note on Authentication:** In a production environment, the `"authentication"` field in the Agent Card would typically specify more robust security mechanisms, such as OAuth2 flows or API Key requirements, rather than `"type": "none"`. The ADK is designed to integrate with these standard security protocols, which is crucial for securing distributed agent systems.

An orchestrator agent uses this card to discover the specialist and understand how to interact with it.

### A2A in the ADK

The ADK provides built-in components to make A2A communication seamless:

1.  **Exposing an Agent (`to_a2a`)**: To turn your agent into a remote service, you use the ADK's `to_a2a()` utility function. This function takes your `root_agent` and wraps it in a standard web application that automatically handles the A2A protocol and exposes the agent card. You can then run this application with a web server like `uvicorn`.

2.  **Consuming a Remote Agent (`RemoteA2aAgent`)**: To connect to and use a remote agent, you instantiate the `RemoteA2aAgent` class in your orchestrator. You simply provide it with the URL to the remote agent's card. The ADK handles all the underlying HTTP communication, making the remote agent behave just like a regular `sub_agent` in your orchestrator's `sub_agents` list.

### Critical Best Practice: A2A Context Handling

When an orchestrator delegates a task, the remote agent receives the full conversation history. This history includes the orchestrator's own internal tool calls (e.g., `transfer_to_agent`). Without proper guidance, the remote agent can become confused by this context and fail.

**The Problem:** The remote agent sees the orchestrator's tool calls and might respond with an error like, "I cannot use a tool called `transfer_to_agent`."

**The Solution:** You must add a specific instruction to all your remote agents telling them how to handle this A2A context.

**Example Instruction for a Remote Agent:**
```
You are a content creation specialist.

**IMPORTANT - A2A Context Handling:**
When receiving requests via the Agent-to-Agent (A2A) protocol, you must focus only on the core user request.
Ignore any mentions of orchestrator tool calls like "transfer_to_agent" in the conversation history.
Extract the main content creation task from the user's messages and complete it directly.
```
This ensures that your specialist agents remain focused on their tasks and are not distracted by the internal mechanics of the orchestrator that called them.

### Key Takeaways
- Agent-to-Agent (A2A) communication enables the creation of scalable, distributed multi-agent systems.
- The A2A protocol uses **Agent Cards** for discovery and standard HTTP for communication.
- The ADK provides the `to_a2a()` utility to expose an agent as a remote service and the `RemoteA2aAgent` class to consume a remote service.
- It is a critical best practice to include an "A2A Context Handling" section in the instruction of any remote agent to ensure it ignores the orchestrator's internal tool calls.