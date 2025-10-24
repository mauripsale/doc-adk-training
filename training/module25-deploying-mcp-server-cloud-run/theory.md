# Module 25: Deploying an MCP Server to Cloud Run

## Theory

### The Challenge of State in a Serverless World

In the previous lab, you built a stateful MCP server. Its state—the contents of the shopping carts—was stored in a simple Python dictionary: `SESSION_CARTS = {}`. This works perfectly as long as the server is a single, long-running process on your local machine.

However, when we move to a cloud platform like Google Cloud Run, this model breaks down. Cloud Run is a **stateless** and **serverless** environment. This means:

*   **Stateless:** Each incoming request could be handled by a completely different container instance. An instance that handles a user's "add item" request might be shut down before the user makes a "view cart" request, which would then be routed to a brand new instance with no memory of the previous one. The in-memory `SESSION_CARTS` dictionary would be lost.
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
3.  The MCP server code inside the container receives the request, which includes the `session_id`.
4.  Instead of looking in a local dictionary, the server connects to the external state store (e.g., Redis).
5.  It retrieves the shopping cart for the given `session_id`, performs the action (adds the new item), and saves the updated cart back to the external store.
6.  It sends the success response back to the ADK agent.

Now, if another request for the same `session_id` arrives a moment later, Cloud Run can send it to a completely different container instance. This new instance will follow the same process, connect to the same external store, and retrieve the correct, up-to-date shopping cart. The state is preserved.

### Connecting the ADK Agent

When the MCP server is running on a public URL on Cloud Run, our ADK agent can no longer use `StdioConnectionParams`, which is designed for running a local subprocess.

Instead, the agent must be configured to connect to the remote server over the network. The MCP library provides connection types for this, such as `StreamableHTTPConnectionParams`, which allows the ADK `MCPToolset` to communicate with the deployed server using standard HTTP requests.

In the lab, you will modify the shopping cart server to be stateless, containerize it, and deploy it to Cloud Run. You will then reconfigure your ADK agent to connect to its public URL.
