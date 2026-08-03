"""
Code Explainer Module for Project Astra.
Generates architectural explanations and function call chain summaries using AST graphs and Knowledge Engine RAG context.
"""

from typing import Dict, Any, Optional
from app.models.repository import Repository
from app.models.symbol import Symbol
from app.utils.logger import logger


class CodeExplainer:
    """
    Architectural explainer converting AST graph structures into natural language explanations.
    """

    def explain_symbol(self, repo: Repository, symbol_name: str) -> str:
        """
        Explains the role, signature, and callers of a specific class or function.
        """
        matching = [s for s in repo.symbols.values() if s.name == symbol_name]
        if not matching:
            return f"Symbol '{symbol_name}' was not found in codebase index."

        sym = matching[0]
        lines = [
            f"### Symbol Explanation: `{sym.name}`",
            f"- **Type**: {sym.symbol_type.value}",
            f"- **File**: {sym.filepath} (Lines {sym.line_number}-{sym.end_line_number})",
            f"- **Signature**: `{sym.signature}`"
        ]

        if sym.docstring:
            lines.append(f"- **Docstring**: {sym.docstring.strip()}")

        # Callers
        callers = [caller for caller, callees in repo.call_graph.items() if symbol_name in callees]
        if callers:
            lines.append(f"- **Called by**: {', '.join(callers[:5])}")

        return "\n".join(lines)

    def generate_architecture_report(self, repo: Repository) -> str:
        """
        Generates an architectural summary report for an indexed project.
        """
        lines = [
            f"# Architecture Report: {repo.name}",
            f"- **Root Path**: `{repo.root_path}`",
            f"- **Total Python Files**: {len(repo.file_paths)}",
            f"- **Total Code Symbols**: {len(repo.symbols)}",
            f"- **Total Dependency Edges**: {len(repo.dependencies)}",
            f"- **Call Graph Nodes**: {len(repo.call_graph)}",
            "\n## Top Classes & Components:"
        ]

        classes = [s for s in repo.symbols.values() if s.symbol_type.value == "class"]
        for cls in classes[:10]:
            lines.append(f"- `{cls.name}` ({cls.filepath})")

        return "\n".join(lines)
