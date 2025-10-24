# Module 9: Integrating Third-Party Tools

## Lab 9: Integrating a LangChain Wikipedia Tool

### Goal

In this lab, you will learn how to integrate a tool from a popular third-party library, LangChain, into your ADK agent. You will build a "Fact-finder" agent that can look up information on Wikipedia. This will demonstrate the power of the ADK's interoperability and how you can leverage the broader Python ecosystem.

### Step 1: Create the Agent Project and Install Dependencies

1.  **Navigate to your training directory:**

    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Create the agent project:**

    ```shell
    adk create --type=config fact-finder-agent
    ```

3.  **Navigate into the new directory:**

    ```shell
    cd fact-finder-agent
    ```

4.  **Install LangChain dependencies:**

    The ADK does not come with third-party libraries pre-installed. You need to add them to your project's environment.

    ```shell
    pip install langchain_community wikipedia
    ```
    *   `langchain_community`: Contains the community-contributed tools for LangChain.
    *   `wikipedia`: The underlying Python library that the LangChain tool uses to connect to the Wikipedia API.

### Step 2: Write the Agent Code (with the Wrapper)

Because we are now importing and instantiating Python objects, we can't define our entire agent in YAML. We need a Python file to set up the tool and the agent.

1.  **Create an `agent.py` file:**

    Inside the `fact-finder-agent` directory, create a new file named `agent.py`.

2.  **Add the following code to `agent.py`:**

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.tools.langchain_tool import LangchainTool
    from langchain_community.tools import WikipediaQueryRun
    from langchain_community.utilities import WikipediaAPIWrapper

    # 1. According to LangChain documentation, instantiate the tool.
    # This sets up the connection to the Wikipedia API.
    api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=2000)
    langchain_tool_instance = WikipediaQueryRun(api_wrapper=api_wrapper)

    # 2. Wrap the LangChain tool instance with the ADK's LangchainTool wrapper.
    # The wrapper automatically inspects the tool and creates the schema for the LLM.
    wikipedia_tool = LangchainTool(tool=langchain_tool_instance)

    # 3. Define the ADK agent and include the wrapped tool in its tools list.
    root_agent = LlmAgent(
        name="fact_finder_agent",
        model="gemini-1.5-flash",
        description="An agent that can look up information on Wikipedia.",
        instruction="""You are a helpful fact-finding assistant.
    If the user asks a question about a specific topic, person, or event, you MUST use the Wikipedia tool to find an accurate answer.
    Summarize the information you find in a clear and concise way.""",
        tools=[wikipedia_tool]
    )
    ```

### Step 3: Configure and Run the Python-based Agent

Since our agent is now defined in a Python file (`agent.py`) instead of a YAML file, the way we run it is slightly different. The `adk` command will automatically discover and run the `root_agent` object from the `agent.py` file.

1.  **Delete the placeholder `root_agent.yaml`:**

    The `adk create` command created a `root_agent.yaml` file that we no longer need. Delete it.

    ```shell
    rm root_agent.yaml
    ```

2.  **Set up your environment variables:**

    Open the `.env` file and ensure it's configured with your Google API key or Vertex AI project.

3.  **Run the agent:**

    Start the web server as usual. The ADK is smart enough to find the `root_agent` object in your `agent.py` file.

    ```shell
    adk web
    ```

### Step 4: Test the Fact-Finder Agent

1.  **Interact with the agent:**
    *   Open the Dev UI in your browser.
    *   Ask it questions that would require an encyclopedia:
        *   "Who was Marie Curie?"
        *   "What is the theory of relativity?"
        *   "Tell me about the history of the internet."
    *   **Examine the Trace View:** In the trace for one of your questions, you will see the `execute_tool` step. Expand it, and you will see the `WikipediaQueryRun` tool being called with the search query the agent decided on. This confirms the third-party tool was successfully integrated and used.

### Lab Summary

You have successfully integrated a tool from an external library into your ADK agent. This is a powerful technique that dramatically expands the capabilities available to you.

You have learned to:
*   Install third-party library dependencies into your project's virtual environment.
*   Instantiate a tool from a library like LangChain.
*   Use an ADK wrapper (`LangchainTool`) to make the third-party tool compatible with your agent.
*   Define an agent in a Python file (`agent.py`) instead of YAML to handle the tool setup.
*   Verify the execution of the third-party tool using the Dev UI.

This concludes Part 2 of the course. You are now proficient in equipping agents with both built-in, custom, and third-party tools. In the next part, you will learn how to build systems with multiple agents that collaborate to solve even more complex problems.
