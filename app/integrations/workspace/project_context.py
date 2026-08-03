"""
Project Context Builder for Project Astra OS.
Unifies VS Code open files, active tasks, memory, and knowledge engine context.
"""

from typing import Dict, List, Any, Optional
from app.models.workspace_context import WorkspaceContext


class ProjectContextBuilder:
    """
    Builds unified project context payloads for AI reasoning.
    """

    def build_context(
        self,
        project_name: str = "astra",
        root_path: str = "c:/Users/rudra/OneDrive/Desktop/astra",
        open_files: Optional[List[str]] = None,
        active_file: Optional[str] = None,
        dependency_graph: Optional[Dict[str, List[str]]] = None
    ) -> WorkspaceContext:
        """
        Constructs a complete WorkspaceContext model.
        """
        return WorkspaceContext(
            project_name=project_name,
            root_path=root_path,
            open_files=open_files or [],
            active_file=active_file,
            dependency_graph=dependency_graph or {}
        )
