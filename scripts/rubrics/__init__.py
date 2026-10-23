"""
Rubrics Registry for ADK Curriculum Lab Grader
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Any


@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str
    hint: Optional[str] = None
    theory_ref: Optional[str] = None


@dataclass
class ModuleRubric:
    module_id: str
    title: str
    required_imports: List[str] = field(default_factory=list)
    forbidden_patterns: List[Tuple[str, str]] = field(default_factory=list)
    required_symbols: List[str] = field(default_factory=list)
    expected_models: List[str] = field(default_factory=lambda: ["gemini-3.5-flash"])
    theory_ref: str = "Theory & Overview"
    hints: Dict[str, str] = field(default_factory=dict)
    has_code: bool = True
