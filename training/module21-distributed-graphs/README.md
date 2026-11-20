---
sidebar_position: 21
title: "Module 21: Distributed Graphs - A2A and External Nodes"
pagination_label: "Module 21: Distributed Graphs (A2A & External Nodes) — 📖 Theory & Overview"
---

# Module 21: Distributed Graphs - A2A and External Nodes

> **🧭 Where We Are in Part 3:** In **Chapters A & B (Modules 15–20)**, every agent lived inside the same Python process. Welcome to **Chapter C: Distributed MAS**! Here in **Module 21**, you connect agents running as independent network microservices across teams or clouds using the **Agent-to-Agent (A2A)** protocol, `RemoteA2aAgent`, and `AgentTool`.

![Distributed Graphs Hero (Light)](img/distributed-graphs-hero-light.webp#gh-light-mode-only)
![Distributed Graphs Hero (Dark)](img/distributed-graphs-hero-dark.webp#gh-dark-mode-only)
*Figure: Distributed cross-service multi-agent federation communicating via standard Agent-to-Agent (A2A) protocol.*


## Theory

### A2A in ADK 2.0: Distributed Graphs

Multi-agent systems don't have to live in a single process. With the **Agent-to-Agent (A2A) protocol**, you can build **Distributed Graphs**. This allows a local `Workflow` to include nodes that are physically running on different servers, in different clouds, or managed by different teams.

Think of A2A as the bridge that connects multiple independent graphs into a single "**Graph of Graphs**."

### The A2A Workflow Components

![A2A Distributed Graph Architecture (Light)](img/distributed-graphs-architecture-light.webp#gh-light-mode-only)
![A2A Distributed Graph Architecture (Dark)](img/distributed-graphs-architecture-dark.webp#gh-dark-mode-only)
*Figure: Network proxy architecture connecting local workflow runners to remote isolated A2A agent services.*


1.  **Exposing a Node (`to_a2a`)**: You can turn any `Agent` or `Workflow` into a remote service using the `to_a2a()` utility. This wraps your node in a web server (typically running on `uvicorn`) that automatically handles the A2A protocol and security.
2.  **The Agent Card**: Every A2A service exposes a "business card" at `/.well-known/agent-card.json`. This card describes the node's capabilities, description, and API endpoint so other graphs can discover it.
3.  **The Proxy Node (`RemoteA2aAgent`)**: To use a remote agent in your local graph, you use the `RemoteA2aAgent` class. This acts as a "Proxy Node"—to your local `Workflow`, it looks like a regular node, but behind the scenes, it routes all calls over the network via A2A.

```python
from google.adk import Workflow
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

# 1. Define the Proxy Node pointing to a remote service
remote_expert = RemoteA2aAgent(
    name="remote_expert",
    agent_card="http://localhost:8001/.well-known/agent-card.json",
    use_legacy=False,
)

# 2. Use it in your local Workflow
root_agent = Workflow(
    name="DistributedSystem",
    edges=[("START", remote_expert)]
)
```

### Composing Multiple Remote Agents with `AgentTool`

What if a conversational coordinator `Agent` needs to consult **two or more** remote A2A specialists in a single turn (for example, checking user preferences *and* searching a remote product catalog)?

Unlike local agents in Module 16, a remote `RemoteA2aAgent` runs in a separate process and has no built-in `mode="single_turn"` or automatic `transfer_to_agent` back to your local coordinator. If you put multiple `RemoteA2aAgent` proxies into a bare `sub_agents=[...]` list, the first hand-off is one-way — your coordinator never regains control in that turn!

The clean solution is **`AgentTool`**: wrap each `RemoteA2aAgent` inside `tools=[AgentTool(agent=...)]`. Your local orchestrator calls each remote service just like a normal function tool, gets its answer back, and **stays in full control**:

```python
from google.adk import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools.agent_tool import AgentTool

preferences_specialist = RemoteA2aAgent(
    name="preferences_specialist",
    agent_card="https://preferences-service.example.com/.well-known/agent-card.json",
    use_legacy=False,
)
catalog_specialist = RemoteA2aAgent(
    name="catalog_specialist",
    agent_card="https://catalog-service.example.com/.well-known/agent-card.json",
    use_legacy=False,
)

# AgentTool gives clean call-and-return semantics across remote A2A services!
root_agent = Agent(
    name="shopping_orchestrator",
    model="gemini-3.8-flash",
    instruction="""
    1. Call `preferences_specialist` to check what the user likes.
    2. Call `catalog_specialist` to search for matching products.
    3. Combine both results into one tailored recommendation.
    """,
    tools=[
        AgentTool(agent=preferences_specialist),
        AgentTool(agent=catalog_specialist),
    ],
)
```

### Critical Best Practice: A2A Context Handling

When a local graph calls a remote A2A node, the remote node receives the full conversation history. This can include internal orchestrator events (like node transitions) that might confuse the remote agent.

**The Solution:** Always include a specific section in your remote agent's `instruction` to ignore orchestrator-specific context.

**Remote Agent Instruction:**
```
You are an inventory & pricing specialist.

**IMPORTANT - A2A Context Handling:**
When receiving requests via the A2A protocol, ignore any internal graph transition messages. 
Focus only on the core user query and fulfill the inventory lookup directly.
```

### Advanced: A2A Reliability

ADK 2.0 also ships an improved `A2aAgentExecutor` implementation that fixes known streaming-mode issues in the legacy A2A path — message duplication, misclassified outputs, and data loss when the remote agent has nested sub-agents. It's opt-in on the client side via `use_legacy=False` (as shown above); the server detects the extension automatically, so no changes are needed on the remote node. If you ever notice duplicate messages in the Trace View while running a distributed graph, this is why — try re-running with `use_legacy=False`.

<KnowledgeCheck
  id="m21-distributed-a2a"
  question="When an orchestrator `Agent` needs to consult two separate `RemoteA2aAgent` services in the same turn and combine their answers, what is the recommended ADK 2.0 pattern?"
  options={[
    "Register both in `sub_agents=[...]` with `mode='chat'`",
    "Wrap each `RemoteA2aAgent` in `AgentTool(agent=...)` inside the orchestrator's `tools=[...]` list",
    "Hardcode raw socket connections inside the system instruction",
    "Set `output_key=None` on the remote server"
  ]}
  correctIndex={1}
  hint="Remember why bare `sub_agents` transfers to remote A2A processes cannot automatically transfer back."
  explanation="Wrapping each `RemoteA2aAgent` in `AgentTool(agent=...)` inside `tools=[...]` gives clean call-and-return tool semantics so the orchestrator stays in control across multiple remote A2A calls."
/>

### Key Takeaways
- **Distributed Intelligence**: Build modular systems where nodes are independent web services.
- **Protocol standard**: A2A uses standard HTTP and JSON (Agent Cards) for cross-platform compatibility.
- **Workflow Integration**: `RemoteA2aAgent` allows remote services to be used as standard nodes in any ADK 2.0 `Workflow`.
- **Latency awareness**: Remote nodes involve network calls; use them for heavy tasks (like complex research) where the network overhead is negligible compared to the processing time.
