# 🧑‍💻 Self-Paced Learning Timetable

**Total Estimated Duration:** ~29.5 Hours (1,770 active learning minutes)  
**Standard Curriculum Agent Model:** `gemini-3.8-flash`  
**Standard Developer CLI:** `agents-cli` & `google-adk`

This self-paced track is optimized for individual software developers, AI practitioners, and cloud architects working autonomously through the 45-module Google ADK 2.0 curriculum. Each module features clear conceptual theory, active coding challenge labs with solution vaults, interactive Socratic Knowledge checks, and unit tests.

---

## 📊 Module Breakdown & Self-Study Estimates

### 🌱 Part 1: Foundations (~4.5 Hours / 275 min)
| Module | Complexity | Estimated Time | Focus |
| :--- | :---: | :---: | :--- |
| 📖 [Module 01: Introduction to AI Agents & Google ADK](./training/module01-intro-to-ai-agents/) | Low | 35 min | Agent loop fundamentals & ADK 2.0 concepts |
| 📖 [Module 02: Setting Up Your Environment (ADK 2.0)](./training/module02-environment-setup/) | Medium | 40 min | `uv`, `google-adk`, `agents-cli`, environment variables |
| 📖 [Module 03: Your First Agent: Echo Agent](./training/module03-first-agent-echo/) | Low | 35 min | Agent constructor & minimal run loop |
| 📖 [Module 04: Core Agent Concepts & Deep Dive](./training/module04-agent-deep-dive/) | Low | 30 min | System instructions & behavior control |
| 📖 [Module 04.5: Model Configuration & LiteLLM](./training/module04_5-multi-model-litellm/) | Medium | 30 min | Multi-model routing and provider fallbacks |
| 📖 [Module 05: Running & Interacting with Agents](./training/module05-running-agents/) | Medium | 30 min | Interactive web UI (`adk web`) & CLI REPL |
| 📖 [Module 06: Programmatic Execution: Apps & Runners](./training/module06-programmatic-execution/) | Medium | 35 min | Python integration with `InMemoryRunner` |
| 📖 [Module 07: Multimodal & Image Processing 📸](./training/module07-multimodal-and-images/) | High | 40 min | Multimodal vision tasks with `gemini-3.8-flash` |

---

### 🛠️ Part 2: Tools & Capabilities (~4.7 Hours / 285 min)
| Module | Complexity | Estimated Time | Focus |
| :--- | :---: | :---: | :--- |
| 🛠️ [Module 08: Introduction to Tools](./training/module08-intro-to-tools/) | Medium | 35 min | Tool declaration & JSON schema mapping |
| 🛠️ [Module 09: Custom Function Tools](./training/module09-intro-custom-function-tools/) | High | 45 min | Python function tools, type hints, error handling |
| 🛠️ [Module 10: Stateful Tools & ToolContext](./training/module10-advanced-function-tools/) | High | 40 min | Accessing session context & mutating state |
| 🛠️ [Module 11: Enterprise Integration with OpenAPI](./training/module11-openapi-tools/) | High | 35 min | Generating tools from OpenAPI / Swagger specs |
| 🛠️ [Module 12: Built-in Tools & Grounding](./training/module12-built-in-tools-grounding/) | Medium | 30 min | Google Search grounding for fresh knowledge |
| 🛠️ [Module 13: Actions & Human-in-the-Loop (HITL)](./training/module13-tool-context/) | High | 40 min | Approval workflows & sensitive actions |
| 🛠️ [Module 13.5: Custom Persistence with Firestore](./training/module13_5-firestore-persistence/) | High | 30 min | NoSQL database session storage |
| 🛠️ [Module 14: Integrating Third-Party Tools](./training/module14-third-party-tools/) | Medium | 30 min | Ecosystem interoperability |

---

### 🤝 Part 3: Multi-Agent Systems (~4.5 Hours / 275 min)
| Module | Complexity | Estimated Time | Focus |
| :--- | :---: | :---: | :--- |
| 🤖 [Module 15: Introduction to MAS](./training/module15-intro-to-multi-agent-systems/) | Low | 15 min | Multi-agent architectures & trade-offs |
| 🤖 [Module 16: Static Orchestration (Linear & Parallel)](./training/module16-static-orchestration/) | Medium | 40 min | Deterministic multi-agent pipelines |
| 🤖 [Module 17: Structured Routing (Edges & Dicts)](./training/module17-structured-routing/) | Medium | 30 min | Routing classifiers & dynamic routing |
| 🤖 [Module 18: Dynamic Orchestration (@node)](./training/module18-dynamic-orchestration/) | High | 40 min | Graph-based dynamic orchestration |
| 🤖 [Module 19: Collaborative Teams (Modes & Handoffs)](./training/module19-collaborative-teams/) | High | 45 min | Collaborative multi-agent communication |
| 🤖 [Module 20: Cyclic Workflows (Self-Correction)](./training/module20-cyclic-workflows/) | High | 40 min | Iteration loops & critic agents |
| 🤖 [Module 21: Distributed Graphs (A2A & External)](./training/module21-distributed-graphs/) | High | 50 min | Agent-to-Agent (A2A) networking |
| 🏁 [Module 21.5: MAS Architecture Milestone](./training/module21_5-mas-knowledge-milestone/) | Low | 15 min | Multi-agent architecture synthesis |

---

### 🏭 Part 4: Production Readiness (~3.9 Hours / 235 min)
| Module | Complexity | Estimated Time | Focus |
| :--- | :---: | :---: | :--- |
| 🧠 [Module 22: State & Memory Management](./training/module22-state-and-memory/) | Medium | 35 min | Session stores, memory rewind, state lifecycle |
| 📦 [Module 23: Handling Files with Artifacts](./training/module23-artifacts/) | Medium | 40 min | Reading & generating files with agents |
| 🏭 [Module 24: Evaluating Agent Performance](./training/module24-evaluation/) | Medium-High | 50 min | `agents-cli eval`, trajectory scoring, LLM judge |
| 🏭 [Module 25: Observability & Tracing Plugins](./training/module25-observability/) | High | 35 min | Cloud Trace, OpenTelemetry & turn logging |
| 🦺 [Module 25.5: Responsible AI (RAI) & Safety Plugins](./training/module25_5-rai-safety-plugins/) | Medium | 35 min | Safety guardrails & content filters |
| 🛡️ [Module 26: Callbacks & Safety Guardrails](./training/module26-callbacks/) | High | 40 min | Pre/Post execution interceptors |

---

### 🔌 Part 5: Integrations & Custom UI (~2.7 Hours / 160 min)
| Module | Complexity | Estimated Time | Focus |
| :--- | :---: | :---: | :--- |
| 🔌 [Module 27: Introduction to MCP & Stateful Tools](./training/module27-intro-to-mcp/) | High | 40 min | Model Context Protocol architecture |
| 🔌 [Module 28: Building Custom MCP Tools](./module28-building-mcp-tools/) | High | 40 min | Creating FastMCP tool servers |
| 🔌 [Module 29: Introduction to UI Integration](./training/module29-ui-integration-intro/) | High | 35 min | Frontend chat integration |
| 🔌 [Module 30: Building Custom Streaming Clients](./training/module30-custom-streaming-client/) | High | 45 min | Real-time token streaming client |

---

### ☁️ Part 6: Deployment & Enterprise (~4.2 Hours / 255 min)
| Module | Complexity | Estimated Time | Focus |
| :--- | :---: | :---: | :--- |
| ☁️ [Module 31: Production Deployment Strategies](./training/module31-production-deployment-strategies/) | Low | 15 min | Deployment architecture choices |
| ☁️ [Module 32: Deployment to Cloud Run](./training/module32-deployment-cloud-run/) | High | 35 min | Containerization & Cloud Run service |
| ☁️ [Module 33: Deployment to GKE](./training/module33-deployment-gke/) | High | 60 min | GKE Autopilot & Kubernetes deployments |
| ☁️ [Module 34: Deploying MCP Server to Cloud Run](./training/module34-deploying-mcp-server-cloud-run/) | High | 70 min | Production remote MCP microservices |
| ☁️ [Module 35: Deploying to Agent Runtime](./training/module35-deployment-agent-runtime/) | High | 60 min | `agents-cli deploy` to Agent Runtime |
| ☁️ [Module 36: Gemini Enterprise Publishing](./training/module36-gemini-enterprise/) | Low | 15 min | Enterprise registry publishing |

---

### 🏆 Part 7: Capstones & Best Practices (~4.8 Hours / 290 min)
| Module | Complexity | Estimated Time | Focus |
| :--- | :---: | :---: | :--- |
| 🏆 [Module 37: Advanced Personalized Shopping Agent](./training/module37-advanced-personalized-shopping-agent/) | High | 85 min | Multi-Agent E-Commerce Capstone |
| 🏆 [Module 38: Production Best Practices & Patterns](./training/module38-best-practices/) | High | 35 min | Enterprise checklist & reliability |
| 🔌 [Module 39: ADK Plugins Deep Dive](./training/module39-plugins/) | High | 35 min | Plugin architecture & extension points |
| 🎓 [Module 39.5: Agent Skills](./training/module39_5-agent-skills/) | High | 35 min | Composable Agent Skills development |
| 🎯 [Module 40: Aegis Incident Response Capstone](./training/module40-advanced-capstone-aegis-incident-response/) | High | 100 min | SRE Incident Management MAS Capstone |

---

## 💡 Recommended Self-Study Strategy
1. **Interactive Self-Assessment:** Complete the 3 Socratic Questions at the end of each module's Theory section before attempting the challenge lab.
2. **Hands-On Coding:** Write your solutions in the `lab.md` files; use the `<SolutionVault>` unlock only after attempting the challenge.
3. **Run Local Tests:** Validate your agent implementations locally using `pytest` and interactive debugging with `adk web` (launched from parent directory).
