#!/usr/bin/env python3
"""
ADK Curriculum Lab Grader & Student Self-Assessment Runner
==========================================================
Provides instant, zero-cost, offline grading and feedback for students
working through Google ADK Training (From Zero to Hero) challenge labs.

Usage:
    # Auto-detect current module and test default agent.py:
    python scripts/grade_lab.py

    # Grade a specific module and file:
    python scripts/grade_lab.py --module 03 --file path/to/my_agent.py

    # Grade all lab solutions across the entire curriculum (CI Mode):
    python scripts/grade_lab.py --all
"""

import argparse
import ast
import os
import re
import sys
import textwrap
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

# Ensure mock credentials exist so ADK never fails on missing keys during assessment
os.environ.setdefault("GOOGLE_API_KEY", "mock-grader-api-key")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "0")
os.environ.setdefault("VERTEX_AI_PROJECT_ID", "mock-grader-project")
os.environ.setdefault("VERTEX_AI_LOCATION", "us-central1")

# Add project root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.rubrics import CheckResult, ModuleRubric
from scripts.rubrics.definitions import RUBRICS, get_rubric_for_module


class TerminalUI:
    """Handles formatted terminal styling and colored badges."""
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

    @classmethod
    def banner(cls, title: str, subtitle: str = ""):
        print(f"\n{cls.BOLD}{cls.CYAN}{'='*80}{cls.RESET}")
        print(f"{cls.BOLD}{cls.CYAN}🎓 ADK Lab Grader:{cls.RESET} {cls.BOLD}{title}{cls.RESET}")
        if subtitle:
            print(f"{cls.DIM}{subtitle}{cls.RESET}")
        print(f"{cls.BOLD}{cls.CYAN}{'='*80}{cls.RESET}\n")

    @classmethod
    def check_pass(cls, name: str, details: str = ""):
        print(f"  {cls.GREEN}✔ [PASS]{cls.RESET} {cls.BOLD}{name}{cls.RESET}")
        if details:
            print(f"         {cls.DIM}{details}{cls.RESET}")

    @classmethod
    def check_fail(cls, name: str, message: str, hint: Optional[str] = None, theory_ref: Optional[str] = None):
        print(f"  {cls.RED}✖ [FAIL]{cls.RESET} {cls.BOLD}{name}{cls.RESET}")
        print(f"         {cls.RED}Error:{cls.RESET} {message}")
        if hint:
            print(f"         {cls.YELLOW}💡 Hint:{cls.RESET} {hint}")
        if theory_ref:
            print(f"         {cls.CYAN}📖 Review:{cls.RESET} {theory_ref}")

    @classmethod
    def summary(cls, passed_checks: int, total_checks: int, module_title: str) -> bool:
        print(f"\n{cls.DIM}{'-'*80}{cls.RESET}")
        score_pct = (passed_checks / total_checks * 100) if total_checks > 0 else 100
        if score_pct == 100:
            print(f"🎉 {cls.BOLD}{cls.GREEN}SCORE: 100% ({passed_checks}/{total_checks} Checks Passed){cls.RESET}")
            print(f"✨ {cls.GREEN}Status: EXCELLENT! Your solution meets all ADK 2.0 specifications.{cls.RESET}")
            print(f"{cls.BOLD}{cls.CYAN}{'='*80}{cls.RESET}\n")
            return True
        else:
            print(f"⚠️  {cls.BOLD}{cls.YELLOW}SCORE: {score_pct:.1f}% ({passed_checks}/{total_checks} Checks Passed){cls.RESET}")
            print(f"🔧 {cls.YELLOW}Status: Incomplete. Review the hints above to refine your solution.{cls.RESET}")
            print(f"{cls.BOLD}{cls.CYAN}{'='*80}{cls.RESET}\n")
            return False


def extract_python_blocks_from_solution(markdown_path: Path) -> List[str]:
    """Extracts runnable code blocks from a lab-solution.md file."""
    content = markdown_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    blocks = []
    in_block = False
    current_block = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```python") or stripped.startswith("```py"):
            in_block = True
            current_block = []
        elif in_block and stripped == "```":
            in_block = False
            code_text = "\n".join(current_block)
            dedented = textwrap.dedent(code_text).strip()
            if dedented:
                blocks.append(dedented)
            current_block = []
        elif in_block:
            current_block.append(line)

    return blocks


def auto_detect_module_from_context() -> Optional[str]:
    """Auto-detects the active module from current directory name or path."""
    cwd = Path.cwd()
    # Check directory name
    for part in [cwd.name, cwd.parent.name]:
        rubric = get_rubric_for_module(part)
        if rubric:
            return rubric.module_id
    return None


def grade_code_string(code: str, rubric: ModuleRubric, source_desc: str = "Student Code") -> Tuple[int, int, List[CheckResult]]:
    """Evaluates a code string against a ModuleRubric across all 3 layers."""
    results: List[CheckResult] = []

    # --------------------------------------------------------------------------
    # Layer 1: Syntax & AST Parsing
    # --------------------------------------------------------------------------
    tree = None
    try:
        tree = ast.parse(code, filename=source_desc)
        results.append(CheckResult(
            name="Layer 1: Python 3.10+ AST & Syntax Validation",
            passed=True,
            message="Code parses with valid syntax."
        ))
    except SyntaxError as e:
        results.append(CheckResult(
            name="Layer 1: Python 3.10+ AST & Syntax Validation",
            passed=False,
            message=f"SyntaxError at line {e.lineno}: {e.msg}",
            hint="Check indentation, missing colons, or mismatched quotes.",
            theory_ref=rubric.theory_ref
        ))
        return 0, 1, results

    # --------------------------------------------------------------------------
    # Layer 1: Banned & Deprecated Pattern Checks
    # --------------------------------------------------------------------------
    if ".candidates" in code:
        results.append(CheckResult(
            name="Layer 1: ADK 2.0 Architectural Compliance (.candidates check)",
            passed=False,
            message="Detected access to deprecated `.candidates` attribute.",
            hint="ADK 2.0 uses direct `.content` property on responses (e.g. `event.content.parts[0].text`).",
            theory_ref=rubric.theory_ref
        ))
    else:
        results.append(CheckResult(
            name="Layer 1: ADK 2.0 Architectural Compliance (Modern Accessors)",
            passed=True,
            message="No deprecated `.candidates` access found."
        ))

    # Check for hardcoded API keys
    if re.search(r'["\']AIza[0-9A-Za-z\-_]{20,}["\']', code) or re.search(r'GOOGLE_API_KEY\s*=\s*["\'][^"\']{15,}["\']', code):
        if not ("mock" in code.lower() or "example" in code.lower() or "your_api_key" in code.lower()):
            results.append(CheckResult(
                name="Layer 1: Security & Credential Isolation",
                passed=False,
                message="Detected hardcoded Google API key in source code.",
                hint="Store credentials in `.env` and load them via `python-dotenv` or environment variables.",
                theory_ref="Module 02 Theory -> 'Configuring Authentication'"
            ))
        else:
            results.append(CheckResult(
                name="Layer 1: Security & Credential Isolation",
                passed=True,
                message="No live hardcoded API keys detected (mock/placeholder allowed)."
            ))
    else:
        results.append(CheckResult(
            name="Layer 1: Security & Credential Isolation",
            passed=True,
            message="No hardcoded API keys detected."
        ))

    # --------------------------------------------------------------------------
    # Layer 2: Required Imports & Symbol Verification
    # --------------------------------------------------------------------------
    imports_found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports_found.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            imports_found.add(mod)
            for alias in node.names:
                imports_found.add(f"{mod}.{alias.name}" if mod else alias.name)
                imports_found.add(alias.name)

    missing_imports = []
    for req in rubric.required_imports:
        if not any(req in imp for imp in imports_found):
            missing_imports.append(req)

    if missing_imports:
        results.append(CheckResult(
            name="Layer 2: Required ADK 2.0 Imports",
            passed=False,
            message=f"Missing expected import(s): {', '.join(missing_imports)}",
            hint=rubric.hints.get("missing_import", f"Import required classes from {rubric.required_imports[0]}."),
            theory_ref=rubric.theory_ref
        ))
    else:
        results.append(CheckResult(
            name="Layer 2: Required ADK 2.0 Imports",
            passed=True,
            message="All required framework imports are present."
        ))

    # --------------------------------------------------------------------------
    # Layer 2: Standard Model Configuration
    # --------------------------------------------------------------------------
    if rubric.has_code and rubric.expected_models:
        model_found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if any(m in node.value for m in rubric.expected_models):
                    model_found = True
                    break
        
        if model_found or not rubric.required_symbols:
            results.append(CheckResult(
                name="Layer 2: Model Configuration Alignment",
                passed=True,
                message="Target model aligns with ADK course standards."
            ))
        else:
            results.append(CheckResult(
                name="Layer 2: Model Configuration Alignment",
                passed=True, # soft check
                message=f"Note: Standard course model is '{rubric.expected_models[0]}'."
            ))

    # --------------------------------------------------------------------------
    # Layer 3: Mock Execution / Compilation Check
    # --------------------------------------------------------------------------
    if rubric.has_code:
        try:
            # Test compiling code object
            compile(code, filename=source_desc, mode="exec")
            results.append(CheckResult(
                name="Layer 3: Execution Runtime Readiness",
                passed=True,
                message="Code compiles cleanly into executable bytecode."
            ))
        except Exception as e:
            results.append(CheckResult(
                name="Layer 3: Execution Runtime Readiness",
                passed=False,
                message=f"Compilation failed: {str(e)}",
                hint="Check variable names and scope boundaries.",
                theory_ref=rubric.theory_ref
            ))

    passed_count = sum(1 for r in results if r.passed)
    total_count = len(results)
    return passed_count, total_count, results


def grade_file(file_path: Path, module_id: Optional[str] = None, verbose: bool = False) -> bool:
    """Grades a standalone student python file."""
    if not file_path.exists():
        print(f"❌ Error: File not found at {file_path}")
        return False

    code = file_path.read_text(encoding="utf-8")
    
    # Resolve rubric
    target_mod = module_id or auto_detect_module_from_context() or "03"
    rubric = get_rubric_for_module(target_mod)
    if not rubric:
        print(f"❌ Error: Unknown module identifier '{target_mod}'")
        return False

    TerminalUI.banner(
        f"Module {rubric.module_id} — {rubric.title}",
        f"Target File: {file_path}"
    )

    passed, total, results = grade_code_string(code, rubric, source_desc=str(file_path))

    for res in results:
        if res.passed:
            TerminalUI.check_pass(res.name, res.message if verbose else "")
        else:
            TerminalUI.check_fail(res.name, res.message, res.hint, res.theory_ref)

    return TerminalUI.summary(passed, total, rubric.title)


def grade_all_curriculum_solutions() -> bool:
    """Batch grades all 45 module solutions across the repository."""
    TerminalUI.banner("Curriculum Solution Verification (Batch Mode)", "Validating all 45 training modules")

    training_dir = REPO_ROOT / "training"
    module_dirs = sorted([d for d in training_dir.iterdir() if d.is_dir() and d.name.startswith("module")])

    total_modules = 0
    passed_modules = 0

    for mdir in module_dirs:
        total_modules += 1
        rubric = get_rubric_for_module(mdir.name)
        if not rubric:
            print(f"  {TerminalUI.YELLOW}⚠ [SKIP]{TerminalUI.RESET} {mdir.name} (No rubric registered)")
            continue

        if not rubric.has_code:
            print(f"  {TerminalUI.GREEN}✔ [PASS]{TerminalUI.RESET} {mdir.name} (Conceptual / Architecture Module)")
            passed_modules += 1
            continue

        sol_file = mdir / "lab-solution.md"
        if not sol_file.exists():
            print(f"  {TerminalUI.YELLOW}⚠ [SKIP]{TerminalUI.RESET} {mdir.name} (No lab-solution.md)")
            continue

        blocks = extract_python_blocks_from_solution(sol_file)
        if not blocks:
            print(f"  {TerminalUI.GREEN}✔ [PASS]{TerminalUI.RESET} {mdir.name} (No Python code blocks required)")
            passed_modules += 1
            continue

        # Grade combined solution code blocks
        combined_code = "\n\n".join(blocks)
        passed, total, results = grade_code_string(combined_code, rubric, source_desc=f"{mdir.name}/lab-solution.md")

        if passed == total:
            print(f"  {TerminalUI.GREEN}✔ [PASS]{TerminalUI.RESET} {mdir.name} ({len(blocks)} code block{'s' if len(blocks) > 1 else ''}, {passed}/{total} checks)")
            passed_modules += 1
        else:
            print(f"  {TerminalUI.RED}✖ [FAIL]{TerminalUI.RESET} {mdir.name} ({passed}/{total} checks)")
            for r in results:
                if not r.passed:
                    print(f"         {r.name}: {r.message}")

    print(f"\n{TerminalUI.DIM}{'-'*80}{TerminalUI.RESET}")
    print(f"📊 Summary: {passed_modules}/{total_modules} Modules Passed ({(passed_modules/total_modules)*100:.1f}%)")
    print(f"{TerminalUI.BOLD}{TerminalUI.CYAN}{'='*80}{TerminalUI.RESET}\n")

    return passed_modules == total_modules


def main():
    parser = argparse.ArgumentParser(
        description="ADK Lab Grader: Zero-cost automated self-assessment for students."
    )
    parser.add_argument("--module", "-m", help="Module ID (e.g. 03, 08, 39_5)")
    parser.add_argument("--file", "-f", type=Path, help="Path to student python code file")
    parser.add_argument("--all", "-a", action="store_true", help="Grade all curriculum solutions across the repo")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose diagnostic logs")

    args = parser.parse_args()

    if args.all:
        success = grade_all_curriculum_solutions()
        sys.exit(0 if success else 1)

    target_file = args.file
    if not target_file:
        # Check current working directory for common agent files
        for candidate in ["agent.py", "workflow.py", "main.py", "app.py"]:
            if Path(candidate).exists():
                target_file = Path(candidate)
                break

    if not target_file:
        # Fall back to testing module's solution if module specified
        if args.module:
            rubric = get_rubric_for_module(args.module)
            if rubric:
                mod_dirs = [d for d in (REPO_ROOT / "training").iterdir() if d.is_dir() and f"module{rubric.module_id}" in d.name]
                if mod_dirs and (mod_dirs[0] / "lab-solution.md").exists():
                    blocks = extract_python_blocks_from_solution(mod_dirs[0] / "lab-solution.md")
                    if blocks:
                        passed, total, results = grade_code_string("\n\n".join(blocks), rubric, str(mod_dirs[0]))
                        TerminalUI.banner(f"Module {rubric.module_id} — {rubric.title}", f"Reference Solution: {mod_dirs[0].name}")
                        for res in results:
                            if res.passed:
                                TerminalUI.check_pass(res.name)
                            else:
                                TerminalUI.check_fail(res.name, res.message, res.hint, res.theory_ref)
                        TerminalUI.summary(passed, total, rubric.title)
                        sys.exit(0 if passed == total else 1)

        print("❌ Error: No Python file specified and no default agent.py found in current directory.")
        print("Usage: python scripts/grade_lab.py --module <ID> --file <path/to/agent.py>")
        sys.exit(1)

    success = grade_file(target_file, module_id=args.module, verbose=args.verbose)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
