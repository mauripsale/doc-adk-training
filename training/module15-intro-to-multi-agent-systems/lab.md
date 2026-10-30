---
sidebar_position: 2
title: "Challenge Lab"
pagination_label: "Module 15: Introduction to MAS — 🧪 Challenge Lab"
---

# Lab 15: Designing a Multi-Agent System Challenge

## Goal

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
*   **Type:** **`Agent`**. It needs the reasoning capability of an LLM to understand the user's intent.
*   **Initial Instruction Idea:**
    ```
    You are a language router. Your job is to understand which language the user wants to be greeted in and delegate to the appropriate specialist.
    If the user asks for a greeting in Spanish, you MUST delegate to the `spanish_greeter_agent`.
    ```
*   **Tools:** None. Its primary action is delegation.

#### Agent 2: The `spanish_greeter_agent`

*   **Purpose:** This is our specialist sub-agent. Its only job is to provide a friendly greeting in Spanish.
*   **Type:** **`Agent`**.
*   **Description (for the router):** This is a critical piece of information -- the `router_agent`'s LLM reads this description to decide whether this specialist is the right match for a given request.
    **Your task:** write this description yourself, in one sentence, before moving on. A good description is specific and action-oriented (what does this agent actually *do*?) and would clearly distinguish it from any other specialist you might add later (say, a future `french_greeter_agent`). Jot it down here -- you'll reuse it in Step 3's plan and in the next module's implementation. (Check the `lab-solution.md` file for one example of a description that works well, once you've written your own.)
*   **Initial Instruction Idea:**
    ```
    You are a friendly assistant who only speaks Spanish.
    Your job is to greet the user warmly in Spanish. Do not say anything else.
    ```

---

### Step 2: Map the Interaction Flow

Now, let's trace the path of a user's request through our designed system.

#### Flow 1: Supported Language (Spanish)

1.  **User Input:** The user starts a conversation with the `router_agent` and says: `"Can you greet me in Spanish?"`
2.  **Router Receives:** The ADK's runner passes this input to the `router_agent`.
3.  **Router Reasons:** The `router_agent`'s LLM receives the user input, its own instruction, and the list of available sub-agents along with their descriptions.
4.  **Router Delegates:** Based on its instructions ("If the user asks for... Spanish, ...delegate to the `spanish_greeter_agent`") and the description you wrote for the sub-agent in Step 1, the LLM decides to perform an **agent transfer**.
5.  **Framework Transfers Control:** The ADK framework intercepts this decision and transfers control of the conversation to the `spanish_greeter_agent`.
6.  **Specialist Executes:** The `spanish_greeter_agent` now takes over. It executes its own instruction ("greet the user warmly in Spanish").
7.  **Specialist Responds:** The `spanish_greeter_agent` generates the final response to the user, such as `"¡Hola, mucho gusto!"`

#### Flow 2: Unsupported Language

1.  **User Input:** The user asks: `"Can you greet me in French?"`
2.  **Router Receives:** The input is passed to the `router_agent`.
3.  **Router Reasons:** The `router_agent`'s LLM analyzes the request. It sees that the user wants "French," but it looks at its list of sub-agents and sees no specialist with a description matching "French."
4.  **Router Responds Directly:** Following its instructions for unsupported languages, the `router_agent` does *not* delegate. Instead, it formulates its own response to the user.
5.  **Router's Final Response:** The `router_agent` replies: `"I'm sorry, I don't have a specialist for that language yet."`

---

### Step 3: Plan the File Structure

Based on our design, we can plan the files we'll need to create in the next lab.

```
adk-training/
└── greeting_system/              <-- New project directory
    ├── .env                      <-- For API keys
    ├── agent.py                  <-- This will define our Workflow and Router node
    ├── __init__.py               <-- Makes the directory a Python package
    └── spanish_greeter_agent.py  <-- This will define our Specialist node
```

**`agent.py` (The Router and Workflow):**
This file will need to:
1.  Import the `Agent` and `Workflow` classes.
2.  Import the `agent` object from your `spanish_greeter_agent.py` module.
3.  Define the `router` agent and register the specialist in its `sub_agents` list.
4.  Define the `root_agent` as a `Workflow` that starts with the `router`.

**`spanish_greeter_agent.py` (The Specialist):**
This file will need to:
1.  Define a standard `Agent` object.
2.  Include a clear `description` for the router.
3.  Include `instruction` that tells the agent to only greet in Spanish.

### Lab Summary

You have successfully designed a multi-agent system on paper! 
- You learned to break down a problem into specialized **Nodes**.
- You defined how nodes are registered via **`sub_agents`** and orchestrated via **`Workflow`**.
- You mapped the flow of control within a **Graph**.

In the next module, you will bring this design to life by implementing this Greeting System.

### Self-Reflection Questions
- What is the most important piece of information that allows the `router_agent` to decide which specialist to delegate to?
- How would you extend this system to support a new language, like French? What new files or modifications would you need to make?
- This lab uses LLM-driven delegation (agent transfer). What might be the advantages or disadvantages of this approach compared to the `router_agent` using an `AgentTool` to explicitly call the `spanish_greeter_agent`? (You haven't built an `AgentTool` yet -- Module 19 covers it in depth. For now, just think about the difference between a permanent, one-way *handoff* to another agent versus calling that agent like a function and getting a result back so you can keep working.)

<hr/>

### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="15">

# Lab 15 Solution: Designing a Multi-Agent System

## Goal

This lab was a conceptual design exercise. There is no single "correct" solution, but this file provides a more detailed example of the design planned in the lab, prioritizing the Python-first approach.

### Python Design (Primary Approach)

Here is a more fleshed-out version of the agent designs as they would be implemented in Python files using ADK 2.0 patterns.

#### `greeting_system/agent.py` (The Router and Workflow)

```python
from google.adk import Agent, Workflow
from . import spanish_greeter_agent

# The Router Node
router = Agent(
    name="router_agent",
    model="gemini-3.8-flash",
    instruction="""
You are a language routing specialist. Your primary function is to identify the language requested by the user and delegate the task to the correct sub-node.

Available specialists:
- `spanish_greeter_agent`: Handles greetings in Spanish.

Your rules:
1.  If the user requests a greeting in Spanish, you MUST transfer control to the `spanish_greeter_agent`.
2.  If the language is not supported, politely inform the user.
""",
    sub_agents=[spanish_greeter_agent.agent] # Crucial for discovery
)

# The System Graph
# In ADK 2.0, the Workflow orchestrates the nodes.
root_agent = Workflow(
    name="GreetingSystem",
    edges=[("START", router)]
)
```

#### `greeting_system/spanish_greeter_agent.py` (The Specialist Node)

```python
from google.adk import Agent

agent = Agent(
    name="spanish_greeter_agent",
    model="gemini-3.8-flash",
    description="This agent is an expert at providing warm greetings in Spanish.",
    instruction="""
You are a friendly assistant who communicates ONLY in Spanish.
Provide a single, warm greeting and then stop.
"""
)
```

### Self-Reflection Answers

1.  **What is the most important piece of information that allows the `router_agent` to decide which specialist to delegate to?**
    *   **Answer:** The **`description`** field of the sub-node. In the ADK 2.0 graph, when an agent performs a transfer, it looks at the descriptions of all registered `sub_agents` to decide where to route the request.

2.  **How would you extend this system to support a new language, like French? What new files or modifications would you need to make?**
    *   **Answer:** 
        1. Create `french_greeter_agent.py`.
        2. Register it in the `router_agent`'s `sub_agents` list.
        3. **Update the router's `instruction` text too, not just the `sub_agents` list.** As written, the instruction hardcodes the Spanish case ("If the user requests a greeting in Spanish, you MUST transfer control to the `spanish_greeter_agent`.") and never mentions French at all. Adding `french_greeter_agent` to `sub_agents` without touching the instruction means the router's LLM has no textual rule telling it when to use the new specialist -- it may never get routed to, even though it's technically registered. You either need to add an equivalent French rule to the instruction, or generalize the wording (e.g. "delegate to whichever specialist's description matches the requested language") so it scales without an instruction edit every time you add a language.
        4. Since we are using LLM-driven delegation, the `Workflow` graph structure itself stays the same, but the "pool" of available nodes -- and the instruction that references them -- grows.

3.  **This lab uses LLM-driven delegation (agent transfer). What might be the advantages or disadvantages of this approach compared to the `router_agent` using an `AgentTool` to explicitly call the `spanish_greeter_agent`?**
    *   **Answer:** Agent Transfer (via `sub_agents`) hands control to `spanish_greeter_agent` with no *automatic* way back -- once transferred, `router_agent` doesn't regain control the way it would with `mode="task"`. In this lab that's fine: `spanish_greeter_agent`'s instruction is to give one greeting and stop, so it's never asked to hand anything back. It's not a mechanical dead end, though -- since neither agent sets `disallow_transfer_to_parent`, `spanish_greeter_agent` could call `transfer_to_agent` back to `router_agent` if its instructions told it to; nothing in the framework blocks that path for a *local* agent. The real failure mode shows up when `router_agent` needs to consult more than one specialist to answer a single request: unless every specialist is explicitly instructed to transfer back (and does), Agent Transfer can leave `router_agent` waiting on a specialist that never hands control back within that turn -- and that risk becomes a hard guarantee, not just a prompting risk, once a specialist is a *remote* agent (a `RemoteA2aAgent` has no framework-injected way to transfer back at all). An `AgentTool(agent=spanish_greeter_agent)` sidesteps this entirely: `router_agent` calls the greeter like a function, gets its greeting back, and stays in control to make further calls or compose a combined response -- at the cost of an extra LLM reasoning step to decide when to call the tool, versus the framework handling the transfer automatically. This distinction -- and exactly how it breaks for remote specialists -- is covered in depth in Module 19.
    *   For a related question -- Agent Transfer vs. a fully **Deterministic Workflow** (extracting a routing key with no LLM reasoning at all) -- see the pattern-comparison table in Module 21.5: Agent Transfer suits natural language where the "key" isn't obvious and the LLM needs to understand intent, while a Deterministic Workflow (Module 16) is faster and more reliable when you can extract a clear key (like a language code) without an LLM reasoning step.

</SolutionVault>
