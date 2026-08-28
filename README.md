# 🎓 Google ADK Training: From Zero to Hero 🚀

Welcome! This repository contains a comprehensive, multi-module training course for the **Google Agent Development Kit (ADK)**. Through a series of hands-on modules, you will learn the core and advanced concepts of the ADK to build, test, deploy, and observe your own AI agents.

## 🎯 Our Philosophy: From Zero to Hero

This course was born from a specific need: to create a complete learning path that takes a developer from the foundational concepts of AI agents to building complex, production-ready systems. The goal is to transform you from "Zero" to "Hero" in the world of AI Agent development with the Google ADK, providing not just the theory, but the hands-on practice required to become confident and proficient.

## ✍️ About the Author

This course was created and is maintained by [**Maurizio Ipsale**](https://www.linkedin.com/in/maurizioipsale/), a Google Cloud Authorized Trainer and Google Developer Expert (GDE) in AI and Cloud. This project stems from a passion for empowering developers with the skills needed to build the next generation of AI agents.

## 🚧 Project Status 🚧

**Current Version:** `v1.0.3`

This training course is complete and production-ready, covering the full ADK 2.0 curriculum across 40 modules — from your first agent to distributed, enterprise-grade multi-agent systems with full AgentOps observability.

We continue to refine and expand the material as the ADK evolves. Your feedback and contributions are highly encouraged! If you find an issue or have a suggestion, please [open an issue on GitHub](https://github.com/mauripsale/doc-adk-training/issues).

**What's new in `v1.0.3`:** ADK 2.4-2.6 coverage completed, plus a full empirical re-validation pass (every change below was actually run, not just reasoned about) that surfaced several pre-existing bugs unrelated to prior updates —

*Coverage:*
*   **Module 18:** a "Going Further" section on using a `@node` directly as an `Agent` tool, paired with `RequestInput`/`ResumabilityConfig` for human-in-the-loop pause-and-resume.
*   **Module 26:** noted `BasePlugin`'s notification-only `on_agent_error_callback`/`on_run_error_callback`, and added an explicit run/test step.
*   **Module 28:** noted `to_mcp_server` as the agent-level counterpart to Module 27's tool-level MCP server.
*   **Module 39.5:** pointed to `GkeCodeExecutor`/`AgentEngineSandboxCodeExecutor` as production-safe alternatives to `UnsafeLocalCodeExecutor`.

*Bugs found and fixed via empirical re-validation (student simulations that actually run the code):*
*   **Module 9 & 12:** fixed `adk run agent.py` (needs a directory, not a file) in both modules.
*   **Module 21:** fixed a nonexistent tool (`GoogleSearchAgentTool` → `google_search`), a missing dependency, and a wrong agent-card URL that silently blocked the entire A2A lab.
*   **Module 24:** fixed `adk eval`'s missing `__init__.py`/`PYTHONPATH` requirement and corrected both bonus sections' JSON formats and CLI commands.
*   **Module 27:** fixed a missing `mcp` install (the extra is required, not optional).
*   **Module 28:** fixed a CWD-dependent path and a directory-naming mismatch that broke the lab when run as documented.
*   **Module 33:** fixed a broken YAML indentation that caused `kubectl` to silently discard the Deployment's `spec`.
*   Removed a handful of stale `adk create` CLI prompts referenced across several modules.

**What's new in `v1.0.2`:** a second pass, this time against ADK 2.6.0 —
*   **Module 12:** noted `ManagedAgent`'s new `instruction` parameter.
*   **Module 24:** added hands-on "Custom Metric" and "Dynamic User Simulation" bonus sections, closing a gap where the theory mentioned both but the lab never demonstrated them.
*   **Module 26:** introduced `ReflectAndRetryModelPlugin` and `ReflectAndRetryToolPlugin` as concrete, production-ready examples of the plugin pattern.

**What's new in `v1.0.1`:** a pass against the latest official ADK documentation, keeping the course current as the framework evolves —
*   **Module 12:** a "Looking Ahead" note on the new (Preview) `ManagedAgent`.
*   **Module 21:** fixed the A2A lab to opt into ADK's reliability-fixed executor (`use_legacy=False`), avoiding known streaming-mode message-duplication bugs.
*   **Module 27:** a new bonus section connecting to a *remote* MCP server (`StreamableHTTPConnectionParams`) via the public GitHub MCP server, in addition to the existing local/Stdio example.
*   **Module 28:** aligned MCP naming (`McpToolset`) with the current official SDK.
*   **Module 33:** a bonus callout showing the automated `adk deploy gke` shortcut alongside the manual walkthrough.
*   **Module 39.5:** noted the Skills feature's experimental status and added a "Going Further" section on the (Preview) Skill Registry.

## ⏱️ Time Estimation

This comprehensive training course is designed for both self-service and instructor-led delivery. The estimates below provide a realistic guide for pacing, considering the technical depth and hands-on nature of the labs.

*   🧑‍💻 **Self-Service (SS) Duration:** This estimate reflects the time a motivated individual learner would take to read the theory, complete the labs, and account for a 25% troubleshooting/review factor.
*   👨‍🏫 **Instructor-Led Training (ILT) Duration:** This estimate is tailored for a classroom environment (up to 16 participants) with a net delivery time of 6 hours per day. It includes a 75% buffer for instructor guidance, Q&A, and assisting students during labs, plus a 5-minute transition buffer between modules.

---

## ⏱️ Course Outline

### 🌱 Part 1: Foundations (Modules 1-7)
This part covers the absolute basics of AI agents and the ADK, getting your environment set up and guiding you through building and running your first agents, including multimodal capabilities.

*   📖 **[Module 1: Introduction to AI Agents & Google ADK](./training/module01-intro-to-ai-agents/)** (🧑‍💻 35 min / 👨‍🏫 55 min)
*   📖 **[Module 2: Setting Up Your Development Environment](./training/module02-environment-setup/)** (🧑‍💻 40 min / 👨‍🏫 60 min)
*   📖 **[Module 3: Your First Agent: The "Echo" Agent](./training/module03-first-agent-echo/)** (🧑‍💻 35 min / 👨‍🏫 55 min)
*   📖 **[Module 4: Core Agent Concepts: `LlmAgent` Deep Dive](./training/module04-agent-deep-dive/)** (🧑‍💻 30 min / 👨‍🏫 50 min)
*   📖 **[Module 4.5: Professional Model Configuration & Resiliency](./training/module04_5-multi-model-litellm/)** (🧑‍💻 30 min / 👨‍🏫 45 min)
*   📖 **[Module 5: Running and Interacting with Agents](./training/module05-running-agents/)** (🧑‍💻 30 min / 👨‍🏫 50 min)
*   📖 **[Module 6: Running an Agent Programmatically](./training/module06-programmatic-execution/)** (🧑‍💻 35 min / 👨‍🏫 55 min)
*   📖 **[Module 7: Multimodal and Images 📸](./training/module07-multimodal-and-images/)** (🧑‍💻 40 min / 👨‍🏫 60 min)

### 🛠️ Part 2: Tools & Capabilities (Modules 8-14)
This part focuses on giving your agents "superpowers" by connecting them to tools, from built-in capabilities to custom functions and third-party libraries.

*   🧰 **[Module 8: Introduction to Tools](./training/module08-intro-to-tools/)** (🧑‍💻 35 min / 👨‍🏫 55 min)
*   🧰 **[Module 9: Intro to Custom Function Tools](./training/module09-intro-custom-function-tools/)** (🧑‍💻 45 min / 👨‍🏫 70 min)
*   🧰 **[Module 10: Stateful Tools & ToolContext](./training/module10-advanced-function-tools/)** (🧑‍💻 40 min / 👨‍🏫 65 min)
*   🧰 **[Module 11: OpenAPI Tools](./training/module11-openapi-tools/)** (🧑‍💻 35 min / 👨‍🏫 55 min)
*   🧰 **[Module 12: Built-in Tools and Grounding](./training/module12-built-in-tools-grounding/)** (🧑‍💻 30 min / 👨‍🏫 45 min)
*   🧰 **[Module 13: Advanced Interactions: Actions & HITL](./training/module13-tool-context/)** (🧑‍💻 40 min / 👨‍🏫 65 min)
*   🧰 **[Module 13.5: Extending ADK - Custom Persistence with Firestore](./training/module13_5-firestore-persistence/)** (🧑‍💻 30 min / 👨‍🏫 45 min)
*   🧰 **[Module 14: Third-Party Tools](./training/module14-third-party-tools/)** (🧑‍💻 30 min / 👨‍🏫 40 min)

### 🤖🤖 Part 3: Multi-Agent Systems (Modules 15-21)
Learn how to go beyond single agents and build complex systems where multiple agents collaborate to solve complex problems using ADK 2.0 Graph-based Workflows.

*   🤝 **[Module 15: Introduction to Multi-Agent Systems](./training/module15-intro-to-multi-agent-systems/)** (🧑‍💻 15 min / 👨‍🏫 30 min)
*   🤝 **[Module 16: Static Orchestration](./training/module16-static-orchestration/)** (🧑‍💻 40 min / 👨‍🏫 60 min)
*   🤝 **[Module 17: Structured Routing](./training/module17-structured-routing/)** (🧑‍💻 30 min / 👨‍🏫 45 min)
*   🤝 **[Module 18: Dynamic Orchestration](./training/module18-dynamic-orchestration/)** (🧑‍💻 40 min / 👨‍🏫 65 min)
*   🤝 **[Module 19: Collaborative Teams](./training/module19-collaborative-teams/)** (🧑‍💻 45 min / 👨‍🏫 75 min)
*   🤝 **[Module 20: Cyclic Workflows](./training/module20-cyclic-workflows/)** (🧑‍💻 40 min / 👨‍🏫 65 min)
*   🤝 **[Module 21: Distributed Graphs](./training/module21-distributed-graphs/)** (🧑‍💻 50 min / 👨‍🏫 70 min)
*   🏁 **[Module 21.5: MAS Knowledge Milestone](./training/module21_5-mas-knowledge-milestone/)** (🧑‍💻 15 min / 👨‍🏫 30 min)

### 🏭 Part 4: Production Readiness (Modules 22-26)
This part covers the essential features for making your agents robust, observable, and reliable in a production environment.

*   🧠 **[Module 22: State and Memory](./training/module22-state-and-memory/)** (🧑‍💻 35 min / 👨‍🏫 55 min)
*   📦 **[Module 23: Artifacts](./training/module23-artifacts/)** (🧑‍💻 40 min / 👨‍🏫 65 min)
*   🧪 **[Module 24: Evaluation](./training/module24-evaluation/)** (🧑‍💻 50 min / 👨‍🏫 75 min)
*   📊 **[Module 25: Observability](./training/module25-observability/)** (🧑‍💻 35 min / 👨‍🏫 55 min)
*   🦺 **[Module 25.5: Responsible AI (RAI) & Safety Plugins](./training/module25_5-rai-safety-plugins/)** (🧑‍💻 35 min / 👨‍🏫 55 min)
*   🛡️ **[Module 26: Callbacks](./training/module26-callbacks/)** (🧑‍💻 40 min / 👨‍🏫 65 min)

### 🔌 Part 5: Advanced Integrations & UI (Modules 27-30)
This section covers advanced tooling with the Model Context Protocol (MCP) and strategies for integrating your agents with user interfaces.

*   🔗 **[Module 27: Introduction to MCP](./training/module27-intro-to-mcp/)** (🧑‍💻 40 min / 👨‍🏫 65 min)
*   🔗 **[Module 28: Building MCP Tools](./training/module28-building-mcp-tools/)** (🧑‍💻 40 min / 👨‍🏫 65 min)
*   🖼️ **[Module 29: UI Integration Intro](./training/module29-ui-integration-intro/)** (🧑‍💻 35 min / 👨‍🏫 55 min)
*   🖼️ **[Module 30: Custom Streaming Client](./training/module30-custom-streaming-client/)** (🧑‍💻 45 min / 👨‍🏫 65 min)

### ☁️ Part 6: Deployment & Enterprise (Modules 31-36)
Learn how to deploy your agents and their components to various scalable cloud environments, including enterprise-grade platforms.

*   🚀 **[Module 31: Production Deployment Strategies](./training/module31-production-deployment-strategies/)** (🧑‍💻 15 min / 👨‍🏫 25 min)
*   🚀 **[Module 32: Deployment to Cloud Run](./training/module32-deployment-cloud-run/)** (🧑‍💻 35 min / 👨‍🏫 50 min)
*   🚀 **[Module 33: Deployment to GKE](./training/module33-deployment-gke/)** (🧑‍💻 60 min / 👨‍🏫 95 min)
*   🚀 **[Module 34: Deploying an MCP Server to Cloud Run](./training/module34-deploying-mcp-server-cloud-run/)** (🧑‍💻 70 min / 👨‍🏫 105 min)
*   🚀 **[Module 35: Deployment to Agent Runtime](./training/module35-deployment-agent-runtime/)** (🧑‍💻 60 min / 👨‍🏫 90 min)
*   🚀 **[Module 36: Gemini Enterprise](./training/module36-gemini-enterprise/)** (🧑‍💻 15 min / 👨‍🏫 25 min)

### 🏆 Part 7: Capstone Project & Best Practices (Modules 37-40)
Apply everything you've learned in a final capstone project, review essential best practices for building production-ready agents, and explore advanced extensibility patterns like plugins and skills before tackling a full enterprise-grade capstone.

*   ✨ **[Module 37: Advanced Personalized Shopping Agent](./training/module37-advanced-personalized-shopping-agent/)** (🧑‍💻 85 min / 👨‍🏫 120 min)
*   ✨ **[Module 38: Best Practices](./training/module38-best-practices/)** (🧑‍💻 35 min / 👨‍🏫 50 min)
*   🔌 **[Module 39: ADK Plugins](./training/module39-plugins/)** (🧑‍💻 35 min / 👨‍🏫 50 min)
*   🎓 **[Module 39.5: Agent Skills](./training/module39_5-agent-skills/)** (🧑‍💻 35 min / 👨‍🏫 50 min)
*   🎯 **[Module 40: Advanced Capstone - Aegis Incident Response & AgentOps](./training/module40-advanced-capstone-aegis-incident-response/)** (🧑‍💻 100 min / 👨‍🏫 140 min)

---
## Detailed Timetables

For a detailed breakdown of the time required for each module, please see the following timetables:

*   **[🧑‍💻 Self-Service (SS) Detailed Timetable](./timetable-self-service.md)**
*   **[👨‍🏫 Instructor-Led Classroom (ILC) Detailed Timetable](./timetable-ilt.md)**

---
## 📚 Course Variants

While this repository contains the full, comprehensive "From Zero to Hero" track, we also offer shorter, focused delivery variants for different training needs:

*   **[Variant A: 1-Day Workshop (ILC)](./variant-a-1-day-workshop.md)**: A high-impact, 6-hour workshop focused on building your first tool-powered agent.
*   **[Variant B: Standard 2-Day ILT](./variant-b-2-day-ilt.md)**: A comprehensive 2-day course covering all foundational and key intermediate skills.
---

## ▶️ Getting Started

Before you begin, please ensure you have the following prerequisites installed:
*   Git
*   Python 3.11+
*   A Google Cloud Project with billing enabled
*   The Google Cloud CLI (`gcloud`)

To get started with the course:
1.  **Clone the repository:** `git clone https://github.com/mauripsale/doc-adk-training.git`
2.  **Navigate to the directory:** `cd training`
3.  **Begin with Module 1** and proceed through the modules in order. Each lab builds upon the concepts and code from the previous one.

Happy building!

---

## 🤝 Contributing

Contributions are welcome! If you find an issue, have a suggestion for a new module, or want to improve the existing content, please see our **[Contributing Guidelines](./CONTRIBUTING.md)** to get started.

---

## 📜 Licensing

The documentation and textual content of this training course are licensed under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)**.

Software components, such as the code in the `sample-agents` directory, are licensed under the **Apache License, Version 2.0**. Please see the `LICENSE` file within those directories for full details.

## 🙏 Acknowledgements

This training course was initially inspired by the ADK Training Hub created by Raphael Mansuy. The course has since evolved its own structure and challenge-lab-based pedagogy, with all content originally written and adapted — but we gratefully acknowledge his early influence.
