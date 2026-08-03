"""
Repository Indexer Module for Project Astra.
Scans Python project codebases, parses AST trees, extracts symbols, and constructs Repository graph objects.
"""

from typing import List, Tuple, Optional, Dict, Any
import os
import ast

from app.ports.project_port import ProjectPort
from app.adapters.filesystem_adapter import FilesystemAdapter
from app.code.ast_parser import ASTParser
from app.code.symbol_extractor import SymbolExtractor
from app.code.dependency_analyzer import DependencyAnalyzer
from app.code.call_graph import CallGraphBuilder
from app.models.repository import Repository
from app.models.symbol import Symbol
from app.utils.logger import logger


class RepositoryIndexer:
    """
    Main repository indexing pipeline for Project Astra.
    """

    def __init__(
        self,
        port: Optional[ProjectPort] = None,
        ast_parser: Optional[ASTParser] = None
    ):
        self.port = port or FilesystemAdapter()
        self.ast_parser = ast_parser or ASTParser()
        self.dep_analyzer = DependencyAnalyzer()
        self.call_graph_builder = CallGraphBuilder()

    def index_repository(self, root_dir: str) -> Repository:
        """
        Indexes an entire Python project directory into a Repository graph.
        """
        root_dir = os.path.abspath(root_dir)
        repo_name = os.path.basename(root_dir) or "project"
        logger.info(f"Starting repository indexing for '{repo_name}' at '{root_dir}'...")

        py_files = self.port.scan_python_files(root_dir)
        all_symbols: List[Symbol] = []
        ast_trees: List[Tuple[str, ast.AST]] = []

        for filepath in py_files:
            code = self.port.read_code_file(filepath)
            tree, err = self.ast_parser.parse_code(code, filename=filepath)
            if tree:
                ast_trees.append((filepath, tree))
                extractor = SymbolExtractor(filepath=filepath)
                symbols = extractor.extract_symbols(tree)
                all_symbols.extend(symbols)

        # Analyze dependencies
        dependencies = self.dep_analyzer.analyze_dependencies(all_symbols)

        # Build Call Graph
        call_graph = self.call_graph_builder.build_call_graph(ast_trees)

        # Map symbols by ID/Name
        symbol_dict = {f"{s.filepath}:{s.name}": s for s in all_symbols}

        repo = Repository(
            name=repo_name,
            root_path=root_dir,
            symbols=symbol_dict,
            dependencies=dependencies,
            call_graph=call_graph,
            file_paths=py_files
        )

        self.port.save_repository_index(repo)
        logger.info(f"Repository '{repo_name}' indexed: {len(py_files)} files, {len(all_symbols)} symbols, {len(dependencies)} dependency edges.")
        return repo
