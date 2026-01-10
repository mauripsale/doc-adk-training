---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 8: Creating a "Researcher" Agent with Google Search Challenge

## Goal
Your task is to build and configure a new agent that can search the web to answer questions about current events.

## Requirements

1.  **Create a new agent** named `researcher_agent` using the `adk create` command, specifying the Python type.
2.  **Enable the Vertex AI API** in your Google Cloud project.
3.  **Configure the `.env` file** inside the `researcher_agent` directory to use Vertex AI, providing your project ID and a location.
4.  **Modify the `agent.py` file** (Python approach):
    *   Define an `LlmAgent` named `root_agent`.
    *   Set the `model` to `gemini-2.5-flash`.
    *   Write a clear `instruction` that directs the agent to use a search tool for any questions about recent or up-to-date information.
    *   Add the `google_search` tool to the `tools` list.
5.  **Run the agent** from your main `adk-training` directory using the `adk web` command (without specifying the agent name).
6.  **Test the agent** by asking it a question about a recent event (e.g., "Who won the last major sports championship?").
7.  **Verify** that the `google_search` tool was used by inspecting the "Trace" view in the Dev UI.

## Self-Reflection Questions
- Why is it important to explicitly instruct the agent *when* to use the `google_search` tool? What might happen if you just gave it the tool with no instructions?
- The `google_search` tool requires a Vertex AI configuration. Why do you think this is a requirement, as opposed to using a simple Google AI Studio API key?
- How does giving an agent access to real-time information fundamentally change the kinds of problems it can solve compared to an agent that only relies on its internal knowledge?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMDgtaW50cm8tdG8tdG9vbHMvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module08-intro-to-tools/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
