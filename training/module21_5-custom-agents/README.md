---
sidebar_position: 21.5
title: "Module 21.5: Dynamic Workflows - Building Programmable Orchestrators"
---

# Module 21.5: Dynamic Workflows - Building Programmable Orchestrators

## Theory

### The Evolution: From Hierarchy to Graphs

In ADK 1.x, agents were organized in a simple parent-child hierarchy. Orchestration was achieved by making one agent call another.

**ADK 2.0** introduces a more powerful paradigm: the **Workflow Runtime**. In this model, your application is a **Graph** where every agent, tool, or Python function is a **Node**. 

While standard workflow agents (`SequentialAgent`, `ParallelAgent`) provide predefined graph structures, **Dynamic Workflows** give you the full power of Python to define your own routing logic on the fly.

### Dynamic Workflows with `@node`

A Dynamic Workflow is a special type of node that can execute other nodes programmatically. You define it using the **`@node`** decorator and the **`Context`** object.

To build a programmable orchestrator in ADK 2.0, you follow these principles:
1.  **Define your components as Nodes:** Use `Agent`, `FunctionTool`, or standard functions decorated with `@node`.
2.  **Create an orchestrator function:** Decorate it with `@node(rerun_on_resume=True)`.
3.  **Use `ctx.run_node()`:** This method is the "heartbeat" of ADK 2.0. It executes a node and returns its output directly to your code.

```python
from google.adk import Agent, Workflow, Context, Event
from google.adk.workflow import node

# 1. Define specialist agents (Nodes)
researcher = Agent(name="researcher", ...)
writer = Agent(name="writer", ...)

# 2. Build the Dynamic Orchestrator
@node(rerun_on_resume=True)
async def newsletter_workflow(ctx: Context, topic: str):
    # Step A: Run the researcher node
    # ADK 2.0 returns the result directly! No more digging into session state.
    research_notes = await ctx.run_node(researcher, topic)
    
    # Step B: Run the writer node using the output from the previous step
    final_article = await ctx.run_node(writer, research_notes)
    
    return final_article

# 3. Register the workflow as the ROOT_AGENT
root_agent = Workflow(
    name="NewsletterSystem",
    edges=[("START", newsletter_workflow)]
)
```

### Why `@node` is superior to legacy `BaseAgent`

1.  **Pythonic Control Flow:** You can use standard `if/else` statements, `for` loops, and `try/except` blocks to manage your agents.
2.  **Simplified Data Passing:** `ctx.run_node()` returns data directly. You don't need to manage `output_key` and `ctx.session.state` manually for internal routing.
3.  **Automatic Checkpointing:** If a workflow is interrupted (e.g., waiting for human input), the ADK automatically saves the progress of each node. When resumed, successful nodes are skipped, and execution continues exactly where it left off.
4.  **Observability:** The Workflow Runtime tracks every node execution, providing detailed logs and traces of how data flowed through your graph.

### The `Context` Object

The `Context` (or `ctx`) is your gateway to the workflow engine. Its most important method is `run_node(node, input_data)`. 
*   If you pass an **Agent** to `run_node`, the ADK executes the full agentic loop (reasoning + tools) and returns its final response.
*   If you pass a **Function**, the ADK executes the code and returns the value.

### Key Takeaways
- **ADK 2.0** uses a graph-based Workflow Runtime.
- **Dynamic Workflows** allow defining complex orchestration logic using standard Python code decorated with `@node`.
- **`ctx.run_node()`** is the primary way to execute other agents or functions within a workflow.
- **Automatic State Management:** The framework handles checkpointing and resumes automatically, ensuring your complex workflows are robust and reliable.
