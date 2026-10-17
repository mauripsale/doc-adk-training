# Spec: Global Rollout of SolutionVault Across All 45 Training Modules

## 1. Objective
Replace the legacy, vulnerable Base64 + 1px hidden link pattern (`🕵️ Hidden Solution 🕵️`) across all 45 training modules in `training/module01` through `training/module40` with the pedagogical, gamified, and secure **`<SolutionVault>`** component.

### Target Audience & Learning Goals:
- **Audience:** Developers taking the *Google ADK: From Zero to Hero* course.
- **Pedagogical Impact:** Replace impulsive copy-pasting with active retrieval practice:
  1. **Comprehension Gate:** 3 curated, sequential multiple-choice questions in English testing module concepts, with instant hints on error.
  2. **Terminal Verification Gate:** A unique SHA256 one-liner command executed in local CLI to prove environment readiness.
  3. **Mindfulness Cooldown:** 15-second intentional reflection timer displaying pedagogical tips every 3 seconds.
  4. **Inline Decrypted Solution:** The reference solution rendered in-place with zero guessable standalone `/lab-solution` URLs.

---

## 2. Tech Stack & Environment
- **Framework:** Docusaurus v3.9.2 (React 18, Webpack 5, MDX v3)
- **Language:** JavaScript (ES6+ / React JSX), CSS Modules, Markdown/MDX
- **Target Python Version for CLI Challenges:** Python 3.10+
- **Git Branches:**
  - `solution` (Instructor Source of Truth, containing `lab.md` + `lab-solution.md`)
  - `main` (Student Repository, stripped of `lab-solution.md` via `scripts/publish_to_students.sh`)

---

## 3. Commands
- **Dev Server:** `cd doc && npm run start -- --port 3000 --no-open`
- **Full Static Build & Verification:** `cd doc && npm run build`
- **Serve Production Build:** `cd doc && npm run serve`
- **Publish to Student Repository:** `./scripts/publish_to_students.sh`
- **Run Student Evaluator Validation:** `python3 -m google.adk.cli run .agent/skills/adk-student-evaluator --input_path training/moduleXX-.../lab.md`

---

## 4. Project Structure & Architecture

```
adk-docs/
├── doc/
│   ├── docusaurus.config.js               # Exclude **/lab-solution.md from static route generation
│   ├── sidebars.js                        # 2-level hierarchy navigation
│   ├── src/
│   │   ├── components/
│   │   │   └── SolutionVault/
│   │   │       ├── index.js               # Core React vault component (dynamic SHA256, 3-q quiz, 15s timer)
│   │   │       └── styles.module.css      # Responsive, accessible, dark/light theme CSS
│   │   ├── data/
│   │   │   └── vaultRegistry.js           # Central registry of 3 English questions & hints per module (01-40)
│   │   └── theme/
│   │       └── MDXComponents.js           # Global MDX registration of <SolutionVault />
└── training/
    ├── module01-intro-to-ai-agents/
    │   ├── lab.md                         # <SolutionVault moduleNumber="01"> ... </SolutionVault>
    │   └── lab-solution.md                # Instructor reference solution
    ├── ...
    └── module40-advanced-capstone-aegis-incident-response/
        ├── lab.md                         # <SolutionVault moduleNumber="40"> ... </SolutionVault>
        └── lab-solution.md                # Instructor reference solution
```

---

## 5. Security & Architectural Hardening (Adversarial Debate Mitigations)

1. **Strict Token Validation:**
   - Remove any length-based bypass (`clean.length >= 6`). Validate exact SHA256 match against deterministic per-module token:
     $$\text{Token}_{\text{mod}} = \text{SHA256}(\text{"adk-v3-mod"} + \text{modId} + \text{"-verified"})[:8]$$
2. **Zero URL Guessing:**
   - Add `exclude: ['**/lab-solution.md']` in `doc/docusaurus.config.js`. Standalone `/lab-solution` URLs return 404, with zero entries leaked in `sitemap.xml`.
3. **Instructor Fast-Track Bypass:**
   - Support `?instructor=1` query parameter or `Ctrl+Alt+U` shortcut to immediately unlock all vaults for live demo presenters and instructors without manual clicking.
4. **Hydration & Responsive CSS:**
   - SSR-safe rendering with `min-height` container to eliminate Cumulative Layout Shift (CLS).
   - Mobile-first responsive layout for terminal input row and buttons (`flex-direction: column` on `<640px`).

---

## 6. Code Style & Integration Standard

### Centralized Registry Pattern (`doc/src/data/vaultRegistry.js`)
```javascript
export const VAULT_REGISTRY = {
  '02': {
    questions: [
      {
        question: "Why is `uv` preferred over standard pip/venv in modern Python AI development?",
        options: [
          "It is written in Rust, resolves dependencies orders of magnitude faster, and manages lockfiles deterministically",
          "It eliminates the need for Python interpreters entirely",
          "It only runs in cloud environments without local execution",
          "It converts Python scripts into C++ binaries automatically"
        ],
        correctIndex: 0,
        hint: "Recall the Module 02 setup overview highlighting uv's performance and deterministic virtual environments."
      },
      // ... 2 more questions
    ]
  },
  // Modules 03..40
};
```

### Module `lab.md` Usage Pattern
```markdown
### 🔐 Reference Solution Vault

<SolutionVault moduleNumber="02">

#### 🎯 Official Lab 2 Reference Solution & Setup Verification

##### 1. Complete `.env` Configuration
...

##### 2. `verify_setup.py` Implementation
...

</SolutionVault>
```

---

## 7. Testing & Verification Strategy

1. **Schema & Integrity Validation:**
   - Automated script (`scripts/validate_vaults.py`) to verify that all 45 modules have:
     - Exactly 3 valid English questions.
     - Exactly 4 options per question.
     - Valid `correctIndex` in range `[0, 3]`.
     - Non-empty contextual `hint`.
     - Matching module ID in `VAULT_REGISTRY`.
2. **Static Site Build Verification:**
   - Run `npm run build` in `doc/` with `onBrokenLinks: 'throw'` to confirm zero MDX syntax errors across all 45 modules.
3. **Sitemap Leak Check:**
   - Verify `grep -i "lab-solution" doc/build/sitemap.xml` produces 0 matches.
4. **Student Evaluator Compatibility:**
   - Verify that running `.agent/skills/adk-student-evaluator` correctly reads the authoritative `lab-solution.md` files on branch `solution`.

---

## 8. Boundaries

- **Always Do:**
  - Write all questions, options, hints, and explanations strictly in **English**.
  - Maintain the authoritative `lab-solution.md` files on the `solution` branch.
  - Verify full `npm run build` before considering any wave complete.
- **Ask First:**
  - Changing existing core lab exercises, code skeletons, or conceptual objectives.
- **Never Do:**
  - Push un-sanitized solution markdown files directly to the `main` student branch.
  - Expose standalone `/lab-solution` public routes in Docusaurus.

---

## 9. Success Criteria
- [ ] All 45 training modules (`01` through `40`, including `.5` milestones) have `<SolutionVault moduleNumber="XX">` integrated.
- [ ] All questions, hints, and solution walkthroughs are in grammatically sound English.
- [ ] Docusaurus `npm run build` compiles 100% cleanly without errors or broken links.
- [ ] Direct browsing to `/docs/.../lab-solution` returns 404 Not Found.
- [ ] `scripts/publish_to_students.sh` successfully syncs cleanly to `main` without leaking `lab-solution.md`.

---

## 10. Open Questions for User
1. **Rollout Execution Strategy:** Would you like us to execute the rollout in 3 sequential waves (**Wave 1: Modules 01-12**, **Wave 2: Modules 13-26**, **Wave 3: Modules 27-40**), verifying each wave with `npm run build`?
