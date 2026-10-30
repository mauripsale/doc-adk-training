# Tasks: Google Agents CLI Modernization & Integration

- [x] Task 1: Module 02 & 05 Tooling Updates
  - Acceptance: `module02` includes `uvx google-agents-cli setup` and coding agent skills; `module05` includes `agents-cli playground` and command taxonomy.
  - Verify: Documentation renders clearly; instructions are step-by-step with zero ambiguity.
  - Files: `training/module02-environment-setup/README.md`, `training/module05-running-agents/README.md`, `training/module05-running-agents/lab.md`

- [x] Task 2: Module 24 Evaluation Flywheel Modernization
  - Acceptance: `module24` covers the Quality Flywheel with `agents-cli eval run` and eval dataset schemas alongside `adk eval`.
  - Verify: Socratic quiz and lab instructions explain trajectory metrics and LLM-as-a-judge scoring.
  - Files: `training/module24-evaluation/README.md`, `training/module24-evaluation/lab.md`

- [x] Task 3: Modules 32, 33, 35 Multi-Target Cloud Deployment
  - Acceptance: Modules 32 (Cloud Run), 33 (GKE), and 35 (Agent Runtime) show how `agents-cli scaffold enhance` generates target-specific Terraform and Cloud Build pipelines.
  - Verify: Clear distinction between manual Dockerfiles and automated CLI scaffolding.
  - Files: `training/module32-deployment-cloud-run/README.md`, `training/module33-deployment-gke/README.md`, `training/module35-deployment-agent-runtime/README.md`, `training/module35-deployment-agent-runtime/lab.md`

- [x] Task 4: Module 36 Gemini Enterprise Publishing
  - Acceptance: `module36` introduces `uvx google-agents-cli publish gemini` for registering ADK agents into the Gemini Enterprise agent catalog.
  - Verify: CLI flags, service account permissions, and ADK vs A2A modes documented.
  - Files: `training/module36-gemini-enterprise/README.md`

- [x] Task 5: Socratic Quizzes, Solution Vault Registry & Grader Sync
  - Acceptance: Regenerate vault registry with `agents-cli` questions and hints.
  - Verify: `python3 scripts/generate_vault_registry.py` runs without errors and updates `doc/src/data/vaultRegistry.js`.
  - Files: `scripts/generate_vault_registry.py`, `doc/src/data/vaultRegistry.js`

- [x] Task 6: Adversarial Debate, Grader Verification & Docusaurus Build
  - Acceptance: Run test suite, student grader, Docusaurus build, and adversarial debate subagents.
  - Verify: `python3 scripts/test_solutions.py` passes 100%, `npm run build` succeeds cleanly.
  - Files: All touched modules, Docusaurus build artifacts.
