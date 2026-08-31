---
sidebar_position: 37
title: "Module 37: Advanced - Building a Personalized Shopping Agent"
---

# Module 37: Advanced - Building a Personalized Shopping Agent

## Theory

### Introduction

Welcome to **Part 7: Capstone Project & Best Practices**, and the first of the two capstone-scale projects that close out the course. This is your first real chance to put nearly everything you've learned so far to work in one system: multi-agent orchestration, distributed A2A, state, tools, and multimodal input. In this advanced module, we'll build a sophisticated AI agent capable of navigating a simulated e-commerce website to help a user find and purchase a product. This agent will demonstrate how to integrate external web environments and use a combination of tools to perform complex, multi-step tasks.

### Agent Architecture

The personalized shopping agent is a **distributed multi-agent system** composed of three specialized agents communicating via the Agent-to-Agent (A2A) protocol:

1.  **Orchestrator Agent:** The main, user-facing agent. It manages the conversation, understands user intent (including multimodal image input), and delegates tasks to the appropriate specialist.
2.  **Personalization Agent:** A remote agent responsible for managing user preferences. It uses the ADK's state management features to remember information like preferred sizes, colors, and brands across sessions.
3.  **Web Agent:** A remote agent that acts as an interface to the e-commerce website. It exposes `search`/`click` as plain `FunctionTool`-wrapped Python functions, abstracting the web environment from the main orchestrator.

### Core Components

1.  **Web Environment:**
    The agent interacts with a small, self-contained mock catalog (`webshop_data.py`) vendored directly in this lab's own `web_agent` project — a handful of in-memory products with an `id`, `name`, `category`, `price`, and `description`, plus a tiny in-process "session" tracking the currently viewed product. This stands in for a real e-commerce backend without requiring any extra install: the real `web_agent_site` Gym environment used by Google's `personalized-shopping` ADK sample pulls in a heavyweight dependency chain (pyserini, torch, spacy, a multi-GB product dataset) that's disproportionate to what this lab is teaching, and the `web_agent_site` package itself doesn't exist on PyPI — see the Setup section in the lab for details.

2.  **Tools:**
    The agent is equipped with two primary tools, both plain Python functions wrapped in `FunctionTool`:
    *   **`search(keywords: str)`:** Filters the mock catalog by keyword and returns a short text listing of matching products (id, name, price).
    *   **`click(button: str)`:** Simulates clicking a product ID from the search results, or a navigation button ("Buy Now", "Back to Search"). It updates the tiny in-process session and returns a text description of the resulting page.

3.  **Prompt Engineering:**
    The agent's instruction prompt is crucial for its success. It defines a state machine-like flow that guides the agent through the shopping process:
    *   **Initial Inquiry:** Ask the user for the product they're looking for.
    *   **Search Phase:** Use the `search` tool and present the results.
    *   **Product Exploration:** Use the `click` tool to navigate to product details, descriptions, features, and reviews.
    *   **Purchase Confirmation:** Use the `click` tool to select options and confirm the purchase.
    *   **Finalization:** Inform the user that the purchase is complete.

    The prompt also includes specific instructions on how to handle the web environment's state, such as using the "`< Prev`" button to navigate back.

4.  **Artifacts (optional extension):**
    This lab's solution doesn't save artifacts — but the `web_agent`'s `click`/`search` tools are a natural place to add `tool_context.save_artifact()` calls, saving the HTML content of the current page after each action. That would let a user see the web page the agent is interacting with in the ADK's web UI, using the same pattern from Module 23.

By combining these components, we can create a powerful agent that can navigate a web environment, gather information, and interact with a user to complete a complex task.

### Key Takeaways
- This advanced challenge project integrates many concepts from the course: distributed multi-agent systems (A2A), state management, and tool abstraction.
- The architecture separates concerns into a main **Orchestrator**, a stateful **Personalization Agent**, and a **Web Agent** that abstracts the web environment.
- The agent's `instruction` is engineered to follow a state machine-like process, guiding it through the complex, multi-step task of navigating a website.
- Artifacts aren't wired up in this lab's solution, but they're a natural optional extension for visualizing the agent's interaction with the web environment (see above).
- **Abstraction via FunctionTool:** Abstracting the website behind plain `search`/`click` functions (rather than having the orchestrator reason about raw HTML or website internals directly) is a superior design because it simplifies the orchestrator's reasoning task. The LLM only needs to know about the `search(keywords: str)` and `click(button: str)` signatures, not the complex and messy details of how the webshop is actually implemented. This improves reliability and makes the system more maintainable, as changes to the web environment's internals only require updating the Web Agent's tool implementations, not the orchestrator.
- **Observability via Callbacks:** Using a `before_tool_callback` for logging separates the concern of observability from the agent's business logic. The orchestrator's core instruction remains focused on delegation, while the callback transparently intercepts and logs the action. This makes the system more maintainable, as the monitoring logic can be updated independently of the agent's reasoning.
- **Advantages of Distributed Architecture:** This distributed A2A architecture offers significant advantages over a monolithic agent. It allows for **independent scalability** (the Web Agent can be scaled separately if it's under heavy load), **modular maintenance** (changes to the website's logic only require updating the Web Agent), and **reusability** (the Personalization Agent could be reused by other agents in the organization).