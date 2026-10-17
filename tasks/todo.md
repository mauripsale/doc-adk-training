# Task List: Global SolutionVault Rollout

- [x] Task 1: Component Hardening & Security Fixes
  - Acceptance: `SolutionVault/index.js` computes deterministic tokens based on `moduleNumber`, eliminates the length bypass, supports instructor fast-track, and handles defensive edge cases.
  - Verify: Test terminal hash command and token validation in isolation.
  - Files: `doc/src/components/SolutionVault/index.js`, `doc/src/components/SolutionVault/styles.module.css`

- [x] Task 2: Docusaurus Global MDX & Route Exclusion Configuration
  - Acceptance: `SolutionVault` is registered in `src/theme/MDXComponents.js` and `lab-solution.md` is excluded from static page generation in `docusaurus.config.js`.
  - Verify: `npm run build` succeeds and `doc/build/sitemap.xml` contains 0 `lab-solution` entries.
  - Files: `doc/docusaurus.config.js`, `doc/src/theme/MDXComponents.js`

- [x] Task 3: Centralized English Questions Registry
  - Acceptance: `doc/src/data/vaultRegistry.js` contains 3 curated, rigorous English questions + options + hints for all 45 modules.
  - Verify: Automated schema validation script confirms all 45 modules have valid entries.
  - Files: `doc/src/data/vaultRegistry.js`, `scripts/validate_vaults.py`

- [x] Task 4: Rollout Wave 1 (Modules 01-12)
  - Acceptance: Modules 01 to 12 have legacy hidden solution replaced by `<SolutionVault moduleNumber="XX">` wrapping the reference solution.
  - Verify: `npm run build` compiles with zero MDX errors.
  - Files: `training/module01*` to `training/module12*` `lab.md`

- [x] Task 5: Rollout Wave 2 (Modules 13-26)
  - Acceptance: Modules 13 to 26 have legacy hidden solution replaced by `<SolutionVault moduleNumber="XX">`.
  - Verify: `npm run build` compiles with zero MDX errors.
  - Files: `training/module13*` to `training/module26*` `lab.md`

- [x] Task 6: Rollout Wave 3 (Modules 27-40)
  - Acceptance: Modules 27 to 40 have legacy hidden solution replaced by `<SolutionVault moduleNumber="XX">`.
  - Verify: `npm run build` compiles with zero MDX errors.
  - Files: `training/module27*` to `training/module40*` `lab.md`

- [x] Task 7: Full Static Build & Zero Trust Validation
  - Acceptance: Entire site builds cleanly (`npm run build`), no console errors, no URL leaks.
  - Verify: `npm run build` in `doc/` completes with exit code 0.
