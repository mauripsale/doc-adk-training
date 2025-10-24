# Module 10: Introduction to Multi-Agent Systems

## Theory

### Beyond a Single Agent

So far, you've built single, specialized agents. This is a great start, but the true power of the ADK is unlocked when you begin to compose multiple agents into a **Multi-Agent System (MAS)**.

As applications grow, trying to pack all the logic, tools, and instructions into a single monolithic agent becomes difficult to manage, debug, and scale. Imagine a customer support bot that needs to handle billing, technical support, and sales. A single agent trying to do all of this would have an incredibly complex instruction prompt and a confusing mix of tools.

A much better approach is to break down the problem.

### The Power of Specialization and Collaboration

A multi-agent system is an application where different, specialized agents collaborate to achieve a larger goal. Instead of one agent that does everything, you create a team of experts:

*   One agent is an expert in billing.
*   Another is an expert in technical support.
*   A third is an expert in sales.
*   And a "manager" or "coordinator" agent whose only job is to understand the user's initial request and route it to the correct specialist.

This design pattern offers significant advantages:

*   **Modularity:** Each agent is a self-contained unit with a clear purpose. Its instructions and tools are focused on a single domain.
*   **Maintainability:** If you need to update the billing logic, you only need to modify the billing agent, without any risk of breaking the technical support functionality.
*   **Reusability:** A well-defined "Billing Agent" can be reused in other applications across your organization.
*   **Scalability:** It's easier to reason about and scale a system of smaller, collaborating components than one giant, complex agent.

### How Agents Collaborate in the ADK

The ADK provides several core mechanisms, or "primitives," that allow agents to work together.

#### 1. **Hierarchy (`sub_agents`)**
The most fundamental concept is the parent-child relationship. You can define a "parent" agent and assign it a list of `sub_agents`. This creates a tree-like structure that forms the basis for collaboration.

#### 2. **LLM-Driven Delegation (Agent Transfer)**
This is the most dynamic form of collaboration. A parent `LlmAgent` can be instructed to analyze a user's request and then **transfer** control of the conversation to the most appropriate `sub_agent`.

For this to work:
*   The parent agent needs a clear `instruction` on how to route tasks.
*   Each sub-agent needs a good `description` of its capabilities so the parent agent's LLM can make an informed choice.

#### 3. **Explicit Invocation (`AgentTool`)**
An agent can be wrapped in an `AgentTool`, which makes it look and feel like a regular function tool to another agent. A parent agent can then "call" the sub-agent to perform a task, wait for the result, and then continue its own reasoning process.

#### 4. **Shared State**
Agents in a system can communicate passively by reading and writing to the shared `session.state`. One agent can perform a task and save the result to the state, and a subsequent agent can then read that result to perform the next step in a process.

In the upcoming modules, you will get hands-on experience with these patterns, starting with the most common one: building a coordinator agent that delegates tasks to a team of specialists.
