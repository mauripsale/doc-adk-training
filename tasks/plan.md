# Implementation Plan: Global SolutionVault Rollout (45 Modules)

## Overview
Roll out the interactive, gamified, and hardened `<SolutionVault>` across all 45 training modules in Google ADK documentation.

---

## Architecture & Technical Tasks Breakdown

### Phase 1: Core Component Hardening & Global Registration
1. **Dynamic Hashing & Security Fixes (`doc/src/components/SolutionVault/index.js`)**:
   - Compute the expected SHA256 token deterministically from `moduleNumber` using a fast client-side JS implementation (Web Crypto API or deterministic SHA256 helper) so each module automatically gets a unique token.
   - Remove the `clean.length >= 6` bypass.
   - Add instructor bypass mechanism (`?instructor=1` query param / `Ctrl+Alt+U`).
   - Fix dynamic counter text: `"All " + questions.length + " comprehension checks passed!"`.
   - Prevent crash if `questions` array is empty or undefined.
2. **Global MDX Registration (`doc/src/theme/MDXComponents.js`)**:
   - Register `SolutionVault` globally in Docusaurus so `<SolutionVault>` can be used directly in any `.md` or `.mdx` file without manual imports.
3. **Docusaurus Config Route Exclusion (`doc/docusaurus.config.js`)**:
   - Add `exclude: ['**/lab-solution.md', '**/lab-solution/**']` to the docs plugin configuration to guarantee zero standalone HTML pages or sitemap entries for `/lab-solution`.

### Phase 2: Central Questions Registry (`doc/src/data/vaultRegistry.js`)
- Construct high-quality, pedagogically curated questions in English for all 45 modules:
  - 3 multiple-choice conceptual & implementation questions per module.
  - 4 distinct options per question.
  - 1 correct index.
  - Clear, educational hint for wrong answers.

### Phase 3: Wave-based Rollout to `training/moduleXX/lab.md`
- **Wave 1 (Modules 01-12):** Fundamentals, Environment, Echo Agent, LiteLLM, Running Agents, Execution, Multimodal, Tools, Custom Functions, OpenAPI, Grounding.
- **Wave 2 (Modules 13-26):** Tool Context, Firestore Persistence, Third-party Tools, MAS Intro, Static Orchestration, Routing, Dynamic, Collaborative Teams, Cyclic Workflows, Distributed Graphs, Knowledge Milestone, State & Memory, Artifacts, Evaluation, Observability, RAI Safety Plugins, Callbacks.
- **Wave 3 (Modules 27-40):** MCP Intro, Building MCP Tools, UI Integration, Streaming Client, Production Deployment, Cloud Run, GKE, MCP Cloud Run, Agent Runtime, Gemini Enterprise, Personalized Shopping Agent, Best Practices, Plugins, Agent Skills, Capstone Incident Response.

### Phase 4: Quality Assurance & Build Verification
1. Run static validation script across all 45 modules.
2. Run `npm run build` in `doc/` to verify 100% clean compilation.
3. Verify that `/docs/module01-intro-to-ai-agents/lab` and other lab routes render cleanly without hydration mismatches.
4. Verify `scripts/publish_to_students.sh` dry-run compatibility.
