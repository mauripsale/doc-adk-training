# Module 15: Handling Files with Artifacts

## Lab 15: Building a Document Summarizer Agent

### Goal

In this lab, you will build an agent that can read a text file uploaded by a user and provide a summary of its content. This will teach you how to use the ADK's artifact management system to handle file-based interactions.

### Step 1: Create the Agent Project

1.  **Navigate to your training directory:**

    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Create the agent project:**

    ```shell
    adk create --type=config doc-summarizer
    ```

3.  **Navigate into the new directory:**

    ```shell
    cd doc-summarizer
    ```

### Step 2: Create the Artifact-Handling Tool

We will create a tool that can list available files and read the content of a specific file.

1.  **Create the `tools` directory and `__init__.py` file:**

    ```shell
    mkdir tools
    touch tools/__init__.py
    ```

2.  **Create the `file_reader.py` file:**

    Inside the `tools` directory, create a file named `file_reader.py` and add the following code:

    ```python
    from google.adk.tools import ToolContext

    def list_files(tool_context: ToolContext) -> dict:
        """
        Lists the names of all files uploaded by the user in the current session.
        Use this tool first to see what files are available to be read.
        """
        try:
            file_names = tool_context.list_artifacts()
            return {"status": "success", "files": file_names}
        except Exception as e:
            return {"status": "error", "message": f"An error occurred: {str(e)}"}

    def read_file(filename: str, tool_context: ToolContext) -> dict:
        """
        Reads the text content of a specific file that the user has uploaded.
        You must know the exact filename to read it. Use list_files first if needed.

        Args:
            filename: The name of the file to read.
            tool_context: The context object provided by the ADK.

        Returns:
            A dictionary containing the text content of the file or an error.
        """
        try:
            artifact = tool_context.load_artifact(filename)
            if artifact and artifact.text:
                return {"status": "success", "content": artifact.text}
            else:
                return {"status": "error", "message": f"File '{filename}' not found or is not a text file."}
        except Exception as e:
            return {"status": "error", "message": f"Failed to read file: {str(e)}"}

    ```

### Step 3: Configure the Summarizer Agent

Now, let's configure the agent to use these tools to summarize documents.

1.  **Set up your `.env` file** with your API key or Vertex AI project.

2.  **Update the `root_agent.yaml` file:**

    Replace the contents of `root_agent.yaml` with the following:

    ```yaml
    # yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
    name: doc_summarizer_agent
    model: gemini-1.5-flash
    description: An agent that can read and summarize uploaded text files.
    instruction: |
      You are a document summarization assistant. Your goal is to help the user by summarizing text files they upload.

      Follow this process:
      1. When the user asks you to summarize a file, first check what files are available by using the `list_files` tool.
      2. If there is only one file, proceed to step 3. If there are multiple files, ask the user which one they would like you to summarize. If there are no files, ask the user to upload one.
      3. Once you know the exact filename, use the `read_file` tool to get the content of the file.
      4. After you have the content, summarize it for the user in a few key bullet points.
    tools:
      - name: tools.file_reader.list_files
      - name: tools.file_reader.read_file
    ```

### Step 4: Test the Agent with a File

1.  **Create a sample text file:**
    In your `doc-summarizer` directory, create a new file named `sample.txt`. Add a few paragraphs of text to it. You can copy and paste text from a news article or a book.

2.  **Start the web server:** `adk web`

3.  **Interact with the agent:**
    *   Open the Dev UI in your browser.
    *   **Upload the file:** Click the paperclip icon next to the chat input box and select the `sample.txt` file you just created.
    *   **Start the conversation:**
        *   **User:** "Please summarize the file I uploaded."
    *   **Observe the agent's process:** The agent should respond by saying it will summarize `sample.txt` and then provide the summary.
    *   **Examine the Trace View:** This is where you can see the artifact system in action.
        1.  You will see an initial `user` event that includes the file you uploaded.
        2.  The agent will first call the `list_files` tool. You'll see the tool's output, which is a list containing `["sample.txt"]`.
        3.  Next, the agent will call the `read_file` tool with `filename="sample.txt"`. You'll see the full content of your file returned as the tool's output.
        4.  Finally, the agent's LLM will take that content and generate the summary as its final response.

### Lab Summary

You have successfully built an agent that can interact with files! This is a major step towards creating agents that can perform complex, real-world tasks.

You have learned to:
*   Use the ADK Dev UI to upload files (artifacts) for an agent to use.
*   Create a custom tool that uses `tool_context.list_artifacts()` to discover available files.
*   Create a custom tool that uses `tool_context.load_artifact()` to read the content of a file.
*   Build a multi-step instruction that guides an agent through the process of listing, reading, and then processing a file.
