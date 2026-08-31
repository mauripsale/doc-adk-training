---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 34: Deploying the "Shopping Cart" Server Challenge

## Goal

In this lab, you will take the "Shopping Cart" MCP server from Module 28, re-architect it to be stateless, containerize it with a `Dockerfile`, and deploy it to Google Cloud Run. You will then configure an ADK agent to connect to this live, cloud-hosted tool.

**Note:** This is an advanced lab. For simplicity, we will simulate an external state store with a file written to a temporary directory. In a real production system, you would replace this with a connection to a service like Redis or Memorystore.

### Prerequisites

*   A Google Cloud Project with billing enabled.
*   Google Cloud CLI installed and authenticated.
*   Docker running on your local machine.
*   **Required APIs:** Ensure the following APIs are enabled in your project:
    *   Cloud Run API
    *   Cloud Build API
    *   Artifact Registry API
    *   Vertex AI API
*   **Set GCP Project:** Before starting, ensure your `gcloud` CLI is configured to the correct project:
    ```shell
    gcloud config set project YOUR_PROJECT_ID
    ```

### Step 1: Create the Stateless MCP Server

We need to modify our server so it doesn't store the shopping carts in memory.

1.  **Create a new project directory:**

    ```shell
    cd /path/to/your/adk-training
    mkdir cloud_mcp_server
    cd cloud_mcp_server
    ```

2.  **Create the `stateless_cart_server.py` file:**
    This is the modified server code, using `mcp.server.fastmcp.FastMCP` -- the MCP SDK's high-level API for building HTTP-based servers (much less boilerplate than the low-level `Server` class from Module 28, which is stdio-only). Instead of a single global list shared by everyone, it reads and writes each session's cart to its own separate JSON file in a `/tmp/carts` directory. This simulates an external persistence layer.

    A real MCP session is still tracked over the wire (via the `Mcp-Session-Id` HTTP header) -- what's "stateless" here is the *server process*, not the protocol: any container instance can handle any request, because the actual cart data lives outside the process.

    ```python
    # Filename: stateless_cart_server.py
    import json
    import os
    from mcp.server.fastmcp import FastMCP, Context

    # --- Configuration ---
    # In a serverless environment, we can use the temporary filesystem for a simple demo.
    # In a real production system, this would be a connection to a dedicated external
    # persistence service like Redis or Memorystore.
    STATE_STORAGE_PATH = "/tmp/carts"
    if not os.path.exists(STATE_STORAGE_PATH):
        os.makedirs(STATE_STORAGE_PATH)

    # --- MCP Server Setup ---
    mcp = FastMCP("stateless_shopping_cart_server")

    def get_session_id(ctx: Context) -> str:
        # The MCP session ID arrives as a standard HTTP header, tracked by the
        # transport itself -- this is what ties requests to the same cart,
        # regardless of which container instance handles each one.
        return ctx.request_context.request.headers.get("mcp-session-id", "unknown")

    # Helper functions to simulate external state
    def get_cart(session_id: str) -> list:
        cart_file = os.path.join(STATE_STORAGE_PATH, f"{session_id}.json")
        if os.path.exists(cart_file):
            with open(cart_file, 'r') as f:
                return json.load(f)
        return []

    def save_cart(session_id: str, cart: list):
        cart_file = os.path.join(STATE_STORAGE_PATH, f"{session_id}.json")
        with open(cart_file, 'w') as f:
            json.dump(cart, f)

    @mcp.tool()
    def add_item_to_cart(item: str, ctx: Context) -> dict:
        """Adds an item to the cart."""
        session_id = get_session_id(ctx)
        print(f"[Server]: Handling add_item_to_cart for session '{session_id}'")
        cart = get_cart(session_id)
        cart.append(item)
        save_cart(session_id, cart)
        return {"status": "success", "message": f"Added '{item}'."}

    @mcp.tool()
    def view_cart(ctx: Context) -> dict:
        """Views items in the cart."""
        session_id = get_session_id(ctx)
        print(f"[Server]: Handling view_cart for session '{session_id}'")
        cart = get_cart(session_id)
        return {"status": "success", "cart": cart}

    # --- ASGI app for HTTP, suitable for Cloud Run ---
    # FastMCP mounts the MCP endpoint at /mcp by default.
    app = mcp.streamable_http_app()
    ```

### Step 2: Containerize the MCP Server

1.  **Create a `requirements.txt` file:**
    Our server needs the `mcp` library and `uvicorn` to actually serve the ASGI app it produces. Pin `mcp` to a `1.x` release: `mcp>=2.0` renamed `FastMCP` to `MCPServer` and removed the `mcp.server.fastmcp` module entirely, which breaks both this server's `from mcp.server.fastmcp import FastMCP` import and `google-adk`'s own `McpToolset` client code (it targets the pre-2.0 API too).

    ```shell
    printf "mcp<2\nuvicorn\n" > requirements.txt
    ```

2.  **Create the `Dockerfile`:**

    ```dockerfile
    FROM python:3.11-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY stateless_cart_server.py .
    
    # Cloud Run provides the PORT env var (defaults to 8080 locally).
    # Shell form (not exec/JSON-array form) is required here so $PORT expands.
    CMD python -m uvicorn stateless_cart_server:app --host 0.0.0.0 --port ${PORT:-8080}
    ```

### Step 3: Build and Deploy the Server to Cloud Run

1.  **Set environment variables:**

    ```shell
    export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
    export GOOGLE_CLOUD_LOCATION=us-central1
    ```

2.  **Build and push the image:**

    ```shell
    gcloud builds submit \
        --tag ${GOOGLE_CLOUD_LOCATION}-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/adk-images/mcp-cart-server:v1
    ```
    *(If you completed Module 33's cleanup, the `adk-images` repository no longer exists -- create it first with `gcloud artifacts repositories create adk-images --repository-format=docker --location=$GOOGLE_CLOUD_LOCATION`.)*

3.  **Deploy to Cloud Run:**

    ```shell
    gcloud run deploy mcp-cart-server \
        --image=${GOOGLE_CLOUD_LOCATION}-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/adk-images/mcp-cart-server:v1 \
        --region=$GOOGLE_CLOUD_LOCATION \
        --allow-unauthenticated
    ```
    This command will deploy your server and give you a public **Service URL**. Copy this URL.

### Step 4: Configure the ADK Client Agent

Now, create an ADK agent that connects to your newly deployed server.

1.  **Create an `agent.py` file** in the same `cloud_mcp_server` directory.
2.  **Add the following code**, replacing `YOUR_CLOUD_RUN_SERVICE_URL` with the URL you copied. Note the `/mcp` suffix -- that's where `FastMCP` mounted the endpoint in Step 1, and the client needs to hit that exact path, not just the bare service URL.

    ```python
    # Filename: agent.py
    from google.adk import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

    # The URL of your deployed MCP server -- note the /mcp path suffix
    MCP_SERVER_URL = "YOUR_CLOUD_RUN_SERVICE_URL/mcp"

    root_agent = Agent(
        model='gemini-3.5-flash',
        name='cloud_shopping_agent',
        instruction='You are a shopping assistant. Help the user by adding items to their cart and showing them their cart contents.',
        tools=[
            McpToolset(
                # Use StreamableHTTPConnectionParams for remote servers
                connection_params=StreamableHTTPConnectionParams(
                    url=MCP_SERVER_URL,
                ),
            )
        ],
    )
    ```
3.  **Create `__init__.py` and `.env` files:**
    Create an empty `__init__.py` file in the `cloud_mcp_server` directory.
    Create a `.env` file in the `cloud_mcp_server` directory with your Vertex AI configuration:
    ```
    GOOGLE_GENAI_USE_VERTEXAI=1
    GOOGLE_CLOUD_PROJECT=<your_gcp_project>
    GOOGLE_CLOUD_LOCATION=us-central1
    ```
    Replace `<your_gcp_project>` with your actual Google Cloud Project ID.

### Step 5: Test the Full Cloud-Based System

1.  **Start the ADK web server locally:**
    This will run your *client* agent from the parent directory.

    ```shell
    uv run adk web cloud_mcp_server
    ```

2.  **Interact with the agent:**
    *   Open the Dev UI.
    *   Have the same conversation as in the previous lab: add 'apples', then add 'bread', then view the cart.
    *   It should work exactly the same! But this time, the state is being managed by your serverless application running on Cloud Run.

### Lab Summary

You have successfully deployed a stateful service to a stateless platform by externalizing the state, and connected your ADK agent to it.

You have learned to:
*   Modify an application to be stateless by moving its state to an external store (simulated with the filesystem).
*   Containerize a Python application with a `Dockerfile`.
*   Deploy a custom server to Google Cloud Run.
*   Configure the `McpToolset` to connect to a remote HTTP-based MCP server using `StreamableHTTPConnectionParams`.

### Cleanup (Important!)

Cloud Run services and Artifact Registry repositories can incur costs if left running. It is crucial to delete the resources you created after completing the lab.

1.  **Delete the Cloud Run Service:**
    ```shell
    gcloud run services delete mcp-cart-server \
        --region=$GOOGLE_CLOUD_LOCATION \
        --async # Runs in background
    ```

2.  **Delete the Artifact Registry Repository:**
    ```shell
    gcloud artifacts repositories delete adk-images \
        --location=$GOOGLE_CLOUD_LOCATION \
        --async # Runs in background
    ```

3.  **Delete the `cloud_mcp_server` directory:**
    ```shell
    cd ..
    rm -rf cloud_mcp_server
    ```

### Self-Reflection Questions
- Our stateless server uses the `/tmp` directory for storage. Why is this approach not truly persistent, and what could happen to a user's shopping cart if the Cloud Run service scales down and then back up?
- What are the advantages of using a managed service like Google Cloud Memorystore (Redis) for storing session state compared to the file-based approach used in this lab?
- The `McpToolset` on the client side doesn't need to know *how* the server is storing its state. Why is this separation of concerns a key benefit of the MCP architecture?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMzQtZGVwbG95aW5nLW1jcC1zZXJ2ZXItY2xvdWQtcnVuL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module34-deploying-mcp-server-cloud-run/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
