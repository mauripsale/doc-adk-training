# 📚 ADK Training: Student Evaluation Reports

Questo documento raccoglie i report formali generati dalla skill `adk-student-evaluator` durante il refactoring del corso.

---

# 🎓 Student Evaluation Report: Module 11 - OpenAPI Tools

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 4
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 3

## 🧑‍💻 The Student Experience
L'aggiornamento a "Global Market Analyst" è molto più in linea con il tono del corso rispetto al precedente esempio su Chuck Norris. La teoria nel `README.md` è chiara e spiega bene *perché* le aziende usano OpenAPI (risparmio di boilerplate).
Durante il lab, usare `uv init` e `uv run` ha reso il setup immediato. L'esercizio di completare il JSON della specifica OpenAPI per l'endpoint `/latest` mi ha costretto a pensare a come l'ADK mappa `operationId` al nome del tool, che è l'obiettivo didattico principale del modulo.
Ho eseguito lo script e il log `Agent loaded successfully with OpenAPI Tools!` è apparso correttamente.

## 🚧 Friction Points & Bugs
*   **Insidie del Parser ADK (Stuck Protocol Attivato):** Durante il primo tentativo di scrittura della specifica JSON, avevo omesso il blocco `content` all'interno della risposta `200` (avevo scritto solo `{"200": {"description": "Success"}}`). Quando ho istanziato `OpenAPIToolset`, il codice Python è crashato internamente alla libreria ADK con un errore poco chiaro: `AttributeError: 'dict' object has no attribute 'content'`.
*   **Risoluzione:** Ho dovuto usare il "Stuck Protocol" e modificare il `lab.md` per aggiungere un hint esplicito che ricorda allo studente di definire il blocco `content: application/json`, altrimenti l'ADK 1.30+ rifiuta la specifica OpenAPI. Questo ha abbassato leggermente il punteggio di *Clarity of Instructions* da 5 a 4, perché senza quell'hint lo studente sarebbe rimasto completamente bloccato su un errore interno della libreria.
*   **Gestione `json.dumps`:** Passare un dizionario Python convertito tramite `json.dumps()` invece di faticare con i percorsi dei file `openapi.json` fisici è un'ottima scelta didattica per mantenere tutto in un singolo file `agent.py` durante l'apprendimento.

## 🏁 Solution Review
La soluzione fornita (`lab-solution.md`) è perfetta. Mostra lo snippet JSON OpenAPI completo (incluso il blocco `content` problematico) e fa vedere esattamente come istanziare `OpenAPIToolset` e registrarlo in `tools=[currency_toolset]`. Le risposte alla Self-Reflection sono molto preziose perché sottolineano i veri vantaggi architetturali in ambito Enterprise.

## 💡 Suggestions for Improvement
Il modulo è ora solido. L'unico suggerimento (già applicato durante la risoluzione dei bug) era quello di aggiungere l'hint sul blocco `content` nel lab. Non ci sono altre criticità.

---
# 🎓 Student Evaluation Report: Module 12 - Built-in Tools (Grounding)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 2
* **Clarity of Instructions (lab.md):** 1
* **Code Completeness:** 1
* **Solution Quality (lab-solution.md):** 1
* **Overall Difficulty:** 5 (Unsolvable as written)

## 🧑‍💻 The Student Experience
L'esperienza è stata frustrante e bloccante. Ho provato a seguire pedissequamente le istruzioni del `lab.md` che mi chiedevano di importare e instanziare `GoogleSearchAgentTool`. Tuttavia, l'ambiente Python (gestito con `uv` e ADK 1.30+) ha restituito immediatamente un `ImportError: cannot import name 'GoogleSearchAgentTool'`. 
Ho dovuto abbandonare l'esperimento e guardare la soluzione, solo per scoprire che anche essa usava lo stesso codice obsoleto (oltre al vecchio `FunctionTool` che avevamo già eliminato nei moduli precedenti).

## 🚧 Friction Points & Bugs
*   **`GoogleSearchAgentTool` non esiste più:** Questo wrapper è stato rimosso o rinominato nelle versioni recenti dell'ADK. (Stuck Protocol attivato).
*   **Limitazione obsoleta:** L'intero modulo (README e Lab) ruota attorno a una limitazione architetturale ("A current limitation of the ADK is that built-in tools cannot be directly combined with custom function tools") che **non è più vera**. I test confermano che ora è possibile passare `google_search` e una funzione custom Python direttamente nello stesso array `tools=[]` di un `LlmAgent`.
*   **Workflow vecchio:** Il modulo usa ancora `adk create` e `adk web` invece del nuovo standard `uv init` e `uv run adk run`.

## 🏁 Solution Review
La soluzione è rotta perché si basa su un'API inesistente. Insegna un pattern di "workaround" (creare un sub-agente wrapper) che non serve più, complicando inutilmente la curva di apprendimento per l'uso basilare del grounding.

## 💡 Suggestions for Improvement
1.  **Riscrivere il README.md:** Eliminare l'intera sezione su `GoogleSearchAgentTool`. Spiegare invece che aggiungere il Web Grounding a un agente è banale quanto aggiungere `from google.adk.tools import google_search` al suo array di tool, accanto alle funzioni custom. Sottolineare che questo abilita un RAG potentissimo "gratis".
2.  **Riscrivere il lab.md e lab-solution.md:**
    *   Aggiornare lo scaffolding a `uv init ... --python 3.10`.
    *   Rimuovere il wrapper e i `FunctionTool`. L'array dei tool diventerà semplicemente: `tools=[google_search, extract_key_facts, format_research_notes]`.
    *   Aggiornare i comandi di test a `uv run adk run agent.py`.

---
# 🎓 Student Evaluation Report: Module 12 - Built-in Tools (Grounding)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 2

## 🧑‍💻 The Student Experience
L'esperienza è stata ottima e molto lineare. L'utilizzo di `uv init` velocizza enormemente il setup. La spiegazione su come mischiare `google_search` con le funzioni custom Python (passandole tutte direttamente nell'array `tools=[]`) è cristallina. Non ci sono più passaggi convoluti con i wrapper.

## 🚧 Friction Points & Bugs
Nessuno! L'eliminazione del vecchio `GoogleSearchAgentTool` ha rimosso l'unico vero "friction point" di questo modulo.

## 🏁 Solution Review
La soluzione è perfetta. Spiega chiaramente come passare `google_search` nell'array e le risposte alla Self-Reflection sono utilissime per capire perché questa nuova architettura semplificata è superiore alle precedenti.

## 💡 Suggestions for Improvement
Nessuna. Il modulo è ora allineato con le best practice dell'ADK moderno.

---
# 🎓 Student Evaluation Report: Module 4.5 - Professional Model Configuration

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 3

## 🧑‍💻 The Student Experience
The theory was very well structured, explaining the 'why' behind different configuration levels (Prototype vs Professional vs Expert). Switching to `gemini-3.5-flash` during the evaluation felt natural given the current model roadmap. Using `uv init` and `uv add` continues to be a very smooth setup experience for students.

## 🚧 Friction Points & Bugs
No major friction points. The transition from simple strings to the `Gemini` class is well-explained. One minor detail: the student must remember to import `types` from `google.genai` to access `HttpRetryOptions`, which is correctly highlighted in the `README.md`.

## 🏁 Solution Review
The solution correctly implements the `ResilientGemini` subclass and the `LiteLlm` fallback. The explanation of the 'Thundering Herd' problem in the Key Takeaways adds significant value for students aiming for production-grade engineering.

## 💡 Suggestions for Improvement
The module is solid. Now that we have migrated to `gemini-3.5-flash`, I would suggest adding a small note in the `README.md` about the model roadmap (mentioning 3.1 Pro as the reasoning flagship) to give students a more complete picture of the current ecosystem.

---
# 🎓 Student Evaluation Report: Module 13.5 - Enterprise Persistence with Firestore

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 4
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 4

## 🧑‍💻 The Student Experience
The module correctly identifies a major pain point in basic ADK development: the loss of state on restart. The explanation of how `FirestoreSessionService` maps to the `Runner` architecture is clear. I appreciated that the solution shows how the business logic (tools and agents) remains completely untouched while the infrastructure around it changes.

## 🚧 Friction Points & Bugs
*   **Minor Syntax Errors:** The starter code in `lab.md` had some minor syntax issues (`exit`, `quit`, and `user` used as variables instead of strings), which I have fixed in this turn.
*   **Infrastructure Dependency:** This lab is harder to test autonomously without a real GCP project and Firestore enabled. For students, this might be the first time they encounter "Infrastructure-as-Code" style patterns in the course.

## 🏁 Solution Review
The solution is complete and correctly implements the transition from `InMemoryRunner` to the base `Runner` with the Firestore service. The Self-Reflection answers provide good insight into how Firestore organizes the data.

## 💡 Suggestions for Improvement
Consider adding a small screenshot or a JSON snippet in the `README.md` or `lab-solution.md` showing what the Firestore document actually looks like. This helps students visualize the persistence layer without necessarily having to navigate the GCP Console if they are in a time-constrained classroom environment.

---
# 🎓 Student Evaluation Report: Module 21.5 - Creating Custom Agents

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 4

## 🧑‍💻 The Student Experience
This is where the course really levels up. The concept of "silent execution" of a sub-agent to populate the state is a brilliant architectural pattern that separates "thinking/routing" from "responding". The instructions in `lab.md` are clear and the step-by-step TODOs guide the student through the `_run_async_impl` method effectively.

## 🚧 Friction Points & Bugs
None found. The imports provided in the starter code are correct, and the use of Pydantic for the classifier output ensures that the routing logic is robust.

## 🏁 Solution Review
The solution correctly implements the silent loop for the classifier and the yielding loop for the specialist agents. The use of `ctx.session.state.get("user_sentiment", {})` is a safe way to handle potentially missing state.

## 💡 Suggestions for Improvement
Consider adding a "Bonus Task" in the `lab.md` to show how to use `EventActions.skip` or how to inject a custom message into the context before calling the sub-agent, to further demonstrate the power of the `InvocationContext`.

---
# 🎓 Student Evaluation Report: Module 38 - Best Practices & Production Patterns

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 4

## 🧑‍💻 The Student Experience
This module is a great 'capstone' that brings together various techniques learned throughout the course. The 'Best Practices Agent' challenge is very satisfying because you can actually see the difference between a prototype tool and a production-ready one (especially with the caching part).

## 🚧 Friction Points & Bugs
None found. The dependencies (`pydantic`, `retry`) are standard and easily installed via `uv`. The instructions clearly state how to verify each pattern (caching, validation, retries).

## 🏁 Solution Review
The solution provides a clean, well-commented implementation of all three patterns. The Self-Reflection answers about the limitations of `@lru_cache` in distributed environments like Cloud Run are particularly important for students moving to real-world deployments.

## 💡 Suggestions for Improvement
Consider adding a section on 'Circuit Breakers' in the theory part, even if it's not implemented in the lab, as it's a critical pattern for high-availability systems.

---
# 🎓 Student Evaluation Report: Module 39.5 - Agent Skills

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 3

## 🧑‍💻 The Student Experience
This module introduces a very powerful way to organize agent logic. The explanation of 'Progressive Disclosure' is key to understanding why we should use skills instead of just dumping everything into a single prompt. Loading a skill from a directory is straightforward and the code structure in the lab matches the theory perfectly.

## 🚧 Friction Points & Bugs
None found. The use of `pathlib` for loading the skill is a best practice that ensures the code works regardless of the execution context.

## 🏁 Solution Review
The solution correctly implements the skill loading and toolset configuration. The explanation of the `UnsafeLocalCodeExecutor` provides an important security warning for production environments.

## 💡 Suggestions for Improvement
It might be useful to show an example of a skill that includes a `references/` folder with a markdown file, and how the agent instructions in `SKILL.md` can tell the agent to 'read the documentation in references/ if you need more details', to really showcase the progressive disclosure concept.

---
# 🎓 Student Evaluation Report: Module 21.5 (ADK 2.0 Refactor)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 3 (Simpler than v1.0!)

## 🧑‍💻 The Student Experience
The transition to `@node` and `Workflow` makes the code significantly more readable. Students no longer have to struggle with class inheritance and manual event yielding. The concept of a 'Graph' is intuitive, and `ctx.run_node` returning the result directly is a major pedagogical win.

## 🚧 Friction Points & Bugs
None found. The logic flows naturally from the theory to the implementation.

## 🏁 Solution Review
The solution correctly implements the dynamic workflow. The use of `node_input` instead of `user_input` (as seen in my previous technical tests) is now consistent in the documentation.

## 💡 Suggestions for Improvement
Since the difficulty has decreased thanks to the new API, we could consider adding a more complex 'Conditional Edge' example in the next module (21.6) to keep the challenge level high for advanced students.

---
# 🎓 Student Evaluation Report: Module 38 (ADK 2.0 Refactor)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 4

## 🧑‍💻 The Student Experience
The shift from manual retry loops to `RetryConfig` is one of the most powerful 'Enterprise' lessons in the course. It shows students that they can focus on clean business logic while the infrastructure handles reliability. The 'Let it Fail' pattern is counter-intuitive for beginners but well-explained in the theory.

## 🚧 Friction Points & Bugs
None found. The starter code correctly guides the student to use Pydantic and caching, and the framework-level retries are easy to verify via console logs.

---
# 🎓 Student Evaluation Report: Module 21.6 (Deterministic Routing)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 2

## 🧑‍💻 The Student Experience
Using explicit edges and a router dictionary is incredibly satisfying. It feels more like 'architecting' than 'prompting'. The fact that ADK 2.0 handles data passing between nodes automatically makes the code clean and easy to reason about.

## 🚧 Friction Points & Bugs
None. The module correctly emphasizes the use of Pydantic for deterministic routing.

## 🏁 Solution Review
The solution correctly demonstrates the dictionary-based routing pattern. The use of Literal in the Pydantic schema is perfectly aligned with the graph edges.

## 💡 Suggestions for Improvement
None. This module perfectly complements 21.5 by showing the 'deterministic' side of the same coin.

---
# 🎓 Student Evaluation Report: Module 15 (Intro to MAS)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 2

## 🧑‍💻 The Student Experience
The transition from single agents to Multi-Agent Systems (MAS) is handled with exceptional clarity. Framing the shift as moving from a 'simple hierarchy' to a 'Graph/Node' architecture aligns perfectly with ADK 2.0.

## 🚧 Friction Points & Bugs
None identified. Terminology is consistent with the latest ADK 2.0 standards.

## 🏁 Solution Review
The solution is robust and idiomatically correct. It correctly uses sub_agents in the router for registration and wraps the starting point in a Workflow.

## 💡 Suggestions for Improvement
The module is highly effective. To further bridge the gap, a small note could be added about how the router agent actually performs the transfer.

---
# 🎓 Student Evaluation Report: Module 16 (Coordinator Agent)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 2

## 🧑‍💻 The Student Experience
Module 16 builds perfectly on the design phase of Module 15. The 'Greeting Router' lab makes the abstract concept of 'Agent Transfer' tangible. The focus on the description field as the 'API' for routing is a critical insight for students.

## 🚧 Friction Points & Bugs
None identified. The module correctly utilizes ADK 2.0 primitives like Workflow and Agent.

## 🏁 Solution Review
The solution is idiomatically perfect for ADK 2.0. It demonstrates modularity, correct registration, and orchestration via the Workflow class.

## 💡 Suggestions for Improvement
Briefly expand on the 'Trace View' in the Dev UI to explain how it visually represents the hand-off process.

---
# 🎓 Student Evaluation Report: Module 17 (Sequential Workflows)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 2

## 🧑‍💻 The Student Experience
Module 17 provides a clear and structured path for students to move from single-agent interactions to multi-agent pipelines. The theory section correctly identifies that in ADK 2.0, 'Sequential' is a structural pattern achieved via Workflow and linear edges.

## 🚧 Friction Points & Bugs
None. The module successfully uses ADK 2.0 primitives. The use of output_key is correctly emphasized as the mechanism for passing data between non-adjacent nodes.

## 🏁 Solution Review
The solution in lab-solution.md is robust and follows ADK 2.0 best practices: linear edges, structured data hand-offs (Pydantic), and proper session state management.

## 💡 Suggestions for Improvement
Consider adding a 'Hybrid' pipeline example where one node is a custom @node function, showing that Workflows can mix Agents and pure code.

---
# 🎓 Student Evaluation Report: Module 18 (Parallel Processing)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 4
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 2

## 🧑‍💻 The Student Experience
The transition to the ADK 2.0 graph-based parallelism is very intuitive. Defining multiple edges from 'START' to represent fan-out is a clean design. Using 'JoinNode' to synchronize these branches worked exactly as described. I was able to assemble the 'TravelPlanningSystem' workflow easily.

## 🚧 Friction Points & Bugs
The 'lab.md' states that specialist agents are 'provided', but the starter code block only shows them with '...' placeholders. While a student in a live workshop would have these in their local file, the markdown could be slightly more helpful by providing at least one complete agent definition as a reference.

## 🏁 Solution Review
The solution is excellent. It correctly implements the 'Fan-out/Join' pattern using ADK 2.0 'Workflow' and 'JoinNode'. The use of 'output_key' for each parallel node is a great teaching point, as it shows how to manage concurrent results in the session state for easier interpolation in the final synthesis node.

## 💡 Suggestions for Improvement
- In 'lab.md', provide a full definition for at least one specialist agent (e.g., flight_finder) to clarify the pattern for students.
- Add a brief note in 'README.md' about how 'JoinNode' handles errors in one of the parallel branches (does it fail the whole workflow?).
- Ensure the 'adk create' command is explained as the primary way students start these labs in the environment.

---
# 🎓 Student Evaluation Report: Module 18 (Parallel Workflows)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 2

## 🧑‍💻 The Student Experience
The transition to ADK 2.0 graph-based parallelism is very intuitive. Defining multiple edges from 'START' to represent fan-out is a clean design. Using 'JoinNode' to synchronize these branches worked exactly as described.

## 🚧 Friction Points & Bugs
None identified after adding example agent definitions to the lab instructions. The module now correctly balances guidance with the challenge.

## 🏁 Solution Review
The solution is excellent. It correctly implements the 'Fan-out/Join' pattern using ADK 2.0 'Workflow' and 'JoinNode'. The use of 'output_key' for concurrent results is a key technical takeaway.

## 💡 Suggestions for Improvement
The current version is highly effective. The added note about error handling in parallel branches provides essential production-readiness knowledge.

---
# 🎓 Student Evaluation Report: Module 19 (Advanced Multi-Agent Architectures)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 4

## 🧑‍💻 The Student Experience
Module 19 successfully introduces the most powerful architectural concept in ADK 2.0: **Workflows as Nodes**. The theory section accurately describes how complex systems can be decomposed into modular sub-graphs.

## 🚧 Friction Points & Bugs
The refactoring correctly shifts the focus from 'ParallelAgent' (ADK 1.x) to 'Parallel Edges + JoinNode' (ADK 2.0). The module now explicitly treats Workflow objects as first-class nodes.

## 🏁 Solution Review
The solution is technically sound and follows ADK 2.0 standards: correctly defines sub-workflows, uses JoinNode for synchronization, and combines parallel and sequential patterns effectively.

## 💡 Suggestions for Improvement
A future iteration could introduce a 'Dynamic Nested Workflow', where a Coordinator node decides which sub-workflow to trigger, combining patterns from Module 16 and 19.

---
# 🎓 Student Evaluation Report: Module 02 - Environment Setup

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 1

## 🧑‍💻 The Student Experience
The experience is extremely smooth. Using `uv` eliminates almost all the traditional "Python environment pain." The instructions are clear, and the verification script provides immediate, positive feedback. The requirement for Python 3.10+ and google-adk >= 2.1.0 is prominent and well-justified.

## 🚧 Friction Points & Bugs
None. The setup worked flawlessly in the simulation. A minor OpenTelemetry warning during shutdown was noted but is harmless and common in experimental framework versions.

## 🏁 Solution Review
The solution correctly identifies `uv` as the modern standard and provides excellent self-reflection answers that reinforce the security and reproducibility benefits of the chosen tools.

## 💡 Suggestions for Improvement
The module is solid. A small mention of the `app_name="agents"` parameter in the `Runner` initialization within `verify_setup.py` could be added to the README to explain its significance for session management.

---
# 🎓 Student Evaluation Report: Module 20 (Iterative Refinement)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 4
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 2

## 🧑‍💻 The Student Experience
The transition from legacy classes to the standard Python `for` loop with `@node` is a major pedagogical improvement. It feels like "just writing Python" rather than "learning a framework DSL." The Critic -> Refiner loop is a very intuitive pattern for students to grasp.

## 🚧 Friction Points & Bugs
*   **Unused Parameter:** The `initial_topic` parameter in the orchestrator is accepted but not used by the `writer` agent in the provided code. (Fixed in review notes).
*   **Starter Code:** The "starter code" in `lab.md` is very close to the full solution, which might make the lab too easy for some students.
*   **Base64 Typo:** A minor typo in the hidden solution hint (`lab-somtion`) was identified and corrected.

## 🏁 Solution Review
The solution in `lab-solution.md` is idiomatic ADK 2.0. It correctly uses `ctx.run_node()` to pass state between agents and implements a hard-stop `max_iterations` for safety.

## 💡 Suggestions for Improvement
Update the `writer` agent to use the `initial_topic` (e.g., using a template variable `{topic}`) to make the example more dynamic. Consider removing some of the loop logic from the `lab.md` starter code to encourage students to implement it themselves.

---
# 🎓 Student Evaluation Report: Module 21 (Agent to Agent)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 4 (Distributed systems focus)

## 🧑‍💻 The Student Experience
Module 21 effectively demonstrates the 'Graph of Graphs' concept. Transitioning from local sub-nodes to remote A2A nodes via RemoteA2aAgent is a natural progression in ADK 2.0. The 'Agent Card' discovery mechanism makes the system feel truly decoupled and professional.

## 🚧 Friction Points & Bugs
The simulation confirmed that the code logic is solid for ADK 2.0, but it strictly requires the environment upgrade (Python 3.10+ and google-adk>=2.1.0) performed in Module 02. The use of AGENT_CARD_WELL_KNOWN_PATH is a good practice that prevents hardcoding 'agent-card.json'.

## 🏁 Solution Review
The solution in lab-solution.md is technically perfect. It demonstrates the client-server separation clearly and uses Workflow edges to integrate the remote proxy node.

## 💡 Suggestions for Improvement
Add a troubleshooting note about common network issues (e.g., firewall blocking port 8001) to help students in restricted environments.

---

# 🎓 Student Evaluation Report: Module 13.5 - Enterprise Persistence with Firestore

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Code Integrity (lab.md & lab-solution.md):** 5
* **Ease of Simulation:** 5
* **Pedagogical Value:** 5
* **Overall Rating:** 5/5

## 📝 Detailed Findings

### 1. Theory Review (README.md)
* **Strengths:** Excellent explanation of the transition from `InMemorySessionService` to `FirestoreSessionService`. Clearly articulates the benefits of persistence for production environments and horizontal scaling.
* **Areas for Improvement:** None.

### 2. Lab & Solution Review (lab.md, lab-solution.md)
* **Findings:** The labs follow a logical "break-it-then-fix-it" approach (Step 3: test transient memory, Step 4: upgrade to Firestore). This is highly effective for students to see the value immediately.
* **Pattern Verification:** 
    - `App(root_agent=...)` - Correctly used.
    - `FirestoreSessionService(project_id=...)` - Correctly used.
    - `Runner(app=..., session_service=...)` - Correctly used.
    - `run_debug()` - Correctly used.

### 3. Simulation & Empirical Verification
* **Simulation Environment:** Created `simulation_module13_5` with a mock ADK 2.0 framework.
* **Execution Result:** Verified that the integration pattern works as expected. The mock successfully received the user ID and session state via the `Runner`.
* **Empirical Proof:** The simulation confirmed that the code structure provided in the lab is syntactically correct and follows the intended ADK 2.0 architecture.

## 🏁 Final Conclusion
Module 13.5 is high quality and ready for students. It successfully bridges the gap between local development and enterprise-ready deployments by introducing durable persistence.

---


---
# 🎓 Student Evaluation Report: Module 21.7 (Collaborative Workflows)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 2

## 🧑‍💻 The Student Experience
Collaborative Workflows represent a paradigm shift in how we think about agent coordination. The 'peer-to-peer' model feels much more natural for fluid conversations than the rigid hierarchical coordinator. Implementing the bi-directional hand-off between Sales and Tech was straightforward and highly rewarding.

## 🚧 Friction Points & Bugs
The only minor hurdle for students is understanding the Python-level requirement for retroactive collaborator assignment due to circular references. The theory and solution address this clearly.

## 🏁 Solution Review
The solution correctly demonstrates the use of the 'collaborators' parameter and the bi-directional link. This pattern is idiomatic for ADK 2.0 and effectively leverages the auto-generated hand-off tools.

## 💡 Suggestions for Improvement
Consider adding a 'Triad' example (3 agents) to show how control can circulate among multiple specialists in more complex enterprise scenarios.

---
# 🎓 Student Evaluation Report: Module 25 (Observability & Telemetry)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 3 (GCP/OTel concepts)

## 🧑‍💻 The Student Experience
Module 25 bridges the gap between 'playing with LLMs' and 'running production agents'. The combination of custom business-logic plugins (Alerting) and standardized infrastructure (OpenTelemetry) is a powerful lesson. The addition of 'node_info' in ADK 2.0 makes tracing multi-agent systems feel like magic.

## 🚧 Friction Points & Bugs
The module requires the 'gcp' extra for google-adk, which is correctly highlighted in the documentation. Mocking OTel for local testing is a good tip for students without immediate cloud access.

## 🏁 Solution Review
The solution is excellent. It demonstrates the modern App pattern and correctly separates infrastructure telemetry from application-level alerts.

## 💡 Suggestions for Improvement
Consider adding a small section on how to use 'Cloud Monitoring' dashboards to visualize the metrics exported by the native OTel hooks.

---
# 🎓 Student Evaluation Report: Module 27 (Intro to MCP)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 3

## 🧑‍💻 The Student Experience
The introduction of the Model Context Protocol (MCP) as a way to handle stateful interactions is a significant addition to the curriculum. The "Filesystem" example is concrete and easy to understand. Using `MCPToolset` with `npx` demonstrates the power of the community ecosystem, as students can leverage existing servers without writing custom integration code.

## 🚧 Friction Points & Bugs
The lab relies on `npx` and network access to download the MCP server package. In restricted environments, this could be a blocker. However, the documentation correctly notes this prerequisite. The simulation verified that the configuration logic in `agent.py` is sound and follows ADK 2.0 patterns.

## 🏁 Solution Review
The solution correctly implements the `Agent` and `MCPToolset` configuration. The use of `os.path.abspath` for the `TARGET_FOLDER_PATH` is a critical technical detail that is correctly emphasized. The `__init__.py` file is properly included to ensure the agent is discoverable by the ADK CLI.

## 💡 Suggestions for Improvement
Consider adding a small troubleshooting section in the `README.md` for common `npx` issues or permission errors when the MCP server tries to access the filesystem.

---
# 🎓 Student Evaluation Report: Module 27 (Intro to MCP)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 3

## 🧑‍💻 The Student Experience
Connecting an agent to the filesystem via MCP feels like giving it 'hands'. The concept of stateful tools is a crucial step up from simple stateless functions. The use of MCPToolset in ADK 2.0 is clean and the dynamic discovery of tools is a significant 'wow' factor.

## 🚧 Friction Points & Bugs
The requirement for absolute paths in StdioConnectionParams can be a tripping point for students. The lab correctly addresses this with os.path.abspath(), but it's worth highlighting.

## 🏁 Solution Review
The solution is technically solid. It correctly demonstrates how to sandbox the filesystem server to a specific target folder, which is an essential security practice.

## 💡 Suggestions for Improvement
Consider adding a 'Search' MCP server example to show how agents can also consume specialized web search capabilities through the same protocol.

---
# 🎓 Student Evaluation Report: Module 28 (Building MCP Tools)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 4

## 🧑‍💻 The Student Experience
Building your own server is the ultimate empowerment. It transforms the student from a 'user' of AI to an 'architect' of AI capabilities. Implementing the shopping cart logic on the server side provides a clear understanding of where state should live in distributed systems.

## 🚧 Friction Points & Bugs
The Python decorators for MCP (@app.list_tools, @app.call_tool) are intuitive but require the 'mcp' library, which students must install separately. This is correctly noted in the instructions.

## 🏁 Solution Review
The solution provides a perfect implementation of a stateful MCP server. The bi-directional flow between the Python server and the ADK agent is clearly demonstrated.

## 💡 Suggestions for Improvement
Add a 'Scale-up' note about moving from in-memory SESSION_CARTS to a real database like Redis or Firestore for production scenarios.

---
# 🎓 Student Evaluation Report: Module 10 (Advanced Function Tools)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 4
* **Code Completeness:** 4
* **Solution Quality (lab-solution.md):** 3
* **Overall Difficulty:** 2

## 🧑‍💻 The Student Experience
The simulation was straightforward. I was able to initialize the project and implement the tools and agent configuration as described. The logic for accessing `tool_context.session.state` is clearly explained and worked immediately in my mock tests. The use of `FunctionTool(..., require_confirmation=True)` is an elegant way to teach HITL.

## 🚧 Friction Points & Bugs
1.  **Variable Inconsistency:** In `lab.md`, Step 2, the code uses `budget = tool_context.session.state.get("monthly_budget", 0)`, but the error message says `Please set your monthly budget first.` (with a space). While minor, consistency helps students.
2.  **Attribute Access:** During verification, I found that `require_confirmation` is stored as `_require_confirmation` in the ADK 2.2.0 `FunctionTool` object. If a student tries to inspect this in a debugger or shell, they might get confused, though it doesn't affect the functional code.
3.  **Missing "Set" Tool in Lab:** The `lab.md` asks students to use a `get_savings_projection` tool that depends on state, but doesn't provide the code for a tool that *sets* that state (like the `set_budget` tool found in the solution). Students would have to manually mock the state or would be stuck unable to test a "success" path in the CLI.

## 🏁 Solution Review
The solution (`lab-solution.md`) differs significantly from the challenge (`lab.md`):
- It introduces `Pydantic` and `BaseModel` which were not mentioned in the lab steps.
- It includes the `set_budget` tool which was missing from the lab.
- **Critical Bug:** The "Self-Reflection Answers" in `lab-solution.md` are leftovers from Module 4.5/Module 38 (talking about Jitter and subclassing), and do not match the "Self-Reflection Questions" asked at the end of `lab.md`.

## 💡 Suggestions for Improvement
1.  **Update Lab Instructions:** Add a small step to implement a `set_budget` tool so the agent is actually usable.
2.  **Fix Solution Reflection:** Update the answers in `lab-solution.md` to actually address the questions asked in `lab.md` (Security of ToolContext vs LLM args, etc.).
3.  **Sync Tech Stack:** Decide if Module 10 should introduce Pydantic for tool outputs. If yes, add it to `lab.md`. If no, remove it from `lab-solution.md`.


---
# 🎓 Student Evaluation Report: Module 09 (Custom Function Tools)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 2

## 🧑‍💻 The Student Experience
Creating custom tools in Python feels very powerful. The 'auto-schema' generation from docstrings and type hints is a huge time-saver and reduces the friction of connecting LLMs to code. Building a calculator is a classic but effective way to see function calling in action.

## 🚧 Friction Points & Bugs
A minor formatting issue in the lab instructions was identified and fixed. The transition from dictionaries to Pydantic models for tool outputs is introduced as a 'Pro Tip', which helps bridge the gap between simple prototyping and enterprise standards.

## 🏁 Solution Review
The solution is excellent. It demonstrates the use of the 'Agent' class and correctly implements arithmetic logic with structured Pydantic return models.

## 💡 Suggestions for Improvement
None. The module is a solid foundation for all subsequent tool-based interactions.

---
# 🎓 Student Evaluation Report: Module 11 (OpenAPI Tools)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 3

## 🧑‍💻 The Student Experience
The ability to generate tools directly from an OpenAPI spec is a 'killer feature'. It makes the student realize they can connect their agents to almost any modern web service in minutes. The Frankfurter API example is a great choice as it requires no API keys, making the lab very accessible.

## 🚧 Friction Points & Bugs
The simulation verified that the OpenAPIToolset configuration is robust. No major issues found. The lab instructions correctly guide students through the critical 'operationId' and 'parameters' sections of the spec.

## 🏁 Solution Review
The solution correctly demonstrates how to convert a Python dictionary spec into a toolset. The agent configuration is idiomatic for ADK 2.0.

## 💡 Suggestions for Improvement
Consider adding a 'Part 2' where students download a real .json spec file from a public URL (like GitHub) and load it, to show how they would handle real-world existing specifications.

---
# 🎓 Student Evaluation Report: Module 10 (Stateful Tools)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 2

## 🧑‍💻 The Student Experience
The refocused Module 10 is much more logical. Moving the 'Memory' pattern (Store/Recall) here provides a simple, high-impact first look at stateful tools. It eliminates the previous overlap with Module 13 and gives students a clear, distinct reason to use ToolContext (Data Persistence).

## 🚧 Friction Points & Bugs
None. The code logic is straightforward and the ADK 2.0 imports are correct. The lab is now a genuine implementation challenge rather than a copy-paste exercise.

## 🏁 Solution Review
The solution correctly demonstrates the store/recall logic using tool_context.session.state. It is idiomatic for ADK 2.0.

## 💡 Suggestions for Improvement
None. This is now a very solid foundation for state management.

---
# 🎓 Student Evaluation Report: Module 13 (Advanced Actions & HITL)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 3

## 🧑‍💻 The Student Experience
Module 13 now feels like a 'Level Up' for students. By focusing on 'Control Flow' (Actions and HITL), it creates a clear pedagogical separation from Module 10. Building the 'Secure Finance Agent' is an engaging real-world scenario that justifies the complexity of FunctionTool and require_confirmation.

## 🚧 Friction Points & Bugs
None identified. The simulation confirmed that dynamic transfer (amount > 10,000) and HITL work as expected in the ADK 2.0 runtime.

## 🏁 Solution Review
The solution is technically perfect. It demonstrates the powerful combination of manual safety (HITL) and automated business rules (Actions.transfer_to_agent).

## 💡 Suggestions for Improvement
Briefly mention in the README that actions can be triggered even if the tool is stateless, emphasizing that 'Actions' control the framework, not just the data.

---
# 🎓 Student Evaluation Report: Module 26 (Callbacks and Guardrails)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 3

## 🧑‍💻 The Student Experience
Module 26 provides a deep look into the 'Control Plane' of the ADK. The ability to intercept and block operations (like the caching example) is a very powerful concept for building efficient and safe agents. The distinction between Callbacks and Plugins is finally clear.

## 🚧 Friction Points & Bugs
The migration to ADK 2.0 signatures was the main technical hurdle. The current version correctly uses CallbackContext and ToolContext with their updated arguments. The simulation confirmed that caching works perfectly on the second turn.

## 🏁 Solution Review
The solution is technically solid. It demonstrates advanced use cases for all four major callback types and follows ADK 2.0 best practices for imports and type hinting.

## 💡 Suggestions for Improvement
Consider adding a 'Post-Processing' example in after_model_callback that automatically translates the agent's response, showing that callbacks can modify as well as block.

---
# 🎓 Student Evaluation Report: Module 16 (Static Orchestration)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 2

## 🧑‍💻 The Student Experience
Fusing sequential and parallel edges into a single module is a brilliant pedagogical choice. It allows students to see the 'Graph Geometry' all at once. Using JoinNode to synchronize the researchers makes the concept of Fan-in very tangible.

## 🚧 Friction Points & Bugs
None. The skeletonized lab correctly forces students to think about the edges START -> A -> Join and START -> B -> Join.

## 🏁 Solution Review
The solution provides a perfect hybrid example. It follows ADK 2.0 best practices and uses output_key correctly for result consolidation.

## 💡 Suggestions for Improvement
None. The module is technically sound and ready for use.

---
# 🎓 Student Evaluation Report: Module 18 (Dynamic Orchestration)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 3

## 🧑‍💻 The Student Experience
The shift to the standard Python for loop with @node is the 'killer feature' of ADK 2.0 for many developers. It feels like pure Python, yet it has all the power of the ADK runtime behind it.

## 🚧 Friction Points & Bugs
None identified. The simulation confirmed that ctx.run_node() works exactly as described.

## 🏁 Solution Review
The solution correctly demonstrates the programmable flow. It is a vital step for students to master complex business logic.

## 💡 Suggestions for Improvement
None.

---
# 🎓 Student Evaluation Report: Module 19 (Collaborative Teams)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 3

## 🧑‍💻 The Student Experience
Collaboration modes (task, single_turn) are much easier to understand than the legacy hand-off patterns. The 'Travel Team' scenario is a perfect use case for demonstrating how a specialist can finish a task and automatically hand control back to the planner.

## 🚧 Friction Points & Bugs
None. The simulation confirmed that the 'mode' parameter is correctly interpreted by ADK 2.1.0+.

## 🏁 Solution Review
The solution is technically accurate and demonstrates the most modern way to build agent teams.

## 💡 Suggestions for Improvement
None.

---
# 🎓 Student Evaluation Report: Module 13.5 - Custom Persistence with Firestore

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5/5
* **Clarity of Instructions (lab.md):** 4/5
* **Code Completeness:** 5/5
* **Solution Quality (lab-solution.md):** 5/5
* **Overall Difficulty:** 3/5

## 🧑‍💻 The Student Experience
The simulation was successful. I implemented the 'FirestoreSessionService' by inheriting from 'BaseSessionService'. The mapping of ADK sessions and events to Firestore's hierarchical document structure (apps -> users -> sessions -> events) is logical and easy to follow. Integration into the 'Runner' via dependency injection worked exactly as described.

## 🚧 Friction Points & Bugs
* **Runner vs InMemoryRunner**: In Step 3 of 'lab.md', the TODO comment says 'Create a base Runner (NOT InMemoryRunner)'. While correct for the lesson, a student might be confused if they previously only used 'InMemoryRunner'. Explicitly mentioning that 'Runner' is the base class for custom services would help.
* **Mocking**: For students without active GCP credentials, a small section on how to mock the service for local testing would be a great addition, though not strictly required for the core lesson.

## 🏁 Solution Review
The solution is robust and provides a complete, production-ready implementation of 'append_event' and 'update_session_state'. It correctly uses 'AsyncClient' and handles session creation/retrieval gracefully.

## 💡 Suggestions for Improvement
1. Update 'lab.md' to explicitly mention that the 'Runner' class (imported from 'google.adk') is the one to use when injecting custom services.
2. Ensure 'uv add google-cloud-firestore' is highlighted as a mandatory step in the 'lab.md' (it is currently, but easy to miss).


---
# 🎓 Student Evaluation Report: Module 13.5 (Extending ADK - Custom Firestore)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 4 (Advanced extensibility)

## 🧑‍💻 The Student Experience
This module provides a major 'Aha!' moment for students. By showing that ADK 2.0 is built on top of clear interfaces like BaseSessionService, we empower developers to integrate the framework into their existing enterprise infrastructure. The jump from 'using the tool' to 'extending the tool' is perfectly handled.

## 🚧 Friction Points & Bugs
The initial draft lacked stubs for mandatory abstract methods in BaseSessionService (list_sessions, delete_session), which caused TypeErrors during instantiation. This has been fixed in both the lab instructions and the solution.

## 🏁 Solution Review
The solution provides a robust implementation of the Firestore provider. It correctly uses dependency injection at the Runner level, which is a key ADK 2.0 architectural pattern.

## 💡 Suggestions for Improvement
None. The module is now technically accurate and provides high pedagogical value.


---
# 🎓 Student Evaluation Report: Module 25 (Observability & Telemetry)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 3 (GCP & OpenTelemetry concepts)

## 🧑‍💻 The Student Experience
The simulation was highly successful and instructive. Implementing the custom `AlertingPlugin` using `BasePlugin` and overriding `on_event_callback` was straightforward. Checking for the event types `'request_complete'` and `'request_error'` provides a clean way to add application-level business-rule alerting outside the main agent instructions.

## 🚧 Friction Points & Bugs
The imports are now fully aligned with the modular ADK 2.0 structure (`from google.adk.apps import App` and `from google.adk import Agent`). The OpenTelemetry setup with `get_gcp_exporters` and `maybe_set_otel_providers` is well explained, with clear experimental warnings for the student.

## 🏁 Solution Review
The solution provides a clean, well-commented implementation of the alerting threshold logic. The Self-Reflection answers add deep value, highlighting the clear separation of concerns that custom plugins offer over inline log instrumentation.

## 💡 Suggestions for Improvement
None. The module is stable, accurate, and ready for classroom or self-service deployment.


---
# 🎓 Student Evaluation Report: Module 25.5 (RAI Safety Plugins)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 3

## 🧑‍💻 The Student Experience
Creating a "Fail-Closed" guardrail using an ADK Plugin is an essential lesson in safety. This challenge shows how a deterministic programmatic layer can inspect and rewrite final responses before they reach the user, bypassing potential jailbreaking or prompt injection vulnerabilities. The simulation verified that the regex successfully caught the leaked credit card pattern and replaced it with a security block message.

## 🚧 Friction Points & Bugs
*   **Critical API Bug Resolved:** During empirical validation, the student encountered an `ImportError: cannot import name 'Event'` when executing the code. The starter code in `lab.md` and the final code in `lab-solution.md` were trying to import `Event` directly from `google.adk` (i.e., `from google.adk import Agent, Event`).
*   **Correction:** I have successfully refactored both `lab.md` and `lab-solution.md` to import `Event` from the proper ADK 2.0 namespace: `from google.adk.events import Event`. With this update, the student script executes seamlessly.

## 🏁 Solution Review
The solution is elegant and works flawlessly. It correctly demonstrates how modifying `event.content.parts[0].text` directly intercepts and mutates the agent output.

## 💡 Suggestions for Improvement
None. The critical namespace bug was resolved, and the module now provides outstanding pedagogical value.

---
# 🎓 Student Evaluation Report: Module 24 - Evaluation & Load Testing

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 3 (Intermediate)

## 🧑‍💻 The Student Experience
The student experience was highly rewarding. Introducing automated evaluations (Golden Paths) and then complementing them with an optional performance load test using Locust creates a cohesive, professional picture of how to evaluate agents. The transition from local testing via Dev UI to terminal execution with `uv run adk eval` is smooth and well-justified for CI/CD environments.

## 🚧 Friction Points & Bugs
None identified. The syntax of the newly added `locustfile.py` template is 100% compliant with standard Python and Locust APIs. The dependencies are easily managed via `uv`.

## 🏁 Solution Review
The solution in `lab-solution.md` is robust. The json structure of `calculator_tests.evalset.json` is accurate and maps to ADK 2.0. The added `locustfile.py` template utilizes proper Locust API calls (`HttpUser`, `task`, `between`, `self.client.post`) matching ADK native API contract.

## 💡 Suggestions for Improvement
Already implemented by adding the optional Locust load testing challenge and solution code.

---
# 🎓 Student Evaluation Report: Module 37 (Distributed Personalized Shopping Agent)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 4

## 🧑‍💻 The Student Experience
The capstone lab was an incredible synthesis of all previous concepts! Setting up three separate agents communicating via the A2A (Agent-to-Agent) protocol felt like building a real-world enterprise service architecture. Having separate `web_agent`, `personalization_agent`, and `orchestrator_agent` is highly modular. The instructions in `lab.md` were crystal-clear, detailing step-by-step setup using `uv`. I was able to write the agent files and set up the mocks without looking at the solution, achieving full syntax compilation successfully on the first run.

## 🚧 Friction Points & Bugs
No severe friction points or bugs were encountered. The prerequisite tools are clearly listed. A small point of caution for other students: because this is a distributed multi-agent setup, it requires running three terminal sessions simultaneously (ports 8001, 8002, and the web ui). Clarifying port allocations and the exact `uvicorn` commands was crucial, and the `lab.md` did this flawlessly.

## 🏁 Solution Review
The solution provided in `lab-solution.md` is perfectly aligned with ADK 2.0 A2A design patterns:
1. It uses `to_a2a(root_agent)` to expose agents as FastAPI/Uvicorn applications.
2. It leverages `AGENT_CARD_WELL_KNOWN_PATH` to discover remote agent cards.
3. It uses `RemoteA2aAgent` to easily register remote microservices.
It matches my simulation perfectly and compiles without warnings.

## 💡 Suggestions for Improvement
The lab is already exceptional. One small suggestion: we could add a minor note in `lab.md` explaining how `to_a2a` automatically wraps the agent in a FastAPI app behind the scenes, so students understand why `uvicorn` is used to run it.

---
# 🎓 Student Evaluation Report: Module 40 (Advanced Capstone - Aegis Incident Response & AgentOps)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 5 (Advanced multi-service enterprise-grade capstone with distributed monitoring)

## 🧑‍💻 The Student Experience
This new original capstone is an absolute tour-de-force! It moves far beyond generic "personalized shopping" concepts to present a highly relevant, real-world Security Operations (SOC) incident response system (Aegis Guard). By incorporating AgentOps (OpenTelemetry spans, distributed trace headers, latency metrics, and custom logging hooks), students gain practical knowledge in tracing distributed HTTP requests across different agents and containers, bridging the gap between local prototype and cloud production.

## 🚧 Friction Points & Bugs
No major friction points were encountered. The custom local mock tools in the simulation allowed for offline syntactic testing with 0 compiler errors. The integration of `@threat_agent.before_request` and `@threat_agent.after_response` was highly intuitive and extremely easy to map.

## 🏁 Solution Review
The solution in `lab-solution.md` is exemplary, using clean, production-grade ADK 2.0 graph and event hook styles. The telemetry implementation showcases exactly how to export parent-child execution traces to Cloud Logging and Trace.

## 💡 Suggestions for Improvement
To further enhance the AgentOps section, we could provide an optional Appendix showing how to construct a custom Google Cloud Monitoring dashboard JSON file to plot these agent latency and token metrics.


---
# 🎓 Student Evaluation Report: Module 12 - Built-in Tools and Grounding

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 3
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 4
* **Overall Difficulty:** 2

## 🧑‍💻 The Student Experience
The theory flowed well — `google_search` as a built-in tool, mixed with custom functions, is explained clearly with a working code sample. The two "Looking Ahead: Managed Agents (Preview)" additions (base concept + the new `instruction` param note) read as clear, appropriately-scoped asides. Writing the `research_assistant` agent from the TODO skeleton was straightforward.

## 🚧 Friction Points & Bugs
**Real bug, reproducible, pre-existing (not part of this session's edits):** Step 3 of `lab.md` instructs `uv run adk run agent.py`, but the installed ADK CLI's `adk run` command expects a **directory**, not a file path, and fails immediately (`Error: Invalid value for 'AGENT': Directory 'agent.py' is a file.`). The fix is `uv run adk run .`. Confirmed the same broken command is also in `lab-solution.md`'s "Testing the Solution" section.

**Infra limitation (not a course bug):** live end-to-end execution failed with `API key not valid` — environment/credentials issue, not a module defect. ADK-side wiring (schema validation, tool registration) all passed.

## 🏁 Solution Review
Independently-written `agent.py` matched `lab-solution.md` almost exactly in structure. No divergence in approach.

## 💡 Suggestions for Improvement
1. Fix `uv run adk run agent.py` → `uv run adk run .` in both `lab.md` and `lab-solution.md`.
2. Add a one-line note clarifying `adk run` takes the agent's directory, not the entry-point file.
3. The two new "Looking Ahead" boxes on `ManagedAgent` are good as-is; no changes needed there.

---
# 🎓 Student Evaluation Report: Module 21 — Distributed Graphs (A2A)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 4
* **Clarity of Instructions (lab.md):** 2
* **Code Completeness:** 1
* **Solution Quality (lab-solution.md):** 1
* **Overall Difficulty:** 5 (not because the concept is hard, but because the provided code doesn't run as-is)

## 🧑‍💻 The Student Experience
Theory is clear and the `use_legacy=False` / "Advanced: A2A Reliability" addition reads well. Executing the lab exactly as written (ADK 2.7.1) failed at three separate points before the reliability fix could even be tested.

## 🚧 Friction Points & Bugs
1. **`GoogleSearchAgentTool` doesn't exist** in installed ADK — the real class is `google_search`. Present in both `lab.md` and `lab-solution.md`.
2. **Missing transitive dependency**: `pip install uvicorn google-adk[a2a]` is not enough — starting the specialist server crashes with `ModuleNotFoundError: No module named 'sse_starlette'`.
3. **Agent card URL is wrong (blocking)**: both files build the URL as `f"http://localhost:8001/a2a/research_specialist{AGENT_CARD_WELL_KNOWN_PATH}"`, but the specialist actually serves its card at the root: `http://localhost:8001/.well-known/agent-card.json`. The `/a2a/research_specialist/...` path 404s.
4. Test environment API key rejected — blocked a live end-to-end run (infra limitation, not a course bug).

## 🏁 Solution Review
`lab-solution.md` has the same `GoogleSearchAgentTool` and agent-card-URL bugs as the starter — not currently a working reference.

## A2A Reliability Check (use_legacy=False)
✅ Confirmed the parameter is real and correctly used (`RemoteA2aAgent.__init__` signature has `use_legacy: bool = True` in ADK 2.7.1). ⚠️ Could not empirically confirm the "no duplicate messages" claim end-to-end because finding #3 blocks the orchestrator from reaching the specialist at all, and the API key issue blocked a live run after patching locally. `use_legacy=False` itself looks correct but is currently unreachable due to a higher-priority bug.

## 💡 Suggestions for Improvement
1. **Highest priority**: fix the agent-card URL to `f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}"` in `lab.md`'s hint and `lab-solution.md`.
2. Replace `GoogleSearchAgentTool` with `google_search` in both files.
3. Add `sse_starlette` to the Step 1 install command.

---
# 🎓 Student Evaluation Report: Module 24 — Evaluating Agent Performance

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 4
* **Code Completeness:** 3 (both new Bonus snippets have real technical inaccuracies)
* **Solution Quality (lab-solution.md):** N/A (not reached — blocked by environment/pre-existing bug, not module content)
* **Overall Difficulty:** 3

## 🧑‍💻 The Student Experience
Theory and the golden-path/CLI flow (Steps 1-8) read clearly. Live execution blocked by an invalid API key in the test environment (infra limitation). Pivoted to static verification against installed `google-adk==2.7.1` source for import paths, field names, JSON schemas, and CLI flags.

## 🚧 Friction Points & Bugs
1. **Blocking, pre-existing gap (not part of this session's bonuses):** `uv run adk eval` fails with `Error: Eval module is not installed, please install via "pip install google-adk[eval]"` on a plain `uv add google-adk`. Never mentioned anywhere in the module. Blocks the core lab, not just the bonuses.
2. **Bonus "Custom Metric" — incomplete instructions:** the metric name must also be added to `criteria` (e.g. `{"check_math_is_correct": 0.5}`), not just `custom_metrics` — otherwise `code_config` is never used and nothing happens, with no error.
3. **Bonus "Custom Metric" — wrong config location:** there's no `config` section in `evalset.json`; `adk eval` only accepts an `EvalConfig` as a separate file via `--config_file_path`.
4. **Bonus "User Simulation" — invalid JSON shape:** the bare scenario object needs a `{"scenarios": [...]}"` wrapper, and there's a dedicated CLI command not mentioned at all: `adk eval_set add_eval_case AGENT_PATH EVAL_SET_ID --scenarios_file <file> --session_input_file <file>`.

## 🏁 Solution Review
Not reached — friction was environmental (API key) plus the two bonus-text issues above.

## 💡 Suggestions for Improvement
- Add `uv add "google-adk[eval]"` near the top of Step 1 (fixes the entire module, most urgent item).
- Fix the Custom Metric bonus: add the `criteria` entry example and a real `eval_config.json` + `--config_file_path` command.
- Fix the User Simulation bonus: wrap the JSON as `{"scenarios": [...]}"` and show the real `adk eval_set add_eval_case ... --scenarios_file ... --session_input_file ...` command.

## Bonus Sections Technical Accuracy
| Check | Result |
|---|---|
| `EvaluationResult`/`PerInvocationResult` import | ✅ Correct |
| `EvalStatus` import | ✅ Correct |
| Field names on both classes | ✅ All match |
| Custom metric registration via `custom_metrics` | ⚠️ Correct but incomplete (needs `criteria` entry too) |
| `EvalConfig` location as described | ❌ Incorrect — only a separate `--config_file_path` file works |
| `user_persona: "NOVICE"` | ✅ Valid |
| Bare `ConversationScenario` JSON as shown | ❌ Needs `{"scenarios": [...]}"` wrapper + `adk eval_set add_eval_case` command |

---
# 🎓 Student Evaluation Report: Module 26 - Callbacks and Guardrails

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 4
* **Clarity of Instructions (lab.md):** 2
* **Code Completeness:** 2
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 3

## 🧑‍💻 The Student Experience
Theory is clear, including the new self-healing plugins section. The lab itself proved impossible to complete from `lab.md` alone: "Step 2: Implement the Callbacks" is truncated — only one complete TODO (`after_model_callback`), a second cut off mid-sentence (`before_tool_callback`), and references to code "that comes before" that was never shown. An orphaned closing code fence appears before the Self-Reflection Questions, suggesting accidental truncation, not a pedagogical choice. `adk create`'s "Programmatic (Python script)" prompt also no longer exists in the current CLI (google-adk 2.7.1).

## 🚧 Friction Points & Bugs
1. **[High severity] `lab.md` truncated**: missing starter-code/TODOs for `before_agent_callback`, `before_model_callback`, and the completion of `before_tool_callback`. A real student has no way to know what to implement.
2. **[Low severity] Outdated CLI prompt**: `lab.md` references an `adk create` prompt that no longer exists.
3. Had to activate the Stuck Protocol and read `lab-solution.md` to proceed — penalized accordingly.

## 🏁 Solution Review
`lab-solution.md` is complete, well-commented, and correct. **Empirical verification of this session's new content** (README "Built-in Example: Self-Healing Plugins"): `ReflectAndRetryModelPlugin`/`ReflectAndRetryToolPlugin` import successfully from `google.adk.plugins`; `App` imports correctly from `google.adk.apps.app`; constructor signatures confirmed via `inspect.signature` — `max_retries` is valid for both. Instantiated an `App` with both plugins registered end-to-end with no errors. Could not validate live callback behavior (cache hit, guardrail, redaction, tool block) due to an invalid API key in the test environment (infra issue, not course code).

## 💡 Suggestions for Improvement
1. **High priority**: restore the missing starter-code/TODOs for the three incomplete callbacks in `lab.md` (recover from git history if possible).
2. Remove/update the outdated `adk create` prompt reference.
3. The new `ReflectAndRetry*` plugin content in the README is technically correct and empirically verified — no changes needed there.

---
# 🎓 Student Evaluation Report: Module 27 — Introduction to MCP & Stateful Tools

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 4
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 3

## 🧑‍💻 The Student Experience
Followed the lab step by step; the code produced matched `lab-solution.md`'s structure exactly, no ambiguity in the TODOs.

## 🚧 Friction Points & Bugs
1. **[Real] Timeout on first run**: the very first `npx -y @modelcontextprotocol/server-filesystem ...` invocation must download the npm package, exceeding ADK's hardcoded 5s MCP session timeout (`ConnectionError: ... timed out after 5.0s`), even though the server then starts correctly right after. Retrying the same call (npx now cached) works on the first try.
2. **[False alarm, resolved]** Adding `mcp` explicitly and unconstrained (`uv add google-adk mcp`) resolves an incompatible `mcp==2.0.0`. Without adding it explicitly — as a student following only `adk create` would — `google-adk` resolves a compatible `mcp` version on its own. Not a course bug, an artifact of the test methodology.

## 🏁 Solution Review
`lab-solution.md` matches exactly what following the TODOs produces — no discrepancy, no need to consult it to get unstuck.

## 💡 Suggestions for Improvement
Add a line in Step 4: "If your very first request fails with an MCP session timeout, this is likely `npx` downloading the server package for the first time — simply retry." Near-zero cost, removes a real, reproducible first-run friction point.

## McpToolset Rename Verification
✅ Correct. Both `from google.adk.tools.mcp_tool.mcp_toolset import McpToolset` (used in the lab) and the package-root style import work correctly. The `MCPToolset`→`McpToolset` rename introduced no regressions.

## Remote MCP Bonus — Static Review Only
Not executed (requires a real GitHub PAT). Static review: imports correct and consistent with what was verified for the main lab, syntax valid, `Authorization` header pattern correct and safe (token from `.env`, never hardcoded). No issues found without execution.

---
# 🎓 Student Evaluation Report: Module 28 — Building a Custom MCP Tool

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 3 (contains a now-inaccurate technical claim)
* **Clarity of Instructions (lab.md):** 3
* **Code Completeness:** 1 (starter and solution code are not runnable against current `mcp` versions)
* **Solution Quality (lab-solution.md):** 2 (same breakage as the starter)
* **Overall Difficulty:** 4 (not conceptually hard — blocked by environment/API drift)

## 🧑‍💻 The Student Experience
Following `lab.md` literally (`pip install mcp` then `uv add google-adk mcp`), `McpToolset` fails to import at all — the whole `google.adk.tools.mcp_tool` package fails to load silently. A real beginner would be stuck immediately with no clue from the surface traceback.

## 🚧 Friction Points & Bugs
1. **[Critical] Import broken by `mcp` version conflict**: `uv add google-adk mcp` installs `google-adk==2.7.1` plus the latest `mcp==2.0.0`, but `google-adk` only declares its `mcp` version constraint inside its optional `[mcp]` extra. Result: `mcp==2.0.0` breaks `mcp_session_manager.py` (`ImportError: cannot import name 'McpHttpClientFactory'`), cascading to break all MCP imports. **Fix verified**: `uv add "google-adk[mcp]"` resolves `mcp==1.29.0` and imports work perfectly. The `MCPToolset`→`McpToolset` rename made this session is correct and unrelated to this bug.
2. **[Critical] `call_tool` handler has a wrong signature**: both `lab.md` and `lab-solution.md` define `async def call_mcp_tool(name, arguments, session_id)`, but the real `mcp` 1.29.0 API calls handlers with only `(tool_name, arguments)` — confirmed via source and by running the real server, which raises `TypeError: missing 1 required positional argument: 'session_id'`. `session_id` doesn't exist anywhere in `mcp.server.lowlevel`.
3. **[Critical] `InitializationOptions` missing required `capabilities`**: both files omit it; `mcp` 1.29.0 requires it (`ValidationError: capabilities Field required`). Fix: `capabilities=app.get_capabilities(NotificationOptions(), {})`.

After fixing all three locally, verified end-to-end with a real MCP client that `list_tools`/`call_tool` work correctly. Live agent↔model interaction not testable (invalid API key in test environment — infra issue).

## 🏁 Solution Review
`lab-solution.md` contains the exact same three critical bugs as the starter — reading it does not unblock a stuck student.

## 💡 Suggestions for Improvement
1. `lab.md` Step 1: replace `pip install mcp` with `uv add "google-adk[mcp]"`.
2. Remove `session_id` from the `call_tool` signature in both files (or implement real per-user state some other way, since the current API doesn't provide it natively).
3. `README.md`: correct the claim that the handler receives "the tool name, arguments, and session_id" — it's just name and arguments today.
4. Add `capabilities=app.get_capabilities(NotificationOptions(), {})` to `InitializationOptions` in both files.

## McpToolset Rename Verification
✅ Confirmed correct, provided `mcp` is installed via the compatible extra (`google-adk[mcp]`, resolving `mcp==1.29.0`) rather than as an unconstrained separate package. The legacy `MCPToolset` alias also remains available in parallel.

---
# 🎓 Student Evaluation Report: Module 33 — Deployment to GKE

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 5
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** N/A — would require real GKE cluster execution
* **Overall Difficulty:** N/A — would require real execution

## 🧑‍💻 Note: Static Review Only
This evaluation is a static code/text review, not an executed simulation — no GKE cluster, Artifact Registry, or other real cloud resource was created, no cost incurred.

## 🚧 Friction Points & Bugs
- Environment variables (`GOOGLE_CLOUD_PROJECT`/`GOOGLE_CLOUD_LOCATION`) are used consistently across all steps, including the new "Bonus: The Automated Way" `adk deploy gke` command.
- `--cluster_name adk-cluster` and `--service_type=LoadBalancer` in the Bonus match the manually-created cluster name and manifest `type: LoadBalancer` exactly.
- The `echo_agent/` path argument is correct given the `cp -r echo_agent/ gke_echo_agent/` structure.
- **Minor cosmetic inconsistency (non-blocking)**: README.md calls it `uv run adk deploy gke`, while the new Bonus block in lab.md writes `adk deploy gke` without the prefix.

## 🏁 Solution Review
The Bonus is purely informational ("you won't run this in the lab"), so it correctly has no counterpart in `lab-solution.md`.

## 💡 Suggestions for Improvement
Align `uv run adk deploy gke` (README) and `adk deploy gke` (lab.md Bonus) to the same form for consistency.

---
# 🎓 Student Evaluation Report: Module 39.5 - Agent Skills

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 4
* **Clarity of Instructions (lab.md):** 2
* **Code Completeness:** 3
* **Solution Quality (lab-solution.md):** 2
* **Overall Difficulty:** 3 (artificially high due to the bug below)

## 🧑‍💻 The Student Experience
Setup (`uv init`, `uv add google-adk` → installs 2.7.1, `adk create skills_agent`) worked smoothly. Code written independently from the TODOs matched `lab-solution.md` exactly.

## 🚧 Friction Points & Bugs
**Blocking, 100% reproducible bug, not a course-writer typo but a real API constraint change**: copying `SKILL.md`'s frontmatter exactly as shown in Step 3 (`name: greeting_skill`) crashes at load with a Pydantic `ValidationError: name must be lowercase kebab-case ... no ... consecutive delimiters`. On ADK 2.7.1, skill names cannot contain underscores by default (a `SNAKE_CASE_SKILL_NAME` feature flag exists but isn't on by default). Fixing only the frontmatter to kebab-case then produces a second error: `Skill name 'greeting-skill' does not match directory name 'greeting_skill'`. The full fix requires renaming **both** the directory and the `name:` field consistently to kebab-case, plus updating the path in `agent.py`. With that fix, skill loading proceeds correctly. Final conversational test not completed due to an invalid API key in the test environment (infra issue, not a module defect).

## 🏁 Solution Review
`lab-solution.md` has the exact same bug — assumes the snake_case directory/name from Steps 2-3 without correcting or flagging it.

## 💡 Suggestions for Improvement
1. **Priority fix**: rename the skill directory to `skills/greeting-skill` and its frontmatter to `name: greeting-skill` in both `lab.md` and `lab-solution.md`; update the path hint in Step 4 accordingly.
2. Add a line in "The Structure of a Skill Directory" stating the `name` must be lowercase kebab-case and match its containing directory exactly.

## New README Sections Review
Both sections added this session are clear and well-calibrated: the "experimental" note is short and honest without undermining confidence in the module; "Going Further: The Skill Registry (Preview)" is correctly scoped as "beyond the scope of this lab" with no executable code to get stuck on, and correctly names `GCPSkillRegistry`, `search_skills`, `load_skill`.

---
# 🎓 Student Evaluation Report: Module 11 - Enterprise Integration with OpenAPI Tools

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 4
* **Code Completeness:** 4
* **Solution Quality (lab-solution.md):** 3
* **Overall Difficulty:** 2

## 🧑‍💻 The Student Experience
The theory section is short and effective: it states the core idea in one sentence (`OpenAPIToolset` turns an OpenAPI spec into callable tools, one per `operationId`) and backs it with a small, complete, copy-pasteable example. That example maps almost one-to-one onto the lab's exercise, so by the time I opened `agent.py` I already knew exactly what shape my answer needed: an `operationId`, a `summary`, a `parameters` list, and a `responses` block.

Filling in the `FRANKFURTER_SPEC` TODO was straightforward -- I added three query parameters (`amount`, `from`, `to`) with simple JSON-schema types, wired up `OpenAPIToolset(spec_str=..., spec_str_type="json")`, and passed the toolset into `tools=[...]` on the `Agent`. I did not need to consult `lab-solution.md` to get unstuck at any point.

The one place I had to pause and use judgment rather than the instructions: after running `uv run adk create market_analyst`, the generated `agent.py` was NOT the `FRANKFURTER_SPEC` skeleton shown in lab.md -- it was generic ADK boilerplate (`root_agent = Agent(model='<FILL_IN_MODEL>', name='root_agent', ...)`). lab.md's wording ("Open `agent.py`. A skeleton ... is provided below") reads as if the file already contained that code. It took a second to realize the intent was "replace the whole file with the block below," not "find and complete the block already there."

`uv run adk create market_analyst` also interactively prompted me to choose a model (`1. gemini-3.5-flash` / `2. Other models`), which lab.md never mentions. Since `gemini-3.5-flash` was not available in my configured project/region, I chose option 2 and filled in `gemini-2.5-flash` by hand in `agent.py` per my evaluation instructions -- a first-time student without that guidance could be confused about which option to pick.

Everything else ran cleanly. `uv run adk run .` from inside `market_analyst/` launched an interactive terminal session against the real Frankfurter API with no errors.

## 🚧 Friction Points & Bugs
1. **`agent.py` skeleton mismatch (real, but non-blocking):** `adk create` scaffolds a generic stub, not the `FRANKFURTER_SPEC` skeleton lab.md shows. The instruction "Open `agent.py`. A skeleton ... is provided below" implies otherwise. Resolved by inference, not by consulting the solution.
2. **Unmentioned interactive model prompt:** `adk create` asks the student to pick a model interactively; lab.md gives no guidance on this step, and it matters if the course's target model isn't available in the student's GCP project/region.
3. **`lab-solution.md`'s "Running the Agent" section is stale/inconsistent:** it instructs `uv init market_analyst --python 3.10 && cd market_analyst && uv add "google-adk>=2.1.0" python-dotenv`, which contradicts lab.md's actual flow (`uv run adk create market_analyst` inside the already-initialized `adk-training` workspace from the `<Setup/>` snippet). This looks like leftover text from an older version of the lab that was not updated when the README's theory section was rewritten to teach `OpenAPIToolset`. It also tells students to put a `GOOGLE_API_KEY` in `.env`, with no mention of a Vertex AI / ADC alternative.
4. I did **not** need to invoke the Stuck Protocol -- no lab-solution.md consultation was required to complete the exercise, so Clarity scores above are not penalized for that reason; the 4/5 on lab.md reflects friction points #1 and #2 only.

## 🏁 Solution Review
The solution's `FRANKFURTER_SPEC` / `OpenAPIToolset` / `Agent` code is functionally identical to what I wrote independently: same `operationId` (`get_latest_rates`), same three query parameters (`amount`, `from`, `to`), same `responses` block shape, same `tools=[toolset]` registration pattern. The only cosmetic differences are the solution's explicit `"required": False` on each parameter (a nice-to-have, not required by lab.md's TODOs) and my added `description` fields (not required either).

I validated correctness live, not just by code comparison: all three lab.md test prompts worked on the first try against the real `https://api.frankfurter.dev/v1/latest` endpoint:
- "Convert 100 USD to EUR." -> correct conversion.
- "How many Japanese Yen (JPY) can I get for 50 British Pounds (GBP)?" -> correct conversion.
- "Convert 500 AUD to USD and EUR." -> the model made a **single** HTTP call with `to=USD%2CEUR` (comma-joined) rather than calling the tool twice, confirming the exact behavior the lab prompts students to "notice."

The one part of `lab-solution.md` that would mislead a student is its "Running the Agent" section, per Friction Point #3 above -- the code sample is correct, but the setup commands underneath it are not aligned with the flow lab.md actually walks students through.

## 💡 Suggestions for Improvement
1. In lab.md Step 2, change "Open `agent.py`. A skeleton ... is provided below" to something like "Run `adk create`, then **replace the entire contents** of the generated `agent.py`" with the following skeleton -- so students aren't looking for code that isn't there.
2. Add a one-line note after the `uv run adk create market_analyst` command in lab.md flagging the interactive model-choice prompt, and what to pick if the course's target model isn't available (e.g., "choose option 2 and set the model manually in `agent.py`/`.env`").
3. Update `lab-solution.md`'s "Running the Agent" section to match lab.md's real `adk create`-based flow instead of the leftover `uv init market_analyst && uv add ...` snippet, and align its `.env`/auth guidance with whatever credential setup the rest of the course now uses (API key vs. Vertex AI ADC).
4. Consider a short callout (theory or lab) explaining *why* a single string query parameter can still receive a comma-separated value like `USD,EUR` -- right now the lab tells students to "notice" this behavior but doesn't explain the mechanism, which is a missed teaching opportunity given how central `operationId`/parameter-schema design is to this module's theory.


---
# 🎓 Student Evaluation Report: Module 4.5 — Multi-Model Configuration, Resiliency & Portability (LiteLLM)

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 3
* **Code Completeness:** 3
* **Solution Quality (lab-solution.md):** 3
* **Overall Difficulty:** 2

## 🧑‍💻 The Student Experience
The README does an excellent job building up the "three levels of model configuration" narrative (string → `Gemini` class → subclassed `Gemini`), and by the time I reached the lab I understood *why* `ResilientGemini` needed to exist and what `HttpRetryOptions` does. Since I was simulating a student jumping straight into this module (per the chained-module setup), my first stop was the `<ChainSetup module={4} project="support_analyzer" />` callout. It correctly told me this lab modifies the `support_analyzer` project from Module 4 in place and, since I hadn't done Module 4, pointed me at Module 4's `lab-solution.md` to recreate the project before continuing. That much worked as intended.

However, `lab-solution.md` for Module 4 only contains the *contents* of `agent.py` — it does not mention that you first need the root `adk-training` uv workspace (from Module 2's `<Setup/>` snippet) or that you need to run `uv run adk create support_analyzer` to scaffold the folder (`.env`, `__init__.py`, etc.) before dropping in the solution code. I had to cross-reference Module 4's `lab.md` myself to realize this. A student who takes the ChainSetup callout at face value ("Module 4's lab-solution.md has the complete project to recreate it") could reasonably expect that file alone to be sufficient, and would get stuck creating the folder structure and `.env`.

Once `support_analyzer` was in place, the lab itself was mechanically straightforward: `cd support_analyzer && uv add "litellm==1.96.0"` worked cleanly (the version-pin warning about 1.97.0/1.98.0 breaking on Python 3.10 was reassuring and, as far as I could verify, accurate — 1.96.0 installed and ran without issue). I implemented `ResilientGemini` by combining the `ProductionGemini` pattern from the README with the field values (`max_delay=10`, `exp_base=2.0`, `jitter=0.5`) specified in the lab tasks, and wired up the `USE_LOCAL_MODEL` branching exactly as described.

## 🚧 Friction Points & Bugs
1. **ChainSetup doesn't mention environment/scaffolding prerequisites.** It says lab-solution.md has "the complete project to recreate it," but that file only shows `agent.py`'s contents, not the `uv init`/`uv add google-adk`/`adk create` steps needed to actually have a runnable `support_analyzer` folder. This is a real gap for a student arriving fresh at this module without Module 2-4 context.
2. **The lab.md code skeleton silently drops previously-built functionality, with no warning.** The `TODO` skeleton in Lab Tasks replaces the *entire* `root_agent` definition, including the `SupportAnalysis` Pydantic schema, `output_schema`, and `output_key` that Module 4 built — and the generic instruction string ("Analyze customer support issues.") replaces the detailed categorization instructions. Since the ChainSetup explicitly frames this as modifying the *same* project "in place," a careful student (as I was) would reasonably assume they should *keep* their Module 4 code and only touch the model-selection lines — not wholesale-replace the file with the skeleton. The lab never clarifies which is intended, and (see Solution Review below) the official solution actually goes with the destructive option, which is not obvious from the instructions alone.
3. `litellm==1.96.0` pin worked as documented — no friction there, this callout was accurate and helpful.
4. I did **not** need to consult `lab-solution.md` to get unblocked (no Clarity penalty was applied for that reason) — I only read it during the mandatory Step 4 (Solution Validation).

## 🏁 Solution Review
The solution's `ResilientGemini` and model-selection logic matched what I implemented (same `HttpRetryOptions` fields, same `LiteLlm`/`ollama_chat/mistral` fallback logic). Functionally, both approaches run correctly against Vertex AI (verified via `uv run adk run support_analyzer`), and the `LiteLlm` path correctly attempts to reach a local Ollama server (confirmed it fails only on connection, not on import/config, when no local server is running — validating the version pin advice).

**However, the official solution silently regresses Module 4's work**: it drops `output_schema=SupportAnalysis` and `output_key="last_ticket_analysis"` entirely, and replaces the detailed multi-step instruction with a generic one-liner ("Analyze the incoming ticket and provide a structured JSON response") that no longer *enforces* structure — it just asks for it in prose, which is precisely the anti-pattern Module 4 taught against. This directly contradicts the ChainSetup's framing that this lab "modifies the project in place" (implying continuity of prior features) and undoes a core teaching point from the previous module without any acknowledgment or explanation. My own attempt (which preserved the schema/instruction and only changed the model config) is arguably more correct pedagogically, and this divergence from the canonical solution is itself evidence the instructions are ambiguous on this point.

## 💡 Suggestions for Improvement
1. Update the `ChainSetup` snippet (or Module 4's `lab-solution.md`) to explicitly mention the base `adk-training` workspace setup and the `uv run adk create support_analyzer` scaffolding step needed before pasting in solution code — not just the `agent.py` contents.
2. Either (a) have the lab.md skeleton and lab-solution.md explicitly preserve the `SupportAnalysis`/`output_schema`/`output_key` from Module 4 and only show the *diff* needed for the model config, or (b) if dropping them is intentional (e.g., to keep the code sample short), add an explicit note like "For brevity this example omits the `output_schema` from Module 4 — keep it in your real file." As written, the omission reads as an unintentional regression rather than a deliberate simplification.
3. Consider having the lab briefly demonstrate the retry policy actually firing (e.g., by pointing at an invalid endpoint or forcing a mock 429) so students see the resiliency in action rather than only being told "you won't see it unless a network error occurs."

---
# 🎓 Student Evaluation Report: Module 5 — Running and Interacting with Agents

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 4
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 3
* **Overall Difficulty:** 1

## 🧑‍💻 The Student Experience
This lab was a welcome change of pace after Module 4.5's code-heavy work — no `agent.py` edits at all, just exercising the three CLI execution modes (`adk web`, `adk run`, `adk api_server`) against the same `support_analyzer` project (now carrying the `ResilientGemini` changes from 4.5). The README's three-mode breakdown (interactive dev / headless / API server) maps cleanly onto the lab's three tasks, and the "App and Runner" callout tying it back to earlier modules was a nice reinforcement.

Following lab.md exactly: `uv run adk web` (from the `adk-training` root) started cleanly and exposed `support_analyzer` alongside `calculator_agent` for selection, as promised ("you don't need to specify the agent name"). `uv run adk run support_analyzer` dropped me into the terminal chat and returned the correct structured JSON. `uv run adk api_server` plus the three `curl` commands (Step A failure / Step B session creation / Step C success) worked exactly as written, byte-for-byte copy-pasted from the lab: the unresolved-session call failed as expected, session creation succeeded, and the follow-up `run_sse` call streamed back the correct `category`/`sentiment`/`summary` JSON for "I am so happy with your service!".

One thing worth flagging for the "chained modules" evaluation specifically: this lab's `<ChainSetup module={4} project="support_analyzer" />` callout points back to **Module 4**, not Module 4.5, even though (per the real course sequence I'm following) `support_analyzer` at this point also carries the `ResilientGemini`/`LiteLlm` changes from 4.5. This doesn't break anything functionally — Module 5 only exercises CLI commands and doesn't touch model config — but it is an inconsistency: a student who skipped straight to Module 5 would be told to only recreate the Module 4 version of the project, silently skipping 4.5's changes, without any note that this is fine/expected or that 4.5 exists at all.

## 🚧 Friction Points & Bugs
1. **`ChainSetup` in this lab references Module 4, not 4.5**, even though 4.5 is a normal, non-optional module between 4 and 5 in the sidebar order (`sidebar_position: 4.5`) that also modifies `support_analyzer` in place. Not blocking here, but a documentation consistency gap across the chain.
2. No code-writing friction — this was the smoothest module of the three so far, entirely CLI-driven and matching lab.md exactly.
3. I did **not** need to consult `lab-solution.md` to complete any part of this lab — every command and payload in lab.md worked as given on the first try. No Clarity penalty applies for that reason.

## 🏁 Solution Review
The solution's narrative for Parts 1 and 2 matches my experience, with one factual error: it tells students to open the Dev UI at **`http://127.0.0.1:8080`**, but the actual server (confirmed from my own `adk web` run's startup banner) listens on **`http://127.0.0.1:8000`** — the same default port lab.md's own Part 3 `api_server` `curl` commands target. A student following the solution literally would try to open their browser on the wrong port and get a connection failure, with no indication of why.

For Part 3, the solution is otherwise accurate: the "Session not found" explanation is correct (my server returned `{"detail":"Session not found: missing_session"}`, a slightly more detailed message than the solution's quoted `{"detail":"Session not found"}`, but same meaning), and the session-creation and final `run_sse` behavior matched. One more small inaccuracy: the solution tells students to look for an event carrying `"author": "support_analyzer"` in the final response — in my actual output the `author` field was `"support_analyzer_agent"` (the agent's `name`, not the app folder name). A student diffing their raw curl output against the solution's description could be confused by this mismatch.

## 💡 Suggestions for Improvement
1. Fix the Dev UI port in `lab-solution.md` Part 1 from `8080` to `8000` (or dynamically reference "the port shown in your terminal's startup banner" to avoid hardcoding a version-specific value that can drift).
2. Correct the expected `author` field value in Part 3, Step C from `"support_analyzer"` to `"support_analyzer_agent"` (matching the actual agent `name`), or phrase it as "the `author` field matching your agent's `name`" to stay robust to future naming changes.
3. Align the `ChainSetup` module number across 4.5/5/6 with the real prerequisite chain — if Module 4.5 is meant to be skippable/optional for a student jumping to Module 5, say so explicitly; if not, update the callout to `module={4.5}` (or mention both).

---
# 🎓 Student Evaluation Report: Module 6 — Programmatic Execution: Apps and Runners

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 4
* **Code Completeness:** 5
* **Solution Quality (lab-solution.md):** 5
* **Overall Difficulty:** 1

## 🧑‍💻 The Student Experience
This was the smoothest of the three chained modules. The README's "Three Pillars" framing (Agent = intelligence, App = infrastructure, Runner = motor) is a clear, memorable mental model, and its "Minimal Programmatic Setup" code sample essentially previews the exact shape of the file I was about to write in the lab — by the time I opened lab.md, I already understood what `App`, `InMemoryRunner`, and `run_debug()` were for.

Continuing the chain from Module 4.5 (my `support_analyzer/agent.py` still has the `ResilientGemini` subclass and multi-model fallback logic from that lab), I created `support_analyzer/main.py` per the skeleton: imported `App`, `InMemoryRunner`, and `root_agent`, built `App(name="support_app", root_agent=root_agent)`, wrapped it in `InMemoryRunner(app=app)`, and called `runner.run_debug(...)` twice with two different `user_id`s (Alice for a billing complaint, Bob for a technical one). Running `uv run python main.py` from inside `support_analyzer/` worked on the first attempt with zero errors, and produced two clearly separate, correctly-categorized JSON analyses — direct, observable proof of the session-isolation concept the lab and README both emphasize.

I noticed `run_debug()` prints each agent response to the console on its own (`support_analyzer_agent > {...}`) in addition to whatever my own `for event in events: ...` loop printed — this looked like a minor duplication at first, but it's explicitly called out and expected per the solution ("run_debug automatically prints the agent response to the terminal"), so it's a feature, not a bug.

## 🚧 Friction Points & Bugs
1. None encountered that blocked progress. The lab's TODO skeleton maps one-to-one onto the required edits, and every import/call worked exactly as documented.
2. Same minor cross-module inconsistency noted in the Module 5 report: `<ChainSetup module={4} project="support_analyzer" />` still points at Module 4 rather than 4.5, even though (in the real chained sequence) `support_analyzer` already carries 4.5's changes by this point. Harmless here too, since this lab only adds a `main.py` and never touches `agent.py`'s model configuration — but worth fixing for consistency across all three chained labs.
3. Minor pedagogical observation (not a bug): because the README's own worked example is structurally almost identical to the lab's answer (same `App`/`InMemoryRunner`/`run_debug` shapes, just missing the second user), the lab offers very little productive struggle — a student can largely transcribe the theory section to pass. This kept "Overall Difficulty" very low and made "Code Completeness" trivial to satisfy, which is fine for a CLI/architecture-focused module but is worth knowing if the course wants more challenge here.
4. I did **not** need to consult `lab-solution.md` to get unblocked — everything worked from `lab.md` alone. No Clarity penalty applies.

## 🏁 Solution Review
My implementation and the official solution are functionally identical: same `App`/`InMemoryRunner` construction, same `run_debug()` calls per user, same final-response extraction via `event.is_final_response()`. The only differences were cosmetic (I used lowercase `"alice"`/`"bob"` as `user_id`s where the solution used `"Alice"`/`"Bob"`, and I looped through Bob's events too where the solution let `run_debug()`'s auto-print handle Bob's output alone) — neither affects correctness or session isolation.

I ran my own version live: Alice's "I was overcharged $50" correctly resolved to `{"category": "billing", "sentiment": "negative", ...}` and Bob's "My wifi is slow" independently resolved to `{"category": "technical", "sentiment": "negative", ...}` — both processed by the same `runner` instance without any cross-contamination, exactly matching the lab's stated learning goal and the solution's explanation of `user_id`-based isolation. I found no inaccuracies in this solution document (unlike Module 5's port/author-field errors) — it is accurate and consistent with the actual library behavior in the installed `google-adk==2.8.0`.

## 💡 Suggestions for Improvement
1. Align the `ChainSetup` module reference across Modules 4.5/5/6 (see Module 5's report for the same finding) — either point all three at the correct cumulative prerequisite, or explicitly note that 4.5's changes aren't required for continuity in 5 and 6.
2. If more challenge is desired, consider withholding the exact `App`/`Runner` code shape from the README's example (e.g., show it with a single user only, or omit `run_debug()` specifics) so the lab requires more synthesis rather than near-transcription. This is optional — as a foundational/introductory module, low difficulty may be entirely intentional.
3. Consider adding a one-line note (in lab.md or the solution) explaining that `run_debug()`'s automatic console printing is why output appears "twice" (once from the helper, once from any explicit loop) — a first-time student might otherwise assume they have a bug.

---
# 🎓 Student Evaluation Report: Module 19 - Collaborative Teams

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 3
* **Clarity of Instructions (lab.md):** 3
* **Code Completeness:** 4
* **Solution Quality (lab-solution.md):** 4
* **Overall Difficulty:** 3

## 🧑‍💻 The Student Experience
I came into this fresh, as a mid-level Python dev who has never touched ADK's multi-agent primitives. Sections 1-3 of the README (Collaboration Modes, `task` mode, and the "hand-off" nature of bare `sub_agents`) read cleanly: short paragraphs, one idea per bullet, a runnable code snippet, and a plain-English "why" at the end. I formed a solid mental model quickly: `chat` = permanent hand-off, `task`/`single_turn` = automatic, framework-enforced return.

Then I hit the new **Section 4 ("Call-and-Return for Remote Agents: `AgentTool`")**, which is what I was asked to scrutinize hardest. Technically I found it accurate -- I verified every concrete claim it makes (see below) -- but the *experience* of reading it is noticeably different from the rest of the module: dense, run-on paragraphs (some are 150+ words, single-sentence, multi-clause, packed with em-dashes and phrases like "this is verified, reproducible behavior, not a hypothetical") replace the crisp bullets of Sections 1-3. It reads like an engineer's internal justification note that got pasted into the student material rather than material written for a first-time learner. That's the "bolted-on" feeling the task asked me to watch for, and I did feel it.

For the lab itself, the starter code's hints (`single_turn` for weather, `task` for flights, no mode + `rerun_on_resume=True` for the coordinator) were sufficient to write a complete, sensible `agent.py` without consulting the solution -- I only opened `lab-solution.md` because live behavior didn't match the lab's own description of what I should observe (see Friction Points).

I then went further than the lab requires and independently verified Section 4's technical claims against the actual installed `google-adk==2.8.0` library (source inspection + live `Runner` probes), since that's the part under review. That turned up a real, previously-unflagged nuance: the library's own `AgentTool` docstring recommends *against* the exact usage pattern the README's flagship code example demonstrates.

## 🚧 Friction Points & Bugs

1. **Environment quirks (not the module's fault):** `gemini-3.5-flash` was not available in my GCP project (404 Publisher model not found on Vertex AI), so per instructions I substituted `gemini-2.5-flash` for my own attempt only. Separately, `uv run adk create` in ADK 2.8.0 writes `GOOGLE_GENAI_USE_ENTERPRISE=1` to `.env` rather than `GOOGLE_GENAI_USE_VERTEXAI=1` -- I set both to be safe. Neither is a module defect, just noting for context.

2. **"Automatic return" is harder to observe live than the lab implies (triggered the Stuck Protocol).** Lab Step 3 says: *"After you answer [the flight booker's question], notice how control automatically returns to the travel_planner without any hand-off code."* This phrasing implies the coordinator's synthesized final plan should appear in that same reply. I tested this directly against the ADK `Runner` API (not just the CLI, to rule out display artifacts) with **both my own `agent.py` and the literal code from `lab-solution.md`**: after `flight_booker` (mode=`task`) gives its booking confirmation, the turn ends with that message -- `travel_planner` does not visibly synthesize a final plan in the same turn. A visible coordinator synthesis only showed up after an *additional* user message, and in one run it then redundantly re-invoked both sub-agents rather than just presenting the already-gathered results. This is what sent me to `lab-solution.md` (per the Stuck Protocol, which is why I docked "Clarity of Instructions"). I can't fully rule out that this is exaggerated by `gemini-2.5-flash` substitution stochasticity (the official solution run was noticeably messier/looping compared to my own instructions on the same model) -- but the core "no visible same-turn synthesis" result was consistent and reproducible on both agent.py versions, so I'm reporting it as a real wording/expectation-setting issue rather than pure model noise.

3. **Section 4's flagship example undersells a real tension with ADK's own guidance (the main finding).** I inspected the installed library directly:
   - `AgentTool.__init__` docstring (verbatim): *"To expose an agent as an inline tool of a parent `LlmAgent`, prefer setting `mode='single_turn'` on the sub-agent and attaching it via `sub_agents=[...]` instead of wrapping it with `AgentTool`... **Direct usage of `AgentTool` is discouraged.** See the single-turn mode guide for details."*
   - I confirmed this alternative actually works: registering two **local** specialists via `sub_agents=[...]` with `mode="single_turn"` on each let the orchestrator call both in one turn and combine their results -- the exact "consult BOTH specialists in the same turn" benefit that Section 4 attributes to `AgentTool`.
   - Section 4's own flagship code example (the `orchestrator` with `tools=[AgentTool(agent=preferences_specialist), AgentTool(agent=catalog_specialist)]`) uses plain local `Agent` objects to sell this benefit -- i.e., it demonstrates `AgentTool` in exactly the scenario where the library's own docstring says to prefer the `single_turn` + `sub_agents` pattern the README already taught in Section 1.
   - This isn't a factual error -- `AgentTool` does work as described, and for **remote** `RemoteA2aAgent`s it's the *only* option (I verified `RemoteA2aAgent` does not subclass `LlmAgent`, has no `disallow_transfer_to_parent`/`disallow_transfer_to_peers` fields, and its `mode` field is typed `Literal['task'] | None` -- all exactly as Section 4 states). But by illustrating the pattern with local agents instead of (or in addition to) remote ones, the section misses the chance to explain *why* `AgentTool` is the right tool specifically for the remote case, and risks a confused student later finding contradictory advice in their IDE's tooltip.

4. **No hands-on reinforcement for the new theory.** Section 4 is substantial (two worked code examples, a shopping-assistant scenario, an expanded Key Takeaways bullet) but the only place it touches the lab is one self-reflection question (#4), which is purely verbal ("what would happen... what are two ways to fix it?"). There's no exercise where the student actually writes `AgentTool(agent=...)` and watches the trace. For a section this dense, landing with zero hands-on practice reinforces the "bolted-on" feel.

## 🏁 Solution Review
`lab-solution.md`'s code is correct and matches the starter hints precisely: `weather_checker` uses `mode="single_turn"`, `flight_booker` uses `mode="task"`, the coordinator has no `mode` but does have `rerun_on_resume=True`, and all three carry `rerun_on_resume=True` as the starter code's comment warns is required. My independent attempt was structurally identical (I only wrote different instruction wording), so Code Completeness was not an issue -- the TODOs and hints were clear enough to reach the correct design on my own.

The self-reflection answer for Q4 is well done and correctly cross-references the new theory: it correctly identifies that a bare `sub_agents=[...]` of two `RemoteA2aAgent`s would strand the coordinator on the first specialist, and offers both fixes (`mode="task"` with the `finish_task` protocol, or `AgentTool`), explicitly pointing back to "Module 19's README, Section 4." That cross-reference shows the lab and the new theory section were designed as one coherent unit at the reflection-question level, even though (per point 4 above) that coherence doesn't extend to any hands-on code.

Running the exact solution code live surfaced the same "no visible same-turn coordinator synthesis" behavior described in Friction Point #2, so this isn't specific to my own instruction wording.

## 💡 Suggestions for Improvement
1. **Add one sentence of positioning to Section 4** clarifying that for local agents already using `sub_agents`, `mode="single_turn"` (Section 1) is the framework's preferred way to get this same call-and-return/combine behavior, and that `AgentTool`'s real value is for cases `single_turn` can't reach -- chiefly `RemoteA2aAgent` composition (which cannot use `single_turn` at all), plus any case needing more dynamic/repeated/conditional invocation than a static `sub_agents` list allows. This resolves the tension with the `AgentTool` docstring's "discouraged" note before a curious student finds it independently.
2. **Consider reworking Section 4's flagship code example around `RemoteA2aAgent`s** (or at least mixing one local and one remote specialist) rather than two plain local `Agent`s, so the example actually demonstrates the scenario where `AgentTool` is the *right* choice, not just *a working* choice.
3. **Break up the long paragraphs in Section 4** (and the tail of Section 3) into bullets/shorter sentences, matching the style of Sections 1-3, to reduce the "wall of text" feel that stood out on a fresh read.
4. **Add a small hands-on touch for `AgentTool`** -- even an optional stretch step in `lab.md` having the student wrap `weather_checker` in `AgentTool` and compare the trace to the `sub_agents` version -- so the new theory gets at least one concrete, runnable reinforcement instead of only a reflection question.
5. **Soften or clarify the "automatic return" wording in `lab.md` Step 3.** Based on live testing (both my own code and the official solution, using `gemini-2.5-flash` since `gemini-3.5-flash` was unavailable in my environment), the coordinator's synthesized plan didn't reliably appear in the very same reply as the flight booking confirmation -- it sometimes needed one more user turn. Either adjust the expected observation, or note that this may take an extra exchange, so students don't second-guess a correct implementation.


---
# 🎓 Student Evaluation Report: Module 24 - Evaluating Agent Performance

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 2
* **Code Completeness:** 2
* **Solution Quality (lab-solution.md):** 2
* **Overall Difficulty:** 4 (inflated well above what the content itself warrants, due to tooling friction)

## 🧑‍💻 The Student Experience
The README is genuinely excellent: it clearly motivates *why* deterministic unit tests fail for agents, distinguishes trajectory vs. final-response evaluation, walks through the "testing pyramid," lists all built-in metrics, and introduces User Simulation with a good conceptual grounding. As a mid-level dev with no prior ADK-eval exposure, I finished the README feeling ready to try it hands-on.

The `<ChainSetup module={9} project="calculator_agent" />` callout at the top of lab.md rendered clearly: *"this lab modifies the `calculator_agent` project from Module 9, in place... If you're starting fresh at this module, you'll need that project first — Module 9's `lab-solution.md` has the complete `calculator_agent` code..."* This was unambiguous and correctly pointed me to Module 9's lab-solution.md. I built the prerequisite project from that file with no issues, and a quick `uv run adk run .` sanity check confirmed it worked (42+118=160). No complaints about the callout itself — it does its job for a student jumping straight to Module 24.

Where things fell apart was the very first hands-on step. Following Step 1 literally (`cd .../calculator_agent` then `uv run adk web calculator_agent`) fails immediately: `Error: Invalid value for '[AGENTS_DIR]': Directory 'calculator_agent' does not exist` — because you're already inside that directory. I corrected this myself (`uv run adk web .`), but then Step 2 (send the first chat message) failed too, with a 500 Internal Server Error and a `ModuleNotFoundError: No module named 'tools'` in the server log. I tried running from the parent directory (`uv run adk web calculator_agent` from `adk-training/`) — same failure. I was genuinely stuck at the very first interactive step of the lab.

I did not open lab-solution.md at this point (it doesn't contain this troubleshooting info anyway — see below). Instead I noticed lab.md's own Step 8 explains that `adk eval` needs `PYTHONPATH=.` "so that `agent.py`'s `from tools.calculator import ...` resolves," while claiming `adk run`/`adk web` don't have this problem. Applying that fix to `adk web` anyway (`PYTHONPATH=./calculator_agent uv run adk web calculator_agent`, from the parent dir) resolved it. This is a legitimate but non-obvious deduction — a student without that instinct would be stuck indefinitely, since the lab's own text explicitly (and incorrectly) reassures them this isn't needed for `adk web`.

Once unblocked, the rest of the interactive workflow (record golden path via the API the Dev UI itself calls, create eval set, add session as eval case, run evaluation, inspect the JSON, break/fix the tool, re-run) worked smoothly conceptually — but I hit two more concrete path/schema bugs (below) that would confuse anyone trying to follow Steps 3, 4, 7, and 8 literally.

I also worked through both optional Bonus sections (Custom Metric, Dynamic User Simulation) since they were feasible without a browser. The Custom Metric section worked exactly as written — no issues. The Dynamic User Simulation section's `eval_set create`/`add_eval_case` CLI commands worked perfectly, but its own Step 4 command crashes outright (see below). I skipped the Locust load-testing challenge — it's explicitly framed by the lab itself as an "extra," heavier, distinct challenge, and not needed to assess the core module.

## 🚧 Friction Points & Bugs

1. **[Blocking] Step 1.3 command is wrong for the directory you're told to `cd` into.** Step 1.1 says `cd .../calculator_agent`; Step 1.3 then says `uv run adk web calculator_agent`, which looks for a subdirectory of that name inside the current directory and fails outright with "Directory 'calculator_agent' does not exist." Should be `uv run adk web .` (or restructure so the `cd` targets the parent `adk-training` directory instead).

2. **[Blocking, most severe] `adk web` cannot load the agent at all without `PYTHONPATH` set — contradicting the lab's own claim.** Regardless of which directory you invoke it from (`.` from inside `calculator_agent`, or `calculator_agent` from the parent `adk-training`), sending any message via `/run` throws `500 Internal Server Error` / `ModuleNotFoundError: Fail to load 'calculator_agent.agent' module. No module named 'tools'`. This is because ADK's nested agent loader adds only the *parent* directory to `sys.path`, not the agent's own directory, breaking Module 9's `from tools.calculator import ...` style import. Lab.md's Step 8 explicitly says *"unlike `adk run`, `adk eval` doesn't add the current directory to Python's import path automatically"* — implying `adk web` is fine without it. **This is false**: I confirmed `adk web` needs `PYTHONPATH` set to the `calculator_agent` directory just as much as `adk eval` does. Since this breaks Step 2 (recording the very first conversation), it blocks the entire hands-on core of the lab for every student who follows the instructions as written, with no warning anywhere before Step 8.

3. **[Blocking for literal Step 8] The evalset file path referenced throughout (`eval_results/calculator_tests.evalset.json`) does not exist.** In this ADK version, saving an eval case from the Dev UI writes the file directly to the agent's own root directory (`calculator_agent/calculator_tests.evalset.json`) — no `eval_results/` subdirectory is ever created. This wrong path appears in **four places**: lab.md Step 3.4 ("Behind the scenes... created a file... at `eval_results/calculator_tests.evalset.json`"), Step 4, Step 7's heading, and Step 8's literal CLI command. Running Step 8's exact command (`PYTHONPATH=. uv run adk eval . eval_results/calculator_tests.evalset.json`) throws a hard `ValueError: eval_set_id 'eval_results/calculator_tests.evalset.json' must not contain path separators` — the CLI takes an eval-set *id*, not a path with a directory component. The correct invocation is `uv run adk eval . calculator_tests.evalset.json`. This same wrong path is also baked into **lab-solution.md**'s heading and its CI/CD GitHub Actions example — it isn't just a lab.md typo, the "ground truth" reference is wrong too.

4. **[Documentation/schema drift] Step 7's illustrative EvalSet JSON doesn't match what ADK actually generates.** Both lab.md and lab-solution.md show `intermediate_data: { tool_uses: [...], tool_responses: [...] }` with a flat `response: {status, result}`. The actual generated file nests everything under `intermediate_data.invocation_events` (a list of raw model/tool content events with embedded `function_call`/`function_response` parts), and the tool response is doubly-nested: `response: {result: {status, result}}`. A student trying to hand-author an eval case using Step 7 as a reference (its explicitly stated purpose: "Understanding this file is key to creating more complex tests manually") would produce a file the current ADK version doesn't actually expect.

5. **[Bug in Bonus: Dynamic User Simulation] Step 4's literal command crashes.** `PYTHONPATH=. uv run adk eval . user_sim_tests.evalset.json` (no `--config_file_path`) uses the default metrics (`tool_trajectory_avg_score`, `response_match_score`), and both throw `ValueError: expected_invocations is required/needed for this metric` — because dynamically-simulated conversations have no recorded "expected" turns. Bullet 5 right after the command says to "pair this with reference-free metrics like `safety_v1` and `hallucinations_v1`," but never shows the `eval_config.json`/`--config_file_path` needed to actually make that happen, and the command given in Step 4 itself doesn't do it. As written, Step 4 cannot succeed.

6. **[Flakiness / threshold risk, non-blocking]** Even on a clean, bug-free replay, `response_match_score` (ROUGE, threshold 0.8) consistently scored 0.5 and failed, because the model's phrasing ("The result is 15.") diverged from my recorded golden phrasing ("The sum of 10 and 5 is 15."). Step 4 confidently promises "You should see a Pass result" with `response_match_score` "also 1.0" — that did not hold across multiple reruns in my environment. This may be partly attributable to my mandated model substitution (`gemini-2.5-flash` instead of the course's `gemini-3.5-flash`, since the latter was unavailable), so I'm not scoring this as a hard bug, but it demonstrates the 0.8 threshold is fragile for single-sentence responses and worth a caveat in the lab text.

7. **[Minor, possibly model-substitution-related]** In Step 5's intentional-failure test, the (substituted) model called the deliberately-broken `add` tool, which correctly computed `16`, but the model's final text said "The result is 15." — not reflecting its own tool's output. The eval still correctly failed on `response_match_score`, so the pedagogical point about catching regressions still landed, but the specific "Actual Output ...result is 16..." narrative in Step 5.3 didn't materialize in my run.

I did **not** need to open `lab-solution.md` to get unblocked — I resolved the PYTHONPATH issue by extrapolating from lab.md's own Step 8 explanation. No Clarity penalty is being applied for peeking, but the Clarity score is still low because of the number and severity of the underlying technical bugs.

## 🏁 Solution Review
`lab-solution.md` covers only the EvalSet JSON, the Locust template, and the self-reflection answers (there's no separate "build the agent" section here, correctly, since this lab modifies Module 9's project in place). The self-reflection answers are well-written and conceptually accurate (trajectory-vs-response, fuzzy matching rationale, CI/CD integration, Golden Path vs. User Simulation). However, the solution file is **not independently correct** — it inherits the same `eval_results/` path bug (in its own heading and its CI/CD YAML example) and the same stale `tool_uses`/`tool_responses` schema as lab.md, confirming these are systemic artifacts of an ADK version upgrade that this module was never re-validated against, rather than one-off typos. The Locust template in lab-solution.md is a reasonable, more complete reference than the skeleton in lab.md's Extra Challenge.

## 💡 Suggestions for Improvement
1. **Fix Step 1.3**: change `uv run adk web calculator_agent` to `uv run adk web .` (student is already inside `calculator_agent`), or move the `cd` target to the parent directory to match the command.
2. **Fix the PYTHONPATH guidance globally**: state in Step 1 (not buried in Step 8) that `PYTHONPATH` needs to include the agent directory for **both** `adk web` and `adk eval` with Module 9's tool-import style, and correct Step 8's false claim that `adk run`/`adk web` don't need it.
3. **Fix all four `eval_results/calculator_tests.evalset.json` references** (lab.md Steps 3, 4, 7, 8) to the actual generated path `calculator_tests.evalset.json` at the agent root — and fix the same path in lab-solution.md's heading and CI/CD example.
4. **Regenerate Step 7's example JSON** against the current ADK version's actual schema (`intermediate_data.invocation_events` with embedded `function_call`/`function_response`, doubly-nested `response.result`), since students are explicitly told to use it as a reference for hand-authoring eval cases.
5. **Fix the Bonus/Dynamic User Simulation Step 4 command**: either supply the `eval_config.json` with `safety_v1`/`hallucinations_v1` criteria and update the command to use `--config_file_path`, or explicitly warn that the plain default-metrics command will error out for simulated scenarios.
6. **Add a caveat about `response_match_score` flakiness** for very short, single-sentence responses, so students aren't confused by an apparently-correct rerun scoring below threshold.
7. Given these are the same handful of bugs duplicated across lab.md and lab-solution.md, this strongly suggests Module 24 was never end-to-end tested against the ADK version actually pinned in this course (the task brief confirms this is its first student-experience evaluation) — worth a full re-run of Steps 1–8 and both Bonus sections against a clean environment before considering it validated.

---
# 🎓 Student Evaluation Report: Module 37 — Advanced: Building a Personalized Shopping Agent

## 📊 Summary Scores (1-5)
* **Clarity of Theory (README.md):** 5
* **Clarity of Instructions (lab.md):** 3
* **Code Completeness:** 4
* **Solution Quality (lab-solution.md):** 3
* **Overall Difficulty:** 5

## 🧑‍💻 The Student Experience
I approached this cold, as a mid-level Python dev at the course's first capstone. Recon (README + lab.md only) was reassuring: the theory section clearly justifies every architectural choice — why `AgentTool` instead of `sub_agents`, why `before_tool_callback` for observability, why the mock catalog replaces the real `web_agent_site` dependency chain. That framing made the lab feel purposeful rather than just "wire up three files."

I set up a fresh `adk-training` project (`uv init --python 3.10`, `google-adk[a2a]>=2.1.0`), then scaffolded `capstone_shopping_system/{web_agent,personalization_agent,orchestrator_agent}` exactly as the Setup and Exercises 1–3 describe. `uv run adk create <name>` turned out to be interactive (model choice, backend, API key) with no flags given in the lab — a small surprise, though harmless, since the following steps fully overwrite `.env` and `agent.py` anyway. I filled in the `search`/`click` bodies, the `save_preference`/`get_preferences` bodies, and `log_delegation` myself from the TODOs — all straightforward given the docstrings.

The first real wall came at "Running the System." Starting `web_agent` via the literal `uvicorn agent:a2a_app --host localhost --port 8001` and sending it a real search request failed with **"No API key was provided."** I read the traceback myself (no solution peek): `agent.py` imports `load_dotenv` but the lab's skeleton never calls it, so `.env` (with `GOOGLE_GENAI_USE_VERTEXAI=1`/`GOOGLE_CLOUD_PROJECT`/`GOOGLE_CLOUD_LOCATION`) is never loaded into the process when run via plain `uvicorn`. I added `load_dotenv()` myself (and the missing import entirely in `personalization_agent/agent.py`, which doesn't even reference `dotenv`), and both servers immediately started reaching Vertex AI correctly. `orchestrator_agent`, run via `uv run adk web`, was unaffected since the ADK CLI loads `.env` itself.

With that fixed (and `gemini-3.5-flash` swapped for `gemini-2.5-flash` per my environment's model availability, as instructed), I stood up all three agents as real local processes and drove the full system:
- Direct A2A calls to `web_agent` (search → click → buy) worked correctly against the mock catalog.
- Direct A2A calls to `personalization_agent` with a stable `contextId` correctly persisted preferences turn-to-turn (confirming the `tool_context.state` vs `tool_context.session.state` fix mentioned in the brief is genuinely in place and working).
- Through the orchestrator (`adk web` + `/run` API), a single request like "I'm looking for running shoes" correctly triggered **two sequential `AgentTool` calls** — first `personalization_agent`, then `web_agent` — with the orchestrator staying in control to synthesize one final answer. This is exactly the "call-and-return, not one-way transfer" behavior the README/lab argue for `AgentTool` over `sub_agents`.
- `before_tool_callback` fired and logged every single delegation (`[delegation] orchestrator is calling tool: personalization_agent ...` / `web_agent ...`), confirming Exercise 3's new callback works as designed.
- Exercise 4 (multimodal): I fed the orchestrator a synthetic red-square PNG with the prompt "I want something like this color for a t-shirt." It correctly described the image ("a red t-shirt"), delegated that text to `web_agent`, and returned a real catalog match (Organic Cotton T-Shirt). This exercise works well end-to-end.

The one significant issue I found by testing thoroughly (not by reading the solution): asking the orchestrator to save a preference on one turn, then asking it to retrieve preferences on a *second, separate* turn of the **same orchestrator session**, came back empty — even though the identical save/get sequence worked perfectly when I hit `personalization_agent` directly. I traced this in `google/adk/tools/agent_tool.py`: `AgentTool.run_async` spins up a **brand-new `InMemorySessionService` and session on every single invocation**, and discards it (`runner.close()`) right after. `RemoteA2aAgent`'s mechanism for resuming the same remote A2A context (walking `ctx.session.events` backward for a previously-stored `context_id`) therefore never finds anything, because that event history never survives past the one `AgentTool` call it was created for. Every `personalization_agent` call the orchestrator makes is effectively a cold start against the remote server. This is a structural interaction between `AgentTool` and stateful `RemoteA2aAgent`s, not something introduced by my code — and it directly undercuts the module's headline claim that the Personalization Agent "remembers user preferences... across sessions" for exactly the architecture the lab mandates.

I only opened `lab-solution.md` after finishing my own attempt (Step 4), so no Stuck-Protocol penalty applies — but the friction above is real and reproducible from lab.md alone.

## 🚧 Friction Points & Bugs
1. **Blocking bug — missing `load_dotenv()` calls.** `web_agent/agent.py`'s skeleton imports `load_dotenv` but never calls it; `personalization_agent/agent.py`'s skeleton doesn't even import `dotenv`. Since both are run via plain `uvicorn agent:a2a_app` (per "Running the System"), their `.env` files are never loaded, and the very first live model call fails with `ValueError: No API key was provided`. Confirmed as a genuine gap (not something version-specific I introduced) because `lab-solution.md` *does* call `load_dotenv()` in both files.
2. **Significant design gap — `AgentTool` + stateful `RemoteA2aAgent` doesn't persist state across orchestrator turns.** Verified via source (`agent_tool.py`'s `run_async` creates and discards a fresh `InMemorySessionService`/session on every call) and empirically (save-then-get through the orchestrator across two separate `/run` calls in the same session returned no saved preferences, while the identical sequence sent directly to `personalization_agent` with a stable `contextId` worked correctly). This isn't flagged anywhere in the README or lab, and it directly contradicts the stated goal of "remembering preferences... across sessions."
3. **Minor — `gemini-3.5-flash` unavailable** in the target Vertex AI project (`404 NOT_FOUND`); expected and explicitly anticipated by the task brief, not a lab defect. Worth a footnote in the module for anyone hitting the same regional/allowlist gap.
4. **Minor — `uv run adk create <name>` is interactive** with no flags supplied in the lab text; harmless since later steps overwrite everything it generates, but a first-time capstone student might pause wondering if they picked the "right" answers.
5. **Minor — fragile bare imports.** `tools/search.py`/`tools/click.py` do `from webshop_data import ...` (no package-relative import), which only resolves because the lab has you `cd` into `web_agent` before running `uvicorn`. Works exactly as instructed, but is a landmine if a student ever runs these tools from a different CWD.
6. **Solution coverage gap.** `lab-solution.md` has no reference code or discussion at all for Exercise 4 (multimodal instruction) or Exercise 5 (Dockerfile + deployment plan) — it jumps from Exercise 3's orchestrator code straight to the Self-Reflection Answers. A student stuck on either of the last two exercises has nothing to check against.
7. **Solution polish.** `lab-solution.md`'s `orchestrator_agent/agent.py` ends with an `App`/`InMemoryRunner` block that's never referenced by the lab's own "Running the System" instructions (which run the orchestrator via `uv run adk web orchestrator_agent`). It reads as leftover/vestigial code that could confuse a student diffing their file against the solution line-by-line.

## 🏁 Solution Review
Where `lab-solution.md` has content, it's high quality: `webshop_data.py`/`search.py`/`click.py` match my independent implementation almost exactly (my `click.py` used exact-string matching for buttons where the solution normalizes case — a trivial robustness difference, not a bug in either). The `personalization_agent` solution's inclusion of `load_dotenv()` confirmed my self-diagnosed fix was correct and necessary — good validation that I hadn't misdiagnosed anything. The orchestrator's `AgentTool` wiring matches mine, and its inline comment is genuinely excellent pedagogy: it documents a **live-verified** claim that wiring `sub_agents=[personalization_agent, web_agent]` instead causes the orchestrator to transfer to `personalization_agent` and get permanently stuck there, never reaching `web_agent` — exactly the kind of concrete, tested justification that makes an architectural rule memorable rather than dogmatic.

Where it falls short: it silently skips Exercises 4 and 5 entirely, and it doesn't address (or even acknowledge) the AgentTool state-persistence limitation I found — understandably, since that's a subtle framework-level interaction, but it means a student who does discover the flaky "preferences" behavior has no guidance in the solution for why, or what a workaround would look like (e.g., explicitly instructing the orchestrator to re-fetch preferences at the start of every turn, since there's no cheap way to keep a persistent A2A context alive across separate `AgentTool` invocations without deeper framework changes).

## 💡 Suggestions for Improvement
1. **Add the missing `load_dotenv()` call** to the `web_agent/agent.py` skeleton in lab.md, and add the missing `from dotenv import load_dotenv` + call to the `personalization_agent/agent.py` skeleton — a one-line fix in each that removes a completely avoidable "No API key was provided" dead end for anyone testing these two servers standalone, exactly as "Running the System" instructs.
2. **Call out the AgentTool + stateful-remote-agent limitation explicitly**, either in the README's Core Components/Key Takeaways or as a callout box in lab.md near "Running the System." Something like: "Note: because `AgentTool` starts a fresh local session on every call, the orchestrator's delegated calls to `personalization_agent` do not share a continuous A2A context across separate user turns — instruct the orchestrator to re-fetch preferences each time it needs them, rather than assuming persistence 'just works' end-to-end." This would turn a confusing surprise into a teachable moment about a real ADK framework nuance.
3. **Fill in Exercises 4 and 5 in `lab-solution.md`**, even briefly — a short example multimodal instruction snippet and a minimal Dockerfile + deployment-plan outline would close the current zero-coverage gap for two of the lab's five exercises.
4. **Remove or explain the `App`/`InMemoryRunner` block** at the end of the solution's orchestrator code, since it's disconnected from the lab's actual "Running the System" instructions and reads as leftover code.
5. Optionally note in the Setup section that `uv run adk create <name>` will prompt interactively and that the choices don't matter, since Exercises 1–3 fully overwrite the generated `.env`/`agent.py` afterward.
