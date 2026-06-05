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
*   [x] **Modulo 02 (Environment):** Aggiornare i requisiti a Python 3.10+ e `google-adk>=2.1.0`.
*   [x] **Modulo 06 (Programmatic):** Introdurre il concetto di `App`, `Runner` e come il runtime v2 gestisce gli eventi. (Aggiornato a pattern `App(root_agent=...)`)

### 🔹 Fase 2: Orchestrazione Moderna (Il core di ADK 2.0)
*   [x] **Modulo 21.5 (Refactoring Totale): "Dynamic Workflows with @node"**
*   [x] **Modulo 21.6: "Graph-based Workflows (Deterministic Edges)"**
*   [x] **Modulo 21.7 (Nuovo): "Collaborative Workflows (Native Hand-offs)"** - Peer-to-peer delegation senza coordinatore centrale.

### 🔹 Fase 3: Multi-Agent Systems (MAS)
*   [x] **Modulo 15 (Intro to MAS):** Refactoring della narrativa Graph/Node.
*   [x] **Modulo 16 (Coordinator Agent):** Implementazione `Agent Transfer` v2.
*   [x] **Modulo 17 (Sequential Workflows):** Migrazione a archi lineari.
*   [x] **Modulo 18 (Parallel Workflows):** Migrazione a `JoinNode`.
*   [x] **Modulo 19 (Advanced Architectures):** Introduzione ai **Nested Workflows**.
*   [x] **Modulo 20 (Iterative Refinement):** Migrazione a Dynamic Workflow Loops (@node).
*   [x] **Modulo 21 (Agent to Agent):** Migrazione a A2A v2 (Distributed Graphs).

### 🔹 Fase 4: Produzione & Best Practices
*   [x] **Modulo 38 (Best Practices):** Allineato a ADK 2.0 Resilience.
*   [x] **Modulo 13_5 (Firestore):** Migrazione a `FirestoreSessionService` v2.
*   [x] **Modulo 25 (Observability):** Integrazione nativa con **OpenTelemetry** e **Cloud Trace**. Focus su `node_info` per il debug dei grafi.
*   [x] **Modulo 25.5 (Nuovo): RAI & Safety Plugins:** Implementazione del pattern **Fail-Closed** per la sicurezza enterprise.

### 🔹 Fase 5: Estensioni & Ecosistema
*   [x] **Modulo 27 (Intro to MCP):** Integrazione del **Model Context Protocol** come set di strumenti per i Nodi Agente.
*   [x] **Modulo 28 (Building MCP Tools):** Sviluppo di server MCP personalizzati per esporre capacità di business ai grafi ADK.

---

## 🛠️ Stato dei Lavori: **100% COMPLETATO**

| Modulo | Stato | Artefatto Simulazione | Note |
| :--- | :--- | :--- | :--- |
| **02** | ✅ OK | `simulation_module02/` | Richiede v2.1.0+ |
| **06** | ✅ OK | `simulation_module06/` | Pattern App/Runner v2 |
| **13.5**| ✅ OK | `simulation_module13_5/`| Firestore v2 |
| **15** | ✅ OK | (Design Lab) | Narrativa Graph/Node |
| **16** | ✅ OK | `simulation_module16/` | Agent Transfer v2 |
| **17** | ✅ OK | `simulation_module17/` | Linear Edges v2 |
| **18** | ✅ OK | `simulation_module18_v2/`| JoinNode v2 |
| **19** | ✅ OK | `simulation_module19_v2/`| Nested Workflows v2 |
| **20** | ✅ OK | `simulation_module20/` | Dynamic @node Loops |
| **21** | ✅ OK | `simulation_module21_client/`| A2A v2 Distributed |
| **21.5**| ✅ OK | `simulation_21_5/` | Dynamic Workflows |
| **21.6**| ✅ OK | `simulation_21_6/` | Deterministic Edges |
| **21.7**| ✅ OK | `simulation_module21_7/` | Collaborative Hand-offs |
| **25** | ✅ OK | `simulation_module25/` | Observability & OTel |
| **25.5**| ✅ OK | `simulation_module25_5/` | Safety RAI |
| **27** | ✅ OK | `simulation_module27/` | **Nuovo!** MCP Consumer |
| **28** | ✅ OK | `simulation_module28/` | **Nuovo!** MCP Provider |
| **38** | ✅ OK | (Theory & Patterns) | Production Readiness |

---

## ✅ Checklist Finale di Validazione
- [x] Tutti i moduli core migrati a ADK 2.0 Workflow Runtime.
- [x] Ogni modulo validato empiricamente (Zero Trust) via `adk-student-evaluator`.
- [x] Artefatti di simulazione presenti e verificati per ogni lab tecnico.
- [x] Requisiti ambientali (Modulo 02) allineati alla v2.1.0+.
- [x] Piano di migrazione aggiornato e chiuso.
