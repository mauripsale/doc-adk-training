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
