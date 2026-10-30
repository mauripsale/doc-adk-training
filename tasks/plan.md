# Plan: gemini-3.8-flash Curriculum Migration & Project Rule Update

## Context & Objectives
Migrate the Google ADK Training curriculum from `gemini-3.5-flash` to `gemini-3.8-flash` as the canonical default standard model across all 45 modules, while allowing `gemini-3.7-flash` and `gemini-3.6-flash` in grader rubrics.

---

## Phases & Tasks

### Phase 1: Project Rules & Environment Defaults
- Update `/Users/maurizio.ipsale/Code/adk-docs/GEMINI.md` to establish the new binding standard model mandate (`gemini-3.8-flash`).
- Update `.env.example` with `ADK_DEFAULT_MODEL="gemini-3.8-flash"`.

### Phase 2: Grader Rubrics & Evaluation Engine
- Update `scripts/rubrics/__init__.py` with default expected models: `["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-2.5-flash"]`.
- Update `scripts/rubrics/definitions.py` across all module rubrics to accept `gemini-3.8-flash`, `gemini-3.7-flash`, `gemini-3.6-flash`.

### Phase 3: Global Curriculum Code & Documentation Migration (45 Modules)
- Update all training modules (`training/module*/README.md`, `lab.md`, `lab-solution.md`).
- Update YAML configs (`support_agent/*.yaml`, etc.).
- Update sample agents (`sample-agents/personalized-shopping/`).
- Preserve Live API models in Module 30 (`gemini-live-2.5-flash-native-audio`).

### Phase 4: Socratic Quiz & Vault Registry Synchronization
- Update `scripts/generate_vault_registry.py` with `gemini-3.8-flash` in Module 04 and other comprehension checks.
- Run `python3 scripts/generate_vault_registry.py` to regenerate `doc/src/data/vaultRegistry.js`.

### Phase 5: Verification, Grader Testing & Docusaurus Build
- Run `python3 scripts/grade_lab.py --all` to verify 100% pass across all 45 modules.
- Run `npm --prefix doc run build` to verify clean compilation with zero broken links.
- Commit all changes to `feat/gemini-3.8-flash-migration`.
