"""
Workspace Context Model for Project Astra OS.
Represents VS Code project workspace state, open tabs, active task, and AST dependency graph.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import time


@dataclass
class WorkspaceContext:
    project_name: str
    root_path: str
    open_files: List[str] = field(default_factory=list)
    active_file: Optional[str] = None
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)
    recent_changes: List[str] = field(default_factory=list)
    indexed_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_name": self.project_name,
            "root_path": self.root_path,
            "open_files": self.open_files,
            "active_file": self.active_file,
            "total_dependencies_mapped": len(self.dependency_graph),
            "indexed_at": self.indexed_at
        }
