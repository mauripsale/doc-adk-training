# ADK Docs Migration Project Guidelines

## Core Mandates
- **Empirical Validation (ZERO TRUST):** After migrating or updating any module, you MUST perform a full empirical review using the `adk-student-evaluator`. 
    - This is NOT just a documentation check.
    - You MUST execute the **Simulation Step**: create a temporary directory, follow instructions exactly, and verify the code executes in a real (or mocked) runtime.
    - **Validation is only complete when artifacts (simulation directories and detailed reports) are physically verified on the filesystem.**
- **ADK 2.0 Object Patterns (API Accuracy):** Always use the simplified, modern accessors for ADK 2.0 internal objects.
    - **`LlmResponse`:** NEVER use `.candidates`. Use the direct **`.content`** attribute.
    - **`LlmRequest`:** Access prompt history via the **`.contents`** list.
    - **`Event`:** Use modern event types and properties (e.g., `is_final_response()`).
    - Verify these patterns by inspecting the installed package source code (`.venv`) if documentation is ambiguous.
- **Pedagogical Balance (Challenge vs. Solution):** Technical `lab.md` files MUST be designed as active learning challenges. 
    - NEVER provide full implementation code in a `lab.md`.
    - USE code skeletons with clear `TODO` comments.
    - PROVIDE conceptual hints and references to the Theory section instead of raw code.
    - ENSURE that the student must write the core ADK logic (e.g., node definitions, workflow edges, context access) themselves.
    - Full, runnable code is ONLY permitted in `lab-solution.md`.
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
