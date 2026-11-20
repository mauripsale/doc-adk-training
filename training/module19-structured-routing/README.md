---
sidebar_position: 19
title: "Module 19: Structured Routing - Dictionary Edges and ctx.route"
pagination_label: "Module 19: Structured Routing (Dict Edges) — 📖 Theory & Overview"
---

# Module 19: Structured Routing - Dictionary Edges and `ctx.route`

> **🧭 Where We Are in Part 3:** In **Module 18**, you wrote `if/else` branching inside a `@node` function — powerful for multi-step chains, but because those branches live inside Python code, the static Dev UI **Graph View** only sees a single `@node` box rather than displaying every downstream specialist! Here in **Module 19**, you combine the `@node` skill you just mastered with **Dictionary Router Edges (`ctx.route`)** so every specialist branch appears explicitly on your visual workflow graph!

![Structured Routing Hero (Light)](img/structured-routing-hero-light.webp#gh-light-mode-only)
![Structured Routing Hero (Dark)](img/structured-routing-hero-dark.webp#gh-dark-mode-only)
*Figure: High-speed intent routing through structured decision dictionaries and deterministic edge resolvers.*

## Theory

### Module 18 (`if/else`) vs. Module 19 (Dictionary Edges)

Why use a Dictionary Edge instead of writing `if/else` inside `@node`?
1.  **Full Graph View Transparency:** Every target branch (`tech_agent`, `billing_agent`, `general_agent`) is wired directly in `edges=[...]`, giving architects and auditors a 1:1 visual map in the Dev UI Graph View.
2.  **Declarative Downstream Pipelines:** Each dictionary branch can continue into further static chains or `JoinNode`s (from Module 17) without writing any extra Python orchestration.
3.  **Zero Routing Hallucinations:** Combined with a Pydantic `Literal[...]` schema, your graph can only follow valid, pre-declared branches.

![Dictionary-Based Intent Routing Architecture (Light)](img/structured-routing-architecture-light.webp#gh-light-mode-only)
![Dictionary-Based Intent Routing Architecture (Dark)](img/structured-routing-architecture-dark.webp#gh-dark-mode-only)
*Figure: 4-stage pipeline showing query classification, route key emission, edge dictionary mapping, and specialist execution.*

### Router Edges (Conditional Dictionary Routing)

Think of an office **switchboard** that routes incoming requests to the right department using a simple lookup table (a Python dictionary) inside `edges`:

```python
edges=[
    ("START", switchboard_router),
    (switchboard_router, {
        "technical": tech_agent,
        "billing": billing_agent,
        "other": general_agent,
    }),
]
```

#### The Switchboard Analogy: Putting `@node` + `ctx.route` Together

Suppose a customer writes: *"I was charged twice on my invoice!"*

Gemini (`classifier_node`) is great at reading that message and replying `{"category": "billing"}`. **However, an `Agent` only generates text or JSON — it doesn't have hands to turn the switchboard dial.**

Using the exact same `@node` + `await ctx.run_node(...)` pattern you learned in **Module 18**, we write a tiny 4-line **switchboard operator** (`switchboard_router`):
1. It asks Gemini which department should handle the message (`await ctx.run_node(...)`).
2. It dials that department's extension (**`ctx.route = result["category"]`**).
3. It transfers the customer on the line (**`return node_input`**) so the specialist hears the real question, not just the word `"billing"`.

> **Think of it in one sentence:** `ctx.route` is the **extension number** you dial; `return node_input` is the **customer on the line** you connect to that extension.

```python
from pydantic import BaseModel
from typing import Literal
from google.adk import Agent, Workflow, Context
from google.adk.workflow import node

class RequestType(BaseModel):
    category: Literal["technical", "billing", "other"]

# 1. The Classifier Agent
classifier_node = Agent(
    name="intent_classifier",
    model="gemini-3.8-flash",
    instruction="Classify the request as 'technical', 'billing', or 'other'.",
    output_schema=RequestType,
)

# 2. The Switchboard Operator (@node)
@node(rerun_on_resume=True)
async def switchboard_router(ctx: Context, node_input: str):
    result = await ctx.run_node(classifier_node, node_input)  # Plain dict from output_schema
    ctx.route = result["category"]                            # Dial the extension
    return node_input                                         # Transfer the customer's prompt

# 3. The Workflow Graph
my_workflow = Workflow(
    name="SmartRouter",
    edges=[
        ("START", switchboard_router),
        (switchboard_router, {
            "technical": tech_agent,
            "billing": billing_agent,
            "other": general_agent,
        }),
    ],
)
```

#### Line-by-Line Recap

*   **`classifier_node = Agent(..., output_schema=RequestType)`**: Reads the message and returns guaranteed JSON matching `RequestType` (e.g., `{"category": "billing"}`).
*   **`@node(rerun_on_resume=True)`**: Marks the Python function as a graph step that re-runs on every new chat turn.
*   **`async def switchboard_router(ctx: Context, node_input: str):`**: Receives the workflow control panel (`ctx`) and the user's message (`node_input`).
*   **`result = await ctx.run_node(classifier_node, node_input)`**: Runs `classifier_node` and returns its JSON as a plain Python `dict` (`{"category": "billing"}`).
*   **`ctx.route = result["category"]`**: **The one new line in Module 19!** Sets the routing signal (`"billing"`), telling ADK which key in the dictionary edge to activate.
*   **`return node_input`**: Passes the customer's original message untouched to `billing_agent` (instead of overwriting it with `{"category": "billing"}`).

### Reserved Graph Keywords (`"START"` and `"END"`)
- **`"START"`**: Mandatory entry point of every `Workflow`.
- **`"END"`**: Optional explicit exit target; any node with no outgoing edges terminates its branch automatically.

<KnowledgeCheck
  id="m19-structured-routing"
  question="In a `Workflow` with a dictionary router edge `(switchboard_router, {'technical': tech_agent, 'billing': billing_agent})`, why must `switchboard_router` both set `ctx.route` AND `return node_input`?"
  options={[
    "`ctx.route` selects which dictionary key to follow, while `return node_input` forwards the user's original prompt to that chosen specialist",
    "Python functions crash if they do not return `ctx.route`",
    "Setting `ctx.route` deletes `session.state` unless `node_input` is returned",
    "ADK ignores `ctx.route` and only matches the returned string against dictionary keys"
  ]}
  correctIndex={0}
  hint="Remember the Switchboard Analogy: extension number vs. customer on the line."
  explanation="ADK separates routing from data flow: `ctx.route` tells the `Workflow` which branch in the dictionary to activate, while the function's return value becomes the input message received by that target node."
/>

### Key Takeaways
- **Dictionary Router Edges** make conditional 1-to-N branching 100% visible in `edges` and in the Dev UI Graph View.
- **`ctx.route`** selects the dictionary branch (extension number), while **`return node_input`** forwards the user's message (customer on the line).
- Use **Module 18** (`if/else` in `@node`) for dynamic multi-step compositions, and **Module 19** (Dictionary Edges) for clean, auditable graph switches!
