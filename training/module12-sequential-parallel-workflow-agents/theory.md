# Module 12: Orchestration with Workflow Agents: Sequential & Parallel

## Theory

### Beyond Dynamic Delegation

In the previous module, you built a multi-agent system where a coordinator `LlmAgent` dynamically decided which specialist to delegate a task to. This is a powerful pattern for handling unpredictable user requests.

However, some tasks are not unpredictable. Many business processes follow a fixed, predictable sequence of steps. For example, to process an order, you might always need to:
1.  Validate the user's input.
2.  Check for the item in an inventory database.
3.  Process the payment.
4.  Send a confirmation email.

Trying to make an `LlmAgent` follow this rigid sequence using only its `instruction` prompt can be unreliable. The LLM might try to skip steps or perform them out of order. For these situations, you need a more deterministic way to control the flow of execution.

### Deterministic Control with Workflow Agents

The ADK provides a special category of agents called **Workflow Agents** for this exact purpose. Unlike `LlmAgent`s, workflow agents do not have an LLM "brain." They are simple, deterministic controllers whose only job is to orchestrate the execution of their `sub_agents` according to a predefined logic.

This allows you to build robust and reliable multi-step processes by combining the deterministic control of a workflow agent with the intelligent reasoning of the `LlmAgent`s that it orchestrates.

In this module, we will focus on the two most fundamental workflow agents: `SequentialAgent` and `ParallelAgent`.

### `SequentialAgent`: Building Pipelines

The `SequentialAgent` is the simplest workflow agent. It executes its `sub_agents` one after another, in the exact order they are defined in the configuration. It forms the basis of a processing pipeline.

**Key Concepts:**
*   **Execution Order:** Guaranteed to be top-to-bottom.
*   **Shared State:** The `SequentialAgent` passes the *same* session state to each sub-agent in the sequence. This is the primary mechanism for passing data between steps. One agent can perform a task and save its result to the state, and the next agent in the sequence can read that result and use it as input.

**Configuration:**
To use it, you set the `agent_class` to `SequentialAgent` in your YAML file.

```yaml
agent_class: SequentialAgent
name: my_processing_pipeline
sub_agents:
  - config_path: step1_validate.yaml
  - config_path: step2_process.yaml
  - config_path: step3_report.yaml
```

### `ParallelAgent`: Concurrent Execution

The `ParallelAgent` executes all of its `sub_agents` at the same time (concurrently). This is useful when you have multiple independent tasks that can be performed simultaneously to save time. For example, fetching data from two different, unrelated APIs.

**Key Concepts:**
*   **Execution Order:** Not guaranteed. The agents run in parallel, and their execution may interleave.
*   **Shared State:** Like the `SequentialAgent`, all sub-agents in a `ParallelAgent` share the same session state. They can all read the initial state, and they can all write their results back to the state.
*   **Avoiding Conflicts:** When using a `ParallelAgent`, it's crucial to ensure that the sub-agents write their results to *different* keys in the state to avoid race conditions (where one agent's result overwrites another's).

**Configuration:**
You set the `agent_class` to `ParallelAgent`.

```yaml
agent_class: ParallelAgent
name: my_concurrent_fetcher
sub_agents:
  - config_path: fetch_weather_agent.yaml  # Writes to state['weather_data']
  - config_path: fetch_news_agent.yaml     # Writes to state['news_data']
```

In the lab for this module, you will build a simple data processing pipeline that uses a `SequentialAgent` to orchestrate multiple `LlmAgent`s.
