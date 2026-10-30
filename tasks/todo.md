# Tasks: gemini-3.8-flash Curriculum Migration & Project Rule Update

- [x] Task 1: Project Rules & Environment Defaults
  - Acceptance: `GEMINI.md` mandates `gemini-3.8-flash` as project standard rule; `.env.example` has `ADK_DEFAULT_MODEL="gemini-3.8-flash"`.
  - Files: `GEMINI.md`, `.env.example`

- [x] Task 2: Grader Rubrics & Evaluation Engine
  - Acceptance: `scripts/rubrics/__init__.py` and `scripts/rubrics/definitions.py` updated to accept `gemini-3.8-flash`, `gemini-3.7-flash`, `gemini-3.6-flash`, and `gemini-3.5-flash`.
  - Files: `scripts/rubrics/__init__.py`, `scripts/rubrics/definitions.py`

- [x] Task 3: Global Curriculum Code & Documentation Migration (45 Modules)
  - Acceptance: Replace all `gemini-3.5-flash` with `gemini-3.8-flash` in training modules, YAML configs, and sample agents while preserving Live API model in M30.
  - Files: `training/module*/*.md`, `sample-agents/personalized-shopping/*.py`

- [x] Task 4: Socratic Quiz & Vault Registry Synchronization
  - Acceptance: Update `scripts/generate_vault_registry.py` and run it to regenerate `doc/src/data/vaultRegistry.js`.
  - Files: `scripts/generate_vault_registry.py`, `doc/src/data/vaultRegistry.js`

- [x] Task 5: Grader Verification & Docusaurus Build
  - Acceptance: Run `python3 scripts/grade_lab.py --all` (100% pass) and `npm --prefix doc run build` (clean build). Commit to `feat/gemini-3.8-flash-migration`.
  - Files: Full repository.
