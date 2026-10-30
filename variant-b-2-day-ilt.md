# Variant B: Standard 2-Day ILT (Core Practitioner Track)

**Total Estimated Instruction & Lab Time:** 680 minutes (~11.3 hours) across 2 days + 120 minutes buffer (Lunch, Breaks, Q&A)

This 2-day Instructor-Led Training (ILT) is the flagship curriculum for engineering teams adopting **Google ADK 2.0** and **Google Agents CLI (`agents-cli`)**. It balances deep single-agent foundations, advanced stateful tools, session memory management, multi-agent orchestration (MAS), agent evaluation, and enterprise deployment with **`gemini-3.8-flash`**.

---

## 🎯 Target Audience & Prerequisites
* **Target Audience:** Software Engineers, Backend Developers, Cloud Architects, and AI Engineers building production-ready autonomous systems.
* **Prerequisites:** Proficient in Python (3.10+), async programming fundamentals, REST APIs, and Google Cloud basics.
* **Standard Model:** `gemini-3.8-flash`.

---

## 📅 Day 1: Single-Agent Mastery, Tools & State Management

**Focus:** Building, executing, testing, and persisting single-agent workflows.

| Time Slot | Module | Duration | Type | Highlights & Key Takeaways |
| :---: | :--- | :---: | :---: | :--- |
| **09:00 - 09:40** | [Module 01: Introduction to AI Agents & Google ADK](./training/module01-intro-to-ai-agents/) | 40 min | Theory | Agent reasoning loops, ADK 2.0 architecture, and component models. |
| **09:40 - 10:20** | [Module 02: Environment Setup & Tooling](./training/module02-environment-setup/) | 40 min | Lab | Python 3.10+ setup, `uv`, `google-adk`, `agents-cli`, and `.env` credentials. |
| **10:20 - 10:35** | *Morning Break* | 15 min | — | — |
| **10:35 - 11:10** | [Module 03: Your First Agent: Echo Agent](./training/module03-first-agent-echo/) | 35 min | Lab | Minimal agent definition, constructor syntax, and running with `gemini-3.8-flash`. |
| **11:10 - 11:50** | [Module 04: Core Agent Concepts: `LlmAgent` Deep Dive](./training/module04-agent-deep-dive/) | 40 min | Theory/Lab | System instructions, output contracts, temperature, and few-shot formatting. |
| **11:50 - 12:30** | [Module 05: Running & Interacting with Agents](./training/module05-running-agents/) | 40 min | Lab | Interactive web UI (`adk web` from parent directory) and CLI runner. |
| **12:30 - 13:30** | *Lunch Break* | 60 min | — | — |
| **13:30 - 14:10** | [Module 06: Running an Agent Programmatically](./training/module06-programmatic-execution/) | 40 min | Lab | Integrating agents into Python backends using `InMemoryRunner` and sessions. |
| **14:10 - 15:10** | [Module 08 & 09: Introduction to Tools & Custom Function Tools](./training/module09-intro-custom-function-tools/) | 60 min | Lab | Type-annotated tool definitions, parameter schemas, error handling, and return formats. |
| **15:10 - 15:25** | *Afternoon Break* | 15 min | — | — |
| **15:25 - 16:05** | [Module 10: Stateful Tools & ToolContext](./training/module10-advanced-function-tools/) | 40 min | Lab | Accessing session context, user auth info, and mutating state inside tools. |
| **16:05 - 16:50** | [Module 22: State, Memory & Session Management](./training/module22-state-and-memory/) | 45 min | Lab | Session lifecycles, memory rewind, state persistence, and cross-turn recall. |
| **16:50 - 17:00** | Day 1 Wrap-up & Q&A | 10 min | Review | Synthesis of Day 1 and preview of Multi-Agent Systems. |

*Day 1 Instructional Time: 340 min (5.67 hrs) + breaks.*

---

## 📅 Day 2: Multi-Agent Systems, Evaluation & Production Deployment

**Focus:** Orchestration patterns, standardized protocols (MCP), evaluation, and cloud deployment.

| Time Slot | Module | Duration | Type | Highlights & Key Takeaways |
| :---: | :--- | :---: | :---: | :--- |
| **09:00 - 09:35** | [Module 12: Built-in Tools and Grounding](./training/module12-built-in-tools-grounding/) | 35 min | Lab | Google Search grounding and enterprise knowledge retrieval. |
| **09:35 - 10:20** | [Module 27: Introduction to MCP & Stateful Tools](./training/module27-intro-to-mcp/) | 45 min | Theory/Lab | Connecting ADK agents to external Model Context Protocol (`McpToolset`) servers. |
| **10:20 - 10:35** | *Morning Break* | 15 min | — | — |
| **10:35 - 11:05** | [Module 15: Introduction to Multi-Agent Systems (MAS)](./training/module15-intro-to-multi-agent-systems/) | 30 min | Theory | When to use MAS, coordinator vs peer topologies, and handoff protocols. |
| **11:05 - 12:00** | [Module 16: Static Orchestration (Linear & Parallel)](./training/module16-static-orchestration/) | 55 min | Lab | Building deterministic multi-agent pipelines with sequential and parallel steps. |
| **12:00 - 12:40** | [Module 17: Structured Routing & Agent Teams](./training/module17-structured-routing/) | 40 min | Lab | Intent-based routing, specialist sub-agents, and dynamic delegation. |
| **12:40 - 13:40** | *Lunch Break* | 60 min | — | — |
| **13:40 - 14:40** | [Module 24: Evaluating Agent Performance](./training/module24-evaluation/) | 60 min | Lab | Evaluating agents using `agents-cli eval` / `adk eval`, LLM-as-judge, and evalsets. |
| **14:40 - 15:30** | [Module 25: Observability & Tracing](./training/module25-observability/) | 50 min | Lab | Cloud Trace, OpenTelemetry plugins, turn logging, and debugging production traffic. |
| **15:30 - 15:45** | *Afternoon Break* | 15 min | — | — |
| **15:45 - 16:35** | [Module 35: Deployment to Agent Runtime & Cloud Run](./training/module35-deployment-agent-runtime/) | 50 min | Lab | Containerization, deployment via `agents-cli deploy`, and Gemini Enterprise publishing. |
| **16:35 - 17:00** | [Module 38: Production Best Practices & Graduation](./training/module38-best-practices/) | 25 min | Review | Security guardrails, rate limiting, enterprise patterns, and final Q&A. |

*Day 2 Instructional Time: 340 min (5.67 hrs) + breaks.*

---

## 🛠️ Assessment & Certification
* **In-Doc Socratic Checks:** Students complete embedded multiple-choice and conceptual verification checks after each module.
* **Challenge Labs:** Students implement working code skeletons against deterministic test requirements.
* **Zero-Trust Verification:** Course authors and instructors validate module reproducibility using the continuous `adk-student-evaluator` harness.
