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

### 🔹 Sezione 2: Tools & Capabilities (Standardizzazione Finance/Wealth)
*   [x] **Modulo 09 (Custom Tools):** Mantenuto l'esempio del "Calculator Agent" ma allineato a `uv` e alla sintassi ADK moderna (passaggio diretto funzioni nell'array `tools`).
*   [x] **Modulo 10 (Advanced Tools):** Evoluzione del Calculator in "Wealth Planner". Introdotto `ToolContext` (per leggere lo state) e `FunctionTool` per l'Human-in-the-Loop (conferma su esecuzione finto trade).
*   [x] **Modulo 11 (OpenAPI):** Sostituito Chuck Norris con "Global Market Analyst" (API Frankfurter). Spiegato l'approccio enterprise al wrapping di REST APIs senza boilerplate manuale.
*   [x] **Modulo 13.5 (Novità): "Enterprise Persistence with Firestore":** Spiegare come registrare e usare un `FirestoreSessionService` per non perdere la memoria al riavvio del server.

### 🔹 Sezione 3: Multi-Agent Systems
*   [x] **Modulo 15 (Orchestrazione):** Introdurre the pattern **"Researcher-specialist"** visto nel Lead Qualifier: un agente principale che delega la ricerca informativa a un sub-agente dedicato con `google_search`.

### 🔹 Sezione 4: Production Readiness (Il salto di qualità)
*   [x] **Modulo 25 (Observability):** Integrare l'uso di OpenTelemetry e **Cloud Trace**. Mostrare come iniettare il `session_id` nelle tracce tramite un plugin (ispirato a `SessionTelemetryPlugin`).
*   [x] **Modulo 25.5 (Novità): "Responsible AI Plugin":** Creare un plugin che usa la Cloud Natural Language API per moderare input/output in tempo reale (Pattern: Fail-Closed).
*   [x] **Modulo 26 (Testing & Eval):**
    *   Introdurre **LLM-as-a-Judge** usando gli `Evalset` di ADK.
    *   Insegnare a scrivere rubriche qualitative (`politeness`, `personalization`).
    *   Aggiungere una sezione sul **Load Testing** con Locust per misurare la latenza dei sistemi multi-agente.

---

## 🏆 Modulo 38: Best Practices & Patterns (Dettaglio Finale)
Riscriveremo questo modulo per essere la "Bibbia" del developer ADK:

1.  [x] **Clean Console Pattern:** Filtrare i warning `[EXPERIMENTAL]` e gestire i livelli di log.
2.  [x] **Configuration Management:** Gestione degli ambienti (Dev, Staging, Prod) tramite file YAML e una classe `Config` singleton.
3.  [x] **Model Configuration Hierarchy:** Riepilogo del pattern Native vs Abstraction (Gemini vs LiteLLM).
4.  [x] **Deployment Best Practices:** Dockerizzazione, Pipeline CI/CD con Cloud Build.
5.  [x] **Human-in-the-loop (HITL):** Pattern per approvazione umana su azioni critiche.

---

## ✅ Prossimi Passi Immediati (Completato)
1.  [x] Migrazione globale a **`gemini-3.5-flash`** (Standard 2026).
2.  [x] Validazione pedagogica di tutti i nuovi moduli (4.5, 13.5, 21.5, 39.5, 38) tramite `adk-student-evaluator`.
3.  [x] Aggiornamento dei timetable (`timetable-ilt.md`, `timetable-self-service.md`).
4.  [x] Implementazione dei plugin di Observability e RAI (Moduli 25 e 25.5).
