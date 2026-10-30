# 👨‍🏫 Instructor-Led Classroom (ILC) Comprehensive Timetable

**Total Estimated Instruction & Lab Time:** 45 Hours 30 Minutes (7 Modular Parts / 45 Modules)  
**Standard Curriculum Agent Model:** `gemini-3.8-flash`  
**Standard Developer CLI:** `agents-cli` & `google-adk`

This detailed timetable maps out the complete multi-day master track for enterprise corporate academies and comprehensive bootcamps. It covers all 45 modules from introductory setup to advanced distributed multi-agent systems and capstone project implementations.

---

## 📅 Part-by-Part Master Breakdown

### 🟢 Part 1: Foundations (Day 1) — 350 min
| Module | Estimated Complexity | Duration (min) | Focus |
| :--- | :---: | :---: | :--- |
| 📖 [Module 01: Introduction to AI Agents & Google ADK](./training/module01-intro-to-ai-agents/) | Low | 45 | Agent loop, ADK 2.0 principles & architecture |
| 📖 [Module 02: Setting Up Your Environment (ADK 2.0)](./training/module02-environment-setup/) | Medium | 45 | `uv`, `google-adk`, `agents-cli`, API keys |
| 📖 [Module 03: Your First Agent: Echo Agent](./training/module03-first-agent-echo/) | Low | 40 | Agent constructor, minimal execution |
| 📖 [Module 04: Core Agent Concepts & Deep Dive](./training/module04-agent-deep-dive/) | Low | 40 | System instructions, temperature, schemas |
| 📖 [Module 04.5: Model Configuration & LiteLLM](./training/module04_5-multi-model-litellm/) | Medium | 40 | Multi-model routing, fallback providers |
| 📖 [Module 05: Running & Interacting with Agents](./training/module05-running-agents/) | Medium | 45 | `adk web` UI and CLI REPL runner |
| 📖 [Module 06: Programmatic Execution: Apps & Runners](./training/module06-programmatic-execution/) | Medium | 45 | `InMemoryRunner`, Python backend integration |
| 📖 [Module 07: Multimodal & Image Processing 📸](./training/module07-multimodal-and-images/) | High | 50 | Vision understanding with `gemini-3.8-flash` |

---

### 🛠️ Part 2: Tools & Capabilities (Day 2) — 340 min
| Module | Estimated Complexity | Duration (min) | Focus |
| :--- | :---: | :---: | :--- |
| 🛠️ [Module 08: Introduction to Tools](./training/module08-intro-to-tools/) | Medium | 40 | Tool mechanics, parameter schemas |
| 🛠️ [Module 09: Custom Function Tools](./training/module09-intro-custom-function-tools/) | High | 55 | Type hints, docstring schemas, validation |
| 🛠️ [Module 10: Stateful Tools & ToolContext](./training/module10-advanced-function-tools/) | High | 50 | Session state mutation inside tools |
| 🛠️ [Module 11: Enterprise Integration with OpenAPI](./training/module11-openapi-tools/) | High | 45 | Auto-generating tools from OpenAPI/Swagger |
| 🛠️ [Module 12: Built-in Tools & Grounding](./training/module12-built-in-tools-grounding/) | Medium | 40 | Google Search grounding integration |
| 🛠️ [Module 13: Actions & Human-in-the-Loop (HITL)](./training/module13-tool-context/) | High | 55 | Approval gates, sensitive action confirmation |
| 🛠️ [Module 13.5: Custom Persistence with Firestore](./training/module13_5-firestore-persistence/) | High | 40 | External NoSQL persistence layer |
| 🛠️ [Module 14: Integrating Third-Party Tools](./training/module14-third-party-tools/) | Medium | 35 | LangChain/CrewAI/LlamaIndex bridge tools |

---

### 🤖🤖 Part 3: Multi-Agent Systems (Day 3) — 355 min
| Module | Estimated Complexity | Duration (min) | Focus |
| :--- | :---: | :---: | :--- |
| 🤖 [Module 15: Introduction to MAS](./training/module15-intro-to-multi-agent-systems/) | Low | 25 | MAS architectures, sub-agent topologies |
| 🤖 [Module 16: Static Orchestration (Linear & Parallel)](./training/module16-static-orchestration/) | Medium | 50 | Sequential and parallel deterministic flows |
| 🤖 [Module 17: Structured Routing (Edges & Dicts)](./training/module17-structured-routing/) | Medium | 45 | Router agents and conditional branching |
| 🤖 [Module 18: Dynamic Orchestration (@node)](./training/module18-dynamic-orchestration/) | High | 55 | Dynamic execution graph construction |
| 🤖 [Module 19: Collaborative Teams (Modes & Handoffs)](./training/module19-collaborative-teams/) | High | 60 | Autonomous agent collaboration & handoffs |
| 🤖 [Module 20: Cyclic Workflows (Self-Correction)](./training/module20-cyclic-workflows/) | High | 50 | Loops, validator agents, iterative refinement |
| 🤖 [Module 21: Distributed Graphs (A2A & External)](./training/module21-distributed-graphs/) | High | 50 | Agent-to-Agent (A2A) network protocol |
| 🏁 [Module 21.5: MAS Architecture Milestone](./training/module21_5-mas-knowledge-milestone/) | Low | 20 | Multi-agent design review milestone |

---

### 🏭 Part 4: Production Readiness & Enterprise Guardrails (Day 4) — 335 min
| Module | Estimated Complexity | Duration (min) | Focus |
| :--- | :---: | :---: | :--- |
| 🧠 [Module 22: State & Memory Management](./training/module22-state-and-memory/) | Medium | 45 | Sessions, memory stores, rewind capabilities |
| 📦 [Module 23: Handling Files with Artifacts](./training/module23-artifacts/) | Medium | 50 | Binary files, CSV/PDF input & outputs |
| 🏭 [Module 24: Evaluating Agent Performance](./training/module24-evaluation/) | Medium-High | 60 | `agents-cli eval`, LLM-as-judge, test evalsets |
| 🏭 [Module 25: Observability & Tracing Plugins](./training/module25-observability/) | High | 50 | Cloud Trace, OpenTelemetry, metrics |
| 🦺 [Module 25.5: Responsible AI (RAI) & Safety Plugins](./training/module25_5-rai-safety-plugins/) | Medium | 45 | Safety policies, toxicity filters, PII masking |
| 🛡️ [Module 26: Callbacks & Safety Guardrails](./training/module26-callbacks/) | High | 55 | Pre/Post-execution hooks and interceptors |

---

### 🔌 Part 5: Integrations & Custom UI (Day 5) — 240 min
| Module | Estimated Complexity | Duration (min) | Focus |
| :--- | :---: | :---: | :--- |
| 🔌 [Module 27: Introduction to MCP & Stateful Tools](./training/module27-intro-to-mcp/) | High | 55 | Model Context Protocol core architecture |
| 🔌 [Module 28: Building Custom MCP Tools](./training/module28-building-mcp-tools/) | High | 55 | Implementing FastMCP servers for ADK |
| 🔌 [Module 29: Introduction to UI Integration](./training/module29-ui-integration-intro/) | High | 50 | Connecting React/Next.js/Streamlit to ADK |
| 🔌 [Module 30: Building Custom Streaming Clients](./training/module30-custom-streaming-client/) | High | 50 | Server-Sent Events (SSE) & WebSocket streaming |

---

### ☁️ Part 6: Deployment & Gemini Enterprise (Day 6) — 320 min
| Module | Estimated Complexity | Duration (min) | Focus |
| :--- | :---: | :---: | :--- |
| ☁️ [Module 31: Production Deployment Strategies](./training/module31-production-deployment-strategies/) | Low | 25 | Cloud Run vs GKE vs Agent Runtime decision tree |
| ☁️ [Module 32: Deployment to Cloud Run](./training/module32-deployment-cloud-run/) | High | 50 | Docker containerization & Cloud Run deploy |
| ☁️ [Module 33: Deployment to GKE](./training/module33-deployment-gke/) | High | 75 | Kubernetes manifests, Autopilot, autoscaling |
| ☁️ [Module 34: Deploying MCP Server to Cloud Run](./training/module34-deploying-mcp-server-cloud-run/) | High | 70 | Remote authenticated MCP microservices |
| ☁️ [Module 35: Deploying to Agent Runtime](./training/module35-deployment-agent-runtime/) | High | 75 | `agents-cli deploy` to managed Agent Runtime |
| ☁️ [Module 36: Gemini Enterprise Publishing](./training/module36-gemini-enterprise/) | Low | 25 | `agents-cli publish gemini` & enterprise catalog |

---

### 🏆 Part 7: Capstones, Plugins & Best Practices (Day 7) — 390 min
| Module | Estimated Complexity | Duration (min) | Focus |
| :--- | :---: | :---: | :--- |
| 🏆 [Module 37: Advanced Personalized Shopping Agent](./training/module37-advanced-personalized-shopping-agent/) | High | 100 | E-Commerce MAS Capstone with search & carts |
| 🏆 [Module 38: Production Best Practices & Patterns](./training/module38-best-practices/) | High | 45 | Production checklist, resiliency, cost tuning |
| 🔌 [Module 39: ADK Plugins Deep Dive](./training/module39-plugins/) | High | 45 | Creating modular ADK plugin packages |
| 🎓 [Module 39.5: Agent Skills](./training/module39_5-agent-skills/) | High | 45 | Reusable composable skills architecture |
| 🎯 [Module 40: Aegis Incident Response Capstone](./training/module40-advanced-capstone-aegis-incident-response/) | High | 125 | Multi-agent SRE incident triaging & remediation |

---

## 🛠️ Hands-on Labs & Knowledge Verification
* **Student Experience:** Interactive Socratic Quizzes, hands-on active coding challenges with `TODO` skeletons, and automated local unit tests (`pytest`).
