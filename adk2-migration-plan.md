# 🚀 ADK 2.0 Migration & Refactoring Plan

Questo documento traccia la migrazione del corso "Google ADK: From Zero to Hero" dalla versione 1.x alla **versione 2.0+ (Workflow Runtime)**.

## 🎯 Obiettivi della Migrazione
1.  **Allineamento Tecnico:** Sostituire i pattern gerarchici legacy con il nuovo **Workflow Graph Engine**.
2.  **Semplificazione Pedagogica:** Sfruttare i **Dynamic Workflows** (`@node`) per rendere l'orchestrazione più accessibile.
3.  **Resilienza Nativa:** Integrare le nuove funzionalità di framework per Retry e Human-in-the-Loop (HITL).
4.  **Zero Legacy:** Rimuovere ogni riferimento a `_run_async_impl` manuale e altre API deprecate.

---

## 📅 Roadmap degli Interventi

### 🔹 Fase 1: Fondamentali & Setup
*   [ ] **Modulo 02 (Environment):** Aggiornare i requisiti a Python 3.10+ e `google-adk>=2.1.0`.
*   [ ] **Modulo 06 (Programmatic):** Introdurre il concetto di `Context` e come il runtime v2 gestisce gli eventi.

### 🔹 Fase 2: Orchestrazione Moderna (Il core di ADK 2.0)
*   [x] **Modulo 21.5 (Refactoring Totale): "Dynamic Workflows with @node"**
    *   Sostituire la classe `SmartRouterAgent` (ereditarietà `BaseAgent`) con una funzione decorata `@node`.
    *   Insegnare l'uso di `ctx.run_node()` per l'esecuzione di sub-agenti e tool.
*   [ ] **Nuovo Modulo 21.6: "Graph-based Workflows (Deterministic Edges)"**
    *   Introdurre la classe `Workflow` e la definizione esplicita di `edges`.
    *   Mostrare il pattern Router deterministico tramite dizionario di archi.

### 🔹 Fase 3: Multi-Agent Systems (MAS)
*   [ ] **Moduli 15-21:** Rivedere la narrativa. Gli agenti non sono più solo "entità", mas **Nodi** in un grafo.
*   [ ] **Collaborative Workflows:** Introdurre i nuovi pattern di collaborazione nativa di ADK 2.0.

### 🔹 Fase 4: Produzione & Best Practices
*   [x] **Modulo 38 (Best Practices):**
    *   **Error Handling:** Insegnare a propagare le eccezioni per farle gestire dal framework (RetryConfig).
    *   **Telemetry:** Spiegare i nuovi campi `node_info` negli Eventi.
*   [ ] **Modulo 13_5 (Firestore):** Verificare la compatibilità del nuovo schema `Event` (campi `node_info` e `output`) con il servizio di persistenza.

---

## 🛠️ Stato dei Lavori

| Modulo | Stato | Note |
| :--- | :--- | :--- |
| 02 | ⏳ In Attesa | Da aggiornare versione ADK |
| 21.5 | ✅ Completato | Migrato a Dynamic Workflows (@node) |
| 13_5 | ⏳ In Attesa | Da verificare schema Firestore |
| 38 | ✅ Completato | Aggiornato a Framework-Level Resilience |

---

## ✅ Checklist di Validazione (per modulo)
- [ ] Codice testato in ambiente Python 3.10 + ADK 2.1.0.
- [ ] README.md aggiornato con terminologia "Graph/Node/Workflow".
- [ ] Lab Challenge completato con successo da `adk-student-evaluator`.
- [ ] Soluzione verificata e spoiler-free nel branch `main`.
