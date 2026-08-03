"""
Code Search Engine Module for Project Astra.
Provides structural and semantic search over indexed codebase symbols, methods, classes, and usages.
"""

from typing import List, Optional, Dict, Any
from app.models.repository import Repository
from app.models.symbol import Symbol, SymbolType
from app.utils.logger import logger


class CodeSearchEngine:
    """
    Search engine for querying code structure and symbol definitions.
    """

    def search_symbols(
        self,
        repo: Repository,
        query: str,
        symbol_type: Optional[SymbolType] = None,
        is_async: Optional[bool] = None
    ) -> List[Symbol]:
        """
        Searches symbols matching name query, type, or async modifier.
        """
        query_lower = query.lower()
        matches: List[Symbol] = []

        for sym in repo.symbols.values():
            if symbol_type and sym.symbol_type != symbol_type:
                continue

            if is_async is not None and sym.is_async != is_async:
                continue

            if query_lower in sym.name.lower() or (sym.docstring and query_lower in sym.docstring.lower()):
                matches.append(sym)

        logger.debug(f"Code search for '{query}' found {len(matches)} matching symbols.")
        return matches

    def find_usages(self, repo: Repository, symbol_name: str) -> List[Dict[str, Any]]:
        """
        Finds all callers and import locations referencing a given symbol.
        """
        usages: List[Dict[str, Any]] = []

        # Check call graph references
        for caller, callees in repo.call_graph.items():
            if symbol_name in callees:
                usages.append({
                    "usage_type": "call",
                    "caller": caller,
                    "target": symbol_name
                })

        # Check import edges
        for edge in repo.dependencies:
            if symbol_name in edge.target:
                usages.append({
                    "usage_type": "import",
                    "source": edge.source,
                    "target": edge.target,
                    "line_number": edge.line_number
                })

        return usages
