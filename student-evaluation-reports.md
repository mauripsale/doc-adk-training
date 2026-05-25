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
