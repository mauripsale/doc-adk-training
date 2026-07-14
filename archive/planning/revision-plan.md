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

## 📋 Stato di Avanzamento della Revisione (Audit completato)

### 🔹 Fase 0: Audit & Sanitize (Risoluzione Leak Soluzioni) — **100% COMPLETATO**
- [x] **Modulo 38 (Best Practices):** Sostituito il codice in `lab.md` con scheletri puliti (`TODO` e `pass`). Rimosse le risposte dal file teorico `README.md` e verificate correttamente in fondo a `lab-solution.md`.
- [x] **Modulo 03 (First Agent):** Aggiunto il paragrafo "Answers to Self-Reflection Questions" in fondo a `lab-solution.md`.
- [x] **Modulo 28 (MCP Tools):** Verificato lo starter code in `lab.md` per assicurare che non ci siano leak di logica e che usi correttamente `# TODO`.

### 🔹 Fase 1: Aggiornamento dei Fondamenti (Moduli 01 - 10) — **100% COMPLETATO**
- [x] **Modulo 04 (LLM Agent Deep Dive):** Introdotti i parametri `output_schema` (con Pydantic) e `output_key` nel `README.md`, nel `lab.md` (Support Analyzer) e nel `lab-solution.md`. Spiegata la limitazione dell'uso dei tool con gli output strutturati.
- [x] **Modulo 04.5 (Professional Model Configuration & Resiliency):** Nuovo modulo creato. Include la spiegazione di `Gemini` per retries resilienti e `LiteLlm` per fallback multi-modello. Laboratorio implementato e validato.

### 🔹 Fase 2: Orchestrazione e Workflow (Moduli 15 - 20) — **100% COMPLETATO**
- [x] **Moduli 17 & 18 (Sequential & Parallel):** Aggiornati i flussi per rimuovere il parsing manuale delle stringhe, passando dati strutturati tramite `ctx.session.state` popolato da `output_key`.
- [x] **Modulo 20 (Loop/Cyclic Agents):** Introdotte logiche di interruzione e loop di self-correction basate sul Workflow Runtime di ADK 2.0.

### 🔹 Fase 3: Estensibilità e Advanced (Moduli 21 - 39) — **100% COMPLETATO**
- [x] **NUOVO Modulo (Post-21): Creazione di Agenti Custom (`BaseAgent` & `_run_async_impl`):** *ESCLUSO* (Deciso di escludere questo modulo poiché in ADK 2.0 l'ereditarietà classica è considerata un pattern avanzato di nicchia, ampiamente sostituita da `@node` e `Workflow` che riducono drasticamente la complessità pedagogica).
- [x] **Modulo 26 (Callbacks):** Introdotti i trigger di callback (come `before_agent_callback`) per logging, convalida e logica di bypass/caching.
- [x] **Modulo 39 (Plugins):** Strutturata la teoria sui pattern *Observing, Intervening, Amending* e integrato l'uso del `ReflectAndRetryToolPlugin`.
- [x] **Modulo 39.5 (Agent Skills):** Nuovo modulo creato per insegnare la "Progressive Disclosure" del contesto tramite `load_skill_from_dir` e `SkillToolset`.

### 🔹 Fase 4: Finalizzazione e Best Practices — **100% COMPLETATO**
- [x] **Modulo 38 (Best Practices):** Integrata la matrice decisionale ufficiale ADK 2.0 per guidare gli studenti nella scelta tra `LlmAgent`, `WorkflowAgent` o `@node` (Custom Workflows).

---

## ⚠️ Note Tecniche per la Revisione
- **Ambiente:** Assicurarsi che `google-adk` sia aggiornato alla v1.0+ in tutti i file `requirements.txt` o `pyproject.toml`.
- **Compatibilità:** Verificare che gli esempi Python siano compatibili con i nuovi type hints di `InvocationContext` e `Event`.
