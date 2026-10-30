# Variant A: 1-Day Fast-Track Workshop (Executive & Crash Course)

**Total Estimated Instruction & Lab Time:** 330 minutes (~5.5 hours) + 60 minutes buffer (Lunch, Breaks, Q&A)

This workshop is a high-impact, fast-paced training variant designed to provide a self-contained, hands-on learning experience. The selected modules form the **critical path of modern agent engineering** with **Google ADK 2.0** and the **Google Agents CLI (`agents-cli`)**, taking developers from zero setup to building, running, and testing a tool-powered, grounded AI agent powered by **`gemini-3.8-flash`**, complete with Model Context Protocol (MCP) tool integration.

---

## 🎯 Target Audience & Prerequisites
* **Target Audience:** Tech Leads, Solution Architects, Backend Engineers, and Product Technical Directors who need an intensive, practical immersion into agent architecture in a single day.
* **Prerequisites:** Intermediate Python (3.10+), familiarity with virtual environments (`uv` / `venv`), and a Google Gemini API Key.
* **Standard Model:** `gemini-3.8-flash`.

---

## 📋 Module Selection & Timetable

| Order | Module | Duration (min) | Type | Justification & Learning Outcomes |
| :---: | :--- | :---: | :---: | :--- |
| **1** | [Module 01: Introduction to AI Agents & Google ADK](./training/module01-intro-to-ai-agents/) | 35 | Theory | Essential foundation: agent loop, reasoning vs deterministic logic, ADK 2.0 architecture. |
| **2** | [Module 02: Setting Up Your Development Environment](./training/module02-environment-setup/) | 35 | Lab | Environment initialization with `uv`, `google-adk`, `agents-cli`, and API credentials. |
| **3** | [Module 03: Your First Agent: The "Echo" Agent](./training/module03-first-agent-echo/) | 30 | Lab | Hands-on: Agent anatomy, constructor patterns, and minimal execution with `gemini-3.8-flash`. |
| **4** | [Module 04: Core Agent Concepts: `LlmAgent` Deep Dive](./training/module04-agent-deep-dive/) | 35 | Theory/Lab | Controlling behavior via system instructions, output schemas, and prompt best practices. |
| **5** | [Module 05: Running and Interacting with Agents](./training/module05-running-agents/) | 30 | Lab | Interactive chat testing via `adk web` (launched from parent dir) and the CLI REPL runner. |
| **6** | [Module 08: Introduction to Tools](./training/module08-intro-to-tools/) | 30 | Theory | Core concept: function calling mechanics, JSON schema translation, and tool declaration. |
| **7** | [Module 09: Intro to Custom Function Tools](./training/module09-intro-custom-function-tools/) | 55 | Lab | Core hands-on: Python type hints, docstrings-as-schemas, error handling, and parameter validation. |
| **8** | [Module 12: Built-in Tools and Grounding](./training/module12-built-in-tools-grounding/) | 25 | Lab | Instant enterprise value: grounding responses with real-time Google Search. |
| **9** | [Module 27: Introduction to MCP](./training/module27-intro-to-mcp/) | 35 | Theory/Lab | Modern standard: connecting ADK agents to external Model Context Protocol (`McpToolset`) servers. |
| **10** | [Module 38: Production Best Practices & Deployment Preview](./training/module38-best-practices/) | 20 | Summary | Architecture review, safety guidelines, and deployment paths (`agents-cli deploy` / Cloud Run). |
| **—** | **Dedicated Q&A, Setup Buffer & Troubleshooting** | **60** | Buffer | Distributed across the day for breaks, instructor debugging, and architecture discussion. |
| **TOTAL** | **1-Day Fast-Track Workshop** | **390 min** | — | **6.5 Hours Total (330 min active instruction + 60 min buffer)** |

---

## 🛠️ Verification & Evaluation
* **Knowledge Checks:** Each module includes interactive **Socratic Quizzes** inside the documentation and hands-on challenge labs with test scripts (`pytest`).
