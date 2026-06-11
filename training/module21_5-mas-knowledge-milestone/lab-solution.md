---
sidebar_position: 3
title: "Solution & Architect Insights"
---

# Lab 21.5 Solution: Architecting Multi-Agent Systems

## Goal

This solution provides the architectural blueprints and justifications for the scenarios presented in the Milestone Challenge.

---

### Scenario 1: The Legal Review Pipeline
**Recommended Pattern:** **Hybrid Static + Structured Routing**

*   **Design:**
    1.  `START` -> `Extractor`
    2.  `Extractor` -> `PrivacyChecker` (Edge 1)
    3.  `Extractor` -> `LiabilityChecker` (Edge 2)
    4.  `PrivacyChecker` -> `JoinNode`
    5.  `LiabilityChecker` -> `JoinNode`
    6.  `JoinNode` -> `ReviewRouter` (Structured Routing via Dictionary)
    7.  `ReviewRouter` -> `SeniorPartner` (IF high risk)
    8.  `ReviewRouter` -> `Summarizer` (IF low risk)

*   **Justification:**
    *   **Performance:** Using parallel edges and a `JoinNode` ensures that both legal checks happen concurrently, minimizing wait time.
    *   **Predictability:** The logic for "High Risk" vs "Low Risk" should be deterministic (Structured Routing) to ensure every contract follows the exact legal procedure.

---

### Scenario 2: The Multi-Turn Story Writer
**Recommended Pattern:** **Cyclic Workflow (Module 20)**

*   **Design:**
    1.  `START` -> `Writer`
    2.  `Writer` -> `Critic`
    3.  `Critic` -> `Writer` (IF "Too Scary") <-- **The Cycle**
    4.  `Critic` -> `END` (IF "Satisfied")

*   **Justification:**
    *   **Iteration:** This scenario requires a feedback loop. A Cyclic graph is the most efficient way to represent self-correction without recursing into a deep call stack.

---

### Scenario 3: The Global Enterprise Support Bot
**Recommended Pattern:** **Distributed Graphs (A2A - Module 21)**

*   **Design:**
    1.  `START` -> `WebOrchestrator`
    2.  `WebOrchestrator` -> `RemoteA2aAgent` (EU Logistics)

*   **Justification:**
    *   **Security & Ownership:** Since the EU agent is in a different project and managed by a different team, the **A2A protocol** is mandatory. It allows the main bot to delegate tasks securely over the network without needing access to the EU agent's source code or private project resources.

---

## Self-Reflection Answers

1.  **Hybrid Approach:** Real systems often start with a static business process (Static) but then encounter "messy" data that needs Python logic (Dynamic) or external expertise (Distributed). Hybrid designs offer the best balance of control and flexibility.
2.  **Collaborative Team Risks:** In a regulated environment, "Collaborative" agents might deviate from a strict protocol or lose the "Chain of Custody." For financial/legal tasks, **Static/Structured** graphs are preferred for auditability.
3.  **Graph Mental Model:** Business leaders understand flowcharts and process maps. Explaining an AI system as a "Graph of Nodes" makes the ROI and process logic much clearer than just saying "it's an intelligent chat."
