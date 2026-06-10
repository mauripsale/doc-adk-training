# 🚀 ADK 2.0 Curriculum Refactor Plan

Questo documento delinea la riorganizzazione pedagogica del corso per ADK 2.1.0+, spostando il focus dai vecchi "template" alla visione unificata di **Graph-based Workflows**.

## 📅 Nuova Roadmap MAS (Fase 3)

| Vecchio Modulo | Nuovo Modulo | Titolo | Focus Pedagogico |
| :--- | :--- | :--- | :--- |
| 15 | **15** | **Pensare a Grafi** | Intro ai Workflow, Nodi e Archi. |
| 17 + 18 | **16** | **Orchestrazione Statica** | Archi Lineari e Paralleli. Sincronizzazione con `JoinNode`. |
| 21.6 | **17** | **Routing Strutturato** | Archi condizionali tramite Dizionari di routing. |
| 21.5 | **18** | **Orchestrazione Dinamica** | Controllo totale via `@node` e Python logic. |
| 21.7 + 16 | **19** | **Team Collaborativi** | Agent Transfer, Task & Single-turn Modes. |
| 20 | **20** | **Grafi Ciclici** | Gestione di loop e self-correction nel grafo. |
| 21 | **21** | **Grafi Distribuiti** | A2A v2 come estensione del grafo locale. |

## 🛠️ Stato dei Lavori: **100% COMPLETATO**

| Modulo | Stato | Artefatto Simulazione | Note |
| :--- | :--- | :--- | :--- |
| **01-14**| ✅ OK | Varie | Fondamentali e Tools validati v2 |
| **15** | ✅ OK | - | Narrativa Graph/Node |
| **16** | ✅ OK | `simulation_module16/` | Fusione Sequenziale + Parallelo |
| **17** | ✅ OK | `simulation_module17/` | Routing Deterministico |
| **18** | ✅ OK | `simulation_module18/` | Dynamic Workflows (@node) |
| **19** | ✅ OK | `simulation_module19/` | Collaboration Modes |
| **20** | ✅ OK | `simulation_module20/` | Grafi Ciclici |
| **21** | ✅ OK | `simulation_module21/` | Distributed A2A |
| **25-38**| ✅ OK | Varie | Produzione e Best Practices validati v2 |

## ✅ Checklist di Qualità (Surgical Refactor)
- [x] Rimuovere file ridondanti (`SequentialAgent`, `ParallelAgent`).
- [x] Rinumerare le cartelle fisiche per riflettere il nuovo ordine.
- [x] Aggiornare i link "Hidden Solution" per puntare ai nuovi percorsi.
- [x] Validazione Empirica (Zero Trust) per ogni modulo rifattorizzato.
