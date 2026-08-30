---
sidebar_position: 14
title: "Module 14: Integrating Third-Party Tools"
---

# Module 14: Integrating Third-Party Tools

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

Once wrapped, a third-party tool behaves just like a **custom function tool** you wrote yourself — you can freely mix multiple wrapped tools (e.g. a `WikipediaQueryRun` from LangChain alongside your own `get_order_status` function) in the same agent's `tools` list.

**Important restriction:** As Module 12 covered, a **built-in tool** like `google_search` **cannot** share an agent's `tools` list with any custom function tools — and a wrapped third-party tool counts as a custom function tool for this purpose. This is a restriction from the Gemini API itself (not the ADK): it constructs fine in Python but fails the moment the model actually runs, with `400 INVALID_ARGUMENT: Multiple tools are supported only when they are all search tools.` So an agent can have `google_search` *or* a mix of custom/third-party tools, but not both together.

If you need grounding *and* a third-party tool like Wikipedia search in the same system, use the same **sequential composition** pattern from Module 12: run a `google_search`-only agent, then feed its output into a second agent that has your wrapped third-party tool(s).

### Why is this important?

*   **Saves Development Time:** Instead of writing your own code to connect to the Wikipedia API, you can use a pre-built, tested, and maintained tool from a library like LangChain in just a few lines of code.
*   **Access to a Huge Library:** You gain immediate access to hundreds of existing tools for a massive variety of tasks.
*   **Focus on Your Core Logic:** You can spend your time building the unique tools and business logic that are specific to your application, while relying on the community for common, general-purpose tools.

In the lab for this module, you will put this into practice by integrating a powerful web search tool from the LangChain ecosystem into your ADK agent.

### Key Takeaways
- The ADK is interoperable and can integrate tools from third-party libraries like LangChain.
- The ADK uses a "Wrapper Pattern" (e.g., `LangchainTool`) to adapt third-party tools for use within an ADK agent.
- This approach saves significant development time by allowing you to leverage a vast ecosystem of pre-built, community-maintained tools.
- **Potential Risk:** Integrating third-party libraries, especially those with extensive dependencies (like LangChain), can introduce the risk of "dependency conflicts" (often called "dependency hell"), where different libraries require incompatible versions of the same underlying package.
- A wrapped third-party tool counts as a custom function tool, so it can freely mix with your own function tools — but, as in Module 12, it still **cannot** share a `tools` list with a built-in tool like `google_search`; use sequential composition if you need both.

This wraps up **Part 2: Tools & Capabilities** — your agent can now search, remember, call your own functions, and borrow tools from an entire ecosystem. In Part 3, you'll learn how to coordinate multiple specialized agents into **Multi-Agent Systems**.