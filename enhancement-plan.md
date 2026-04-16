# 🚀 ADK Training: Course Enhancement Plan

Questo documento delinea la strategia per elevare la qualità pedagogica e tecnica del corso "Google ADK: From Zero to Hero", integrando le best practice enterprise estratte dai progetti reali (Lead Qualifier Agent).

## 🎯 Obiettivi Principali
1.  **Industrializzazione:** Passare da script isolati a una struttura di progetto professionale (uv, Makefile, linting).
2.  **Resilienza & Sicurezza:** Integrare Responsible AI (RAI) e logica di Retry avanzata.
3.  **Persistenza Enterprise:** Introdurre Firestore per la gestione reale di sessioni e dati di business.
4.  **Osservabilità & Qualità:** Implementare telemetria OTel e valutazione qualitativa (LLM-as-a-Judge).
5.  **Validazione Pedagogica:** Utilizzare sistematicamente la skill `adk-student-evaluator` per garantire l'assenza di "friction points" nei lab.

---

## 📅 Roadmap degli Interventi

### 🔹 Sezione 1: Fondamentali (Update Tecnico)
*   [x] **Refactoring base completato:** Passaggio a "Support Analyzer" e architettura App/Runner per i moduli 1-7.
*   [x] **Validazione Modulo 06:** Risolti bug nell'utilizzo di `run_debug` e ripulita la console usando lo Student Evaluator.
*   [x] **Modulo 02 (Environment):** Sostituito `pip` con **`uv`** come package manager consigliato. Introdotto il concetto di gestione automatica della versione Python (3.10+).

### 🔹 Sezione 2: Tools & Capabilities (Standardizzazione)
*   **Modulo 09 (Custom Tools):** Mantenere l'esempio del "Calculator Agent" in quanto ottimo per comprendere i fondamenti dei tool, ma aggiornare le istruzioni per usare il nuovo scaffolding `uv init` e testarlo con `uv run adk run`. Semplificare la registrazione tool (niente più `FunctionTool(fn=...)`, ma passaggio diretto della funzione come da ADK moderno).
*   **Modulo 11 (OpenAPI):** (Da definire, valutare se mantenere Chuck Norris o passare a un'API più business-oriented).
*   **Modulo 13.5 (Novità): "Enterprise Persistence with Firestore":** Spiegare come registrare e usare un `FirestoreSessionService` per non perdere la memoria al riavvio del server.

### 🔹 Sezione 3: Multi-Agent Systems
*   **Modulo 15 (Orchestrazione):** Introdurre il pattern **"Researcher-specialist"** visto nel Lead Qualifier: un agente principale che delega la ricerca informativa a un sub-agente dedicato con `google_search`.

### 🔹 Sezione 4: Production Readiness (Il salto di qualità)
*   **Modulo 25 (Observability):** Integrare l'uso di OpenTelemetry e **Cloud Trace**. Mostrare come iniettare il `session_id` nelle tracce tramite un plugin (ispirato a `SessionTelemetryPlugin`).
*   **Modulo 25.5 (Novità): "Responsible AI Plugin":** Creare un plugin che usa la Cloud Natural Language API per moderare input/output in tempo reale (Pattern: Fail-Closed).
*   **Modulo 26 (Testing & Eval):**
    *   Introdurre **LLM-as-a-Judge** usando gli `Evalset` di ADK.
    *   Insegnare a scrivere rubriche qualitative (`politeness`, `personalization`).
    *   Aggiungere una sezione sul **Load Testing** con Locust per misurare la latenza dei sistemi multi-agente.

---

## 🏆 Modulo 38: Best Practices & Patterns (Dettaglio Finale)
Riscriveremo questo modulo per essere la "Bibbia" del developer ADK:

1.  **Clean Console Pattern:**
    *   Filtrare i warning `[EXPERIMENTAL]` e gestire i livelli di log (`logging.WARNING` per le librerie Google).
2.  **Configuration Management:**
    *   Gestione degli ambienti (Dev, Staging, Prod) tramite file YAML e una classe `Config` singleton.
3.  **Model Configuration Hierarchy:**
    *   Riepilogo del pattern Native vs Abstraction (Gemini vs LiteLLM).
4.  **Deployment Best Practices:**
    *   Dockerizzazione ottimizzata.
    *   Pipeline CI/CD con Cloud Build che includono unit test, integration test e **eval-tests**.
5.  **Human-in-the-loop (HITL):**
    *   Pattern per approvazione umana su azioni critiche.

---

## ✅ Prossimi Passi Immediati (In Corso)
1.  [x] Upgrade a `uv` e Python 3.10 per il Modulo 02 completato.
2.  [ ] **Modulo 09:** Refactoring del lab Calculator (aggiornamento all'API ADK moderna `tools=[my_func]` e uso di `uv`).
3.  [ ] Valutazione Modulo 09 tramite `adk-student-evaluator`.
4.  [ ] Creare lo skeleton del Modulo 38 basato su questo piano.
