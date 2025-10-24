# Module 11: Building a Coordinator/Dispatcher Agent

## Lab 11: Implementing the "Greeting Router"

### Goal

In this lab, you will implement the multi-agent "Greeting Router" system that you designed in Module 10. You will create a main router agent and a specialist `spanish_greeter` agent, and configure them to work together using the coordinator/dispatcher pattern.

### Step 1: Create the Project Structure

1.  **Navigate to your training directory:**

    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Create the agent project:**

    ```shell
    adk create --type=config greeting-agent
    ```

3.  **Navigate into the new directory:**

    ```shell
    cd greeting-agent
    ```

### Step 2: Create the Specialist Agent

First, we'll create the configuration for our Spanish language expert.

1.  **Create the `spanish_greeter.yaml` file:**

    Inside the `greeting-agent` directory, create a new file named `spanish_greeter.yaml`.

2.  **Add the specialist agent's configuration:**

    Open `spanish_greeter.yaml` and add the following content. This is based directly on the design from the previous lab.

    ```yaml
    # yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
    name: spanish_greeter_agent
    model: gemini-1.5-flash
    description: "An expert at providing friendly greetings in Spanish."
    instruction: |
      You are a friendly assistant who only speaks Spanish.
      Your job is to greet the user warmly in Spanish.
      Do not say anything else or try to answer questions. Just provide a simple, warm greeting.
    ```
    Note the `description` field. This is the text the `router_agent` will use to understand this specialist's capability.

### Step 3: Configure the Coordinator (Router) Agent

Now, let's configure the main `root_agent.yaml` to act as the router.

1.  **Set up your environment variables:**

    Open the `.env` file and configure it with your Google API key or Vertex AI project details.

2.  **Update the `root_agent.yaml` file:**

    Replace the contents of `root_agent.yaml` with the configuration we designed for our router.

    ```yaml
    # yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
    name: router_agent
    model: gemini-1.5-flash
    description: The main greeter agent that routes to language specialists.
    instruction: |
      You are a language router. Your job is to understand which language the user wants to be greeted in and delegate to the appropriate specialist agent.
      If the user asks for a greeting in Spanish, you MUST delegate to the `spanish_greeter_agent`.
      Do not greet the user yourself.
    sub_agents:
      - config_path: spanish_greeter.yaml
    ```
    The key here is the `sub_agents` section, which tells the `router_agent` that the `spanish_greeter_agent` (defined in `spanish_greeter.yaml`) is its child.

### Step 4: Test the Multi-Agent System

1.  **Start the web server:**

    From the `greeting-agent` directory, run `adk web`.

2.  **Interact with the router:**
    *   Open the Dev UI in your browser.
    *   **Test Case 1: Triggering the specialist.**
        *   **User:** "Say hello to me in Spanish."
        *   **Expected Response:** Something like `"¡Hola! ¿Cómo estás?"`
    *   **Examine the Trace:** In the Trace view for this conversation, you will see the execution flow.
        1.  The `router_agent` runs first.
        2.  It makes a decision to call the `transfer_to_agent` function.
        3.  Control is then passed to the `spanish_greeter_agent`, which runs and produces the final output.
        This confirms your coordinator is working correctly!
    *   **Test Case 2: A request the router can't handle.**
        *   **User:** "Say hello in French."
        *   **Expected Response:** The router should respond by saying it cannot fulfill the request, as it has no specialist for French. For example, "I'm sorry, I don't have a specialist for French greetings at the moment."

### Lab Summary

You have successfully built your first multi-agent system! You have implemented the coordinator/dispatcher pattern to create a modular and extensible application.

You have learned to:
*   Create separate YAML configuration files for different agents.
*   Use the `sub_agents` and `config_path` keys to establish a parent-child hierarchy.
*   Write a clear `description` for a specialist agent so the coordinator can understand its function.
*   Write an `instruction` for a coordinator agent that tells it how to delegate tasks.
*   Verify the agent transfer process by inspecting the Trace View.

**Challenge (Optional):**
Can you add another specialist? Create an `english_greeter.yaml` and add it to the `sub_agents` list in `root_agent.yaml`. Update the router's instruction and see if you can get it to delegate to both the Spanish and English greeters correctly.
