# Module 9: Integrating Third-Party Tools

## Theory

### Standing on the Shoulders of Giants

While the ADK provides a powerful framework for building custom tools, you don't always have to reinvent the wheel. The AI and Python ecosystems are vast, with many open-source libraries that already provide pre-built tools for a wide range of tasks.

Frameworks like **LangChain** have a rich ecosystem of "toolkits" and "agents" that come with ready-to-use integrations for services like Wikipedia, WolframAlpha, various search APIs, and more.

The Google ADK is designed with **interoperability** in mind. It allows you to tap into this vast ecosystem by providing simple wrappers that make it possible to use tools from other popular frameworks directly within your ADK agent. This lets you leverage the best of both worlds: the robust, scalable architecture of the ADK and the extensive tool library of the broader community.

### The Wrapper Pattern

The key to this integration is the **Wrapper Pattern**. The ADK provides special wrapper classes, like `LangchainTool`, that act as adapters.

Here's how it works:

1.  **You find a tool** you want to use from a third-party library (e.g., a Wikipedia search tool from LangChain).
2.  **You instantiate** this third-party tool according to its own library's documentation.
3.  **You "wrap"** this instance inside the corresponding ADK wrapper class (e.g., `LangchainTool(tool=your_langchain_tool_instance)`).
4.  **You add the wrapped tool** to your ADK agent's `tools` list.

The ADK wrapper handles all the translation behind the scenes. It inspects the third-party tool, extracts its name, description, and parameters, and generates the necessary schema for the Gemini LLM to understand it. When the LLM decides to call the tool, the wrapper receives the request, calls the underlying third-party tool's execution method, and then formats the result back into a standard dictionary that the ADK agent can understand.

This seamless integration means you can mix and match tools from different sources:
*   A built-in `google_search` tool.
*   A custom `get_order_status` function tool you wrote.
*   A `WikipediaQueryRun` tool from LangChain.

Your ADK agent sees them all as a unified set of capabilities, and the LLM can reason about and choose the best one for the job, regardless of where it came from.

### Why is this important?

*   **Saves Development Time:** Instead of writing your own code to connect to the Wikipedia API, you can use a pre-built, tested, and maintained tool from a library like LangChain in just a few lines of code.
*   **Access to a Huge Library:** You gain immediate access to hundreds of existing tools for a massive variety of tasks.
*   **Focus on Your Core Logic:** You can spend your time building the unique tools and business logic that are specific to your application, while relying on the community for common, general-purpose tools.

In the lab for this module, you will put this into practice by integrating a powerful web search tool from the LangChain ecosystem into your ADK agent.
