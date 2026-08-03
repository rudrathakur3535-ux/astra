"""
Unit tests for Day 10 Coding Intelligence Engine.
Tests ASTParser, SymbolExtractor, DependencyAnalyzer, CallGraphBuilder, RepositoryIndexer,
CodeSearchEngine, RefactoringEngine, CodeExplainer, and ProjectService.
"""

import os
import pytest
from typing import List

from app.models.symbol import Symbol, SymbolType
from app.models.dependency import DependencyEdge, DependencyType
from app.models.repository import Repository
from app.adapters.filesystem_adapter import FilesystemAdapter
from app.code.ast_parser import ASTParser
from app.code.symbol_extractor import SymbolExtractor
from app.code.dependency_analyzer import DependencyAnalyzer
from app.code.call_graph import CallGraphBuilder
from app.code.repository_indexer import RepositoryIndexer
from app.code.code_search import CodeSearchEngine
from app.code.refactoring_engine import RefactoringEngine
from app.code.code_explainer import CodeExplainer
from app.code.project_service import ProjectService


@pytest.fixture
def sample_python_file(tmp_path):
    py_file = tmp_path / "sample_service.py"
    code = """
import os
import sys

class BaseService:
    \"\"\"Base service docstring.\"\"\"
    def initialize(self) -> bool:
        return True

class CalculatorService(BaseService):
    \"\"\"Calculator service docstring.\"\"\"
    
    @staticmethod
    def add(a: int, b: int) -> int:
        return a + b

    def compute_all(self, val: int) -> int:
        res = self.add(val, 10)
        return res
"""
    py_file.write_text(code, encoding="utf-8")
    return str(py_file)


class TestASTParserAndSymbolExtractor:
    def test_ast_parsing(self, sample_python_file):
        adapter = FilesystemAdapter()
        code = adapter.read_code_file(sample_python_file)

        parser = ASTParser()
        tree, err = parser.parse_code(code, filename=sample_python_file)
        assert tree is not None
        assert err is None

    def test_symbol_extraction(self, sample_python_file):
        adapter = FilesystemAdapter()
        code = adapter.read_code_file(sample_python_file)
        parser = ASTParser()
        tree, _ = parser.parse_code(code, filename=sample_python_file)

        extractor = SymbolExtractor(filepath=sample_python_file)
        symbols = extractor.extract_symbols(tree)

        assert len(symbols) >= 5
        sym_names = [s.name for s in symbols]
        assert "BaseService" in sym_names
        assert "CalculatorService" in sym_names
        assert "add" in sym_names
        assert "compute_all" in sym_names

    def test_invalid_python_syntax_handling(self):
        parser = ASTParser()
        tree, err = parser.parse_code("def broken_syntax(:", filename="broken.py")
        assert tree is None
        assert err is not None
        assert "SyntaxError" in err


class TestDependencyAndCallGraph:
    def test_dependency_analysis(self, sample_python_file):
        adapter = FilesystemAdapter()
        code = adapter.read_code_file(sample_python_file)
        parser = ASTParser()
        tree, _ = parser.parse_code(code, filename=sample_python_file)
        extractor = SymbolExtractor(filepath=sample_python_file)
        symbols = extractor.extract_symbols(tree)

        analyzer = DependencyAnalyzer()
        edges = analyzer.analyze_dependencies(symbols)
        assert len(edges) >= 2
        edge_targets = [e.target for e in edges]
        assert "os" in edge_targets
        assert "sys" in edge_targets

    def test_circular_dependency_detection(self):
        analyzer = DependencyAnalyzer()
        edges = [
            DependencyEdge(source="module_a.py", target="module_b.py", dep_type=DependencyType.IMPORT),
            DependencyEdge(source="module_b.py", target="module_a.py", dep_type=DependencyType.IMPORT)
        ]
        cycles = analyzer.detect_circular_dependencies(edges)
        assert len(cycles) >= 1

    def test_call_graph_building(self, sample_python_file):
        adapter = FilesystemAdapter()
        code = adapter.read_code_file(sample_python_file)
        parser = ASTParser()
        tree, _ = parser.parse_code(code, filename=sample_python_file)

        builder = CallGraphBuilder()
        graph = builder.build_call_graph([(sample_python_file, tree)])
        assert "compute_all" in graph
        assert "add" in graph["compute_all"]


class TestRepositoryIndexerAndSearch:
    def test_repository_indexing(self, tmp_path, sample_python_file):
        indexer = RepositoryIndexer(port=FilesystemAdapter(index_dir=str(tmp_path / "index_db")))
        repo = indexer.index_repository(str(tmp_path))

        assert repo.name == tmp_path.name
        assert len(repo.file_paths) >= 1
        assert len(repo.symbols) >= 5

    def test_code_search_and_refactoring(self, tmp_path, sample_python_file):
        indexer = RepositoryIndexer(port=FilesystemAdapter(index_dir=str(tmp_path / "index_db")))
        repo = indexer.index_repository(str(tmp_path))

        search_engine = CodeSearchEngine()
        results = search_engine.search_symbols(repo, "CalculatorService", symbol_type=SymbolType.CLASS)
        assert len(results) == 1
        assert results[0].name == "CalculatorService"

        refactoring = RefactoringEngine()
        health = refactoring.analyze_repository_health(repo)
        assert "total_issues" in health


class TestProjectServiceFacade:
    def test_project_service_full_flow(self, tmp_path, sample_python_file):
        service = ProjectService(port=FilesystemAdapter(index_dir=str(tmp_path / "svc_index")))
        repo = service.index_project(str(tmp_path))

        # Symbol Search
        symbols = service.search_codebase(repo.name, "add")
        assert len(symbols) >= 1

        # Code explanation
        explanation = service.explain_code_symbol(repo.name, "CalculatorService")
        assert "CalculatorService" in explanation

        # Architecture Report
        report = service.generate_architecture_report(repo.name)
        assert "Architecture Report" in report
