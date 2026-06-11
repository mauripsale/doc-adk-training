---
sidebar_position: 2
title: "Milestone Challenge"
---

# Lab 21.5: MAS Architecture Design Challenge

## Goal

In this milestone lab, you will not write code. Instead, you will act as a **Lead AI Architect**. You will be given three business scenarios, and for each, you must:
1.  **Select** the best ADK MAS pattern.
2.  **Sketch** the graph geometry (Nodes and Edges).
3.  **Justify** your choice based on performance, cost, or maintainability.

---

### Scenario 1: The Legal Review Pipeline
A law firm needs a system to process incoming contracts.
- **Step A:** Extract all dates and names.
- **Step B:** Simultaneously check for "Privacy" violations AND "Liability" risks.
- **Step C:** If either check finds a "High" risk, send to a Senior Partner agent for final review.
- **Step D:** Otherwise, generate a "Safe to Sign" summary.

**Task:** Design the graph. Which ADK primitive handles the "Simultaneous" part? Which handles the "High Risk" decision?

---

### Scenario 2: The Multi-Turn Story Writer
A creative agency wants an agent to write children's books.
- The agent must write a chapter, then send it to a "Critic" agent.
- If the Critic says "Too Scary," the agent must rewrite the chapter and send it back to the Critic.
- This continues until the Critic is satisfied.

**Task:** What type of graph geometry is this? Which module covered this pattern?

---

### Scenario 3: The Global Enterprise Support Bot
A multinational corp has a main website agent.
- When a user asks about "Shipping in Europe," the main agent must talk to a specialized "EU Logistics" agent.
- The "EU Logistics" agent is managed by a different team in a different country and runs in its own secure Google Cloud project.

**Task:** Which MAS pattern allows agents in different projects/teams to work together?

---

### Self-Reflection Questions
- Why is a "Hybrid" approach (combining static and dynamic nodes) often the reality of production systems?
- What are the risks of using a fully "Collaborative" team (Module 19) for a strictly regulated financial process?
- How does the "Graph" mental model help you communicate with business stakeholders compared to "Chatbot" terminology?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2RvYy1hZGstdHJhaW5pbmcvbW9kdWxlMjFfNS1tYXMta25vd2xlZGdlLW1pbGVzdG9uZS9sYWItc29sdXRpb24=`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/doc-adk-training/module21_5-mas-knowledge-milestone/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>
