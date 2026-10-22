# SPEC: CI/CD Automated Solution Code Testing

## 1. Objective & Scope
The objective is to establish an automated quality assurance pipeline for all 41 curriculum modules in `doc-adk-training`. 

Every time code or documentation changes are pushed to `solution` (or submitted via PR), GitHub Actions will automatically extract, parse, and verify all Python code snippets located within `training/**/lab-solution.md`.

---

## 2. Technical Architecture & Test Strategy

### 2.1 Multi-Layer Verification Pipeline (`scripts/test_solutions.py`)

The test runner will execute a 3-layer validation pipeline for every code block found in `lab-solution.md`:

```
┌────────────────────────────────────────────────────────┐
│                   lab-solution.md                      │
└───────────────────────────┬────────────────────────────┘
                            │ (Regex / Markdown AST)
                            ▼
┌────────────────────────────────────────────────────────┐
│             Extracted Python Code Blocks               │
└───────────────────────────┬────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│    LAYER 1    │   │    LAYER 2    │   │    LAYER 3    │
│  AST & Syntax │   │ ADK Symbol    │   │ Safe Sandbox  │
│  Verification │   │ Import Audit  │   │ Instantiation │
│  (ast.parse)  │   │ (Dynamic Imp) │   │ (Mock Env)    │
└───────────────┘   └───────────────┘   └───────────────┘
```

1. **Layer 1: AST & Syntax Verification (`ast.parse`)**
   - Parses the Python code block into an Abstract Syntax Tree.
   - Detects syntax errors, mismatched brackets, malformed f-strings, or invalid indentation.
   - Fails immediately if any block is syntactically invalid.

2. **Layer 2: ADK 2.0 Symbol & Import Audit**
   - Statically identifies all `import` and `from ... import ...` statements targeting `google.adk`, `google.genai`, `pydantic`, etc.
   - Verifies that all referenced modules, classes, and helper functions exist in the installed `google-adk` package (flagging any deprecated or renamed symbols).

3. **Layer 3: Safe Sandbox Instantiation (Dry Run)**
   - Executes the code blocks in an isolated Python namespace with mocked environment variables (`GOOGLE_API_KEY="mock-ci-key"`, `PROJECT_ID="mock-project"`).
   - Verifies that agent definitions, toolsets, and workflow graphs instantiate without runtime initialization errors, preventing real network calls.

---

## 3. GitHub Actions Workflow (`.github/workflows/test-solutions.yml`)

- **Triggers:**
  - `push` on `solution`
  - `pull_request` on `solution`
- **Environment:**
  - `ubuntu-latest`
  - `python-version: "3.10"`
- **Steps:**
  1. Checkout repository
  2. Setup Python 3.10 + Cache pip
  3. Install dependencies (`google-adk`, `pydantic`, `pytest`, etc.)
  4. Run `python scripts/test_solutions.py`
  5. Print structured report table in job summary

---

## 4. CLI Developer Experience (DX)

Developers and instructors can run the test locally with a single command:
```bash
python scripts/test_solutions.py
# or targeting a specific module:
python scripts/test_solutions.py --module module10
```

**Sample Output:**
```text
================================================================================
ADK Curriculum Solution Code Quality Suite
================================================================================
[PASS] Module 01: Introduction to AI Agents (1 code block)
[PASS] Module 02: Setting Up Your Environment (1 code block)
...
[PASS] Module 10: Advanced Function Tools (2 code blocks)
...
[PASS] Module 39.5: Agent Skills (1 code block)
[PASS] Module 40: Aegis Incident Response Capstone (3 code blocks)
--------------------------------------------------------------------------------
Summary: 41/41 modules passed (100% success rate, 0 syntax/import errors).
================================================================================
```

---

## 5. Success Criteria & Boundaries

- [x] **Zero Regressions:** All 41 `lab-solution.md` files pass syntax and import audits.
- [x] **Zero Paid Cloud Dependencies:** Testing runs 100% offline using mock credentials.
- [x] **Fast Feedback:** CI suite completes in under 30 seconds.
- [x] **Maintainability:** New modules added to `training/` are automatically discovered without modifying workflow config.
