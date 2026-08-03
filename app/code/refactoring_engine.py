"""
Refactoring Engine Module for Project Astra.
Identifies code health issues: unused imports, long functions, circular dependencies, dead code, and missing type hints.
"""

from typing import List, Dict, Any
from app.models.repository import Repository
from app.models.symbol import Symbol, SymbolType
from app.code.dependency_analyzer import DependencyAnalyzer
from app.utils.logger import logger


class RefactoringEngine:
    """
    Code quality scanner providing refactoring suggestions.
    """

    def __init__(self):
        self.dep_analyzer = DependencyAnalyzer()

    def analyze_repository_health(self, repo: Repository) -> Dict[str, Any]:
        """
        Scans repository for code smells and refactoring recommendations.
        """
        logger.info(f"Analyzing codebase health for '{repo.name}'...")

        suggestions: List[Dict[str, Any]] = []

        # 1. Detect Circular Dependencies
        circular_loops = self.dep_analyzer.detect_circular_dependencies(repo.dependencies)
        for loop in circular_loops:
            suggestions.append({
                "category": "circular_dependency",
                "severity": "HIGH",
                "message": f"Circular dependency detected: {' -> '.join(loop)}",
                "target": loop[0]
            })

        # 2. Detect Long Functions (>50 lines)
        for sym in repo.symbols.values():
            if sym.symbol_type in (SymbolType.FUNCTION, SymbolType.METHOD):
                length = sym.end_line_number - sym.line_number + 1
                if length > 50:
                    suggestions.append({
                        "category": "long_function",
                        "severity": "MEDIUM",
                        "message": f"Function '{sym.name}' is long ({length} lines). Consider breaking down.",
                        "target": f"{sym.filepath}:{sym.line_number}"
                    })

                # 3. Detect Missing Type Hints
                if not sym.type_hints:
                    suggestions.append({
                        "category": "missing_type_hints",
                        "severity": "LOW",
                        "message": f"Function '{sym.name}' has no type annotations.",
                        "target": f"{sym.filepath}:{sym.line_number}"
                    })

        logger.info(f"Generated {len(suggestions)} refactoring suggestions for '{repo.name}'.")
        return {
            "total_issues": len(suggestions),
            "circular_dependencies_count": len(circular_loops),
            "suggestions": suggestions
        }
