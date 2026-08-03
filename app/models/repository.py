"""
Repository Model for Project Astra.
Aggregates indexed symbols, dependency graph edges, call graph nodes, and repository metrics.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import time

from app.models.symbol import Symbol
from app.models.dependency import DependencyEdge


@dataclass
class Repository:
    """
    Graph representation of an indexed software repository.
    """
    name: str
    root_path: str
    symbols: Dict[str, Symbol] = field(default_factory=dict)
    dependencies: List[DependencyEdge] = field(default_factory=list)
    call_graph: Dict[str, List[str]] = field(default_factory=dict)
    file_paths: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "root_path": self.root_path,
            "total_files": len(self.file_paths),
            "total_symbols": len(self.symbols),
            "total_dependencies": len(self.dependencies),
            "call_graph_nodes": len(self.call_graph),
            "created_at": self.created_at
        }
