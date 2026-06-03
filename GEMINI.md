# ADK Docs Migration Project Guidelines

## Core Mandates
- **Empirical Validation (ZERO TRUST):** After migrating or updating any module, you MUST perform a full empirical review using the `adk-student-evaluator`. 
    - This is NOT just a documentation check.
    - You MUST execute the **Simulation Step**: create a temporary directory, follow instructions exactly, and verify the code executes in a real (or mocked) runtime.
    - **Validation is only complete when artifacts (simulation directories and detailed reports) are physically verified on the filesystem.**
- **ADK 2.0 Patterns:** Always use the graph-based Workflow Runtime patterns (e.g., `@node`, `ctx.run_node()`, `App(root_agent=...)`). Legacy patterns (ADK 1.x) are strictly forbidden unless explicitly noted.
- **Pedagogical Consistency (Solution Hints):** Every technical `lab.md` MUST include a "Hidden Solution" section at the end.
    - It must contain a Base64-encoded hint of the solution path.
    - It must contain a direct link to the solution hidden via CSS opacity (0.01) to prevent accidental spoilers while enabling quick access for instructors.
- **Python Version:** Target Python 3.10+ as per the migration plan.

## How to run the Student Evaluator
If the `adk` command is not in the PATH, use:
```bash
python3 -m google.adk.cli run .agent/skills/adk-student-evaluator --input_path <path_to_lab_or_solution>
```
Always verify the resulting `simulation_<module>` directory exists and contains functional code.
