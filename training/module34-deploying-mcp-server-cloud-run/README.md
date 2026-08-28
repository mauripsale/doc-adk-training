---
sidebar_position: 34
title: "Module 34: Deploying an MCP Server to Cloud Run"
---

# Module 34: Deploying an MCP Server to Cloud Run

## Theory

### The Challenge of State in a Serverless World

In Module 28, you built a stateful MCP server. Its state—the contents of the shopping cart—was a single global Python list: `CART = []`. That worked fine because the server ran over stdio, talking to exactly one client (your local agent) at a time — there was no notion of "whose cart is this" because there was only ever one.

Moving to Cloud Run over HTTP changes that completely: the server can now be talking to *many* clients concurrently, each of whom needs their own, isolated cart. A single global list would mean every user shares the exact same cart — a correctness bug, not just a scaling one. And even setting that aside, Cloud Run is a **stateless** and **serverless** environment, which introduces a second problem on top of the first:

*   **Stateless:** Each incoming request could be handled by a completely different container instance. An instance that handles a user's "add item" request might be shut down before the user makes a "view cart" request, which would then be routed to a brand new instance with no memory of the previous one. The in-memory cart data would be lost.
*   **Serverless:** You don't have a single, persistent "server." Cloud Run automatically starts and stops container instances based on traffic. It might run ten instances to handle a spike in traffic and then scale down to zero when idle.

If we deploy our simple, in-memory MCP server directly to Cloud Run, every user's shopping cart would be wiped out between requests. We need a new architecture.

### The Solution: Externalized State

The solution to this challenge is to **externalize the state**. Instead of storing the session data in the memory of the MCP server process, the server must save it to and load it from an external, persistent storage service that all of its instances can access.

This is a fundamental pattern in cloud-native application design. The application instances themselves remain stateless, which makes them easy to scale and replace, while the important data lives in a durable, centralized location.

**Common choices for an external state store include:**
*   **In-memory caches:** Services like **Redis** or **Google Cloud Memorystore**. These are extremely fast and are a perfect fit for session data that needs to be accessed quickly but may not need to be stored forever.
*   **Databases:** Services like **Firestore**, **DynamoDB**, or a traditional SQL database like **Cloud SQL**. These are better for data that needs to be stored permanently and queried in more complex ways.

### The New Architecture

With externalized state, the interaction flow for our MCP server on Cloud Run looks like this:

1.  An ADK agent (the client) sends a `call_tool` request (e.g., `add_item_to_cart`) to the Cloud Run service URL.
2.  Cloud Run starts or selects a container instance to handle the request.
3.  The MCP server code inside the container reads the `Mcp-Session-Id` HTTP header that the MCP transport itself tracks for the connection.
4.  Instead of appending to a global in-memory list, the server connects to the external state store (e.g., Redis), keyed by that session ID.
5.  It retrieves the shopping cart for the given session, performs the action (adds the new item), and saves the updated cart back to the external store.
6.  It sends the success response back to the ADK agent.

Now, if another request for the same `session_id` arrives a moment later, Cloud Run can send it to a completely different container instance. This new instance will follow the same process, connect to the same external store, and retrieve the correct, up-to-date shopping cart. The state is preserved.

### Connecting the ADK Agent

When the MCP server is running on a public URL on Cloud Run, our ADK agent can no longer use `StdioConnectionParams`, which is designed for running a local subprocess.

Instead, the agent must be configured to connect to the remote server over the network. The MCP library provides connection types for this, such as `StreamableHTTPConnectionParams`, which allows the ADK `McpToolset` to communicate with the deployed server using standard HTTP requests.

In the lab, you will modify the shopping cart server to be stateless, containerize it, and deploy it to Cloud Run. You will then reconfigure your ADK agent to connect to its public URL.

### Production Considerations for MCP

When deploying MCP servers to production, security and safety become paramount. The ADK provides advanced features to handle these requirements.

#### Authentication

You must secure your MCP server to ensure that only authorized agents can access its tools. The `McpToolset` supports several authentication methods:

*   **OAuth2 (Recommended):** The most secure, standard method for production systems. The ADK handles the client credentials flow, automatically requesting and refreshing access tokens.
*   **HTTP Bearer Token:** For services that use a simple static bearer token for authentication.
*   **HTTP Basic Authentication:** For legacy systems or internal tools that use a simple username and password.
*   **API Key:** For services that require an API key to be passed in a specific header.

You configure the chosen method via the `credential` parameter in the `McpToolset`, and the ADK handles the rest.

#### Human-in-the-Loop (HITL)

When an MCP server provides powerful or destructive tools (e.g., `write_file`, `delete_database_entry`), it's crucial to have a human approval step to prevent accidental data loss or misuse. This is known as a "Human-in-the-Loop" (HITL) workflow.

You can implement HITL in the ADK using a `before_tool_callback`. This callback function is triggered *before* any tool is executed. Inside the callback, you can:
1.  Check if the tool being called is on a list of "destructive" operations.
2.  If it is, you can block the execution and return a message to the agent indicating that approval is required.
3.  This allows a user in the UI (or an automated policy) to review the requested operation and approve or deny it before it runs.

### Key Takeaways
- Serverless platforms like Cloud Run are **stateless**, meaning in-memory state is lost between requests.
- To deploy a stateful service (like an MCP server) to a stateless platform, you must **externalize the state** using a persistent storage service like Redis or Firestore.
- When connecting an ADK agent to a remote MCP server, you must use a network-based connection type, such as `StreamableHTTPConnectionParams`.
- For production, it is critical to secure your MCP server with authentication (e.g., OAuth2) and implement Human-in-the-Loop (HITL) workflows for destructive tools.
- **Separation of Concerns in MCP:** A key benefit of the MCP architecture is that the client (`McpToolset`) is completely decoupled from the server's state management implementation. The agent only needs to know the server's URL and the tool schema. This allows the server's backend to be changed (e.g., migrating from a file-based system to Redis) without requiring any changes to the agent client, promoting modular maintenance and reducing the client's complexity.
- **Advantages of Memorystore (Redis):** For production session state, a managed in-memory service like Google Cloud Memorystore (Redis) is far superior to a file-based approach. It offers true persistence (data survives container restarts), low-latency performance (ideal for fast tool access), and scalability (all Cloud Run instances connect to the same central data source, ensuring state consistency).
- **Persistence in Cloud Run:** Using the `/tmp` directory for storage in a Cloud Run container is not truly persistent. The `/tmp` directory is part of the container's volatile filesystem. When Cloud Run scales a service to zero due to inactivity or recycles an instance, the container is terminated, and all data in `/tmp` is permanently lost. This means any state (like a shopping cart) stored there would be erased.