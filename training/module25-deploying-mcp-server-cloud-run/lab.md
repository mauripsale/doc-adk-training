# Module 25: Deploying an MCP Server to Cloud Run

## Lab 25: Deploying the "Shopping Cart" Server

### Goal

In this lab, you will take the "Shopping Cart" MCP server from Module 24, re-architect it to be stateless, containerize it with a `Dockerfile`, and deploy it to Google Cloud Run. You will then configure an ADK agent to connect to this live, cloud-hosted tool.

**Note:** This is an advanced lab. For simplicity, we will simulate an external state store with a file written to a temporary directory. In a real production system, you would replace this with a connection to a service like Redis or Memorystore.

### Step 1: Create the Stateless MCP Server

We need to modify our server so it doesn't store the shopping carts in memory.

1.  **Create a new project directory:**

    ```shell
    cd /path/to/your/adk-training
    mkdir cloud-mcp-server
    cd cloud-mcp-server
    ```

2.  **Create the `stateless_cart_server.py` file:**
    This is the modified server code. Instead of a global dictionary, it reads and writes the cart for each session to a separate JSON file in a `/tmp/carts` directory. This simulates an external persistence layer.

    ```python
    # Filename: stateless_cart_server.py
    import asyncio
    import json
    import os
    from mcp import types as mcp_types
    from mcp.server.lowlevel import Server
    import mcp.server.http_stream

    # --- Configuration ---
    # In a serverless environment, we can use the temporary filesystem.
    # In a real app, this would be a Redis/database connection string.
    STATE_STORAGE_PATH = "/tmp/carts"
    if not os.path.exists(STATE_STORAGE_PATH):
        os.makedirs(STATE_STORAGE_PATH)

    # --- MCP Server Setup ---
    app = Server("stateless_shopping_cart_server")

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

    @app.list_tools()
    async def list_mcp_tools() -> list[mcp_types.Tool]:
        # (Same as Module 24's list_tools function)
        add_item_tool = mcp_types.Tool(name="add_item_to_cart", description="Adds an item to the cart.", inputSchema={"type": "object", "properties": {"item": {"type": "string"}}, "required": ["item"]})
        view_cart_tool = mcp_types.Tool(name="view_cart", description="Views items in the cart.", inputSchema={"type": "object", "properties": {}})
        return [add_item_tool, view_cart_tool]

    @app.call_tool()
    async def call_mcp_tool(name: str, arguments: dict, session_id: str) -> list[mcp_types.Content]:
        print(f"[Server]: Handling '{name}' for session '{session_id}'")
        cart = get_cart(session_id)

        if name == "add_item_to_cart":
            item = arguments.get("item")
            cart.append(item)
            save_cart(session_id, cart)
            response_text = json.dumps({"status": "success", "message": f"Added '{item}'."})
            return [mcp_types.TextContent(type="text", text=response_text)]

        elif name == "view_cart":
            response_text = json.dumps({"status": "success", "cart": cart})
            return [mcp_types.TextContent(type="text", text=response_text)]
        
        else:
            return [mcp_types.TextContent(type="text", text=json.dumps({"status": "error", "message": "Unknown tool."}))]

    # --- Server Runner for HTTP ---
    # This uses the HTTP stream runner, suitable for Cloud Run
    main = mcp.server.http_stream.create_main(app)

    if __name__ == "__main__":
        main()
    ```

### Step 2: Containerize the MCP Server

1.  **Create a `requirements.txt` file:**
    Our server needs the `mcp` library.

    ```shell
    echo "mcp" > requirements.txt
    ```

2.  **Create the `Dockerfile`:**

    ```dockerfile
    FROM python:3.11-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY stateless_cart_server.py .
    
    # Cloud Run provides the PORT env var.
    # The http_stream runner automatically uses it.
    CMD ["python", "stateless_cart_server.py"]
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
    *(This assumes you created the `adk-images` repository in Module 19. If not, you may need to run `gcloud artifacts repositories create ...` first.)*

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

1.  **Create an `agent.py` file** in the same `cloud-mcp-server` directory.
2.  **Add the following code**, replacing `YOUR_CLOUD_RUN_SERVICE_URL` with the URL you copied.

    ```python
    # Filename: agent.py
    from google.adk.agents import LlmAgent
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
    from mcp import StreamableHTTPConnectionParams

    # The URL of your deployed MCP server
    MCP_SERVER_URL = "YOUR_CLOUD_RUN_SERVICE_URL"

    root_agent = LlmAgent(
        model='gemini-1.5-flash',
        name='cloud_shopping_agent',
        instruction='You are a shopping assistant. Help the user by adding items to their cart and showing them their cart contents.',
        tools=[
            MCPToolset(
                # Use StreamableHTTPConnectionParams for remote servers
                connection_params=StreamableHTTPConnectionParams(
                    url=MCP_SERVER_URL,
                ),
            )
        ],
    )
    ```
3.  **Create `__init__.py` and `.env` files** as in previous labs.

### Step 5: Test the Full Cloud-Based System

1.  **Start the ADK web server locally:**
    This will run your *client* agent.

    ```shell
    adk web
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
*   Configure the `MCPToolset` to connect to a remote HTTP-based MCP server using `StreamableHTTPConnectionParams`.
