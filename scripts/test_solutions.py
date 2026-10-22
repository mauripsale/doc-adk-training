#!/usr/bin/env python3
"""
ADK Curriculum Solution Code Quality Suite
Extracts and validates all Python code blocks across curriculum lab-solution.md files.
Performs:
  - Layer 1: AST / Syntax Analysis (Python 3.10+ compliance, dedented)
  - Layer 2: ADK 2.0 Import & Symbol Resolution
"""

import ast
import argparse
import importlib
import os
import re
import sys
import textwrap
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Ensure mock credentials exist in environment so ADK doesn't fail on missing keys
os.environ.setdefault("GOOGLE_API_KEY", "mock-ci-api-key-for-testing")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "0")
os.environ.setdefault("VERTEX_AI_PROJECT_ID", "mock-ci-project")
os.environ.setdefault("VERTEX_AI_LOCATION", "us-central1")


def extract_python_blocks(markdown_path: Path) -> List[Tuple[int, str]]:
    """
    Extracts all ```python ... ``` code blocks from a markdown file.
    Returns a list of (start_line_number, code_string).
    """
    content = markdown_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    
    blocks = []
    in_block = False
    current_block = []
    start_line = 0
    
    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```python") or stripped.startswith("```py"):
            in_block = True
            current_block = []
            start_line = idx + 1
        elif in_block and stripped == "```":
            in_block = False
            code_text = "\n".join(current_block)
            # Dedent code block to account for markdown list indentation
            dedented_code = textwrap.dedent(code_text)
            if dedented_code.strip():
                blocks.append((start_line, dedented_code))
            current_block = []
        elif in_block:
            current_block.append(line)
            
    return blocks


def verify_syntax(code: str, file_path: Path, start_line: int) -> Tuple[bool, str, ast.AST]:
    """
    Layer 1: Parses code with ast.parse to detect syntax and indentation errors.
    """
    try:
        tree = ast.parse(code, filename=str(file_path))
        return True, "", tree
    except SyntaxError as err:
        err_line = (start_line + err.lineno - 1) if err.lineno else start_line
        msg = f"SyntaxError at line {err_line}: {err.msg}"
        if err.text:
            msg += f"\n  --> {err.text.strip()}"
        return False, msg, None


def extract_imports(tree: ast.AST) -> List[Tuple[str, List[str]]]:
    """
    Extracts all import statements from the AST.
    Returns a list of (module_name, [imported_names]).
    """
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.name, []))
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            names = [alias.name for alias in node.names]
            imports.append((mod, names))
    return imports


def verify_imports(imports: List[Tuple[str, List[str]]], ignore_missing_optional: bool = False) -> List[str]:
    """
    Layer 2: Verifies that imported modules and symbols can be resolved.
    Skips local relative imports and lab-local companion files.
    """
    # Lab-specific local companion files created in multi-file capstone projects
    LOCAL_LAB_MODULES = {
        "tools", "custom_tools", "agent_setup", "my_module", "app", "agent",
        "webshop_data", "support_agent", "support_agent.agent", "threat_intel_agent",
        "mitigation_agent", "forensic_agent", "aegis_master", "common", "config",
        "firestore_provider", "user_simulator", "eval_helpers"
    }

    errors = []
    for mod_name, symbols in imports:
        # Skip empty module names or relative imports / lab-local companion files
        root_pkg = mod_name.split(".")[0] if mod_name else ""
        if not mod_name or mod_name.startswith(".") or root_pkg in LOCAL_LAB_MODULES or mod_name in LOCAL_LAB_MODULES:
            continue
            
        try:
            mod = importlib.import_module(mod_name)
            for sym in symbols:
                if sym == "*":
                    continue
                if not hasattr(mod, sym):
                    # Check if 'sym' is a submodule of 'mod_name' (e.g. from google.cloud import firestore, from vertexai import agent_engines)
                    try:
                        importlib.import_module(f"{mod_name}.{sym}")
                    except (ImportError, ModuleNotFoundError):
                        if not (ignore_missing_optional and any(p in f"{mod_name}.{sym}" for p in ["Workflow", "Context", "skills", "workflow"])):
                            errors.append(f"Symbol or submodule '{sym}' not found in module '{mod_name}'")
        except (ImportError, Exception) as e:
            err_str = str(e)
            # Check if this is an optional subsystem missing in local dev / specialized environment
            is_optional_extension = any(
                opt in err_str for opt in [
                    "No module named 'mcp'",
                    "No module named 'a2a'",
                    "No module named 'litellm'",
                    "No module named 'langchain_core'",
                    "No module named 'langchain_community'",
                    "No module named 'wikipedia'",
                    "No module named 'locust'",
                    "LiteLLM support requires",
                    "requires Python 3.10",
                    "google.adk.skills",
                    "google.adk.tools.skill_toolset",
                    "google.adk.workflow",
                ]
            ) or any(
                opt in mod_name for opt in [
                    "google.adk.skills",
                    "google.adk.tools.skill_toolset",
                    "google.adk.workflow",
                ]
            )
            if is_optional_extension and ignore_missing_optional:
                continue
                
            # If core ADK package is missing or renamed, flag it
            if mod_name.startswith("google.adk"):
                errors.append(f"Cannot import ADK module '{mod_name}': {e}")
            elif mod_name in ("pydantic", "fastapi", "uvicorn", "click") or not ignore_missing_optional:
                errors.append(f"Missing dependency '{mod_name}': {e}")
    return errors


def test_solution_file(file_path: Path, ignore_missing_optional: bool = False, verbose: bool = False) -> Dict[str, Any]:
    """
    Runs full verification on a single lab-solution.md file.
    """
    blocks = extract_python_blocks(file_path)
    result = {
        "file": file_path,
        "module": file_path.parent.name,
        "block_count": len(blocks),
        "passed": True,
        "errors": []
    }
    
    if not blocks:
        return result
        
    for block_idx, (start_line, code) in enumerate(blocks, 1):
        # Layer 1: Syntax
        ok, err_msg, tree = verify_syntax(code, file_path, start_line)
        if not ok:
            result["passed"] = False
            result["errors"].append(f"[Block {block_idx} @ L{start_line}] {err_msg}")
            continue
            
        # Layer 2: Imports
        imports = extract_imports(tree)
        import_errors = verify_imports(imports, ignore_missing_optional=ignore_missing_optional)
        if import_errors:
            result["passed"] = False
            for ie in import_errors:
                result["errors"].append(f"[Block {block_idx} @ L{start_line}] {ie}")
                
    return result


def main():
    parser = argparse.ArgumentParser(description="Test Python code blocks in ADK lab solutions.")
    parser.add_argument("--module", type=str, help="Target a specific module (e.g. module10)")
    parser.add_argument("--ignore-missing-optional", action="store_true", help="Ignore missing optional 3rd party packages in local dev")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print verbose output")
    args = parser.parse_args()
    
    repo_root = Path(__file__).resolve().parent.parent
    training_dir = repo_root / "training"
    
    if not training_dir.exists():
        print(f"Error: Training directory not found at {training_dir}", file=sys.stderr)
        sys.exit(1)
        
    solution_files = sorted(training_dir.glob("**/lab-solution.md"))
    if args.module:
        solution_files = [f for f in solution_files if args.module in f.parent.name]
        
    if not solution_files:
        print(f"No lab-solution.md files found matching criteria.")
        sys.exit(0)
        
    print("=" * 80)
    print("ADK Curriculum Solution Code Quality Suite")
    print("=" * 80)
    
    total = len(solution_files)
    passed_count = 0
    failed_count = 0
    
    for file_path in solution_files:
        res = test_solution_file(file_path, ignore_missing_optional=args.ignore_missing_optional, verbose=args.verbose)
        mod_name = res["module"]
        blocks = res["block_count"]
        
        if res["passed"]:
            passed_count += 1
            print(f"[PASS] {mod_name} ({blocks} code block{'s' if blocks != 1 else ''})")
        else:
            failed_count += 1
            print(f"[FAIL] {mod_name} ({blocks} code block{'s' if blocks != 1 else ''})")
            for err in res["errors"]:
                print(f"       ERROR: {err}")
                
    print("-" * 80)
    print(f"Summary: {passed_count}/{total} modules passed ({(passed_count/total)*100:.1f}%)")
    print("=" * 80)
    
    if failed_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
