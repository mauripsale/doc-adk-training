# Module 10: Introduction to Multi-Agent Systems

## Lab 10: Designing a Multi-Agent System

### Goal

Before writing any code, a crucial step in building a multi-agent system is to design it conceptually. In this lab, you will design a simple two-agent system on paper (or in a text file). This process of planning will make the implementation in the next module much smoother.

Our system will be a "Greeting Router." It will consist of a main router agent and one specialist agent that knows how to greet in Spanish.

### The Scenario

We want to build an agent that can handle greetings in multiple languages. A monolithic approach would require a very complex `instruction` prompt. Instead, we will create a system with specialized agents for each language, and a router to direct the user's request. For this lab, we will only design the router and the Spanish specialist.

---

### Step 1: Define the Roles and Responsibilities

First, let's define what each agent in our system will do.

#### Agent 1: The `router_agent`

*   **Purpose:** This will be our main, parent agent. Its only job is to understand the user's request and delegate the task to the correct specialist agent. It should not perform any greetings itself.
*   **Type:** `LlmAgent`. It needs the reasoning capability of an LLM to understand the user's intent.
*   **Initial Instruction Idea:**
    ```
    You are a language router. Your job is to understand which language the user wants to be greeted in and delegate to the appropriate specialist.
    If the user asks for a greeting in Spanish, you MUST delegate to the `spanish_greeter_agent`.
    ```
*   **Tools:** None. Its primary action is delegation.

#### Agent 2: The `spanish_greeter_agent`

*   **Purpose:** This is our specialist sub-agent. Its only job is to provide a friendly greeting in Spanish.
*   **Type:** `LlmAgent`.
*   **Description (for the router):** This is a critical piece of information. The `router_agent`'s LLM will read this description to understand what the `spanish_greeter_agent` is capable of. A good description would be:
    ```
    "An expert at providing friendly greetings in Spanish."
    ```
*   **Initial Instruction Idea:**
    ```
    You are a friendly assistant who only speaks Spanish.
    Your job is to greet the user warmly in Spanish. Do not say anything else.
    ```

---

### Step 2: Map the Interaction Flow

Now, let's trace the path of a user's request through our designed system.

1.  **User Input:** The user starts a conversation with the `router_agent` and says: `"Can you greet me in Spanish?"`
2.  **Router Receives:** The ADK's runner passes this input to the `router_agent`.
3.  **Router Reasons:** The `router_agent`'s LLM receives the user input, its own instruction, and the list of available sub-agents along with their descriptions.
4.  **Router Delegates:** Based on its instructions ("If the user asks for... Spanish, ...delegate to the `spanish_greeter_agent`") and the sub-agent's description ("...expert at... greetings in Spanish"), the LLM decides to perform an **agent transfer**.
5.  **Framework Transfers Control:** The ADK framework intercepts this decision and transfers control of the conversation to the `spanish_greeter_agent`.
6.  **Specialist Executes:** The `spanish_greeter_agent` now takes over. It executes its own instruction ("greet the user warmly in Spanish").
7.  **Specialist Responds:** The `spanish_greeter_agent` generates the final response to the user, such as `"¡Hola, mucho gusto!"`

---

### Step 3: Plan the File Structure

Based on our design, we can plan the files we'll need to create in the next lab.

```
adk-training/
└── greeting-agent/              <-- New project directory
    ├── .env                     <-- For API keys
    ├── root_agent.yaml          <-- This will define our router_agent
    └── spanish_greeter.yaml     <-- This will define our specialist agent
```

**`root_agent.yaml` (The Router):**
We know this file will need a `sub_agents` section to link to our specialist.
```yaml
name: router_agent
model: gemini-2.5-flash
instruction: |
  You are a language router...
sub_agents:
  - config_path: spanish_greeter.yaml
```

**`spanish_greeter.yaml` (The Specialist):**
This will be a standard agent configuration file.
```yaml
name: spanish_greeter_agent
model: gemini-1.5-flash
description: "An expert at providing friendly greetings in Spanish."
instruction: |
  You are a friendly assistant who only speaks Spanish...
```

### Lab Summary

You have successfully designed a multi-agent system on paper! This conceptual work is a vital skill for building complex, maintainable agentic applications.

You have learned to:
*   Break down a problem into specialized agent roles.
*   Define the purpose, instructions, and descriptions for each agent.
*   Map the flow of information and control between agents.
*   Plan the file structure for a multi-agent project.

In the next module, you will bring this design to life by implementing this Greeting Router system.
