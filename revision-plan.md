# Piano di Revisione: ADK "From Zero to Hero" (v1.0 / Main Alignment)

Questo documento delinea le modifiche necessarie per allineare il corso "ADK from zero to hero" alla versione 1.0 (branch main) del Google Agent Development Kit (ADK), basandosi sulla documentazione ufficiale aggiornata.

## 🔍 Analisi delle Discrepanze Riscontrate

L'analisi della documentazione `llms-full.txt` (v1.0) ha evidenziato quattro aree principali in cui il corso attuale risulta incompleto o basato su pattern meno efficienti:

1.  **Integrazione Modelli Multi-Provider (LiteLLM):** ADK ora supporta nativamente OpenAI, Anthropic, Ollama e vLLM tramite il wrapper `LiteLlm`. Il corso è attualmente troppo focalizzato sui soli modelli Gemini nativi.
2.  **Custom Agents (`BaseAgent` & `_run_async_impl`):** La v1.0 introduce i Custom Agents come standard per orchestrazioni complesse. Il corso si ferma agli agenti pre-definiti (Sequential, Parallel, Loop).
3.  **Output Strutturati (`output_schema` & `output_key`):** L'uso di Pydantic per forzare output JSON e il salvataggio automatico nello stato di sessione tramite `output_key` sono funzionalità critiche per la stabilità del sistema, non ancora coperte.
4.  **Controllo Esecuzione Avanzato (Callbacks):** I nuovi trigger di callback consentono di saltare l'esecuzione di agenti (`skip`) o terminare invocazioni, funzionalità non presenti nei moduli attuali.
5.  **Agent Skills & SkillToolset:** ADK ha introdotto il supporto nativo per l'architettura delle "Agent Skills" (struttura a cartelle con `SKILL.md`), caricabili programmaticamente tramite `load_skill_from_dir` e `SkillToolset`.

---

## 📋 Roadmap della Revisione

### Fase 0: Audit & Sanitize (Risoluzione Leak Soluzioni)

Prima di introdurre nuovi concetti, è fondamentale "ripulire" i laboratori attuali dove le soluzioni sono trapelate nel codice di partenza e dove le domande di riflessione sono mal gestite.
*   **Modulo 38 (Best Practices):**
    *   *Problema:* Il file `lab.md` contiene già l'implementazione completa (es. `try/except`, `@retry`). Inoltre, le risposte alle *Self-Reflection Questions* sono state inserite per errore in fondo al file teorico `README.md` (sotto "Key Takeaways") anziché nel `lab-solution.md`.
    *   *Azione:* Sostituire il codice nel `lab.md` con funzioni vuote (usando `pass` o commenti `TODO`). Spostare le risposte dal `README.md` al `lab-solution.md`.
*   **Modulo 03 (First Agent):**
    *   *Problema:* Le *Self-Reflection Questions* presenti nel `lab.md` non hanno una risposta nel `lab-solution.md`.
    *   *Azione:* Aggiungere un paragrafo "Answers to Self-Reflection Questions" in fondo a `lab-solution.md`.
*   **Modulo 28 (MCP Tools):**
    *   *Problema:* Verificare e rimuovere eventuale logica risolutiva avanzata trapelata nello starter code di `lab.md`.

### Fase 1: Aggiornamento dei Fondamenti (Moduli 01 - 10)

*   **Modulo 04 (LLM Agent Deep Dive):**
    *   **Revisione:** Introdurre i parametri `output_schema` (con Pydantic) e `output_key`.
    *   **Laboratorio:** Creare un esercizio dove l'agente deve restituire un oggetto JSON rigido (es. estrazione entità da un testo) e salvarlo automaticamente in sessione.
    *   **Nota:** Spiegare che l'uso di `output_schema` disabilita i tool per quell'agente.

*   **NUOVO Modulo 04.5: Supporto Multi-Modello con LiteLLM**
    *   **Contenuto:** Installazione di `litellm` e configurazione del wrapper `LiteLlm`.
    *   **Laboratorio:** Switch a caldo di un agente tra Gemini e un modello locale (Ollama/Mistral) o esterno (Claude/GPT-4o) cambiando solo la riga `model=LiteLlm(...)`.
    *   **Troubleshooting:** Gestione dei prompt di sistema per modelli locali per evitare loop infiniti di chiamate a funzioni.

### Fase 2: Orchestrazione e Workflow (Moduli 15 - 20)

*   **Modulo 17 & 18 (Sequential & Parallel):**
    *   **Revisione:** Aggiornare i flussi per eliminare il parsing manuale delle stringhe.
    *   **Focus:** Passaggio di dati strutturati tra agenti tramite `ctx.session.state` popolato da `output_key`.

*   **Modulo 20 (Loop Agents):**
    *   **Revisione:** Introdurre logiche di interruzione del loop basate su flag di stato o tool di escalation (`tool_context.actions.escalate = True`).

### Fase 3: Estensibilità e Advanced (Moduli 21 - 39)

*   **NUOVO Modulo (Post-21): Creazione di Agenti Custom**
    *   **Contenuto:** Ereditarietà da `BaseAgent`, override del costruttore `__init__` e implementazione di `_run_async_impl`.
    *   **Laboratorio:** Implementare un orchestratore con logica condizionale complessa (es: "Se l'analisi del sentiment è negativa, invia a un agente umano, altrimenti prosegui con l'agente di supporto automatico").

*   **Modulo 26 (Callbacks):**
    *   **Revisione:** Introdurre `before_agent_callback`.
    *   **Laboratorio:** Implementare un meccanismo di caching: se il risultato è già nello stato, il callback usa `skip` per non invocare il modello LLM, risparmiando token e tempo.

*   **Modulo 39 (Plugins):**
    *   **Revisione:** Allineare la teoria alla doc v1.0, formalizzando l'ereditarietà da `BasePlugin` e i tre pattern operativi: *Observing, Intervening, Amending*.
    *   **Focus:** Verificare che il `ReflectAndRetryToolPlugin` e l'aggancio al `Runner` usino le firme dei metodi aggiornate.

*   **NUOVO Modulo 39.5: Integrazione Agent Skills**
    *   **Contenuto:** Concetto di "Progressive Disclosure" del context. Architettura a tre livelli di una skill (`L1 Frontmatter`, `L2 Instructions` in `SKILL.md`, `L3 Resources` in `references/`, `assets/`, `scripts/`).
    *   **Laboratorio:** Usare `google.adk.skills.load_skill_from_dir` e `google.adk.tools.skill_toolset.SkillToolset` per caricare la skill `adk-skill` che abbiamo appena creato, aggiungendola ai `tools` dell'agente. Mostrare come l'agente decide autonomamente quando leggere i file di riferimento associati alla skill.

### Fase 4: Finalizzazione e Best Practices (Modulo 38)

*   **Modulo 38 (Best Practices):**
    *   **Integrazione:** Aggiungere la matrice decisionale ufficiale ADK per la scelta del tipo di agente (`LlmAgent` vs `WorkflowAgent` vs `CustomAgent`).

---

## ⚠️ Note Tecniche per la Revisione
- **Ambiente:** Assicurarsi che `google-adk` sia aggiornato alla v1.0+ in tutti i file `requirements.txt` o `pyproject.toml`.
- **Compatibilità:** Verificare che gli esempi Python siano compatibili con i nuovi type hints di `InvocationContext` e `Event`.
