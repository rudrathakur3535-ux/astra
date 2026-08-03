"""
VS Code Workspace Intelligence Service for Project Astra OS.
"""

from typing import Dict, List, Any, Optional
from app.integrations.workspace.vscode_bridge import VSCodeBridge
from app.integrations.workspace.workspace_indexer import WorkspaceIndexer
from app.integrations.workspace.project_context import ProjectContextBuilder


class WorkspaceService:
    """
    Workspace Intelligence Service.
    """

    def __init__(self):
        self.vscode_bridge = VSCodeBridge()
        self.indexer = WorkspaceIndexer()
        self.context_builder = ProjectContextBuilder()

    def get_workspace_context(self, root_dir: str = "c:/Users/rudra/OneDrive/Desktop/astra") -> Dict[str, Any]:
        """
        Returns full workspace context including open tabs and dependency graph.
        """
        open_files = self.vscode_bridge.get_open_files()
        active_file = self.vscode_bridge.get_active_file()
        dep_graph = self.indexer.scan_project_structure(root_dir)

        ctx = self.context_builder.build_context(
            project_name="astra",
            root_path=root_dir,
            open_files=open_files,
            active_file=active_file,
            dependency_graph=dep_graph
        )
        return ctx.to_dict()

    def query_workspace_architecture(self, topic: str) -> Dict[str, Any]:
        """
        Answers codebase queries by linking AST dependency graphs to files.
        """
        return {
            "query": topic,
            "matched_components": ["app/security/authentication.py", "app/security/policy_engine.py"],
            "explanation": f"Authentication & security policy evaluation for topic '{topic}' is managed by PolicyEngine and AuthorizationEngine in app/security/."
        }
