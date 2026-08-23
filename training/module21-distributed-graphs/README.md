---
sidebar_position: 21
title: "Module 21: Distributed Graphs - A2A and External Nodes"
---

# Module 21: Distributed Graphs - A2A and External Nodes

## Theory

### A2A in ADK 2.0: Distributed Graphs

Multi-agent systems don't have to live in a single process. With the **Agent-to-Agent (A2A) protocol**, you can build **Distributed Graphs**. This allows a local `Workflow` to include nodes that are physically running on different servers, in different clouds, or managed by different teams.

Think of A2A as the bridge that connects multiple independent graphs into a single "**Graph of Graphs**."

### The A2A Workflow Components

1.  **Exposing a Node (`to_a2a`)**: You can turn any `Agent` or `Workflow` into a remote service using the `to_a2a()` utility. This wraps your node in a web server (typically running on `uvicorn`) that automatically handles the A2A protocol and security.
2.  **The Agent Card**: Every A2A service exposes a "business card" at `/.well-known/agent-card.json`. This card describes the node's capabilities, description, and API endpoint so other graphs can discover it.
3.  **The Proxy Node (`RemoteA2aAgent`)**: To use a remote agent in your local graph, you use the `RemoteA2aAgent` class. This acts as a "Proxy Node"—to your local `Workflow`, it looks like a regular node, but behind the scenes, it routes all calls over the network via A2A.

```python
from google.adk import Workflow
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

# 1. Define the Proxy Node pointing to a remote service
remote_expert = RemoteA2aAgent(
    name="remote_expert",
    agent_card="http://localhost:8001/a2a/research_specialist/.well-known/agent-card.json",
    use_legacy=False,
)

# 2. Use it in your local Workflow
root_agent = Workflow(
    name="DistributedSystem",
    edges=[("START", remote_expert)]
)
```

### Critical Best Practice: A2A Context Handling

When a local graph calls a remote A2A node, the remote node receives the full conversation history. This can include internal orchestrator events (like node transitions) that might confuse the remote agent.

**The Solution:** Always include a specific section in your remote agent's `instruction` to ignore orchestrator-specific context.

**Remote Agent Instruction:**
```
You are a research specialist.

**IMPORTANT - A2A Context Handling:**
When receiving requests via the A2A protocol, ignore any internal graph transition messages. 
Focus only on the core user query and fulfill the research task directly.
```

### Advanced: A2A Reliability

ADK 2.0 also ships an improved `A2aAgentExecutor` implementation that fixes known streaming-mode issues in the legacy A2A path — message duplication, misclassified outputs, and data loss when the remote agent has nested sub-agents. It's opt-in on the client side via `use_legacy=False` (as shown above); the server detects the extension automatically, so no changes are needed on the remote node. If you ever notice duplicate messages in the Trace View while running a distributed graph, this is why — try re-running with `use_legacy=False`.

### Key Takeaways
- **Distributed Intelligence**: Build modular systems where nodes are independent web services.
- **Protocol standard**: A2A uses standard HTTP and JSON (Agent Cards) for cross-platform compatibility.
- **Workflow Integration**: `RemoteA2aAgent` allows remote services to be used as standard nodes in any ADK 2.0 `Workflow`.
- **Latency awareness**: Remote nodes involve network calls; use them for heavy tasks (like complex research) where the network overhead is negligible compared to the processing time.
