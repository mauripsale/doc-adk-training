# Module 6: Introduction to Tools

## Theory

### Beyond Conversation

So far, your agent can only rely on the knowledge baked into its Large Language Model. While impressive, this has limitations: the model's knowledge is not real-time, and it can't interact with the outside world. It can *talk* about what the weather might be like, but it can't *check* the current weather.

This is where **Tools** come in. Tools are the single most important feature for building capable, useful agents. They are what give your agent superpowers, allowing it to break out of the conversational box and interact with external systems.

### What is a Tool?

In the context of the ADK, a Tool is a specific capability that you grant to an agent. It's a component that allows the agent to perform a concrete action beyond just generating text.

Think of the `LlmAgent` as the "brain" and the tools as its "hands." The brain can reason and decide what to do, but it needs hands to execute the action.

**Examples of actions a tool can perform:**
*   **Fetch real-time information:** Get the latest news, stock prices, or weather forecasts from an API.
*   **Access private data:** Look up customer information in a database or search internal company documents.
*   **Execute code:** Perform complex calculations or run a script.
*   **Interact with other services:** Send an email, book a calendar event, or control a smart home device.

### How Do Agents Use Tools?

The process of an agent using a tool is a fascinating dance between the LLM's reasoning and the structured execution of code. This is often called **Function Calling**.

1.  **User Request:** The user gives the agent a prompt (e.g., "What's the weather in Paris?").
2.  **Reasoning and Selection:** The agent's LLM analyzes the request and its own `instruction`. It looks at the list of available tools it has been given and sees one called `get_weather` that takes a `city` as an argument. It concludes that this is the right tool for the job.
3.  **Invocation:** The LLM generates a structured "function call," specifying the name of the tool to use (`get_weather`) and the arguments to pass (`city="Paris"`).
4.  **Execution:** The ADK framework receives this function call, executes the actual `get_weather` code with the provided arguments, and captures the result (e.g., `"Sunny, 22°C"`).
5.  **Observation and Final Response:** The result from the tool is sent back to the LLM. The LLM now has the information it needs and formulates a natural language response to the user (e.g., "The current weather in Paris is sunny with a temperature of 22°C.").

### Types of Tools in ADK

The ADK provides a rich and flexible ecosystem for tools, which can be categorized into three main types:

1.  **Built-in Tools:** Ready-to-use tools provided by the ADK for common tasks. The most prominent example is `google_search`, which allows your agent to perform a Google search to answer questions about recent events or topics outside its training data.
2.  **Custom Function Tools:** This is where you can define your own capabilities. You can take any Python function you write and turn it into a tool that your agent can use. This is the most common and powerful way to extend your agent.
3.  **Third-Party Tools:** The ADK is designed to be extensible, allowing you to integrate tools from other popular agent frameworks like LangChain and CrewAI.

In the following modules, you will get hands-on experience with these different types of tools, starting with the powerful and easy-to-use `google_search` tool.
